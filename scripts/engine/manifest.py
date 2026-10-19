"""group / project manifest 自重建。

`manifest.json` 是可重建派生视图，不作为业务真相源（业务真相源是 `state.json` + 确认包）。
缺失 / 陈旧 / 条目缺失时从各 `state.json` 重建。

红线：本模块只做确定性派生与重建，不渲染、不做语义判断。

依赖：canvas_registry / paths（零副作用）+ 标准库。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import canvas_registry, paths


def summarize_instance(inst: dict[str, Any]) -> dict[str, Any]:
    """单实例摘要（只取确定性字段，不引入语义）。"""
    return {
        "version": inst.get("version"),
        "status": inst.get("status"),
        "gate_recommendation": inst.get("gate_recommendation"),
        "confirmation_mode": inst.get("confirmation_mode"),
    }


def summarize_topic_state(state: dict[str, Any]) -> dict[str, Any]:
    """从单个 state.json 派生 topic 摘要（含 MVL 模块与所有 instance map）。"""
    summary: dict[str, Any] = {
        "project_slug": state.get("project_slug"),
        "group_id": state.get("group_id"),
        "topic_slug": state.get("topic_slug"),
        "topic_name": state.get("topic_name"),
    }

    modules = state.get("modules")
    if isinstance(modules, dict):
        summary["modules"] = {
            m: summarize_instance(modules[m])
            for m in canvas_registry.MVL_MODULES
            if isinstance(modules.get(m), dict)
        }

    for spec in canvas_registry.CANVASES:
        if not spec.is_instance_map:
            continue
        block = state.get(spec.state_key_root)
        if isinstance(block, dict):
            summary[spec.state_key_root] = {
                slug: summarize_instance(inst)
                for slug, inst in block.items()
                if isinstance(inst, dict)
            }

    return summary


def derive_group_manifest(
    group_id: str,
    topic_states: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """group 级派生视图：topics 汇总。"""
    return {
        "group_id": group_id,
        "topics": {slug: summarize_topic_state(s) for slug, s in topic_states.items()},
    }


def derive_project_manifest(
    project_slug: str,
    group_topic_states: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, Any]:
    """project 级派生视图：groups + topics 嵌套。"""
    return {
        "project_slug": project_slug,
        "groups": {
            gid: derive_group_manifest(gid, topics)
            for gid, topics in group_topic_states.items()
        },
    }


def rebuild_group_manifest(group_dir: str | Path, *, group_id: str | None = None) -> dict[str, Any]:
    """重建 group manifest：枚举 `*/state.json`，写回 `manifest.json`。"""
    group = Path(group_dir)
    group_id = group_id or group.name
    topic_states: dict[str, dict[str, Any]] = {}
    if group.is_dir():
        for topic in group.iterdir():
            if not topic.is_dir() or topic.name.startswith("."):
                continue
            state_path = paths.state_file(topic)
            if state_path.exists():
                topic_states[topic.name] = json.loads(state_path.read_text(encoding="utf-8"))

    manifest = derive_group_manifest(group_id, topic_states)
    paths.group_manifest_file(group).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def rebuild_project_manifest(
    project_dir: str | Path,
    *,
    project_slug: str | None = None,
) -> dict[str, Any]:
    """重建 project manifest：枚举 `*/{topic}/state.json`，写回 `manifest.json`。"""
    project = Path(project_dir)
    project_slug = project_slug or project.name
    group_topic_states: dict[str, dict[str, dict[str, Any]]] = {}
    if project.is_dir():
        for group in project.iterdir():
            if not group.is_dir() or group.name.startswith("."):
                continue
            topics: dict[str, dict[str, Any]] = {}
            for topic in group.iterdir():
                if not topic.is_dir() or topic.name.startswith("."):
                    continue
                state_path = paths.state_file(topic)
                if state_path.exists():
                    topics[topic.name] = json.loads(state_path.read_text(encoding="utf-8"))
            group_topic_states[group.name] = topics

    manifest = derive_project_manifest(project_slug, group_topic_states)
    paths.project_manifest_file(project).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest
