"""Persona Canvas 的内容/授权 Gate 回归测试。"""

from __future__ import annotations

import json
import re
from pathlib import Path

from scripts.audit_canvas_html import PERSONA_CONTRACT, audit, persona_source_identity


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = REPO_ROOT / "examples" / "canvas-html" / "user-persona-canvas.html"
STATE_GATE_PASS = REPO_ROOT / "tests" / "fixtures" / "state" / "persona-gate-pass.json"
STATE_OVERRIDE = REPO_ROOT / "tests" / "fixtures" / "state" / "persona-override.json"

PERSONA_SECTIONS = (
    "canvas-headline",
    "persona-name", "persona-gender", "persona-age", "persona-location", "persona-education",
    "persona-job-title", "persona-industry", "persona-family-status", "persona-income",
    "persona-description", "persona-goals-needs", "persona-behaviors", "persona-pain-points",
    "persona-motivation", "persona-decision-factors",
    "persona-quality-evidence", "persona-quality-concrete", "persona-quality-voice",
    "persona-quality-representative", "quality-panel", "local-notes", "canvas-data",
)


def write_formal_persona(tmp_path: Path, auth: dict | None) -> Path:
    """从示例生成只用于审计的最小正式 Persona 页面。"""
    text = TEMPLATE.read_text(encoding="utf-8")
    text = text.replace('<header class="canvas-head">', '<header class="canvas-head" id="canvas-header">')
    data: dict[str, object] = {
        "canvas_type": "persona",
        "version": "1",
        "sections": {section: {} for section in PERSONA_SECTIONS},
    }
    if auth is not None:
        data["auth"] = auth
    text = re.sub(
        r'(<script type="application/json" id="canvas-data">).*?(</script>)',
        lambda match: f"{match.group(1)}\n{json.dumps(data, ensure_ascii=False)}\n{match.group(2)}",
        text,
        count=1,
        flags=re.DOTALL,
    )
    output = tmp_path / "persona.html"
    output.write_text(text, encoding="utf-8")
    return output


def test_persona_formal_page_requires_canvas_data_auth(tmp_path: Path) -> None:
    page = write_formal_persona(tmp_path, auth=None)

    findings = audit(page, PERSONA_CONTRACT, STATE_GATE_PASS, None, "persona")

    assert any(finding.code == "AUTH" for finding in findings)


def test_persona_override_requires_visible_caveat(tmp_path: Path) -> None:
    state = json.loads(STATE_OVERRIDE.read_text(encoding="utf-8"))["persona"]
    page = write_formal_persona(
        tmp_path,
        {
            "gate_recommendation": state["gate_recommendation"],
            "render_authorized": state["render_authorized"],
            "confirmation_mode": state["confirmation_mode"],
            "override_audit": state["override_audit"],
        },
    )

    findings = audit(page, PERSONA_CONTRACT, STATE_OVERRIDE, None, "persona")

    assert any(finding.code == "CAVEAT" for finding in findings)


def test_persona_source_identity_accepts_design_confirmation_title(tmp_path: Path) -> None:
    package = tmp_path / "PERSONA-v1.md"
    package.write_text("# User Persona 确认包 v1\n", encoding="utf-8")

    assert persona_source_identity(package) == ("PERSONA", "v1")


def test_persona_formal_page_rejects_source_content_drift(tmp_path: Path) -> None:
    state = json.loads(STATE_GATE_PASS.read_text(encoding="utf-8"))["persona"]
    page = write_formal_persona(
        tmp_path,
        {
            "gate_recommendation": state["gate_recommendation"],
            "render_authorized": state["render_authorized"],
            "confirmation_mode": state["confirmation_mode"],
            "override_audit": state.get("override_audit"),
        },
    )
    html = page.read_text(encoding="utf-8").replace(
        'id="persona-name" contenteditable="true"></span>',
        'id="persona-name" contenteditable="true">错误姓名</span>',
    )
    page.write_text(html, encoding="utf-8")
    package = tmp_path / "PERSONA-v1.md"
    package.write_text(
        "# User Persona 确认包 v1\n\n"
        "### 6. 9 基本信息 + 6 宫格\n\n"
        "| 字段 | 内容 | 来源引用 |\n|---|---|---|\n| name（姓名） | 正确姓名 | Key Points 1 |\n",
        encoding="utf-8",
    )

    findings = audit(page, PERSONA_CONTRACT, STATE_GATE_PASS, package, "persona")

    assert any(finding.code == "CONTENT_MAPPING" for finding in findings)
