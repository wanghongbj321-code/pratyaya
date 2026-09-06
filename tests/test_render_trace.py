"""render-trace.jsonl 渲染计时插桩与 L1 workflow 结构签名断言测试（v3.6.2）。

覆盖（对应执行计划 §4 / F3 缺口）：
- L1 trace 落盘：PASS 与 FAIL 均向被检 HTML 同目录 `.render-trace.jsonl` 追加一条
  `audit_l1` 记录（含 exit_code / status / duration_ms / html 绝对路径）；
- L1 trace 静默失败：被检目录不可写时不反噬审计退出码、不产生 trace、无异常输出；
- L1 增强断言（自 L2 下沉）：workflow 形态的 `quality-panel` 存在、`bpmn-legend` 恰好 1 个、
  `bpmn-flow` SVG 存在——正样本 PASS、三组负样本 FAIL；
- L2 trace（可选增强，Q4）：node + puppeteer-core 可用时运行 `canvas-smoke.mjs`，断言
  `audit_l2` 记录落盘且 status 与退出码映射一致；环境缺失 skipif（不视为回归）。
- noflow 外溢防护：不新增重复用例——既有 `test_two_phase_render.py` / `test_audit_maau.py`
  的 noflow PASS 用例已证明增强断言未外溢（L1 增强位于 `audit_workflow_flow()`，
  无 `#workflow-flow` 时提前 return）。
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT = REPO_ROOT / "skills" / "canvas-render" / "scripts" / "audit_canvas_html.py"
SMOKE = REPO_ROOT / "skills" / "canvas-render" / "scripts" / "canvas-smoke.mjs"
MAAU_HTML = REPO_ROOT / "tests" / "fixtures" / "maau" / "maau-global-canvas-retail-demo.html"
PYTHON = sys.executable

TRACE_NAME = ".render-trace.jsonl"


def run_audit(html: Path) -> subprocess.CompletedProcess:
    # html 必须为首个位置参数：audit trace 解析 `sys.argv[1]` 的第一个非 -- 参数
    return subprocess.run(
        [
            PYTHON, str(AUDIT), str(html),
            "--artifact-policy", "legacy",
            "--type", "mvl",
            "--page-type", "global",
        ],
        capture_output=True,
        text=True,
    )


def copy_fixture(tmp_path: Path) -> Path:
    out = tmp_path / "canvas.html"
    shutil.copyfile(MAAU_HTML, out)
    return out


def mutate_fixture(tmp_path: Path, old: str, new: str) -> Path:
    out = tmp_path / "canvas.html"
    text = MAAU_HTML.read_text(encoding="utf-8")
    assert old in text, f"mutate target not found: {old}"
    out.write_text(text.replace(old, new), encoding="utf-8")
    return out


def read_trace(directory: Path) -> list[dict]:
    trace_path = directory / TRACE_NAME
    if not trace_path.exists():
        return []
    return [
        json.loads(line)
        for line in trace_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _has_puppeteer_core() -> bool:
    if os.environ.get("PUPPETEER_CORE_PATH") and Path(os.environ["PUPPETEER_CORE_PATH"]).exists():
        return True
    if (SMOKE.parent / "node_modules" / "puppeteer-core").exists():
        return True
    home = Path.home()
    for sub in (".workbuddy", ".codebuddy"):
        for rel in (
            "binaries/node/workspace/node_modules/puppeteer-core",
            "plugins/cache/node/workspace/node_modules/puppeteer-core",
        ):
            if (home / sub / rel).exists():
                return True
    return False


class TestL1TraceAppend:
    def test_l1_trace_written_on_pass(self, tmp_path: Path) -> None:
        html = copy_fixture(tmp_path)
        result = run_audit(html)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "PASS" in result.stdout

        records = read_trace(tmp_path)
        assert len(records) == 1, records
        rec = records[0]
        assert rec["stage"] == "audit_l1"
        assert rec["tool"] == "audit_canvas_html.py"
        assert rec["html"] == str(html.resolve())
        assert rec["exit_code"] == 0
        assert rec["status"] == "PASS"
        assert rec["duration_ms"] >= 0
        assert rec["started_at"] and rec["ended_at"]

    def test_l1_trace_written_on_fail(self, tmp_path: Path) -> None:
        html = mutate_fixture(tmp_path, 'class="bpmn-legend"', 'class="bpmn-legend-removed"')
        result = run_audit(html)
        assert result.returncode != 0

        records = read_trace(tmp_path)
        assert len(records) == 1, records
        rec = records[0]
        assert rec["stage"] == "audit_l1"
        assert rec["exit_code"] == result.returncode
        assert rec["status"] == "FAIL"

    def test_l1_trace_write_failure_is_silent(self, tmp_path: Path) -> None:
        html = copy_fixture(tmp_path)
        os.chmod(tmp_path, 0o500)  # 目录只读：trace 写入失败须静默
        try:
            result = run_audit(html)
        finally:
            os.chmod(tmp_path, 0o700)
        assert result.returncode == 0, result.stdout + result.stderr
        assert not (tmp_path / TRACE_NAME).exists()
        assert "Traceback" not in result.stderr


class TestL1StructureSignature:
    def test_enhanced_signature_passes_on_workflow_fixture(self, tmp_path: Path) -> None:
        html = copy_fixture(tmp_path)
        result = run_audit(html)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "PASS" in result.stdout

    @pytest.mark.parametrize(
        ("old", "new", "expect"),
        [
            (
                'class="bpmn-legend"',
                'class="bpmn-legend-removed"',
                "bpmn-legend 应恰好 1 个",
            ),
            (
                'id="quality-panel"',
                'id="quality-panel-removed"',
                "缺少治理面板",
            ),
            (
                'class="bpmn-flow" role="img"',
                'class="bpmn-flow-removed" role="img"',
                "缺少 BPMN SVG",
            ),
        ],
    )
    def test_enhanced_signature_negative(self, tmp_path: Path, old: str, new: str, expect: str) -> None:
        html = mutate_fixture(tmp_path, old, new)
        result = run_audit(html)
        assert result.returncode != 0
        assert "WORKFLOW_FLOW" in result.stdout
        assert expect in result.stdout


@pytest.mark.skipif(
    not shutil.which("node") or not _has_puppeteer_core(),
    reason="Q4：node 或 puppeteer-core 缺失，L2 trace 用例跳过（不视为回归）",
)
class TestL2Trace:
    def test_l2_trace_record_matches_exit_code(self, tmp_path: Path) -> None:
        html = copy_fixture(tmp_path)
        try:
            result = subprocess.run(
                [
                    "node", str(SMOKE), str(html),
                    "--type", "mvl",
                    "--page-type", "global",
                    "--workflow-variant", "workflow",
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            pytest.skip("canvas-smoke 执行超时（本机 L2 环境异常，不视为回归）")

        records = read_trace(tmp_path)
        assert records, "L2 运行后应有 .render-trace.jsonl"
        rec = records[-1]
        assert rec["stage"] == "audit_l2"
        assert rec["tool"] == "canvas-smoke.mjs"
        assert rec["html"] == str(html.resolve())
        assert rec["exit_code"] == result.returncode
        expected = {0: "PASS", 2: "DEGRADED"}.get(result.returncode, "FAIL")
        assert rec["status"] == expected
        assert rec["workflow_variant"] == "workflow"
