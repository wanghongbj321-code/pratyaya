"""HMW / Persona / Journey distill-gate 结构一致性测试。

覆盖执行计划 §3.2 要求：
- HMW Skill 注册与实际路径一致。
- 确认包规范包含 6 / 6a / 6b / 6c / 12 节。
- HMW-Cxx / HMW-Gxx / HMW-Inf-N / HMW-Idea-N 命名互不冲突。
- hmw-spec.md、Gate 与 render contract 对章节事实源的引用一致。
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS = REPO_ROOT / "skills"
DISTILL = SKILLS / "hmw-distill"
GATE = SKILLS / "hmw-gate"
JOURNEY_DISTILL = SKILLS / "journey-distill"
JOURNEY_GATE = SKILLS / "journey-gate"
PERSONA_DISTILL = SKILLS / "persona-distill"
PERSONA_GATE = SKILLS / "persona-gate"
CONTRACT = SKILLS / "canvas-render" / "references" / "render-contract-hmw.md"
JOURNEY_CONTRACT = SKILLS / "canvas-render" / "references" / "render-contract-journey.md"
PERSONA_CONTRACT = SKILLS / "canvas-render" / "references" / "render-contract-persona.md"
EXAMPLES = REPO_ROOT / "examples" / "modules"
CANVAS_EXAMPLES = REPO_ROOT / "skills" / "canvas-render" / "examples"

EXPECTED_HMW_SKILLS = (
    "./skills/hmw-distill",
    "./skills/hmw-gate",
)
EXPECTED_JOURNEY_PLACEHOLDER_SKILLS = (
    "./skills/journey-distill",
    "./skills/journey-gate",
)
EXPECTED_PERSONA_SKILLS = (
    "./skills/persona-distill",
    "./skills/persona-gate",
)
EXPECTED_HMW_FILES = (
    "SKILL.md",
    "frameworks/hmw-frame.md",
    "references/hmw-spec.md",
)
EXPECTED_GATE_FILES = (
    "SKILL.md",
    "references/HMW-gate.md",
)
EXPECTED_JOURNEY_DISTILL_FILES = (
    "SKILL.md",
    "frameworks/journey-frame.md",
    "references/journey-spec.md",
)
EXPECTED_JOURNEY_GATE_FILES = (
    "SKILL.md",
    "references/JOURNEY-gate.md",
)
REQUIRED_PACKAGE_SECTIONS = (
    "6. HMW 陈述",
    "6a. 质量鉴别",
    "6b. 想法种子",
    "6c. 想法 ↔ HMW 对应",
    "12. Gate 与用户决策",
)
REQUIRED_JOURNEY_PACKAGE_SECTIONS = (
    "6. 阶段地图",
    "6a. 质量鉴别",
    "6b. 关键断点与机会",
    "7. 结论登记表",
    "8. 缺口表",
    "9. 推断表",
    "12. Gate 与用户决策",
)
JOURNEY_ROWS = (
    "action",
    "touchpoint_system",
    "emotion",
    "wait_rework",
    "risk",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestSkillRegistration:
    def test_plugin_registers_hmw_skills(self) -> None:
        plugin = json.loads(read(REPO_ROOT / ".codebuddy-plugin" / "plugin.json"))
        for skill in EXPECTED_HMW_SKILLS:
            assert skill in plugin["skills"], f"plugin.json missing {skill}"
        for skill in EXPECTED_JOURNEY_PLACEHOLDER_SKILLS:
            assert skill in plugin["skills"], f"plugin.json missing Journey skill {skill}"
        for skill in EXPECTED_PERSONA_SKILLS:
            assert skill in plugin["skills"], f"plugin.json missing Persona skill {skill}"
        assert plugin["version"] == "2.3.1"

    def test_plugin_registers_persona_skills(self) -> None:
        plugin = json.loads(read(REPO_ROOT / ".codebuddy-plugin" / "plugin.json"))
        for skill in EXPECTED_PERSONA_SKILLS:
            assert skill in plugin["skills"], f"plugin.json missing {skill}"

    def test_agent_registers_hmw_skills(self) -> None:
        agent = read(REPO_ROOT / "agents" / "pratyaya.md")
        m = re.search(r"^skills:\s*\[(.*?)\]", agent, re.MULTILINE)
        assert m, "agent frontmatter missing skills field"
        skills = [s.strip() for s in m.group(1).split(",")]
        assert "hmw-distill" in skills
        assert "hmw-gate" in skills
        assert "persona-distill" in skills
        assert "persona-gate" in skills
        assert "journey-distill" in skills
        assert "journey-gate" in skills

    def test_agent_and_plugin_skills_have_identical_order(self) -> None:
        plugin = json.loads(read(REPO_ROOT / ".codebuddy-plugin" / "plugin.json"))
        agent = read(REPO_ROOT / "agents" / "pratyaya.md")
        match = re.search(r"^skills:\s*\[(.*?)\]", agent, re.MULTILINE)
        assert match, "agent frontmatter missing skills field"
        agent_order = [name.strip() for name in match.group(1).split(",")]
        plugin_order = [path.removeprefix("./skills/") for path in plugin["skills"]]
        assert agent_order == plugin_order

    def test_skills_order_distill_gate_render(self) -> None:
        """执行计划 §7 步骤 10：plugin 与 agent 的 skills 顺序按 distill→gate→render。"""
        plugin = json.loads(read(REPO_ROOT / ".codebuddy-plugin" / "plugin.json"))
        plugin_order = [p.removeprefix("./skills/") for p in plugin["skills"]]
        # HMW 的 distill 在 gc-gate 前、render 在最后：全序必须满足 distill < gate < render 工作流
        workflow_rank = {
            "mvl-distill": 0,
            "gc-distill": 0,
            "hmw-distill": 0,
            "persona-distill": 0,
            "journey-distill": 0,
            "module-conclusion-gate": 1,
            "gc-gate": 1,
            "hmw-gate": 1,
            "persona-gate": 1,
            "journey-gate": 1,
            "canvas-render": 2,
        }
        ranks = [workflow_rank[name] for name in plugin_order]
        assert ranks == sorted(ranks), f"plugin skills order violates distill→gate→render: {plugin_order}"


class TestPluginMetadata:
    def test_workbuddy_quick_prompts_are_limited_to_three_primary_entries(self) -> None:
        plugin = json.loads(read(REPO_ROOT / ".codebuddy-plugin" / "plugin.json"))
        quick_prompts = plugin["quickPrompts"]

        assert len(quick_prompts) == 3
        assert quick_prompts[0] == plugin["defaultInitPrompt"]
        assert "MVL" in quick_prompts[1]["zh"]
        assert "MVL" in quick_prompts[1]["en"]
        assert "用户旅程" in quick_prompts[2]["zh"]
        assert "User Journey" in quick_prompts[2]["en"]

    def test_workbuddy_zh_display_description_length(self) -> None:
        plugin = json.loads(read(REPO_ROOT / ".codebuddy-plugin" / "plugin.json"))
        description_zh = plugin["displayDescription"]["zh"]

        assert 40 <= len(description_zh) <= 50


class TestHmwSkillFiles:
    @pytest.mark.parametrize("fname", EXPECTED_HMW_FILES)
    def test_distill_file_exists(self, fname: str) -> None:
        assert (DISTILL / fname).exists(), f"missing {DISTILL / fname}"

    @pytest.mark.parametrize("fname", EXPECTED_GATE_FILES)
    def test_gate_file_exists(self, fname: str) -> None:
        assert (GATE / fname).exists(), f"missing {GATE / fname}"

    def test_distill_frontmatter_name(self) -> None:
        assert re.search(r"^name:\s*hmw-distill\s*$", read(DISTILL / "SKILL.md"), re.MULTILINE)

    def test_gate_frontmatter_name(self) -> None:
        assert re.search(r"^name:\s*hmw-gate\s*$", read(GATE / "SKILL.md"), re.MULTILINE)

    def test_distill_output_paths_fixed(self) -> None:
        text = read(DISTILL / "SKILL.md")
        assert "modules/HMW-keypoints.md" in text
        assert "modules/HMW-v{N}.md" in text


class TestJourneySkillFiles:
    @pytest.mark.parametrize("fname", EXPECTED_JOURNEY_DISTILL_FILES)
    def test_distill_file_exists(self, fname: str) -> None:
        assert (JOURNEY_DISTILL / fname).exists(), f"missing {JOURNEY_DISTILL / fname}"

    @pytest.mark.parametrize("fname", EXPECTED_JOURNEY_GATE_FILES)
    def test_gate_file_exists(self, fname: str) -> None:
        assert (JOURNEY_GATE / fname).exists(), f"missing {JOURNEY_GATE / fname}"

    def test_distill_frontmatter_name(self) -> None:
        assert re.search(
            r"^name:\s*journey-distill\s*$",
            read(JOURNEY_DISTILL / "SKILL.md"),
            re.MULTILINE,
        )

    def test_gate_frontmatter_name(self) -> None:
        assert re.search(
            r"^name:\s*journey-gate\s*$",
            read(JOURNEY_GATE / "SKILL.md"),
            re.MULTILINE,
        )

    def test_distill_output_paths_fixed(self) -> None:
        text = read(JOURNEY_DISTILL / "SKILL.md")
        assert "modules/JOURNEY-keypoints.md" in text
        assert "modules/JOURNEY-v{N}.md" in text
        assert "modules/JOURNEY-gaps.md" in text

    def test_distill_keeps_five_row_dynamic_stage_contract(self) -> None:
        frame = read(JOURNEY_DISTILL / "frameworks" / "journey-frame.md")
        spec = read(JOURNEY_DISTILL / "references" / "journey-spec.md")
        for row in JOURNEY_ROWS:
            assert row in frame
            assert row in spec
        assert "5 行合并结构" in frame
        assert "动态生成" in frame
        assert "不得写入 MVL" in frame

    def test_confirmation_package_contains_required_sections(self) -> None:
        template = read(JOURNEY_DISTILL / "SKILL.md")
        for section in REQUIRED_JOURNEY_PACKAGE_SECTIONS:
            assert section in template, f"Journey SKILL.md template missing section: {section}"

    def test_quality_assessment_is_formal_external_canvas_capability(self) -> None:
        skill = read(JOURNEY_DISTILL / "SKILL.md")
        gate = read(JOURNEY_GATE / "SKILL.md")
        spec = read(JOURNEY_DISTILL / "references" / "journey-spec.md")
        for text in (skill, gate, spec):
            assert "正式画布外显" in text
        for dimension in (
            "business_outcome",
            "user_perspective",
            "no_solution_bias",
            "friction_visible",
        ):
            assert dimension in skill
            assert dimension in spec

    def test_journey_gate_has_six_stable_ids(self) -> None:
        gate = read(JOURNEY_GATE / "references" / "JOURNEY-gate.md")
        ids = re.findall(r"JOURNEY-GATE-0([1-6])", gate)
        assert sorted(set(ids)) == ["1", "2", "3", "4", "5", "6"]

    def test_journey_gate_categories_and_sources(self) -> None:
        gate = read(JOURNEY_GATE / "references" / "JOURNEY-gate.md")
        assert gate.count("information_integrity") >= 3
        assert gate.count("business_risk") >= 3
        for src in ("JOURNEY-map", "JOURNEY-friction", "JOURNEY-quality"):
            assert src in gate, f"Journey Gate 缺来源 ID: {src}"

    def test_journey_gate_does_not_authorize_rendering(self) -> None:
        skill = read(JOURNEY_GATE / "SKILL.md")
        assert "不写入 render_authorized" in skill
        assert "gate_recommendation" in skill


class TestJourneyRenderContract:
    def test_canvas_render_registers_journey_type_and_example(self) -> None:
        skill = read(SKILLS / "canvas-render" / "SKILL.md")
        assert "`journey`" in skill
        assert "render-contract-journey.md" in skill
        assert "modules/JOURNEY-v{N}.md" in skill
        assert "modules/JOURNEY-keypoints.md" in skill
        assert "output/journey-canvas.html" in skill
        assert "skills/canvas-render/examples/user-journey-canvas.html" in skill

    def test_journey_render_contract_exists_and_defines_dynamic_stages(self) -> None:
        contract = read(JOURNEY_CONTRACT)
        for anchor in (
            "journey-map",
            "journey-stage-{n}",
            "journey-stage-{n}-action",
            "journey-stage-{n}-touchpoint-system",
            "journey-stage-{n}-emotion",
            "journey-stage-{n}-wait-rework",
            "journey-stage-{n}-risk",
            "journey-frictions",
            "journey-friction-summary",
            "journey-quality-user-perspective",
            "journey-quality-business-outcome",
            "journey-quality-friction-visible",
            "journey-quality-no-solution-bias",
        ):
            assert anchor in contract
        assert 'data-page-type="journey"' in contract
        assert "阶段数量不少于 3" in contract
        assert "action → touchpoint-system → emotion → wait-rework → risk" in contract

    def test_journey_example_has_template_profile_anchors(self) -> None:
        example = read(CANVAS_EXAMPLES / "user-journey-canvas.html")
        for anchor in (
            'id="canvas-header"',
            'id="journey-map"',
            'id="journey-frictions"',
            'id="journey-quality"',
            'id="quality-panel"',
            'id="local-notes"',
            'id="canvas-data"',
        ):
            assert anchor in example
        assert 'data-page-type="journey"' in example
        assert '"canvas_type": "journey"' in example
        for number in range(1, 4):
            assert f'id="journey-stage-{number}"' in example
            for field in ("action", "touchpoint-system", "emotion", "wait-rework", "risk"):
                assert f'id="journey-stage-{number}-{field}"' in example

    def test_journey_contract_audit_script_and_example_share_quality_anchors(self) -> None:
        contract = read(JOURNEY_CONTRACT)
        audit = read(REPO_ROOT / "skills" / "canvas-render" / "scripts" / "audit_canvas_html.py")
        example = read(CANVAS_EXAMPLES / "user-journey-canvas.html")
        for anchor in (
            "journey-quality-user-perspective",
            "journey-quality-business-outcome",
            "journey-quality-friction-visible",
            "journey-quality-no-solution-bias",
            "journey-friction-summary",
        ):
            assert anchor in contract
            assert anchor in audit
            assert anchor in example


class TestJourneyExamples:
    def test_journey_example_files_exist(self) -> None:
        for fname in ("JOURNEY-keypoints.md", "JOURNEY-v1.md", "JOURNEY-gaps.md"):
            assert (EXAMPLES / fname).exists(), f"missing examples/modules/{fname}"

    def test_journey_example_package_has_required_content(self) -> None:
        package = read(EXAMPLES / "JOURNEY-v1.md")
        for section in REQUIRED_JOURNEY_PACKAGE_SECTIONS:
            assert section in package
        for token in ("JOURNEY-C", "JOURNEY-G", "JOURNEY-Inf", "JOURNEY-F"):
            assert token in package
        for key in ("user_perspective", "business_outcome", "friction_visible", "no_solution_bias"):
            assert key in package
        stage_rows = re.findall(r"^\|\s*[1-9]\d*\s*\|", package, re.MULTILINE)
        assert len(stage_rows) >= 3

    def test_journey_gaps_example_reuses_package_gap_ids(self) -> None:
        package = read(EXAMPLES / "JOURNEY-v1.md")
        gaps = read(EXAMPLES / "JOURNEY-gaps.md")
        package_gap_ids = set(re.findall(r"JOURNEY-G\d+", package))
        gaps_ids = set(re.findall(r"JOURNEY-G\d+", gaps))
        assert gaps_ids
        assert gaps_ids.issubset(package_gap_ids)


class TestJourneyAgentContract:
    def test_agent_contains_journey_phase_and_routing(self) -> None:
        agent = read(REPO_ROOT / "agents" / "pratyaya.md")
        for phrase in (
            "## Phase Journey：用户旅程工作流",
            "用户提到 \"用户旅程\" / \"Journey\" / \"User Journey\" / \"旅程画布\" / \"当前旅程\"",
            "不属于 MVL / GC / HMW / Persona",
            "直接进入 Phase Journey",
            "Persona 为独立画布",
        ):
            assert phrase in agent

    def test_agent_contains_journey_mandatory_instruction_card(self) -> None:
        agent = read(REPO_ROOT / "agents" / "pratyaya.md")
        for phrase in (
            "### Journey 强制执行指令",
            "不修改 MVL M2 的 `09-user-journey.md`",
            "不写 `state.modules.M2`",
            "主表忠实保留 5 行合并结构",
            "正式渲染只读 `JOURNEY-v{N}.md`",
            "质量鉴别必须在正式画布外显",
            "只有 `business_risk` 可 override",
            "`information_integrity` 不可 override",
        ):
            assert phrase in agent

    def test_agent_contains_journey_state_and_render_paths(self) -> None:
        agent = read(REPO_ROOT / "agents" / "pratyaya.md")
        for phrase in (
            "state.journey",
            "transcripts/journey-TXX-raw.md",
            "modules/JOURNEY-keypoints.md",
            "modules/JOURNEY-v{N}.md",
            "modules/JOURNEY-gaps.md",
            "output/journey-canvas.html",
            "--type journey",
            "--template skills/canvas-render/examples/user-journey-canvas.html",
            "render-contract-journey.md",
        ):
            assert phrase in agent


class TestConfirmationPackageSections:
    def test_skill_template_contains_required_sections(self) -> None:
        template = read(DISTILL / "SKILL.md")
        for section in REQUIRED_PACKAGE_SECTIONS:
            assert section in template, f"SKILL.md template missing section: {section}"

    def test_example_package_contains_required_sections(self) -> None:
        example = read(EXAMPLES / "HMW-v1.md")
        for section in REQUIRED_PACKAGE_SECTIONS:
            assert section in example, f"HMW-v1.md missing section: {section}"


class TestIdNaming:
    """执行计划 §8 规则 12 + 设计 §6.4：推断 ID 与想法种子 ID 严格区分。"""

    def test_spec_defines_both_id_spaces(self) -> None:
        spec = read(DISTILL / "references" / "hmw-spec.md")
        assert "HMW-Inf-N" in spec, "spec 必须定义推断 ID HMW-Inf-N"
        assert "HMW-Idea-N" in spec, "spec 必须定义想法种子 ID HMW-Idea-N"

    def test_skill_warns_about_id_distinction(self) -> None:
        skill = read(DISTILL / "SKILL.md")
        assert "HMW-Inf" in skill and "HMW-Idea" in skill

    def test_gate_spec_uses_inference_id(self) -> None:
        gate = read(GATE / "references" / "HMW-gate.md")
        assert "HMW-Inf-N" in gate

    def test_example_uses_inference_id_not_idea_confusion(self) -> None:
        example = read(EXAMPLES / "HMW-v1.md")
        assert re.search(r"HMW-Inf\d+", example), "示例推断 ID 必须用 HMW-Inf-N"
        assert re.search(r"HMW-Idea-\d+", example), "示例想法种子 ID 必须用 HMW-Idea-N"


class TestGateConditions:
    def test_six_stable_gate_ids(self) -> None:
        gate = read(GATE / "references" / "HMW-gate.md")
        ids = re.findall(r"HMW-GATE-0([1-6])", gate)
        assert sorted(set(ids)) == ["1", "2", "3", "4", "5", "6"]

    def test_category_split_4_info_2_business(self) -> None:
        gate = read(GATE / "references" / "HMW-gate.md")
        info = gate.count("information_integrity")
        biz = gate.count("business_risk")
        # 表格 6 行：4 info + 2 biz；README 中的"分类汇总"行也计入，因此用 ≥ 校验
        assert info >= 4 and biz >= 2

    def test_gate_report_format_columns(self) -> None:
        skill = read(GATE / "SKILL.md")
        for col in ("稳定 ID", "PASS/FAIL", "分类", "风险等级", "来源 ID", "影响", "建议"):
            assert col in skill, f"Gate 报告缺列: {col}"

    def test_gate_only_advisory(self) -> None:
        skill = read(GATE / "SKILL.md")
        assert "不决定最终渲染授权" in skill or "只输出建议" in skill
        assert "render_authorized" in skill  # 提到但不得写入


class TestCrossReferenceConsistency:
    def test_render_contract_anchors_match_spec(self) -> None:
        contract = read(CONTRACT)
        spec = read(DISTILL / "references" / "hmw-spec.md")
        # 仅取 spec「Canvas 映射」表中的 HTML 锚点（hmw-* 且非 skill 名），
        # 排除 hmw-distill / hmw-gate 这类 skill 标识
        mapping_section = spec.split("## Canvas 映射")[1] if "## Canvas 映射" in spec else spec
        spec_anchors = set(re.findall(r"`(hmw-(?!distill|gate)[a-z0-9-]+)`", mapping_section))
        assert spec_anchors, "spec Canvas 映射表未找到 hmw-* 锚点"
        contract_text = contract
        missing = [a for a in spec_anchors if a not in contract_text]
        assert not missing, f"render contract 缺锚点: {missing}"

    def test_contract_has_eight_idea_anchors(self) -> None:
        contract = read(CONTRACT)
        for n in range(1, 9):
            assert f"hmw-idea-{n}" in contract, f"contract 缺 hmw-idea-{n}"

    def test_coherence_map_is_contract_anchor(self) -> None:
        contract = read(CONTRACT)
        assert "hmw-coherence-map" in contract

    def test_gate_sources_reference_package_sections(self) -> None:
        gate = read(GATE / "references" / "HMW-gate.md")
        for src in ("HMW-state", "HMW-quality", "HMW-idea", "HMW-coherence"):
            assert src in gate, f"Gate 缺来源 ID: {src}"
