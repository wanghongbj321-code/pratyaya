"""legacy 迁移：v2.6 default instance / v2.9 default topic（staging 流程）。

规则源：`scripts/legacy_migration_v2_6_0.py`（v2.6 instance map，逻辑复用）、
`agents/pratyaya.md`「实例管理」+ 执行计划（v2.9 default topic 三层）。

红线：迁移只做数据改写与 staging，不渲染、不做语义判断。
`default` 作为迁移 legacy slug 允许 force_consent 引入，但**新建实例仍须拒绝 `default`**
（由 `session.assert_valid_slug` 保证，本模块不改写该规则）。

依赖：canvas_registry / paths（零副作用）+ 标准库。
"""

from __future__ import annotations

import copy
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import canvas_registry, paths

# v2.6 前存在 legacy 单画布态的四类画布（v2c-vac / 5w 自始即 instance map，无 legacy 态）。
_LEGACY_CANVAS_IDS = ("gc", "hmw", "persona", "journey")

# v2.9 default topic 迁移的 staging 目录名。
STAGING_DIR_NAME = ".migrating-default"

# legacy 单画布态的字段集合（完整子集才判定为 legacy）。
_STATE_FIELDS = {
    "version",
    "status",
    "gate_recommendation",
    "render_authorized",
    "confirmation_mode",
}


def _legacy_canvas_config() -> dict[str, dict[str, str]]:
    """从 registry 派生 legacy 四类的 {state_key_root: {prefix, output}}，避免硬编码漂移。"""
    cfg: dict[str, dict[str, str]] = {}
    for cid in _LEGACY_CANVAS_IDS:
        spec = canvas_registry.by_id(cid)
        if spec is not None:
            cfg[spec.state_key_root] = {"prefix": spec.file_prefix, "output": spec.output_prefix}
    return cfg


def is_legacy_single_canvas(value: Any) -> bool:
    """是否为 v2.6 前单画布态对象（完整含 5 字段）。"""
    return isinstance(value, dict) and _STATE_FIELDS.issubset(value.keys())


def migrate_state_to_instance_map(
    state: dict[str, Any],
    *,
    legacy_slug: str = "default",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """v2.6：单画布字段 → instance map（逻辑与 legacy 脚本一致，配置从 registry 派生）。"""
    migrated = copy.deepcopy(state)
    details: dict[str, Any] = {}
    cfg = _legacy_canvas_config()

    meta = migrated.setdefault("_meta", {})
    if isinstance(meta, dict):
        meta["instance_map_schema_version"] = "2.6-instance-map-1"

    for canvas_key, c in cfg.items():
        value = migrated.get(canvas_key)
        if value is None or not is_legacy_single_canvas(value):
            continue

        instance = copy.deepcopy(value)
        version = int(instance.get("version", 0))
        instance["slug"] = legacy_slug
        if version > 0:
            instance.setdefault("source_file", f"modules/{c['prefix']}-{legacy_slug}-v{version}.md")
            instance.setdefault("output_file", f"output/{c['output']}-canvas-{legacy_slug}.html")
        migrated[canvas_key] = {legacy_slug: instance}

        details[canvas_key] = {
            "old_path": f"state.{canvas_key}",
            "new_path": f"state.{canvas_key}.{legacy_slug}",
            "slug": legacy_slug,
            "force_consent": legacy_slug == "default",
        }

    return migrated, {
        "applied": bool(details),
        "force_consent": any(item["force_consent"] for item in details.values()),
        "details": details,
    }


def append_group_meta_migration(
    group_meta: dict[str, Any],
    migration: dict[str, Any],
    *,
    applied_at: str | None = None,
    actor: str = "agent",
) -> dict[str, Any]:
    updated = copy.deepcopy(group_meta)
    if not migration.get("applied"):
        return updated
    migrations = updated.setdefault("legacy_migrations", {})
    migrations["v2_6_0_instance_map"] = {
        "applied_at": applied_at or datetime.now(timezone.utc).isoformat(),
        "by": actor,
        "force_consent": bool(migration.get("force_consent")),
        "details": migration.get("details", {}),
    }
    return updated


# --- v2.9 default topic 三层迁移 ---

def migrate_v2_9_topic_state(
    state: dict[str, Any],
    *,
    topic_slug: str = "default",
    topic_name: str = "default",
) -> dict[str, Any]:
    """v2.9：把 project+group 双层 state 改写为 default topic 三层。"""
    migrated = copy.deepcopy(state)
    migrated["topic_slug"] = topic_slug
    migrated["topic_name"] = topic_name
    return migrated


def build_default_topic_meta(
    *,
    topic_slug: str = "default",
    topic_name: str = "default",
    created_by: str = "agent",
) -> dict[str, Any]:
    return {
        "topic_slug": topic_slug,
        "topic_name": topic_name,
        "topic_owner": "",
        "contact": "",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by": created_by,
    }


def stage_default_topic(
    group_root: str | Path,
    *,
    topic_slug: str = "default",
    topic_name: str = "default",
) -> dict[str, Any]:
    """staging 复制 group 内容到 `.migrating-default/`，改写 state 与 topic_meta。

    返回 {staging_dir, migrated_state, topic_meta}；**不执行 rename**——rename 由调用方
    校验一致性后决定，避免半迁移覆盖。
    """
    group = Path(group_root)
    staging = group / STAGING_DIR_NAME
    ignore = shutil.ignore_patterns(STAGING_DIR_NAME, ".git")
    shutil.copytree(group, staging, dirs_exist_ok=True, ignore=ignore)

    state_path = paths.state_file(staging)
    state = json.loads(state_path.read_text(encoding="utf-8"))
    migrated = migrate_v2_9_topic_state(state, topic_slug=topic_slug, topic_name=topic_name)
    state_path.write_text(
        json.dumps(migrated, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    topic_meta = build_default_topic_meta(topic_slug=topic_slug, topic_name=topic_name)
    paths.topic_meta_file(staging).write_text(
        json.dumps(topic_meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return {"staging_dir": staging, "migrated_state": migrated, "topic_meta": topic_meta}
