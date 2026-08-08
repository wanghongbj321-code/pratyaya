"""Project/group directory schema checks for workshop isolation."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from scripts.legacy_migration_v2_6_0 import migrate_state_to_instance_map

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "project_manifest"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_schema_ready_state(path: Path) -> dict:
    state = load_json(path)
    migrated, _ = migrate_state_to_instance_map(state)
    return migrated


def validation_errors(instance: dict, schema: dict) -> list[str]:
    validator = jsonschema.Draft202012Validator(schema)
    return [error.message for error in sorted(validator.iter_errors(instance), key=lambda e: list(e.path))]


def manifest_consistency_errors(manifest: dict) -> list[str]:
    errors: list[str] = []
    for index, group in enumerate(manifest.get("groups", [])):
        expected = f"{group.get('group_id')}/state.json"
        if group.get("state_path") != expected:
            errors.append(f"groups[{index}].state_path must equal {expected}")
    return errors


def test_project_manifest_schema_accepts_group_layer_manifest() -> None:
    schema = load_json(REPO_ROOT / "schemas" / "project_manifest.schema.json")
    manifest = load_json(FIXTURES / "valid.json")

    assert validation_errors(manifest, schema) == []
    assert manifest_consistency_errors(manifest) == []


def test_project_manifest_rejects_cross_group_state_path() -> None:
    schema = load_json(REPO_ROOT / "schemas" / "project_manifest.schema.json")
    manifest = load_json(FIXTURES / "invalid-state-path.json")

    errors = validation_errors(manifest, schema)

    assert any("does not match" in error for error in errors)


def test_project_manifest_rejects_state_path_that_points_to_another_group() -> None:
    schema = load_json(REPO_ROOT / "schemas" / "project_manifest.schema.json")
    manifest = load_json(FIXTURES / "valid.json")
    manifest["groups"][0]["state_path"] = "group-b/state.json"

    assert validation_errors(manifest, schema) == []
    assert manifest_consistency_errors(manifest) == [
        "groups[0].state_path must equal group-a/state.json"
    ]


def test_group_meta_schema_accepts_human_friendly_fields() -> None:
    schema = load_json(REPO_ROOT / "schemas" / "group_meta.schema.json")
    meta = load_json(FIXTURES / "group-meta-valid.json")

    assert validation_errors(meta, schema) == []


def test_state_schema_requires_project_slug_and_normalized_group_id() -> None:
    schema = load_json(REPO_ROOT / "schemas" / "state.schema.json")
    state = load_schema_ready_state(REPO_ROOT / "tests" / "fixtures" / "state" / "hmw-draft.json")

    assert validation_errors(state, schema) == []

    state["group_id"] = "G1"
    errors = validation_errors(state, schema)

    assert any("does not match" in error for error in errors)


def test_state_schema_rejects_non_strict_kebab_case_slugs() -> None:
    schema = load_json(REPO_ROOT / "schemas" / "state.schema.json")
    state = load_schema_ready_state(REPO_ROOT / "tests" / "fixtures" / "state" / "hmw-draft.json")

    state["project_slug"] = "project-"
    state["group_id"] = "group--1"
    errors = validation_errors(state, schema)

    assert len([error for error in errors if "does not match" in error]) == 2
