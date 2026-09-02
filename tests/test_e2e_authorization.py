"""B 组正式授权链路审计（§最终验证 / §10 提交 6b）。

目标：对「确认包 ↔ state 授权 ↔ HTML 三者同版本、同 instance、同 generation_path」
的授权链路做端到端审计。八类画布各有一份最小 fixture（`tests/fixtures/e2e/{canvas}/`，
布局 `modules/*.md` + `state.json` + `output/*.html`），按 agent 画布注册表的
`audit_type` / `page_type` 取 CLI 参数跑正式授权链路审计。

fixture 的 output HTML 为 canvas-render Skill（LLM 渲染）产出的正式成品：
参照 examples 模板 + 用 retail-demo 确认包内容填充 + 注入授权 canvas-data，
经 `audit_canvas_html.py` 验证 PASS 后入库。测试不新增渲染脚本、不伪造成品 HTML。

A 组 / B 组区别：
- A 组（模板自审计，见 test_audit_canvas_html.py 等）：模板版面结构 / Template Gate。
- B 组（本文件）：确认包 ↔ state ↔ HTML 的授权链路一致性，含反向用例。
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

# 八类画布正式授权链路审计配置（CLI 参数值取自 agent 注册表 audit_type / page_type；
# canvas_type 为 HTML `canvas-data.canvas_type` 期望值，GC 为 golden-circle / CLI gc 双值）。
E2E_CANVASES: dict[str, dict[str, str | None]] = {
    "gc": {
        "fixture": "gc",
        "source": "modules/GC-retail-demo-v1.md",
        "html": "output/gc-canvas-retail-demo.html",
        "state": "state.json",
        "state_unauthorized": "state-unauthorized.json",
        "instance": "retail-demo",
        "cli": ["--type", "gc"],
        "template": None,
        "canvas_type": "golden-circle",
    },
    "hmw": {
        "fixture": "hmw",
        "source": "modules/HMW-retail-demo-v1.md",
        "html": "output/hmw-canvas-retail-demo.html",
        "state": "state.json",
        "state_unauthorized": "state-unauthorized.json",
        "instance": "retail-demo",
        "cli": ["--type", "hmw"],
        "template": "skills/canvas-render/examples/hmw-canvas.html",
        "canvas_type": "hmw",
    },
    "persona": {
        "fixture": "persona",
        "source": "modules/PERSONA-retail-demo-v1.md",
        "html": "output/persona-canvas-retail-demo.html",
        "state": "state.json",
        "state_unauthorized": "state-unauthorized.json",
        "instance": "retail-demo",
        "cli": ["--type", "persona"],
        "template": "skills/canvas-render/examples/user-persona-canvas.html",
        "canvas_type": "persona",
    },
    "journey": {
        "fixture": "journey",
        "source": "modules/JOURNEY-retail-demo-v1.md",
        "html": "output/journey-canvas-retail-demo.html",
        "state": "state.json",
        "state_unauthorized": "state-unauthorized.json",
        "instance": "retail-demo",
        "cli": ["--type", "journey"],
        "template": "skills/canvas-render/examples/user-journey-canvas.html",
        "canvas_type": "journey",
    },
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
    "mvl": {
        "fixture": "mvl",
        "source": "modules/M1-v1.md",
        "html": "output/module-1-canvas.html",
        "state": "state.json",
        "state_unauthorized": "state-unauthorized.json",
        "instance": None,  # module-detail 无 instance，以 body data-module 标识
        "cli": ["--type", "mvl"],
        "template": None,
        "canvas_type": "mvl",
    },
}


def _audit(rel_html: Path, rel_source: Path, rel_state: Path, spec: dict) -> subprocess.CompletedProcess[str]:
    cmd = [
        PYTHON, str(AUDIT),
        str(rel_html),
        "--source", str(rel_source),
        "--state", str(rel_state),
    ]
    if spec.get("instance"):
        cmd += ["--instance", str(spec["instance"])]
    cmd += list(spec["cli"])
    if spec.get("template"):
        cmd += ["--template", str(REPO_ROOT / spec["template"])]
    return subprocess.run(cmd, capture_output=True, text=True)


def _html_canvas_type(spec: dict) -> str:
    import re

    html = (E2E / str(spec["fixture"]) / str(spec["html"])).read_text(encoding="utf-8")
    match = re.search(r'<script[^>]*id="canvas-data"[^>]*>(.*?)</script>', html, re.DOTALL)
    assert match, f"{spec['fixture']} HTML 缺少 canvas-data"
    data = json.loads(match.group(1).strip())
    return str(data.get("canvas_type"))


@pytest.mark.parametrize("canvas_id", sorted(E2E_CANVASES))
def test_authorized_chain_passes(canvas_id: str) -> None:
    """已授权 fixture（state render_authorized=true）必须通过正式授权链路审计。"""
    spec = E2E_CANVASES[canvas_id]
    base = E2E / str(spec["fixture"])
    result = _audit(base / str(spec["html"]), base / str(spec["source"]), base / str(spec["state"]), spec)
    assert result.returncode == 0, f"{canvas_id} 授权链路应 PASS：{result.stdout + result.stderr}"


@pytest.mark.parametrize("canvas_id", sorted(E2E_CANVASES))
def test_unauthorized_chain_fails(canvas_id: str) -> None:
    """未授权 fixture（render_authorized=false）必须 FAIL——反向用例。"""
    spec = E2E_CANVASES[canvas_id]
    base = E2E / str(spec["fixture"])
    result = _audit(
        base / str(spec["html"]),
        base / str(spec["source"]),
        base / str(spec["state_unauthorized"]),
        spec,
    )
    assert result.returncode != 0, f"{canvas_id} 未授权链路必须 FAIL"


@pytest.mark.parametrize("canvas_id", sorted(E2E_CANVASES))
def test_html_canvas_type_matches_state(canvas_id: str) -> None:
    """HTML canvas-data.canvas_type 必须与注册表语义一致（GC 为 golden-circle / CLI gc 双值）。"""
    spec = E2E_CANVASES[canvas_id]
    assert _html_canvas_type(spec) == spec["canvas_type"], (
        f"{canvas_id} HTML canvas-data.canvas_type 与注册表不一致"
    )


def test_fixture_layout_complete() -> None:
    """八类画布 fixture 必须三段式齐备（modules / state.json / output）。"""
    assert set(E2E_CANVASES) == {"gc", "hmw", "persona", "journey", "mvl", "maau", "v2c-vac", "5w"}
    for canvas_id, spec in E2E_CANVASES.items():
        base = E2E / str(spec["fixture"])
        for rel in (spec["source"], spec["state"], spec["html"]):
            assert (base / rel).is_file(), f"{canvas_id} 缺 {rel}"
        assert (base / str(spec["state_unauthorized"])).is_file(), f"{canvas_id} 缺未授权 state"
