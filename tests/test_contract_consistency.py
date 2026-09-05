"""HMW / Persona / Journey distill-gate 结构一致性测试。

覆盖执行计划 §3.2 要求：
- HMW Skill 注册与实际路径一致。
- 确认包规范包含 6 / 6a / 6b / 6c / 12 节。
- HMW-Cxx / HMW-Gxx / HMW-Inf-N / HMW-Idea-N 命名互不冲突。
- hmw-spec.md、Gate 与 render contract 对章节事实源的引用一致。

v2.3.2 PATCH 重构：Journey 阶段字段从 `wait_rework / risk` 切换为
`pain_point / opportunity`；6a 维度 `friction_visible` → `pain_opportunity_visible`；
6b 节标题与列结构调整；旧字段不得再列为必填。
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# v3.3.0 P2：注册表解析器随契约检查器一同提供，供结构化断言使用
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.contract_consistency.canvas_registry import (  # noqa: E402
    by_id,
    parse_canvas_registry,
)

SKILLS = REPO_ROOT / "skills"
DISTILL = SKILLS / "hmw-distill"
GATE = SKILLS / "hmw-gate"
JOURNEY_DISTILL = SKILLS / "journey-distill"
JOURNEY_GATE = SKILLS / "journey-gate"
PERSONA_DISTILL = SKILLS / "persona-distill"
PERSONA_GATE = SKILLS / "persona-gate"
MVL_CONTRACT = SKILLS / "canvas-render" / "references" / "render-contract.md"
CONTRACT = SKILLS / "canvas-render" / "references" / "render-contract-hmw.md"
JOURNEY_CONTRACT = SKILLS / "canvas-render" / "references" / "render-contract-journey.md"
PERSONA_CONTRACT = SKILLS / "canvas-render" / "references" / "render-contract-persona.md"
AUDIT = SKILLS / "canvas-render" / "scripts" / "audit_canvas_html.py"
CONTRACT_CHECKER = REPO_ROOT / "scripts" / "check_contract_consistency.py"
EXAMPLES = REPO_ROOT / "examples" / "modules"
CANVAS_EXAMPLES = REPO_ROOT / "skills" / "canvas-render" / "examples"
V2C_VAC_DISTILL = SKILLS / "v2c-vac-distill"
V2C_VAC_GATE = SKILLS / "v2c-vac-gate"
V2C_VAC_CONTRACT = SKILLS / "canvas-render" / "references" / "render-contract-v2c-vac.md"
V2C_VAC_TEMPLATE = CANVAS_EXAMPLES / "v2c-value-attribution-canvas.html"
V2C_VAC_FIXTURES = REPO_ROOT / "tests" / "fixtures" / "v2c-vac"

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
EXPECTED_FAQ_SKILLS = (
    "./skills/faq-answer",
)
EXPECTED_MAAU_SKILLS = (
    "./skills/maau-synthesize",
)
EXPECTED_V2C_VAC_SKILLS = (
    "./skills/v2c-vac-distill",
    "./skills/v2c-vac-gate",
)
EXPECTED_5W_SKILLS = (
    "./skills/5w-distill",
    "./skills/5w-gate",
)
EXPECTED_MAAU_FILES = (
    "SKILL.md",
    "references/maau-synth-spec.md",
    "references/maau-synthesize-example.md",
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
    "6b. 痛点与机会",
    "7. 结论登记表",
    "8. 缺口表",
    "9. 推断表",
    "12. Gate 与用户决策",
)

# v2.3.2 新契约 stage 字段（snake_case，用于 frame / spec 文档断言）
JOURNEY_ROWS = (
    "action",
    "touchpoint_system",
    "emotion",
    "pain_point",
    "opportunity",
)

# v2.3.2 新契约 DOM 子锚点后缀（kebab-case，用于 contract / template 断言）
JOURNEY_DOM_FIELDS = (
    "action",
    "touchpoint-system",
    "emotion",
    "pain-point",
    "opportunity",
)

# v2.3.2 新契约稳定锚点（替换旧 friction 锚点）
JOURNEY_QUALITY_ANCHORS_V232 = (
    "journey-quality-user-perspective",
    "journey-quality-business-outcome",
    "journey-quality-pain-opportunity-visible",
    "journey-quality-no-solution-bias",
)
JOURNEY_PAIN_OPPORTUNITY_ANCHORS_V232 = JOURNEY_QUALITY_ANCHORS_V232

# v2.3.2 已废弃的旧锚点（必须不再出现）
JOURNEY_LEGACY_FORBIDDEN_ANCHORS = (
    "journey-quality-friction-visible",
    "journey-friction-summary",
)
JOURNEY_LEGACY_FORBIDDEN_DOM = (
    "journey-stage-{n}-wait-rework",
    "journey-stage-{n}-risk",
)
JOURNEY_LEGACY_FORBIDDEN_DATA = (
    "wait_rework",
    "risk",
)
JOURNEY_LEGACY_FORBIDDEN_DIMENSIONS = (
    "friction_visible",
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
        for skill in EXPECTED_FAQ_SKILLS:
            assert skill in plugin["skills"], f"plugin.json missing FAQ skill {skill}"
        for skill in EXPECTED_MAAU_SKILLS:
            assert skill in plugin["skills"], f"plugin.json missing MAAU skill {skill}"
        for skill in EXPECTED_V2C_VAC_SKILLS:
            assert skill in plugin["skills"], f"plugin.json missing V2C VAC skill {skill}"
        for skill in EXPECTED_5W_SKILLS:
            assert skill in plugin["skills"], f"plugin.json missing 5W skill {skill}"

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
        assert "maau-synthesize" in skills
        assert "v2c-vac-distill" in skills
        assert "v2c-vac-gate" in skills
        assert "5w-distill" in skills
        assert "5w-gate" in skills

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
            "v2c-vac-distill": 0,
            "5w-distill": 0,
            "module-conclusion-gate": 1,
            "gc-gate": 1,
            "hmw-gate": 1,
            "persona-gate": 1,
            "journey-gate": 1,
            "v2c-vac-gate": 1,
            "5w-gate": 1,
            "faq-answer": 2,
            "maau-synthesize": 2,
            "canvas-render": 3,
        }
        ranks = [workflow_rank[name] for name in plugin_order]
        assert ranks == sorted(ranks), f"plugin skills order violates distill→gate→render: {plugin_order}"


class TestPluginMetadata:
    def test_workbuddy_quick_prompts_are_limited_to_three_primary_entries(self) -> None:
        plugin = json.loads(read(REPO_ROOT / ".codebuddy-plugin" / "plugin.json"))
        quick_prompts = plugin["quickPrompts"]

        assert len(quick_prompts) == 3
        assert quick_prompts[0] == plugin["defaultInitPrompt"]
        assert "V2C" in quick_prompts[1]["en"]
        assert "V2C" in quick_prompts[1]["zh"]
        assert "transcript-direct" in quick_prompts[1]["en"]
        assert "transcript-direct" in quick_prompts[1]["zh"]
        assert "使用问题" in quick_prompts[2]["zh"]
        assert "usage issue" in quick_prompts[2]["en"]

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
        assert "modules/HMW-{slug}-keypoints.md" in text
        assert "modules/HMW-{slug}-v{N}.md" in text


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
        assert "modules/JOURNEY-{slug}-keypoints.md" in text
        assert "modules/JOURNEY-{slug}-v{N}.md" in text
        assert "modules/JOURNEY-{slug}-gaps.md" in text

    def test_distill_keeps_five_row_dynamic_stage_contract(self) -> None:
        """v2.3.2 步骤 1：frame / spec 必须列出 5 行新字段（pain_point / opportunity）。"""
        frame = read(JOURNEY_DISTILL / "frameworks" / "journey-frame.md")
        spec = read(JOURNEY_DISTILL / "references" / "journey-spec.md")
        for row in JOURNEY_ROWS:
            assert row in frame, f"frame.md missing row {row}"
            assert row in spec, f"spec.md missing row {row}"
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
            "pain_opportunity_visible",
        ):
            assert dimension in skill, f"skill.md missing dimension {dimension}"
            assert dimension in spec, f"spec.md missing dimension {dimension}"

    def test_journey_gate_has_six_stable_ids(self) -> None:
        gate = read(JOURNEY_GATE / "references" / "JOURNEY-gate.md")
        ids = re.findall(r"JOURNEY-GATE-0([1-6])", gate)
        assert sorted(set(ids)) == ["1", "2", "3", "4", "5", "6"]

    def test_journey_gate_categories_and_sources(self) -> None:
        gate = read(JOURNEY_GATE / "references" / "JOURNEY-gate.md")
        assert gate.count("information_integrity") >= 3
        assert gate.count("business_risk") >= 3
        for src in ("JOURNEY-map", "JOURNEY-pain-opportunity", "JOURNEY-quality"):
            assert src in gate, f"Journey Gate 缺来源 ID: {src}"

    def test_journey_gate_does_not_authorize_rendering(self) -> None:
        skill = read(JOURNEY_GATE / "SKILL.md")
        assert "不写入 render_authorized" in skill
        assert "gate_recommendation" in skill


class TestMaauSkillFiles:
    @pytest.mark.parametrize("fname", EXPECTED_MAAU_FILES)
    def test_maau_file_exists(self, fname: str) -> None:
        assert (SKILLS / "maau-synthesize" / fname).exists(), f"missing skills/maau-synthesize/{fname}"

    def test_maau_distill_frontmatter_name(self) -> None:
        assert re.search(
            r"^name:\s*maau-synthesize\s*$",
            read(SKILLS / "maau-synthesize" / "SKILL.md"),
            re.MULTILINE,
        )

    def test_maau_skill_does_not_render_or_gate_or_write_state(self) -> None:
        skill = read(SKILLS / "maau-synthesize" / "SKILL.md")
        assert "不调用 Canvas 渲染" in skill
        assert "不执行闸门判定" in skill
        assert "不写 state" in skill

    def test_maau_skill_output_path_fixed(self) -> None:
        skill = read(SKILLS / "maau-synthesize" / "SKILL.md")
        assert "modules/MAAU-{slug}-v{N}.md" in skill

    def test_maau_spec_has_generation_path_and_six_boards(self) -> None:
        spec = read(SKILLS / "maau-synthesize" / "references" / "maau-synth-spec.md")
        assert "transcript-direct" in spec
        for board in ("Intent", "User", "Agent Team", "Workflow", "Context", "Validation"):
            assert board in spec, f"maau-synth-spec.md 缺板块 {board}"


class TestMaauRenderContract:
    def test_render_contract_and_skill_contain_maau_source_and_generation_path(self) -> None:
        contract = read(MVL_CONTRACT)
        skill = read(SKILLS / "canvas-render" / "SKILL.md")
        for token in ("MAAU-{slug}-v{N}.md", "transcript-direct", "state.maau.{slug}", "maau-global-canvas-{slug}.html"):
            assert token in contract, f"render-contract.md 缺 {token}"
            assert token in skill, f"canvas-render/SKILL.md 缺 {token}"

    def test_render_contract_and_skill_require_instance_and_generation_path_in_canvas_data(self) -> None:
        contract = read(MVL_CONTRACT)
        skill = read(SKILLS / "canvas-render" / "SKILL.md")
        for token in ('"instance"', '"generation_path"', '"source_file"'):
            assert token in contract, f"render-contract.md 缺 canvas-data 字段 {token}"
        assert 'data-instance="{slug}"' in skill or "data-instance=\"{slug}\"" in skill

    def test_transcript_direct_header_mandatory(self) -> None:
        contract = read(MVL_CONTRACT)
        assert "[来源: transcript-direct]" in contract

    def test_no_module_drilldown_rule_for_transcript_direct(self) -> None:
        contract = read(MVL_CONTRACT)
        assert "无模块详情" in contract
        assert "不得生成指向" in contract

    def test_optional_index_page_conflict_rule(self) -> None:
        contract = read(MVL_CONTRACT)
        assert "冲突规则" in contract
        assert "二选一" in contract

    def test_skill_registers_maau_transcript_direct_formal_mode(self) -> None:
        skill = read(SKILLS / "canvas-render" / "SKILL.md")
        assert "MAAU transcript-direct 正式模式" in skill
        assert "generation_path=transcript-direct" in skill

    def test_skill_reuses_existing_global_example(self) -> None:
        skill = read(SKILLS / "canvas-render" / "SKILL.md")
        assert "examples/mvl-canvas/maau-global-canvas.html" in skill


class TestJourneyRenderContract:
    def test_canvas_render_registers_journey_type_and_example(self) -> None:
        skill = read(SKILLS / "canvas-render" / "SKILL.md")
        assert "`journey`" in skill
        assert "render-contract-journey.md" in skill
        assert "modules/JOURNEY-{slug}-v{N}.md" in skill
        assert "modules/JOURNEY-{slug}-keypoints.md" in skill
        assert "output/journey-canvas-{slug}.html" in skill
        assert "skills/canvas-render/examples/user-journey-canvas.html" in skill

    def test_journey_render_contract_exists_and_defines_dynamic_stages(self) -> None:
        """v2.3.2 步骤 1：render contract 必须列出 5 行新 DOM 子锚点；旧字段不得出现。"""
        contract = read(JOURNEY_CONTRACT)
        for anchor in (
            "journey-map",
            "journey-stage-{n}",
        ):
            assert anchor in contract, f"contract 缺锚点 {anchor}"
        for field in JOURNEY_DOM_FIELDS:
            assert f"journey-stage-{{n}}-{field}" in contract, f"contract 缺 stage 子锚点 journey-stage-{{n}}-{field}"
        for anchor in JOURNEY_PAIN_OPPORTUNITY_ANCHORS_V232:
            assert anchor in contract, f"contract 缺新契约锚点 {anchor}"
        for forbidden in JOURNEY_LEGACY_FORBIDDEN_ANCHORS:
            assert forbidden not in contract, f"contract 不应再包含旧锚点 {forbidden}"
        for forbidden in JOURNEY_LEGACY_FORBIDDEN_DOM:
            assert forbidden not in contract, f"contract 不应再包含旧 DOM 子锚点 {forbidden}"
        assert 'data-page-type="journey"' in contract
        assert "阶段数量不少于 3" in contract
        assert "action → touchpoint-system → emotion → pain-point → opportunity" in contract

    def test_journey_example_has_template_profile_anchors(self) -> None:
        """v2.3.2 步骤 1：示例 HTML 必须含新契约 DOM 子锚点。"""
        example = read(CANVAS_EXAMPLES / "user-journey-canvas.html")
        for anchor in (
            'id="canvas-header"',
            'id="journey-map"',
            'id="journey-quality"',
            'id="quality-panel"',
            'id="local-notes"',
            'id="canvas-data"',
        ):
            assert anchor in example, f"示例 HTML 缺 id={anchor}"
        assert 'data-page-type="journey"' in example
        assert '"canvas_type": "journey"' in example
        for number in range(1, 4):
            assert f'id="journey-stage-{number}"' in example
            for field in JOURNEY_DOM_FIELDS:
                assert f'id="journey-stage-{number}-{field}"' in example, f"示例 HTML 缺 id=journey-stage-{number}-{field}"

    def test_journey_contract_audit_script_and_example_share_pain_opportunity_anchors(self) -> None:
        """v2.3.2 步骤 1：contract / audit 脚本 / example 三方必须共享新契约锚点。"""
        contract = read(JOURNEY_CONTRACT)
        audit = read(AUDIT)
        example = read(CANVAS_EXAMPLES / "user-journey-canvas.html")
        for anchor in JOURNEY_PAIN_OPPORTUNITY_ANCHORS_V232:
            assert anchor in contract, f"contract 缺 {anchor}"
            assert anchor in audit, f"audit 脚本缺 {anchor}"
            assert anchor in example, f"example 缺 {anchor}"
        for forbidden in JOURNEY_LEGACY_FORBIDDEN_ANCHORS:
            assert forbidden not in audit, f"audit 脚本不应再包含旧锚点 {forbidden}"
            assert forbidden not in example, f"example 不应再包含旧锚点 {forbidden}"

    def test_journey_audit_script_does_not_require_legacy_stage_data_fields(self) -> None:
        """v2.3.2 步骤 1：audit 脚本不得将 wait_rework / risk 列为 stage data 必填字段。"""
        audit = read(AUDIT)
        # 旧 snake_case 字段不得在「Journey stage data 必填」上下文出现
        for forbidden in JOURNEY_LEGACY_FORBIDDEN_DATA:
            # 当前实现会在 JOURNEY_STAGE_DATA_FIELDS 中包含；本断言要求移除该必填。
            # 用正则匹配「Journey stage data」上下文内的引用，避免误报文档中的"旧字段说明"。
            legacy_stage_field_pattern = re.compile(
                rf"\"{re.escape(forbidden)}\"\s*,", re.MULTILINE
            )
            assert not legacy_stage_field_pattern.search(audit), (
                f"audit 脚本不应再把 {forbidden} 列为 Journey stage data 必填字段"
            )

    def test_journey_stage_data_required_fields_are_pain_point_and_opportunity(self) -> None:
        """v2.3.2 步骤 1：JOURNEY_STAGE_DATA_FIELDS 必须包含 pain_point / opportunity。"""
        audit = read(AUDIT)
        # 通过简单成员性查找 contract 字段集合（精确度高，避开注释）
        # audit 脚本中定义 JOURNEY_STAGE_DATA_FIELDS = (...) 的元组
        match = re.search(r"JOURNEY_STAGE_DATA_FIELDS\s*=\s*\((.*?)\)", audit, re.DOTALL)
        assert match, "audit 脚本缺 JOURNEY_STAGE_DATA_FIELDS 定义"
        field_block = match.group(1)
        for field in ("pain_point", "opportunity"):
            assert f'"{field}"' in field_block, f"JOURNEY_STAGE_DATA_FIELDS 缺 {field}"
        for forbidden in JOURNEY_LEGACY_FORBIDDEN_DATA:
            assert f'"{forbidden}"' not in field_block, f"JOURNEY_STAGE_DATA_FIELDS 仍含旧字段 {forbidden}"


class TestJourneyExamples:
    def test_journey_example_files_exist(self) -> None:
        for fname in ("JOURNEY-retail-demo-keypoints.md", "JOURNEY-retail-demo-v1.md", "JOURNEY-retail-demo-gaps.md"):
            assert (EXAMPLES / fname).exists(), f"missing examples/modules/{fname}"

    def test_journey_example_package_has_required_content(self) -> None:
        """v2.3.2 步骤 1：示例包 6b 节标题为「痛点与机会」；阶段表列含「痛点/机会」。"""
        package = read(EXAMPLES / "JOURNEY-retail-demo-v1.md")
        for section in REQUIRED_JOURNEY_PACKAGE_SECTIONS:
            assert section in package, f"JOURNEY-retail-demo-v1.md 缺章节 {section}"
        for token in ("JOURNEY-C", "JOURNEY-G", "JOURNEY-Inf", "JOURNEY-F"):
            assert token in package, f"JOURNEY-retail-demo-v1.md 缺 ID 前缀 {token}"
        for key in ("user_perspective", "business_outcome", "pain_opportunity_visible", "no_solution_bias"):
            assert key in package, f"JOURNEY-retail-demo-v1.md 缺质量维度 {key}"
        for forbidden in JOURNEY_LEGACY_FORBIDDEN_DIMENSIONS:
            assert forbidden not in package, (
                f"JOURNEY-retail-demo-v1.md 不应再包含旧质量维度 {forbidden}（应使用 pain_opportunity_visible）"
            )
        stage_rows = re.findall(r"^\|\s*[1-9]\d*\s*\|", package, re.MULTILINE)
        assert len(stage_rows) >= 3
        # 主表必须列标题包含 痛点 与 机会（取代"等待与返工"与"风险节点"）
        main_table = package.split("### 6. 阶段地图", 1)[1].split("###", 1)[0]
        assert "痛点" in main_table, "JOURNEY-retail-demo-v1.md §6 阶段表缺「痛点」列"
        assert "机会" in main_table, "JOURNEY-retail-demo-v1.md §6 阶段表缺「机会」列"
        # 6b 节必须有 F04 这种 inferred_from_pain_point 机会
        assert "inferred_from_pain_point" in package, "JOURNEY-retail-demo-v1.md 缺 inferred_from_pain_point 机会"

    def test_journey_gaps_example_reuses_package_gap_ids(self) -> None:
        package = read(EXAMPLES / "JOURNEY-retail-demo-v1.md")
        gaps = read(EXAMPLES / "JOURNEY-retail-demo-gaps.md")
        package_gap_ids = set(re.findall(r"JOURNEY-G\d+", package))
        gaps_ids = set(re.findall(r"JOURNEY-G\d+", gaps))
        assert gaps_ids
        assert gaps_ids.issubset(package_gap_ids)


class TestJourneyAgentContract:
    def test_agent_contains_journey_phase_and_routing(self) -> None:
        agent = read(REPO_ROOT / "agents" / "pratyaya.md")
        for phrase in (
            "用户提到 \"用户旅程\" / \"Journey\" / \"User Journey\" / \"旅程画布\" / \"当前旅程\"",
            "不属于 MVL / 黄金圈 / HMW / 用户画像语境",
            "直接进入 Phase Journey",
            "Persona 为独立画布",
        ):
            assert phrase in agent
        # v3.3.0 P2：Journey 专属 Phase 章节已并入「标准画布管线」，
        # 章节标题字面量断言由注册表结构化断言替代（Q3-B）。
        journey = by_id(parse_canvas_registry(agent), "journey")
        assert journey is not None, "画布注册表缺少 journey 条目"
        assert journey.distill == "journey-distill"
        assert journey.gate == "journey-gate"
        assert "## 标准画布管线" in agent

    def test_agent_contains_journey_mandatory_instruction_card(self) -> None:
        """v3.3.0 P3：Journey 强制执行指令已下沉到 JOURNEY-pipeline.md（§6.3 不删除只下沉）。

        agent md 内联指令卡已移除，改为跨画布 3 条红线 + 引用标注；指令原文保留在
        JOURNEY-pipeline.md，故改为「反内联 + 下沉原文」双层断言。
        """
        agent = read(REPO_ROOT / "agents" / "pratyaya.md")
        # 内联指令卡已移除
        assert "### Journey 强制执行指令" not in agent
        # 指令原文完整保留在 JOURNEY-pipeline.md
        pipeline = read(JOURNEY_DISTILL / "references" / "JOURNEY-pipeline.md")
        for phrase in (
            "不属于 MVL / GC / HMW / Persona",
            "不修改 MVL M2 的 `09-user-journey.md`",
            "不写 `state.modules.M2`",
            "主表忠实保留 5 行合并结构",
            "正式渲染只读 `JOURNEY-{slug}-v{N}.md`",
            "质量鉴别必须在正式画布外显",
            "只有 `business_risk` 可 override",
            "`information_integrity` 不可 override",
        ):
            assert phrase in pipeline, f"JOURNEY-pipeline.md 缺强制指令：{phrase}"

    def test_agent_contains_journey_state_and_render_paths(self) -> None:
        """v3.3.0 P2：Journey 的产物路径由画布注册表推导，不再硬编码在正文。

        参数化后正文只保留 ``modules/{文件前缀}-{slug}-v{N}.md`` 这类模板，
        具体值（JOURNEY / journey）的唯一事实源是注册表，故改为双层断言：
        ① 注册表 journey 条目取值正确；② 标准管线仍声明了参数化路径模板。
        """
        agent = read(REPO_ROOT / "agents" / "pratyaya.md")
        journey = by_id(parse_canvas_registry(agent), "journey")
        assert journey is not None, "画布注册表缺少 journey 条目"
        assert journey.state_key == "journey.{slug}"
        assert journey.file_prefix == "JOURNEY"
        assert journey.output_prefix == "journey"
        assert journey.audit_type == "journey"
        assert (
            journey.template
            == "skills/canvas-render/examples/user-journey-canvas.html"
        )
        for pattern in (
            "modules/{文件前缀}-{slug}-keypoints.md",
            "modules/{文件前缀}-{slug}-v{N}.md",
            "modules/{文件前缀}-{slug}-gaps.md",
            "output/{输出前缀}-canvas-{slug}.html",
            "state.{state_key}.gate_recommendation",
            "render-contract-journey.md",
        ):
            assert pattern in agent, f"标准管线缺参数化路径模板：{pattern}"


class TestExplicitCanvasRoutingContract:
    """v3.0.0：主 Agent 必须显式判定画布类型，不再把未指定逐字稿默认送入 MAAU。"""

    def test_agent_asks_canvas_type_for_untyped_transcript(self) -> None:
        agent = read(REPO_ROOT / "agents" / "pratyaya.md")
        assert "**未指定画布分支**" in agent
        assert "追问画布类型，不进入 MAAU、V2C VAC 或任何其他画布" in agent
        assert "只给逐字稿 / 会议材料时不进入任何默认画布" in agent
        assert "不推荐默认画布" in agent

    def test_agent_requires_explicit_m1_m6_selection(self) -> None:
        agent = read(REPO_ROOT / "agents" / "pratyaya.md")
        assert "**M1-M6 六模块管线（显式备选，Phase 1）**" in agent
        assert "MVL 六模块管线" in agent
        assert "显式备选" in agent

    def test_agent_collects_metadata_before_writing_state_for_maau(self) -> None:
        agent = read(REPO_ROOT / "agents" / "pratyaya.md")
        # 元数据前置收集：缺 project_slug/group_id/instance_slug 时先收集，确认前不写 state
        assert "**元数据前置收集**" in agent
        assert "`project_slug` / `group_id` / `instance_slug`" in agent
        assert "确认前不创建目录、不写 `state.json`、不存档逐字稿、不调用 `maau-synthesize`" in agent

    def test_agent_removed_legacy_default_routing_text(self) -> None:
        agent = read(REPO_ROOT / "agents" / "pratyaya.md")
        # 旧默认兜底（无画布类型信息时先问 MVL/画布类型和阶段）必须已删除
        assert "如果用户的消息没有画布类型信息" not in agent
        # 旧"平行一次性综合路径"措辞必须已删除
        assert "平行一次性综合路径" not in agent
        # 重复的"不明确"追问（两个不明确块）应已合并为单一分支
        assert agent.count("不明确") <= 3

    def test_agent_has_single_persona_route(self) -> None:
        agent = read(REPO_ROOT / "agents" / "pratyaya.md")
        # 重复 Persona 判定应已合并为单一入口（此前存在两处"用户画像/PERSONA"路由）
        persona_route = agent.count('用户提到 "用户画像"')
        assert persona_route == 1, f"Persona 判定应只有 1 处，实际 {persona_route} 处"

    def test_plugin_json_entry_context(self) -> None:
        plugin = json.loads(read(REPO_ROOT / ".codebuddy-plugin" / "plugin.json"))
        # v3.0 入口语境：displayDescription 与 quickPrompts 已显式包含 V2C VAC，且不再宣称 MAAU 默认
        assert "V2C VAC" in plugin["displayDescription"]["zh"]
        assert "V2C" in plugin["displayDescription"]["en"]
        assert "V2C" in plugin["quickPrompts"][1]["zh"]
        assert "V2C" in plugin["quickPrompts"][1]["en"]
        assert "default" not in plugin["description"].lower()
        assert "默认" not in plugin["displayDescription"]["zh"]
        assert "MAAU" in plugin["displayDescription"]["zh"]
        assert "MAAU" in plugin["displayDescription"]["en"]


class TestV2CVacContract:
    def test_v2c_vac_skill_files_and_frontmatter_exist(self) -> None:
        for path, expected_name in (
            (V2C_VAC_DISTILL / "SKILL.md", "v2c-vac-distill"),
            (V2C_VAC_GATE / "SKILL.md", "v2c-vac-gate"),
        ):
            text = read(path)
            assert re.search(rf"^name:\s*{expected_name}\s*$", text, re.MULTILINE)
        assert (V2C_VAC_DISTILL / "references" / "v2c-vac-spec.md").is_file()
        assert (V2C_VAC_DISTILL / "frameworks" / "v2c-vac-value-attribution.md").is_file()
        assert (V2C_VAC_GATE / "references" / "V2C-gate.md").is_file()

    def test_v2c_vac_gate_has_twelve_stable_ids_and_default_gaps(self) -> None:
        gate = read(V2C_VAC_GATE / "references" / "V2C-gate.md")
        ids = sorted(set(re.findall(r"V2C-GATE-\d{2}", gate)))
        assert ids == [f"V2C-GATE-{n:02d}" for n in range(1, 13)]
        assert gate.count("information_integrity") >= 7
        assert gate.count("business_risk") >= 5
        for gap_id in (f"V2C-AG{n:02d}" for n in range(1, 7)):
            assert gap_id in gate

    def test_v2c_vac_render_contract_and_template_share_canvas_type_and_anchors(self) -> None:
        contract = read(V2C_VAC_CONTRACT)
        template = read(V2C_VAC_TEMPLATE)
        for text in (contract, template):
            assert "v2c-vac" in text
            assert "canvas_type=v2c" not in text
            assert '"canvas_type":"v2c"' not in text
            assert '"canvas_type": "v2c"' not in text
        assert 'data-page-type="v2c-vac"' in template
        for anchor in (
            "v2c-vac-headline",
            "v2c-vac-attribution-chain",
            "v2c-vac-primary-capability",
            "v2c-vac-primary-change",
            "v2c-vac-impact-chain",
            "v2c-vac-value-anchor",
            "v2c-vac-quality-check",
            "quality-panel",
            "canvas-data",
        ):
            assert f"`{anchor}`" in contract, f"contract 缺 {anchor}"
            assert f'id="{anchor}"' in template, f"template 缺 {anchor}"
        for gate_id in (f"V2C-VAC-TPL-GATE-{n:02d}" for n in range(1, 9)):
            assert gate_id in contract

    def test_v2c_vac_fixtures_exist_for_audit_regression(self) -> None:
        for name in (
            "V2C-VAC-sample-vac-v1.md",
            "state-gate-pass.json",
            "state-override-business-risk.json",
            "state-index.json",
            "v2c-vac-canvas-sample-vac.html",
            "v2c-vac-canvas-index.html",
        ):
            assert (V2C_VAC_FIXTURES / name).is_file(), f"missing V2C VAC fixture {name}"

    def test_contract_consistency_lists_and_runs_v2c_vac_rules(self) -> None:
        listed = subprocess.run(
            [sys.executable, str(CONTRACT_CHECKER), "--list"],
            capture_output=True,
            text=True,
            check=True,
        )
        for rule in (
            "V2C_VAC_SKILL_PATH",
            "V2C_VAC_GATE_FILE",
            "V2C_VAC_RENDER_CONTRACT",
            "V2C_VAC_STATE_SCHEMA",
        ):
            assert rule in listed.stdout
        result = subprocess.run(
            [
                sys.executable,
                str(CONTRACT_CHECKER),
                "--rules",
                "V2C_VAC_SKILL_PATH,V2C_VAC_GATE_FILE,V2C_VAC_RENDER_CONTRACT,V2C_VAC_STATE_SCHEMA",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr


class TestMvlGateTableWidthContract:
    def test_mvl_gate_five_column_format_is_formally_accepted(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(CONTRACT_CHECKER),
                "--rules",
                "GATE_TABLE_WIDTH",
                "--json",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(result.stdout)
        assert payload["count"] == 0


class TestConfirmationPackageSections:
    def test_skill_template_contains_required_sections(self) -> None:
        template = read(DISTILL / "SKILL.md")
        for section in REQUIRED_PACKAGE_SECTIONS:
            assert section in template, f"SKILL.md template missing section: {section}"

    def test_example_package_contains_required_sections(self) -> None:
        example = read(EXAMPLES / "HMW-retail-demo-v1.md")
        for section in REQUIRED_PACKAGE_SECTIONS:
            assert section in example, f"HMW-retail-demo-v1.md missing section: {section}"


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
        example = read(EXAMPLES / "HMW-retail-demo-v1.md")
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


# ---------------------------------------------------------------------------
# v3.3.0 P3：薄控制面门禁 + pipeline 下沉契约（执行计划 §8.4 / §6.2）
# ---------------------------------------------------------------------------

# P3 门禁：agent md ≤ 400 行（方案 A；P2 为 900 防回涨，P3 顺延至 400）
CURRENT_GATE = 400

# distill SKILL → pipeline reference 映射（按目录清单显式声明，不按命名推断；
# mvl-distill 双文件，maau-synthesize 非 *-distill 命名）
DISTILL_PIPELINE_REFERENCES: dict[str, tuple[str, ...]] = {
    "mvl-distill": ("references/M-pipeline.md", "references/global-pipeline.md"),
    "maau-synthesize": ("references/MAAU-pipeline.md",),
    "gc-distill": ("references/GC-pipeline.md",),
    "hmw-distill": ("references/HMW-pipeline.md",),
    "persona-distill": ("references/PERSONA-pipeline.md",),
    "journey-distill": ("references/JOURNEY-pipeline.md",),
    "v2c-vac-distill": ("references/V2C-VAC-pipeline.md",),
    "5w-distill": ("references/5W-pipeline.md",),
}

PIPELINE_REQUIRED_SECTIONS = ("输入", "输出", "状态写入", "Gate", "渲染审计")


class TestThinControlPlaneContract:
    """v3.3.0 P3：主 Agent 薄控制面门禁（§8.4）。"""

    def test_agent_is_thin_control_plane(self) -> None:
        """主 Agent 必须是薄控制面：行数硬门禁，防回涨。"""
        agent = read(REPO_ROOT / "agents" / "pratyaya.md")
        n = len(agent.splitlines())
        assert n <= CURRENT_GATE, (
            f"agent md 已回涨至 {n} 行（门禁 {CURRENT_GATE}）；请把新增细节下沉到 skills/"
        )

    def test_agent_has_no_full_pipeline(self) -> None:
        """反 D1 回归：agent md 不得复述完整 8 步执行细节（应引用 references）。"""
        agent = read(REPO_ROOT / "agents" / "pratyaya.md")
        assert agent.count("步骤 7：视觉模式选择与渲染") <= 1

    def test_agent_retains_universal_governance_principles(self) -> None:
        """通用治理原则不得下沉到 skill（否则 8 处重复 + 决策点不可见，§6.2 黑名单）。"""
        agent = read(REPO_ROOT / "agents" / "pratyaya.md")
        for principle in ("Gate 只输出建议", "人确认的是版本", "未讨论就明确标空"):
            assert principle in agent, f"agent md 缺通用治理原则：{principle}"


class TestPipelineReferenceContract:
    """v3.3.0 P3：distill SKILL 必须引用 pipeline reference（§6.2）。"""

    def test_each_distill_declares_pipeline_reference(self) -> None:
        """每个 distill SKILL.md 必须引用对应 pipeline reference，否则下沉细节读不到。"""
        for skill_name, refs in DISTILL_PIPELINE_REFERENCES.items():
            skill_md = read(SKILLS / skill_name / "SKILL.md")
            for ref in refs:
                assert ref in skill_md, f"{skill_name}/SKILL.md 未声明 {ref}"

    def test_pipeline_reference_has_required_sections(self) -> None:
        """每个 pipeline reference 必须覆盖五类小节，否则执行细节不完整。"""
        for skill_name, refs in DISTILL_PIPELINE_REFERENCES.items():
            for ref in refs:
                ref_text = read(SKILLS / skill_name / ref)
                for section in PIPELINE_REQUIRED_SECTIONS:
                    assert f"## {section}" in ref_text, (
                        f"{skill_name}/{ref} 缺「{section}」小节"
                    )
