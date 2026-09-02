"""B 组正式授权链路审计（§最终验证 / §10 提交 6b）。

目标：对「确认包 ↔ state 授权 ↔ HTML 三者同版本、同 instance、同 generation_path」
的授权链路做端到端审计。本文件只复用仓库**已有人工成品 sample**（5w / v2c-vac /
maau 三段式，位于 `tests/fixtures/e2e/{canvas}/`），不新增渲染脚本、不伪造成品 HTML。

A 组 / B 组区别：
- A 组（模板自审计，见 test_audit_canvas_html.py 等）：模板版面结构 / Template Gate。
- B 组（本文件）：确认包 ↔ state ↔ HTML 的授权链路一致性，含反向用例。

缺成品的画布（gc / hmw / persona / journey / mvl 模块页）显式 skip 并标注原因：
`test_audit_canvas_html.py` 文档记载——正式成品 HTML 只能由 canvas-render Skill
（LLM）人工生成，无法作为稳定自动化输入；examples/ 模板仅为结构骨架，content
gate 会因缺 content-mapping / sections 而 FAIL（GC 已实测）。待各画布经 canvas-render
Skill 产出成品并入库 `tests/fixtures/e2e/{canvas}/` 后移除 skip。
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT = REPO_ROOT / "skills" / "canvas-render" / "scripts" / "audit_canvas_html.py"
E2E = REPO_ROOT / "tests" / "fixtures" / "e2e"
PYTHON = sys.executable

# 各画布正式授权链路审计 CLI 参数（值与 agent 注册表 audit_type / page_type 一致）。
E2E_CANVASES: dict[str, dict[str, str]] = {
    "5w": {
        "fixture": "5w",
        "source": "modules/5W-sample-5w-v1.md",
        "html": "output/5w-canvas-sample-5w.html",
        "state": "state.json",
        "state_unauthorized": "state-unauthorized.json",
        "instance": "sample-5w",
        "cli": ["--type", "5w"],
        "template": "skills/canvas-render/examples/5w-canvas.html",
        "canvas_type": "5w",
    },
    "v2c-vac": {
        "fixture": "v2c-vac",
        "source": "modules/V2C-VAC-sample-vac-v1.md",
        "html": "output/v2c-vac-canvas-sample-vac.html",
        "state": "state.json",
        "state_unauthorized": "state-unauthorized.json",
        "instance": "sample-vac",
        "cli": ["--type", "v2c-vac"],
        "template": "skills/canvas-render/examples/v2c-value-attribution-canvas.html",
        "canvas_type": "v2c-vac",
    },
    "maau": {
        "fixture": "maau",
        "source": "modules/MAAU-retail-demo-v1.md",
        "html": "output/maau-global-canvas-retail-demo.html",
        "state": "state.json",
        "state_unauthorized": "state-unauthorized.json",
        "instance": "retail-demo",
        "cli": ["--type", "mvl", "--page-type", "global", "--generation-path", "transcript-direct"],
        "template": None,
        "canvas_type": "mvl",
    },
}

# 缺正式成品 HTML 的画布（需 canvas-render Skill 人工产出后入库）。
SKIPPED_CANVASES: dict[str, str] = {
    "gc": "缺 canvas-render 成品 HTML：examples/goden-circle-canvas.html 为结构骨架，content gate 缺 canvas-header / sections（实测 FAIL）",
    "hmw": "缺 canvas-render 成品 HTML：examples/hmw-canvas.html 为结构骨架（test_audit_canvas_html.py 文档明确正式成品须人工生成）",
    "persona": "缺 canvas-render 成品 HTML：examples/user-persona-canvas.html 为结构骨架",
    "journey": "缺 canvas-render 成品 HTML：examples/user-journey-canvas.html 为结构骨架",
    "mvl": "缺 canvas-render 成品 HTML：examples/mvl-canvas/module-N-canvas.html 为结构骨架（6 模块各需成品）",
}


def _audit(rel_html: Path, rel_source: Path, rel_state: Path, spec: dict[str, str]) -> subprocess.CompletedProcess[str]:
    cmd = [
        PYTHON, str(AUDIT),
        str(rel_html),
        "--source", str(rel_source),
        "--state", str(rel_state),
        "--instance", spec["instance"],
        *spec["cli"],
    ]
    if spec.get("template"):
        cmd += ["--template", str(REPO_ROOT / spec["template"])]
    return subprocess.run(cmd, capture_output=True, text=True)


def _html_canvas_type(spec: dict[str, str]) -> str:
    import re

    html = (E2E / spec["fixture"] / spec["html"]).read_text(encoding="utf-8")
    match = re.search(r'<script[^>]*id="canvas-data"[^>]*>(.*?)</script>', html, re.DOTALL)
    assert match, f"{spec['fixture']} HTML 缺少 canvas-data"
    data = json.loads(match.group(1).strip())
    return str(data.get("canvas_type"))


@pytest.mark.parametrize("canvas_id", sorted(E2E_CANVASES))
def test_authorized_chain_passes(canvas_id: str) -> None:
    """已授权 fixture（state render_authorized=true）必须通过正式授权链路审计。"""
    spec = E2E_CANVASES[canvas_id]
    base = E2E / spec["fixture"]
    result = _audit(base / spec["html"], base / spec["source"], base / spec["state"], spec)
    assert result.returncode == 0, f"{canvas_id} 授权链路应 PASS：{result.stdout + result.stderr}"


@pytest.mark.parametrize("canvas_id", sorted(E2E_CANVASES))
def test_unauthorized_chain_fails(canvas_id: str) -> None:
    """未授权 fixture（render_authorized=false）必须 FAIL——反向用例。"""
    spec = E2E_CANVASES[canvas_id]
    base = E2E / spec["fixture"]
    result = _audit(base / spec["html"], base / spec["source"], base / spec["state_unauthorized"], spec)
    assert result.returncode != 0, f"{canvas_id} 未授权链路必须 FAIL"


@pytest.mark.parametrize("canvas_id", sorted(E2E_CANVASES))
def test_html_canvas_type_matches_state(canvas_id: str) -> None:
    """HTML canvas-data.canvas_type 必须与注册表/state 语义一致（防 GC 双值错写类回归）。"""
    spec = E2E_CANVASES[canvas_id]
    assert _html_canvas_type(spec) == spec["canvas_type"], (
        f"{canvas_id} HTML canvas-data.canvas_type 与注册表不一致"
    )


def test_fixture_layout_complete() -> None:
    """已提供 fixture 的画布必须三段式齐备（modules / state.json / output）。"""
    for canvas_id, spec in E2E_CANVASES.items():
        base = E2E / spec["fixture"]
        for rel in (spec["source"], spec["state"], spec["html"]):
            assert (base / rel).is_file(), f"{canvas_id} 缺 {rel}"


@pytest.mark.parametrize("canvas_id", sorted(SKIPPED_CANVASES))
def test_skipped_canvases_await_canvas_render_artifact(canvas_id: str) -> None:
    """缺 canvas-render 成品 HTML 的画布：占位标注，待成品入库后移除 skip。"""
    pytest.skip(f"{canvas_id}: {SKIPPED_CANVASES[canvas_id]}")
