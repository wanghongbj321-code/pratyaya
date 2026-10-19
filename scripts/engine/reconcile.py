"""跨模块 caveat 浮现 + 对齐总检数据收集（Phase 2 全局汇总）。

只做**数据收集与确定性规则判定**；跨模块语义审核 5 项、对齐总检 5 项由 LLM 在
global-pipeline 完成，本模块不介入。

依赖：canvas_registry（零副作用）+ 标准库。
"""

from __future__ import annotations

from typing import Any, Iterator

from . import canvas_registry


def iter_instances(state: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """遍历所有画布实例（含 MVL 模块），yield {root, key, slug, instance}。"""
    modules = state.get("modules")
    if isinstance(modules, dict):
        for key in canvas_registry.MVL_MODULES:
            inst = modules.get(key)
            if isinstance(inst, dict):
                yield {"root": "modules", "key": key, "slug": None, "instance": inst}

    for spec in canvas_registry.CANVASES:
        if not spec.is_instance_map:
            continue
        block = state.get(spec.state_key_root)
        if not isinstance(block, dict):
            continue
        for slug, inst in block.items():
            if isinstance(inst, dict):
                yield {"root": spec.state_key_root, "key": slug, "slug": slug, "instance": inst}


def collect_all_instances(state: dict[str, Any]) -> list[dict[str, Any]]:
    return list(iter_instances(state))


def collect_override_caveats(state: dict[str, Any]) -> list[dict[str, Any]]:
    """收集所有 `confirmation_mode == "override"` 的实例（跨模块 caveat 浮现）。"""
    return [i for i in iter_instances(state) if i["instance"].get("confirmation_mode") == "override"]


def has_override(state: dict[str, Any]) -> bool:
    return bool(collect_override_caveats(state))


def all_rendered(state: dict[str, Any]) -> bool:
    """确定性判定：所有实例是否均已 `rendered`（空实例集视为 False）。"""
    instances = collect_all_instances(state)
    return bool(instances) and all(i["instance"].get("status") == "rendered" for i in instances)


def render_status_summary(state: dict[str, Any]) -> dict[str, Any]:
    """渲染状态汇总（供对齐总检 5 项输入）：按 status 分组计数 + 未渲染实例键。"""
    counts: dict[str, int] = {}
    unrendered: list[str] = []
    for item in iter_instances(state):
        status = item["instance"].get("status", "unknown")
        counts[status] = counts.get(status, 0) + 1
        if status != "rendered":
            key = item["key"] if item["root"] == "modules" else f"{item['root']}.{item['slug']}"
            unrendered.append(key)
    return {"counts": counts, "unrendered": unrendered, "all_rendered": not unrendered}
