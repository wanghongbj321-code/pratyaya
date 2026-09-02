"""规则一致性防线测试（§7.8 / R14）。

references（`{canvas}-distill/references/{PREFIX}-pipeline.md`）中声明了会被引擎
强制的确定性规则。引擎不运行时读这些 Markdown（保持 §7.6 依赖边界），一致性由
本测试在 CI 校验：references 的规则块内容必须与 `skills/_engine` 实现一致，
防止「agent 说 A、引擎判 B、references 写 C」的三处分散。

本测试只校验**确定性规则**（升版重置 / 授权 if-then / Gate 汇总），不校验语义
判定（内容充分性、推断识别等归 LLM）。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# 引擎事实词：从 skills/_engine 模块中确定性规则的关键 token 派生。
# 若引擎规则语义变化，此处应随之更新（本测试的作用正是让这类变化强制同步 references）。
from skills._engine import gate as engine_gate  # noqa: E402
from skills._engine import state as engine_state  # noqa: E402

# 每份 pipeline reference 的确定性规则块（规则 id → 该引擎实现必须包含的事实 token）。
# 语料与 references 中的 `<!-- rule:{id}: ... -->` 注释对应。
ENGINE_RULE_FACTS: dict[str, tuple[str, ...]] = {
    # state.reset_for_bump：version+1 / gate_recommendation→pending /
    # render_authorized→false / confirmation_mode→null / override_audit 移除
    "bump-version": (
        "升版",
        "version+1",
        "render_authorized",
        "confirmation_mode",
        "override_audit",
        "第 12 节",
    ),
    # state.validate_if_then：override → fail+true+override_audit；
    # gate_pass → pass+true；draft/gaps_open/review_ready → render_authorized=false
    "authorization-if-then": (
        "override",
        "gate_pass",
        "render_authorized",
        "gate_recommendation",
        "override_audit",
        "false",
    ),
    # gate.evaluate：全 PASS→pass；仅 business_risk FAIL→fail+可 override；
    # 含 information_integrity FAIL→fail+不可 override
    "gate-summary": (
        "business_risk",
        "information_integrity",
        "pass",
        "fail",
        "override",
    ),
}

# 规则 id 全集 = 引擎确定性规则清单（测试强制 references 至少各声明一次）。
KNOWN_RULE_IDS = frozenset(ENGINE_RULE_FACTS)

# pipeline reference 清单（与 tests/test_contract_consistency.py 的
# DISTILL_PIPELINE_REFERENCES 一致，显式声明不按命名推断）。
PIPELINE_REFERENCES: dict[str, tuple[str, ...]] = {
    "mvl-distill": ("references/M-pipeline.md", "references/global-pipeline.md"),
    "maau-synthesize": ("references/MAAU-pipeline.md",),
    "gc-distill": ("references/GC-pipeline.md",),
    "hmw-distill": ("references/HMW-pipeline.md",),
    "persona-distill": ("references/PERSONA-pipeline.md",),
    "journey-distill": ("references/JOURNEY-pipeline.md",),
    "v2c-vac-distill": ("references/V2C-VAC-pipeline.md",),
    "5w-distill": ("references/5W-pipeline.md",),
}

# `<!-- rule:{id}: ... -->` 单行注释块。
_RULE_COMMENT_RE = re.compile(r"<!--\s*rule:([a-z0-9-]+):\s*(.+?)\s*-->")


def _iter_rule_blocks() -> list[tuple[str, str]]:
    """遍历所有 pipeline references，返回 [(rule_id, 块文本)]。"""
    blocks: list[tuple[str, str]] = []
    for skill_name, refs in PIPELINE_REFERENCES.items():
        for ref in refs:
            text = (REPO_ROOT / "skills" / skill_name / ref).read_text(encoding="utf-8")
            for m in _RULE_COMMENT_RE.finditer(text):
                blocks.append((m.group(1), m.group(2)))
    return blocks


def _engine_rule_guard(*, rule_id: str) -> None:
    """显式引用引擎实现，确保规则 id 与引擎模块语义对应（防幽灵 id）。"""
    if rule_id == "bump-version":
        # 引擎升版重置目标状态必须含 draft / gaps_open。
        assert {"draft", "gaps_open"} <= set(engine_state.BUMP_TARGET_STATUSES)
    elif rule_id == "authorization-if-then":
        # 引擎 if/then 允许的确认模式必须含 gate_pass / override。
        assert {"gate_pass", "override"} <= set(engine_state.ALLOWED_CONFIRMATION_MODES)
    elif rule_id == "gate-summary":
        # 引擎 Gate 分类必须含 business_risk / information_integrity。
        assert {"business_risk", "information_integrity"} <= set(
            engine_gate.ALLOWED_CATEGORIES
        )


def test_each_pipeline_reference_declares_all_rule_ids() -> None:
    """每个 pipeline reference 都必须声明全部确定性规则（升版重置 / 授权 / Gate 汇总）。

    防「某画布 references 缺失规则锚点 → 该画布执行细节失去引擎一致性参照」。
    """
    for skill_name, refs in PIPELINE_REFERENCES.items():
        for ref in refs:
            text = (REPO_ROOT / "skills" / skill_name / ref).read_text(encoding="utf-8")
            declared = {m.group(1) for m in _RULE_COMMENT_RE.finditer(text)}
            missing = KNOWN_RULE_IDS - declared
            assert not missing, (
                f"{skill_name}/{ref} 缺确定性规则块：{sorted(missing)}"
            )


def test_no_unknown_rule_id_declared() -> None:
    """references 不得声明引擎未实现的规则 id（未知 id 视为待引擎化清单的遗漏）。"""
    for rule_id, _text in _iter_rule_blocks():
        assert rule_id in KNOWN_RULE_IDS, f"references 声明了引擎未实现的规则 id：{rule_id!r}"


def test_rule_blocks_match_engine_implementation() -> None:
    """references 规则块的事实须与引擎实现一致（§7.8）。

    对每个 rule id，先以引擎模块做守卫断言（确保测试语料与引擎语义绑定），
    再校验 references 块文本包含该规则的全部事实 token。
    """
    blocks = _iter_rule_blocks()
    assert blocks, "未在 pipeline references 中找到任何 rule 块"

    seen: set[str] = set()
    for rule_id, text in blocks:
        _engine_rule_guard(rule_id=rule_id)
        seen.add(rule_id)
        for token in ENGINE_RULE_FACTS[rule_id]:
            assert token in text, (
                f"rule:{rule_id} 块缺引擎事实 token {token!r}（references 与引擎实现不一致）："
                f"{text}"
            )

    assert seen == KNOWN_RULE_IDS, f"references 规则块覆盖不全：{sorted(KNOWN_RULE_IDS - seen)} 缺失"
