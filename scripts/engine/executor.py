"""标准 8 步推进 / 回退 / 轮次与版本映射。

规则源（`agents/pratyaya.md`「标准 8 步」「轮次与版本的关系」）：
- 步骤 0（模式选择）→ 1（Key Points）→ 用户决策分支 2/3/4 → 5（确认包展示）→ 6（Gate）→ 7（渲染）→ 8（完成）；
- 补问（步骤 3）回步骤 1 进入下一轮转写；先看个样子（步骤 4）状态不变，仍可提炼 / 补问；
- 轮次 N = 版本 vN（第 N 轮 Key Points 抽取后生成确认包 vN）。

红线：本模块只做步骤图与映射的规则判定，不做语义判断、不渲染、不写授权。
状态约束由 `state.py` 负责，授权写入由 `authorization.py` 负责。
"""

from __future__ import annotations

from typing import Any

STEPS: tuple[int, ...] = (0, 1, 2, 3, 4, 5, 6, 7, 8)

# 步骤合法后继。步骤 2/3/4 为用户决策的并行分支（提炼 / 补问 / 先看个样子）。
NEXT_STEPS: dict[int, frozenset[int]] = {
    0: frozenset({1}),
    1: frozenset({2, 3, 4}),
    2: frozenset({5}),          # 提炼 → 确认包展示
    3: frozenset({1}),          # 补问 → 下一轮转写（升版）
    4: frozenset({2, 3}),       # 先看个样子状态不变，仍可提炼 / 补问
    5: frozenset({6}),          # 确认包展示 → 自动进 Gate
    6: frozenset({7}),          # Gate + 用户决策 → 渲染
    7: frozenset({8}),          # 渲染验收 → 完成
    8: frozenset(),             # 终点
}

# 用户决策分支 → 目标状态（preview 状态不变 → None）。
BRANCH_STATUS: dict[str, str | None] = {
    "refine": "review_ready",
    "supplement": "gaps_open",
    "preview": None,
}


class ExecutorError(ValueError):
    """非法步骤推进 / 分支参数。"""


def is_valid_step(step: Any) -> bool:
    return step in STEPS


def assert_valid_step(step: Any) -> None:
    if not is_valid_step(step):
        raise ExecutorError(f"非法步骤：{step!r}（须为 0..8 之一）")


def can_advance(from_step: int, to_step: int) -> bool:
    if not is_valid_step(from_step) or not is_valid_step(to_step):
        return False
    return to_step in NEXT_STEPS.get(from_step, frozenset())


def assert_advance(from_step: int, to_step: int) -> None:
    if not can_advance(from_step, to_step):
        raise ExecutorError(f"非法步骤推进：{from_step} -> {to_step}")


def round_to_version(round_number: Any) -> int:
    """第 N 轮 Key Points → 确认包 vN（N 与 vN 数值等同，语义不同）。"""
    if not isinstance(round_number, int) or isinstance(round_number, bool) or round_number < 1:
        raise ExecutorError(f"轮次须为 >=1 的整数：{round_number!r}")
    return round_number


def branch_to_status(branch: str) -> str | None:
    """用户决策分支 → 目标状态；preview 状态不变返回 None。"""
    if branch not in BRANCH_STATUS:
        raise ExecutorError(f"非法用户决策分支：{branch!r}（须为 refine/supplement/preview）")
    return BRANCH_STATUS[branch]
