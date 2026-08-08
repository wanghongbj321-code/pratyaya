"""Legacy state migration for pratyaya v2.6.0 instance maps."""

from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CANVAS_CONFIG = {
    "golden_circle": {"prefix": "GC", "output": "gc"},
    "hmw": {"prefix": "HMW", "output": "hmw"},
    "persona": {"prefix": "PERSONA", "output": "persona"},
    "journey": {"prefix": "JOURNEY", "output": "journey"},
}

STATE_FIELDS = {
    "version",
    "status",
    "gate_recommendation",
    "render_authorized",
    "confirmation_mode",
}


def is_legacy_single_canvas(value: Any) -> bool:
    """Return true when a canvas value is the pre-v2.6 single state object."""
    return isinstance(value, dict) and STATE_FIELDS.issubset(value.keys())


def default_source_file(canvas_key: str, slug: str, version: int) -> str | None:
    if version <= 0:
        return None
    prefix = CANVAS_CONFIG[canvas_key]["prefix"]
    return f"modules/{prefix}-{slug}-v{version}.md"


def default_output_file(canvas_key: str, slug: str, version: int) -> str | None:
    if version <= 0:
        return None
    output = CANVAS_CONFIG[canvas_key]["output"]
    return f"output/{output}-canvas-{slug}.html"


def migrate_state_to_instance_map(
    state: dict[str, Any],
    *,
    legacy_slug: str = "default",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Migrate old single canvas blocks to map form.

    The returned metadata includes `force_consent=true` when a legacy `default`
    slug is introduced. New instance creation must still reject `default`.
    """
    migrated = copy.deepcopy(state)
    details: dict[str, Any] = {}

    meta = migrated.setdefault("_meta", {})
    if isinstance(meta, dict):
        meta["instance_map_schema_version"] = "2.6-instance-map-1"

    for canvas_key in CANVAS_CONFIG:
        value = migrated.get(canvas_key)
        if value is None or not is_legacy_single_canvas(value):
            continue

        instance = copy.deepcopy(value)
        version = int(instance.get("version", 0))
        instance["slug"] = legacy_slug
        instance.setdefault("source_file", default_source_file(canvas_key, legacy_slug, version))
        instance.setdefault("output_file", default_output_file(canvas_key, legacy_slug, version))
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


def migrate_state_file(state_path: Path, group_meta_path: Path | None = None) -> dict[str, Any]:
    state = json.loads(state_path.read_text(encoding="utf-8"))
    migrated, migration = migrate_state_to_instance_map(state)
    state_path.write_text(
        json.dumps(migrated, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    if group_meta_path is not None:
        group_meta = {}
        if group_meta_path.exists():
            group_meta = json.loads(group_meta_path.read_text(encoding="utf-8"))
        updated_group_meta = append_group_meta_migration(group_meta, migration)
        group_meta_path.write_text(
            json.dumps(updated_group_meta, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    return migration


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", type=Path, help="workshop/{project}/{group}/state.json")
    parser.add_argument("--group-meta", type=Path, help="optional group_meta.json path")
    args = parser.parse_args()

    migration = migrate_state_file(args.state, args.group_meta)
    print(json.dumps(migration, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
