"""Journey Canvas HTML 静态审计测试。

覆盖 User Journey 一等公民画布的 render contract、动态阶段规则与 Template Gate。
测试只使用静态模板和 fixture，不引入渲染脚本。
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT = REPO_ROOT / "skills" / "canvas-render" / "scripts" / "audit_canvas_html.py"
TEMPLATE = REPO_ROOT / "skills" / "canvas-render" / "examples" / "user-journey-canvas.html"
PACKAGE = REPO_ROOT / "tests" / "fixtures" / "journey" / "JOURNEY-v1.md"
STATE = REPO_ROOT / "tests" / "fixtures" / "state" / "journey-gate-pass.json"
OVERRIDE_STATE = REPO_ROOT / "tests" / "fixtures" / "journey" / "state-override.json"
FAULT_CASES = REPO_ROOT / "tests" / "fixtures" / "journey" / "fault-cases.json"
PYTHON = sys.executable


def run_audit(html: Path, *extra: str) -> subprocess.CompletedProcess:
    cmd = [PYTHON, str(AUDIT), str(html), "--type", "journey", "--template", str(TEMPLATE), *extra]
    return subprocess.run(cmd, capture_output=True, text=True)


def copy_template(tmp_path: Path, name: str = "journey.html") -> Path:
    shared_dir = tmp_path / "shared"
    shared_dir.mkdir(exist_ok=True)
    shutil.copy2(TEMPLATE.parent / "shared" / "canvas-theme.css", shared_dir / "canvas-theme.css")
    out = tmp_path / name
    out.write_text(TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")
    return out


def replace_canvas_data(html: Path, data: dict) -> None:
    text = html.read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    text = re.sub(
        r'(<script type="application/json" id="canvas-data">\n)(.*?)(\n</script>)',
        rf"\1{payload}\3",
        text,
        flags=re.DOTALL,
    )
    html.write_text(text, encoding="utf-8")


def canvas_data(html: Path) -> dict:
    text = html.read_text(encoding="utf-8")
    match = re.search(
        r'<script type="application/json" id="canvas-data">\n(.*?)\n</script>',
        text,
        re.DOTALL,
    )
    assert match
    return json.loads(match.group(1))


def formal_html(tmp_path: Path) -> Path:
    out = copy_template(tmp_path, "formal-journey.html")
    data = canvas_data(out)
    state = json.loads(STATE.read_text(encoding="utf-8"))
    data["auth"] = state["journey"]
    replace_canvas_data(out, data)
    return out


def load_fault_cases() -> list[dict]:
    raw = json.loads(FAULT_CASES.read_text(encoding="utf-8"))
    return raw["cases"]


class TestJourneyAuditPositive:
    def test_template_structure_passes(self) -> None:
        result = run_audit(TEMPLATE)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "PASS" in result.stdout

    def test_formal_page_passes_with_source_and_state(self, tmp_path: Path) -> None:
        out = formal_html(tmp_path)
        result = run_audit(out, "--source", str(PACKAGE), "--state", str(STATE))
        assert result.returncode == 0, result.stdout + result.stderr

    def test_draft_without_source_or_state_passes_structure(self) -> None:
        result = run_audit(TEMPLATE)
        assert result.returncode == 0, result.stdout + result.stderr


class TestJourneyDynamicStages:
    def test_missing_journey_map_fails(self, tmp_path: Path) -> None:
        out = copy_template(tmp_path)
        text = out.read_text(encoding="utf-8").replace('id="journey-map"', 'id="journey-map-x"')
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        assert result.returncode != 0
        assert "journey-map" in result.stdout

    def test_less_than_three_stages_fails(self, tmp_path: Path) -> None:
        out = copy_template(tmp_path)
        text = out.read_text(encoding="utf-8").replace('id="journey-stage-3"', 'id="journey-stage-30"')
        text = re.sub(r'id="journey-stage-3-(action|touchpoint-system|emotion|wait-rework|risk)"', r'id="journey-stage-30-\1"', text)
        data = canvas_data(out)
        data["stages"] = data["stages"][:2]
        out.write_text(text, encoding="utf-8")
        replace_canvas_data(out, data)
        result = run_audit(out)
        assert result.returncode != 0
        assert "at least 3 stages" in result.stdout or "continuous" in result.stdout

    def test_non_continuous_stage_numbers_fail(self, tmp_path: Path) -> None:
        out = copy_template(tmp_path)
        text = out.read_text(encoding="utf-8").replace('id="journey-stage-2"', 'id="journey-stage-4"')
        text = re.sub(r'id="journey-stage-2-(action|touchpoint-system|emotion|wait-rework|risk)"', r'id="journey-stage-4-\1"', text)
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        assert result.returncode != 0
        assert "continuous" in result.stdout

    def test_missing_stage_child_anchor_fails(self, tmp_path: Path) -> None:
        out = copy_template(tmp_path)
        text = out.read_text(encoding="utf-8").replace(
            'id="journey-stage-2-risk"', 'id="journey-stage-2-risk-x"'
        )
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        assert result.returncode != 0
        assert "journey-stage-2-risk" in result.stdout

    def test_stage_child_order_fails(self, tmp_path: Path) -> None:
        out = copy_template(tmp_path)
        text = out.read_text(encoding="utf-8")
        text = text.replace('id="journey-stage-1-action"', 'id="journey-stage-1-action-x"', 1)
        text = text.replace('id="journey-stage-1-emotion"', 'id="journey-stage-1-action"', 1)
        text = text.replace('id="journey-stage-1-action-x"', 'id="journey-stage-1-emotion"', 1)
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        assert result.returncode != 0
        assert "JOURNEY_STAGE_ORDER" in result.stdout or "JOURNEY-TPL-GATE-04" in result.stdout

    def test_canvas_data_stage_length_mismatch_fails(self, tmp_path: Path) -> None:
        out = copy_template(tmp_path)
        data = canvas_data(out)
        data["stages"] = data["stages"][:2]
        replace_canvas_data(out, data)
        result = run_audit(out)
        assert result.returncode != 0
        assert "stages length" in result.stdout

    def test_source_stage_order_mismatch_fails(self, tmp_path: Path) -> None:
        out = formal_html(tmp_path)
        source = tmp_path / "JOURNEY-v1.md"
        source.write_text(
            PACKAGE.read_text(encoding="utf-8").replace("阶段名待填写", "另一个阶段", 1),
            encoding="utf-8",
        )
        result = run_audit(out, "--source", str(source), "--state", str(STATE))
        assert result.returncode != 0
        assert "JOURNEY_SOURCE_ORDER" in result.stdout


class TestJourneyRequiredAnchorsAndAuth:
    @pytest.mark.parametrize(
        "target",
        [
            'id="journey-quality-user-perspective"',
            'id="journey-quality-business-outcome"',
            'id="journey-quality-friction-visible"',
            'id="journey-quality-no-solution-bias"',
            'id="journey-friction-summary"',
        ],
    )
    def test_missing_quality_or_friction_anchor_fails(self, tmp_path: Path, target: str) -> None:
        out = copy_template(tmp_path)
        text = out.read_text(encoding="utf-8").replace(target, target.replace('"', '-x"', 1))
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        assert result.returncode != 0
        assert "MISSING_ANCHOR" in result.stdout or "JOURNEY-TPL-GATE-04" in result.stdout

    def test_canvas_data_auth_mismatch_fails(self, tmp_path: Path) -> None:
        out = formal_html(tmp_path)
        data = canvas_data(out)
        data["auth"]["render_authorized"] = False
        replace_canvas_data(out, data)
        result = run_audit(out, "--source", str(PACKAGE), "--state", str(STATE))
        assert result.returncode != 0
        assert "AUTH_MISMATCH" in result.stdout

    def test_source_version_mismatch_fails(self, tmp_path: Path) -> None:
        out = formal_html(tmp_path)
        source = tmp_path / "JOURNEY-v2.md"
        source.write_text(PACKAGE.read_text(encoding="utf-8").replace("v1", "v2", 1), encoding="utf-8")
        result = run_audit(out, "--source", str(source), "--state", str(STATE))
        assert result.returncode != 0
        assert "SOURCE_VERSION" in result.stdout

    def test_missing_journey_state_fails_clearly(self, tmp_path: Path) -> None:
        out = formal_html(tmp_path)
        state = tmp_path / "state.json"
        state.write_text('{"schema_version":"2.3","group_id":"G1","project_name":"x"}', encoding="utf-8")
        result = run_audit(out, "--source", str(PACKAGE), "--state", str(state))
        assert result.returncode != 0
        assert "state.json has no journey record" in result.stdout

    def test_override_caveat_hidden_fails(self, tmp_path: Path) -> None:
        out = copy_template(tmp_path)
        data = canvas_data(out)
        data["auth"] = json.loads(OVERRIDE_STATE.read_text(encoding="utf-8"))["journey"]
        replace_canvas_data(out, data)
        result = run_audit(out)
        assert result.returncode != 0
        assert "CAVEAT" in result.stdout


class TestJourneyFaultFixtures:
    @pytest.mark.parametrize("case", load_fault_cases(), ids=lambda case: case["id"])
    def test_fault_case_definitions_fail(self, tmp_path: Path, case: dict) -> None:
        out = copy_template(tmp_path, f"{case['id']}.html")
        text = out.read_text(encoding="utf-8")
        for target, replacement in case["replace"]:
            text = text.replace(target, replacement)
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        assert result.returncode != 0
        assert case["expect"] in result.stdout


class TestJourneyTemplateGate:
    def test_isomorphic_template_gate_passes_after_content_change(self, tmp_path: Path) -> None:
        out = copy_template(tmp_path)
        text = out.read_text(encoding="utf-8").replace("阶段名待填写", "真实阶段名")
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        assert "JOURNEY-TPL-GATE" not in result.stdout

    def test_delete_quality_module_fails_template_gate(self, tmp_path: Path) -> None:
        out = copy_template(tmp_path)
        text = re.sub(
            r'<section class="journey-quality" id="journey-quality".*?</section>\s*',
            "",
            out.read_text(encoding="utf-8"),
            flags=re.DOTALL,
        )
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        assert result.returncode != 0
        assert "JOURNEY-TPL-GATE-02" in result.stdout or "JOURNEY-TPL-GATE-04" in result.stdout

    def test_swap_main_order_fails_template_gate(self, tmp_path: Path) -> None:
        out = copy_template(tmp_path)
        text = out.read_text(encoding="utf-8")
        text = text.replace('id="journey-map"', 'id="journey-map-x"', 1)
        text = text.replace('id="journey-frictions"', 'id="journey-map"', 1)
        text = text.replace('id="journey-map-x"', 'id="journey-frictions"', 1)
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        assert result.returncode != 0
        assert "JOURNEY-TPL-GATE-03" in result.stdout

    def test_hidden_quality_or_governance_fails(self, tmp_path: Path) -> None:
        out = copy_template(tmp_path)
        text = out.read_text(encoding="utf-8").replace(
            '<section class="journey-quality" id="journey-quality"',
            '<section class="journey-quality hidden" id="journey-quality"',
        )
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        assert result.returncode != 0
        assert "JOURNEY-TPL-GATE-06" in result.stdout or "HIDDEN_SECTION" in result.stdout

    def test_template_self_audit_fails_on_external_dependency(self, tmp_path: Path) -> None:
        broken = tmp_path / "broken-template.html"
        text = TEMPLATE.read_text(encoding="utf-8").replace(
            '<link rel="stylesheet" href="shared/canvas-theme.css">',
            '<link rel="stylesheet" href="https://example.com/canvas-theme.css">',
        )
        broken.write_text(text, encoding="utf-8")
        result = subprocess.run(
            [PYTHON, str(AUDIT), str(TEMPLATE), "--type", "journey", "--template", str(broken)],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "JOURNEY-TPL-GATE-06" in result.stdout

    def test_formal_delivery_without_template_fails(self) -> None:
        result = subprocess.run(
            [PYTHON, str(AUDIT), str(TEMPLATE), "--type", "journey", "--source", str(PACKAGE), "--state", str(STATE)],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "JOURNEY-TPL-GATE-00" in result.stdout
