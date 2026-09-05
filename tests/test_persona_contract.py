"""Persona 画布工作流和契约的回归测试。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT = REPO_ROOT / "skills" / "canvas-render" / "scripts" / "audit_canvas_html.py"
TEMPLATE = REPO_ROOT / "skills" / "canvas-render" / "examples" / "user-persona-canvas.html"
GATE = REPO_ROOT / "skills" / "persona-gate" / "SKILL.md"
AGENT = REPO_ROOT / "agents" / "pratyaya.md"


def test_persona_template_passes_its_own_template_gate() -> None:
    result = subprocess.run(
        [sys.executable, str(AUDIT), "--artifact-policy", "legacy", str(TEMPLATE), "--type", "persona", "--template", str(TEMPLATE)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_persona_gate_is_advisory_and_uses_confirmed_override_boundary() -> None:
    text = GATE.read_text(encoding="utf-8")

    assert "PERSONA-GATE-01" in text and "PERSONA-GATE-06" in text
    assert "更新 `state.json`" not in text
    assert "写入 `persona.gate_recommendation`" not in text
    assert "PERSONA-GATE-03 / 04" in text
    assert "P3 / P4 / P5 / P6" not in text


def test_agent_has_persona_route_initialization_and_phase() -> None:
    text = AGENT.read_text(encoding="utf-8")

    for required in ("Phase Persona", "PERSONA-{slug}-gaps.md", "state.json.persona.{slug}", "MVL / 黄金圈 / HMW / 用户画像"):
        assert required in text, f"agent missing Persona workflow element: {required}"


def test_contract_checker_registers_persona_rules() -> None:
    checker = REPO_ROOT / "scripts" / "check_contract_consistency.py"
    result = subprocess.run(
        [sys.executable, str(checker), "--list"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    assert result.returncode == 0
    assert "PERSONA_SKILL_PATH" in result.stdout
