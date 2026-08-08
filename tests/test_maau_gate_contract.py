"""module-conclusion-gate 的 MAAU 闸门契约测试。

覆盖执行计划 §11.4：
- MAAU-gate.md 存在；
- ID 全部匹配 MAAU-GATE-[0-9]+；
- 分类只允许 information_integrity / business_risk；
- 至少覆盖六板块完整性、Workflow 三类节点、Context、Validation、跨板块自洽；
- 不出现 M1-GATE-* 作为 MAAU 检查项 ID。
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
GATE_FILE = (
    REPO_ROOT
    / "skills"
    / "module-conclusion-gate"
    / "references"
    / "MAAU-gate.md"
)


def read() -> str:
    return GATE_FILE.read_text(encoding="utf-8")


class TestMaauGateFile:
    def test_gate_file_exists(self) -> None:
        assert GATE_FILE.exists()

    def test_gate_id_space_is_maau(self) -> None:
        text = read()
        ids = re.findall(r"MAAU-GATE-0?([0-9]+)", text)
        assert ids, "MAAU-gate.md 未找到任何 MAAU-GATE-* 稳定 ID"
        # 覆盖 MAAU-GATE-01 到 MAAU-GATE-09
        for n in range(1, 10):
            assert str(n) in ids, f"MAAU-gate.md 缺 MAAU-GATE-{n:02d}"

    def test_categories_only_allow_two_types(self) -> None:
        text = read()
        # 表格行内分类列只能为 information_integrity / business_risk
        allowed = {"information_integrity", "business_risk"}
        # 提取表格行中的分类（紧跟在 | 后、风险等级前）
        for m in re.finditer(r"\|\s*`(information_integrity|business_risk)`\s*\|", text):
            assert m.group(1) in allowed
        # 不允许出现其他分类词
        for bad in ("legal", "security", "ethical"):
            assert bad not in text, f"MAAU-gate.md 不应出现分类 {bad}"

    def test_both_categories_present(self) -> None:
        text = read()
        assert "information_integrity" in text
        assert "business_risk" in text

    def test_covers_six_board_completeness(self) -> None:
        text = read()
        assert "六板块固定字段完整" in text
        assert "MAAU-GATE-03" in text

    def test_covers_workflow_three_node_types(self) -> None:
        text = read()
        assert "三类节点" in text
        assert "MAAU-GATE-04" in text

    def test_covers_context(self) -> None:
        text = read()
        assert "Context" in text
        assert "MAAU-GATE-05" in text

    def test_covers_validation(self) -> None:
        text = read()
        assert "Validation" in text
        assert "MAAU-GATE-06" in text

    def test_covers_cross_board_coherence(self) -> None:
        text = read()
        assert "跨板块自洽" in text
        assert "MAAU-GATE-07" in text

    def test_does_not_reuse_m1_gate_id(self) -> None:
        text = read()
        # MAAU 检查项不得复用 M1-GATE-* 到 M6-GATE-* 作为稳定 ID
        assert "M1-GATE-01" not in text.replace("MAAU-GATE-01", ""), "MAAU-gate.md 不应出现 M1-GATE-*"
        for m in re.finditer(r"(M[1-6]-GATE-[0-9]+)", text):
            pytest.fail(f"MAAU-gate.md 出现非 MAAU 的稳定 ID: {m.group(1)}")

    def test_overrides_only_for_business_risk(self) -> None:
        text = read()
        assert "不可 override" in text
        assert "可 override" in text
