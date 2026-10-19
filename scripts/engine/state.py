"""状态机与升版边界 —— 5 态机、if/then 授权约束、业务变更升版重置。

红线：本模块只做**规则型判定与字段变换**，不做语义判断、不渲染、不替人拍板。
状态机与约束以 `agents/pratyaya.md`「模块状态机 / 升版边界 / 标准 8 步」和
`schemas/state.schema.json` 为唯一事实源。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import paths

# schema_version 恒定（§7.4 红线 4：引擎不改 schema_version）。
SCHEMA_VERSION = "2.4"

ALLOWED_STATUSES: tuple[str, ...] = (
    "draft", "gaps_open", "review_ready", "confirmed", "rendered",
)
ALLOWED_GATE_RECOMMENDATIONS: tuple[str, ...] = ("pass", "fail", "pending")
ALLOWED_CONFIRMATION_MODES: tuple[str, ...] = ("gate_pass", "override")
# single_canvas_state_base 的 override_audit.items[].category 约束为 business_risk。
ALLOWED_OVERRIDE_CATEGORIES: tuple[str, ...] = ("business_risk",)

# 普通跃迁（不含升版）。自环为幂等更新，允许。
# 升版（业务内容变更）从任意态回 draft / gaps_open，走 `reset_for_bump`，不经此表。
TRANSITIONS: dict[str, frozenset[str]] = {
    "draft": frozenset({"draft", "gaps_open", "review_ready"}),
    "gaps_open": frozenset({"gaps_open", "review_ready"}),
    "review_ready": frozenset({"gaps_open", "review_ready", "confirmed"}),
    "confirmed": frozenset({"confirmed", "rendered"}),
    "rendered": frozenset({"rendered"}),
}

# 升版允许回落的目标状态。
BUMP_TARGET_STATUSES: tuple[str, ...] = ("draft", "gaps_open")


class StateMachineError(ValueError):
    """非法状态跃迁 / 升版参数错误。"""


def is_valid_status(status: Any) -> bool:
    return status in ALLOWED_STATUSES


def can_transition(from_status: str, to_status: str) -> bool:
    """普通跃迁是否合法（不含升版）。"""
    if not is_valid_status(from_status) or not is_valid_status(to_status):
        return False
    return to_status in TRANSITIONS.get(from_status, frozenset())


def assert_transition(from_status: str, to_status: str) -> None:
    """普通跃迁校验；非法即 raise（绕过检测的拦截点）。"""
    if not can_transition(from_status, to_status):
        raise StateMachineError(
            f"非法状态跃迁：{from_status!r} -> {to_status!r}"
        )


def reset_for_bump(instance: dict[str, Any], new_status: str = "draft") -> dict[str, Any]:
    """升版重置（业务内容变更）：version+1、清 4 字段、清 override_audit、状态回落。

    对应 `agents/pratyaya.md` 升版边界 8 条中的状态与治理字段部分；旧 HTML 过期标记
    由 `files.py` 负责，重跑 Gate 由流程负责。不改入参，返回新 dict。
    """
    if new_status not in BUMP_TARGET_STATUSES:
        raise StateMachineError(
            f"升版只能回落到 {BUMP_TARGET_STATUSES!r}，得到 {new_status!r}"
        )
    bumped = dict(instance)
    bumped["version"] = int(instance.get("version", 0)) + 1
    bumped["gate_recommendation"] = "pending"
    bumped["render_authorized"] = False
    bumped["confirmation_mode"] = None
    bumped["status"] = new_status
    bumped.pop("override_audit", None)
    return bumped


def validate_if_then(instance: dict[str, Any]) -> list[str]:
    """校验实例治理字段的 if/then 约束，返回违反项列表（空 = 通过）。

    约束来源 `schemas/state.schema.json` 的 `allOf`：
    - override → gate_recommendation=fail 且 render_authorized=true 且 override_audit 必填；
    - gate_pass → gate_recommendation=pass 且 render_authorized=true；
    - status ∈ {draft, gaps_open, review_ready} → render_authorized=false 且 confirmation_mode=null。
    """
    problems: list[str] = []
    status = instance.get("status")
    mode = instance.get("confirmation_mode")
    gr = instance.get("gate_recommendation")
    ra = instance.get("render_authorized")

    if mode == "override":
        if gr != "fail":
            problems.append("override：gate_recommendation 必须为 fail")
        if ra is not True:
            problems.append("override：render_authorized 必须为 true")
        if not instance.get("override_audit"):
            problems.append("override：override_audit 必填")
    if mode == "gate_pass":
        if gr != "pass":
            problems.append("gate_pass：gate_recommendation 必须为 pass")
        if ra is not True:
            problems.append("gate_pass：render_authorized 必须为 true")
    if status in ("draft", "gaps_open", "review_ready"):
        if ra is not False:
            problems.append(f"status={status}：render_authorized 必须为 false")
        if mode is not None:
            problems.append(f"status={status}：confirmation_mode 必须为 null")
    return problems


def assert_valid_if_then(instance: dict[str, Any]) -> None:
    problems = validate_if_then(instance)
    if problems:
        raise StateMachineError("治理字段 if/then 约束违反：" + "; ".join(problems))


# ---- state.json 读写（执行期 IO；纯规则函数与 IO 分离，便于测试） ----


def load_state(topic: str | Path) -> dict[str, Any]:
    """读取 `{topic}/state.json`；文件不存在则 raise FileNotFoundError。"""
    p = paths.state_file(topic)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_state(topic: str | Path, state: dict[str, Any]) -> None:
    """写回 `{topic}/state.json`（不修改 schema_version）。"""
    state.setdefault("schema_version", SCHEMA_VERSION)
    p = paths.state_file(topic)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")
