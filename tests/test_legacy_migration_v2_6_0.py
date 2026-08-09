from __future__ import annotations

import json
from pathlib import Path

from scripts.legacy_migration_v2_6_0 import (
    append_group_meta_migration,
    migrate_state_file,
    migrate_state_to_instance_map,
)


def legacy_block(version: int = 1) -> dict:
    return {
        "version": version,
        "status": "confirmed",
        "gate_recommendation": "pass",
        "render_authorized": True,
        "confirmation_mode": "gate_pass",
        "output_file": "output/legacy-canvas.html",
    }


def base_state() -> dict:
    return {
        "schema_version": "2.3",
        "project_slug": "demo-project",
        "project_name": "Demo Project",
        "group_id": "group-a",
        "topic_slug": "default",
        "topic_name": "default",
        "updated_at": "2026-08-08T10:00:00+08:00",
    }


def test_migrate_persona_single() -> None:
    state = base_state()
    state["persona"] = legacy_block(version=2)

    migrated, migration = migrate_state_to_instance_map(state)

    assert migration["applied"] is True
    assert migration["force_consent"] is True
    assert migrated["_meta"]["instance_map_schema_version"] == "2.6-instance-map-1"
    assert migrated["persona"]["default"]["slug"] == "default"
    assert migrated["persona"]["default"]["source_file"] == "modules/PERSONA-default-v2.md"


def test_migrate_all_canvases() -> None:
    state = base_state()
    state["golden_circle"] = legacy_block()
    state["hmw"] = legacy_block()
    state["persona"] = legacy_block()
    state["journey"] = legacy_block()

    migrated, migration = migrate_state_to_instance_map(state)

    assert sorted(migration["details"]) == ["golden_circle", "hmw", "journey", "persona"]
    assert migrated["golden_circle"]["default"]["source_file"] == "modules/GC-default-v1.md"
    assert migrated["hmw"]["default"]["source_file"] == "modules/HMW-default-v1.md"
    assert migrated["persona"]["default"]["source_file"] == "modules/PERSONA-default-v1.md"
    assert migrated["journey"]["default"]["source_file"] == "modules/JOURNEY-default-v1.md"


def test_migrate_force_consent() -> None:
    state = base_state()
    state["hmw"] = legacy_block()

    _migrated, migration = migrate_state_to_instance_map(state)

    assert migration["details"]["hmw"]["force_consent"] is True


def test_group_meta_record() -> None:
    _migrated, migration = migrate_state_to_instance_map({"hmw": legacy_block()})
    group_meta = append_group_meta_migration(
        {"group_id": "group-a"},
        migration,
        applied_at="2026-08-08T00:00:00+00:00",
    )

    record = group_meta["legacy_migrations"]["v2_6_0_instance_map"]
    assert record["force_consent"] is True
    assert record["details"]["hmw"]["new_path"] == "state.hmw.default"


def test_migrate_state_file_writes_state_and_group_meta(tmp_path: Path) -> None:
    state_path = tmp_path / "state.json"
    group_meta_path = tmp_path / "group_meta.json"
    state = base_state()
    state["journey"] = legacy_block()
    state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    group_meta_path.write_text('{"group_id":"group-a"}', encoding="utf-8")

    migration = migrate_state_file(state_path, group_meta_path)

    migrated_state = json.loads(state_path.read_text(encoding="utf-8"))
    migrated_group_meta = json.loads(group_meta_path.read_text(encoding="utf-8"))
    assert migration["applied"] is True
    assert migrated_state["journey"]["default"]["slug"] == "default"
    assert "v2_6_0_instance_map" in migrated_group_meta["legacy_migrations"]
