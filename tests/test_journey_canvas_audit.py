"""Journey Canvas HTML 静态审计测试。

覆盖 User Journey 一等公民画布的 render contract、动态阶段规则与 Template Gate。
测试只使用静态模板和 fixture，不引入渲染脚本。

v2.3.2 PATCH：阶段字段从 `wait-rework / risk` 改为 `pain-point / opportunity`；
6b 节标题 `关键断点与机会` → `痛点与机会`；6a 维度 `friction_visible` → `pain_opportunity_visible`。
本测试文件按新契约定义预期；旧字段在 audit 中仅作为"历史镜像"分支保留，不应再触发断言。
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

# v2.3.2 新契约阶段子锚点（DOM 内每个 stage 必须包含的 5 个子锚点）
JOURNEY_STAGE_FIELDS_V232 = (
    "action",
    "touchpoint-system",
    "emotion",
    "pain-point",
    "opportunity",
)

# v2.3.2 新契约 stage data 字段（canvas-data.stages[] 内每个 stage 必须包含的 snake_case 字段）
JOURNEY_STAGE_DATA_FIELDS_V232 = (
    "stage_index",
    "stage_name",
    "action",
    "touchpoint_system",
    "emotion",
    "pain_point",
    "opportunity",
)


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
        text = re.sub(
            r'id="journey-stage-3-(' + "|".join(JOURNEY_STAGE_FIELDS_V232) + r')"',
            r'id="journey-stage-30-\1"',
            text,
        )
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
        text = re.sub(
            r'id="journey-stage-2-(' + "|".join(JOURNEY_STAGE_FIELDS_V232) + r')"',
            r'id="journey-stage-4-\1"',
            text,
        )
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        assert result.returncode != 0
        assert "continuous" in result.stdout

    def test_missing_stage_child_pain_point_anchor_fails(self, tmp_path: Path) -> None:
        """v2.3.2 步骤 1：删除 `journey-stage-N-pain-point` 必须 FAIL。"""
        out = copy_template(tmp_path)
        text = out.read_text(encoding="utf-8").replace(
            'id="journey-stage-2-pain-point"', 'id="journey-stage-2-pain-point-x"'
        )
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        assert result.returncode != 0
        assert "journey-stage-2-pain-point" in result.stdout

    def test_missing_stage_child_opportunity_anchor_fails(self, tmp_path: Path) -> None:
        """v2.3.2 步骤 1：删除 `journey-stage-N-opportunity` 必须 FAIL。"""
        out = copy_template(tmp_path)
        text = out.read_text(encoding="utf-8").replace(
            'id="journey-stage-2-opportunity"', 'id="journey-stage-2-opportunity-x"'
        )
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        assert result.returncode != 0
        assert "journey-stage-2-opportunity" in result.stdout

    def test_stage_child_order_fails(self, tmp_path: Path) -> None:
        """v2.3.2 步骤 1：DOM 顺序不是 action → touchpoint-system → emotion → pain-point → opportunity 必须 FAIL。"""
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

    def test_canvas_data_stage_missing_pain_point_fails(self, tmp_path: Path) -> None:
        """v2.3.2 步骤 1：canvas-data.stages[] 缺 `pain_point` 必须 FAIL。"""
        out = copy_template(tmp_path)
        data = canvas_data(out)
        for stage in data.get("stages", []):
            stage.pop("pain_point", None)
        replace_canvas_data(out, data)
        result = run_audit(out)
        assert result.returncode != 0
        assert "pain_point" in result.stdout or "JOURNEY_DATA" in result.stdout

    def test_canvas_data_stage_missing_opportunity_fails(self, tmp_path: Path) -> None:
        """v2.3.2 步骤 1：canvas-data.stages[] 缺 `opportunity` 必须 FAIL。"""
        out = copy_template(tmp_path)
        data = canvas_data(out)
        for stage in data.get("stages", []):
            stage.pop("opportunity", None)
        replace_canvas_data(out, data)
        result = run_audit(out)
        assert result.returncode != 0
        assert "opportunity" in result.stdout or "JOURNEY_DATA" in result.stdout

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
            'id="journey-quality-pain-opportunity-visible"',
            'id="journey-quality-no-solution-bias"',
            'id="journey-pain-opportunity-summary"',
        ],
    )
    def test_missing_quality_or_pain_opportunity_anchor_fails(self, tmp_path: Path, target: str) -> None:
        """v2.3.2 步骤 1：6a 四锚点 + 6b 摘要锚点任一缺失必须 FAIL。

        注：原 v2.3.1 的 `journey-quality-friction-visible` 与 `journey-friction-summary`
        在新契约中已被 `journey-quality-pain-opportunity-visible` 与
        `journey-pain-opportunity-summary` 取代。"""
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


class TestJourneyLegacyReject:
    """v2.3.2 步骤 1：旧契约拒绝用例——产物只含 wait-rework/risk 而不含 pain-point/opportunity 时必须 FAIL。"""

    def test_legacy_only_template_fails(self, tmp_path: Path) -> None:
        """仅替换 template 中的新字段为旧字段（wait-rework/risk）→ audit 必须 FAIL。"""
        out = copy_template(tmp_path, "legacy-only-journey.html")
        text = out.read_text(encoding="utf-8")
        legacy_map = {
            'id="journey-stage-1-pain-point"': 'id="journey-stage-1-wait-rework"',
            'id="journey-stage-2-pain-point"': 'id="journey-stage-2-wait-rework"',
            'id="journey-stage-3-pain-point"': 'id="journey-stage-3-wait-rework"',
            'id="journey-stage-1-opportunity"': 'id="journey-stage-1-risk"',
            'id="journey-stage-2-opportunity"': 'id="journey-stage-2-risk"',
            'id="journey-stage-3-opportunity"': 'id="journey-stage-3-risk"',
            'id="journey-quality-pain-opportunity-visible"': 'id="journey-quality-friction-visible"',
            'id="journey-pain-opportunity-summary"': 'id="journey-friction-summary"',
        }
        for old, new in legacy_map.items():
            text = text.replace(old, new)
        out.write_text(text, encoding="utf-8")
        # 同时把 canvas-data 字段同步回旧名
        data = canvas_data(out)
        for stage in data.get("stages", []):
            if "pain_point" in stage:
                stage["wait_rework"] = stage.pop("pain_point")
            if "opportunity" in stage:
                stage["risk"] = stage.pop("opportunity")
        if data.get("quality", {}).get("pain_opportunity_visible") is not None:
            data["quality"]["friction_visible"] = data["quality"].pop("pain_opportunity_visible")
        replace_canvas_data(out, data)
        result = run_audit(out)
        assert result.returncode != 0
        # 必须报告新契约字段缺失
        assert (
            "pain_point" in result.stdout
            or "pain-point" in result.stdout
            or "pain_opportunity_visible" in result.stdout
            or "JOURNEY-pain-opportunity" in result.stdout
        ), result.stdout


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
        text = text.replace('id="journey-pain-opportunities"', 'id="journey-map"', 1)
        text = text.replace('id="journey-map-x"', 'id="journey-pain-opportunities"', 1)
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
