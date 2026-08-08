"""maau-synthesize Skill 的源包契约测试（六板块 / 来源线索 / 缺口表 / 推断表 / Gate 决策 / 禁止污染 M1-M6）。"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "maau-synthesize"

SKILL_MD = SKILL_DIR / "SKILL.md"
SPEC_MD = SKILL_DIR / "references" / "maau-synth-spec.md"
EXAMPLE_MD = SKILL_DIR / "references" / "maau-synthesize-example.md"

SIX_BOARDS = [
    "Intent",
    "User",
    "Agent Team",
    "Workflow",
    "Context",
    "Validation",
]

REQUIRED_SPEC_MARKERS = [
    "来源线索",
    "缺口表",
    "推断表",
    "Gate 与用户决策",
    "transcript-direct",
]


@pytest.fixture(scope="module")
def files() -> dict[str, str]:
    return {
        "skill": SKILL_MD.read_text(encoding="utf-8"),
        "spec": SPEC_MD.read_text(encoding="utf-8"),
        "example": EXAMPLE_MD.read_text(encoding="utf-8"),
    }


class TestSkillFilesExist:
    def test_all_skill_files_present(self) -> None:
        assert SKILL_MD.exists()
        assert SPEC_MD.exists()
        assert EXAMPLE_MD.exists()


class TestSkillFrontmatter:
    def test_skill_name_is_maau_synthesize(self, files: dict[str, str]) -> None:
        head = files["skill"].split("---", 2)[1]
        assert "name: maau-synthesize" in head

    def test_skill_description_says_no_gate_no_render_no_state(self, files: dict[str, str]) -> None:
        head = files["skill"].split("---", 2)[1]
        assert "不调用 Canvas 渲染" in head
        assert "不执行闸门判定" in head
        assert "不写 state" in head


class TestSpecSixBoards:
    def test_spec_contains_all_six_boards(self, files: dict[str, str]) -> None:
        spec = files["spec"]
        for board in SIX_BOARDS:
            assert board in spec, f"spec 缺少板块 {board}"

    def test_spec_contains_required_markers(self, files: dict[str, str]) -> None:
        spec = files["spec"]
        for marker in REQUIRED_SPEC_MARKERS:
            assert marker in spec, f"spec 缺少标记 {marker}"

    def test_spec_has_generation_path(self, files: dict[str, str]) -> None:
        assert "transcript-direct" in files["spec"]
        assert "generation_path" in files["spec"]

    def test_spec_mentions_three_workflow_node_types(self, files: dict[str, str]) -> None:
        spec = files["spec"]
        assert "Agent 执行节点" in spec
        assert "人工操作" in spec
        assert "人审" in spec


class TestSourcePackageNoMvlPollution:
    def test_spec_does_not_output_m1_vN(self, files: dict[str, str]) -> None:
        """源包输出不得使用 Mx-v{N}.md 文件名，避免污染 MVL 状态机。"""
        spec = files["spec"]
        assert "MAAU-{slug}-v{N}.md" in spec
        # 文件名命名节不应出现把源包输出命名为 M1/M2...M6 的写法
        assert "M1-v" not in spec.replace("MAAU", "")

    def test_skill_does_not_call_render_or_write_state(self, files: dict[str, str]) -> None:
        skill = files["skill"]
        assert "不调用 Canvas 渲染" in skill
        assert "不写 `state.json`" in skill or "不写 state" in skill


class TestExampleSourcePackage:
    def test_example_contains_all_six_boards(self, files: dict[str, str]) -> None:
        example = files["example"]
        for board in SIX_BOARDS:
            assert board in example, f"example 缺少板块 {board}"

    def test_example_has_source_traces_and_gap_inference_gate(self, files: dict[str, str]) -> None:
        example = files["example"]
        assert "来源线索" in example
        assert "缺口表" in example
        assert "推断表" in example
        assert "Gate 与用户决策" in example

    def test_example_generation_path_is_transcript_direct(self, files: dict[str, str]) -> None:
        assert "transcript-direct" in files["example"]

    def test_example_does_not_use_m1_vN_filename(self, files: dict[str, str]) -> None:
        # example 语义应为 MAAU-retail-demo-v1.md，不承载 M1-M6
        assert "MAAU-retail-demo-v1.md" in files["example"]
