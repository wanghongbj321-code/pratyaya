"""授权与 override —— 强制「用户确认证据」的授权写入。

红线（§7.4 红线 3）：引擎不替人拍板。任何越过 Gate 的授权（override）必须携带
用户确认证据；`grant()` 缺失必填证据即 raise（§7.7）。

override_audit 结构与 `schemas/state.schema.json` 的 `override_audit` 一致。
"""

from __future__ import annotations

from typing import Any


class AuthorizationError(ValueError):
    """授权证据缺失 / 结构不完整。"""


REQUIRED_OVERRIDE_FIELDS: tuple[str, ...] = (
    "version", "items", "reason", "confirmed_by", "confirmed_at",
)
REQUIRED_OVERRIDE_ITEM_FIELDS: tuple[str, ...] = (
    "assessment_id", "category", "source_id", "original_result", "risk_level", "impact",
)
# 仅 business_risk 可 override（schema 约束 category const business_risk）。
ALLOWED_OVERRIDE_CATEGORY = "business_risk"


def validate_override_audit(override_audit: Any) -> list[str]:
    """校验 override_audit 结构完整性，返回问题列表（空 = 通过）。"""
    problems: list[str] = []
    if not isinstance(override_audit, dict):
        return ["override_audit 必须为对象"]

    for f in REQUIRED_OVERRIDE_FIELDS:
        if not override_audit.get(f):
            problems.append(f"override_audit 缺必填字段 {f}")

    items = override_audit.get("items")
    if not isinstance(items, list) or len(items) == 0:
        problems.append("override_audit.items 必须为非空数组")
    else:
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                problems.append(f"override_audit.items[{i}] 必须为对象")
                continue
            for f in REQUIRED_OVERRIDE_ITEM_FIELDS:
                if not item.get(f):
                    problems.append(f"override_audit.items[{i}] 缺必填字段 {f}")
            if item.get("category") != ALLOWED_OVERRIDE_CATEGORY:
                problems.append(
                    f"override_audit.items[{i}].category 必须为 {ALLOWED_OVERRIDE_CATEGORY!r}"
                )
    return problems


def _require_non_empty(**fields: Any) -> list[str]:
    return [f"{name} 必填" for name, val in fields.items() if val in (None, "", [])]


def grant(
    *,
    canvas_type: str,
    slug: str,
    version: int,
    confirmation_mode: str,
    confirmed_by: str,
    confirmed_at: str,
    user_confirmation_text: str,
    override_audit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """构建一次确认的授权写入。缺失必填证据即 raise `AuthorizationError`。

    - gate_pass：确认走正常 Gate 通过，需 confirmed_by / confirmed_at / user_confirmation_text。
    - override：确认走 override，除上述证据外，还必须提供结构完整的 override_audit。
    """
    problems = _require_non_empty(
        canvas_type=canvas_type,
        slug=slug,
        confirmation_mode=confirmation_mode,
        confirmed_by=confirmed_by,
        confirmed_at=confirmed_at,
        user_confirmation_text=user_confirmation_text,
    )
    if not isinstance(version, int) or version < 1:
        problems.append("version 必须为 >=1 的整数")
    if problems:
        raise AuthorizationError("授权证据缺失：" + "; ".join(problems))

    if confirmation_mode not in ("gate_pass", "override"):
        raise AuthorizationError(f"非法 confirmation_mode：{confirmation_mode!r}")

    if confirmation_mode == "gate_pass":
        return {
            "confirmation_mode": "gate_pass",
            "gate_recommendation": "pass",
            "render_authorized": True,
        }

    # override
    audit_problems = validate_override_audit(override_audit)
    if audit_problems:
        raise AuthorizationError(
            "override 需结构完整的 override_audit：" + "; ".join(audit_problems)
        )
    return {
        "confirmation_mode": "override",
        "gate_recommendation": "fail",
        "render_authorized": True,
        "override_audit": override_audit,
    }
