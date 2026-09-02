"""Gate 汇总 —— 三态判定与 override 资格。

规则（`agents/pratyaya.md` 决策矩阵，§「Gate 检查点 / 决策矩阵」）：
- 全 PASS → gate_recommendation=pass，可正常确认（gate_pass）。
- 仅 business_risk FAIL → gate_recommendation=fail，override_eligible=True（可 override）。
- 含 information_integrity FAIL → gate_recommendation=fail，override_eligible=False（不可 override）。

红线：本模块只做「结果的规则型归类」，不做语义判定——每一项 PASS/FAIL 的语义判断
由各 gate Skill 完成，本模块只按其 verdict + category 汇总。
"""

from __future__ import annotations

from dataclasses import dataclass

ALLOWED_VERDICTS: tuple[str, ...] = ("pass", "fail", "warn")
ALLOWED_CATEGORIES: tuple[str, ...] = ("business_risk", "information_integrity")
# warn 不阻塞（视为通过，但保留记录）。
BLOCKING_VERDICTS: frozenset[str] = frozenset({"fail"})


@dataclass(frozen=True)
class Assessment:
    assessment_id: str
    verdict: str          # pass / fail / warn
    category: str         # business_risk / information_integrity


@dataclass(frozen=True)
class GateSummary:
    gate_recommendation: str                 # "pass" / "fail"
    override_eligible: bool                  # 仅 business_risk fail 时 True
    has_information_integrity_fail: bool
    failed: tuple[Assessment, ...]


def evaluate(assessments: list[Assessment] | tuple[Assessment, ...]) -> GateSummary:
    failed = tuple(a for a in assessments if a.verdict in BLOCKING_VERDICTS)
    if not failed:
        return GateSummary("pass", False, False, ())
    has_ii = any(a.category == "information_integrity" for a in failed)
    # 含 information_integrity fail 即不可 override；否则（仅 business_risk）可 override。
    return GateSummary("fail", not has_ii, has_ii, failed)
