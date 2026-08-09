"""Project/group directory schema checks for workshop isolation."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from scripts.legacy_migration_v2_6_0 import migrate_state_to_instance_map

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "project_manifest"
GROUP_MANIFEST_FIXTURES = REPO_ROOT / "tests" / "fixtures" / "group_manifest"
TOPIC_META_FIXTURES = REPO_ROOT / "tests" / "fixtures" / "topic_meta"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_schema_ready_state(path: Path) -> dict:
    state = load_json(path)
    migrated, _ = migrate_state_to_instance_map(state)
    return migrated


def validation_errors(instance: dict, schema: dict) -> list[str]:
    validator = jsonschema.Draft202012Validator(schema)
    return [error.message for error in sorted(validator.iter_errors(instance), key=lambda e: list(e.path))]


def group_manifest_consistency_errors(manifest: dict) -> list[str]:
    errors: list[str] = []
    for index, topic in enumerate(manifest.get("topics", [])):
        expected_state = f"{topic.get('topic_slug')}/state.json"
        expected_meta = f"{topic.get('topic_slug')}/topic_meta.json"
        if topic.get("state_path") != expected_state:
            errors.append(f"topics[{index}].state_path must equal {expected_state}")
        if topic.get("topic_meta_path") != expected_meta:
            errors.append(f"topics[{index}].topic_meta_path must equal {expected_meta}")
    return errors


def project_manifest_consistency_errors(manifest: dict) -> list[str]:
    errors: list[str] = []
    for group_index, group in enumerate(manifest.get("groups", [])):
        group_id = group.get("group_id")
        for topic_index, topic in enumerate(group.get("topics", [])):
            expected_state = f"{group_id}/{topic.get('topic_slug')}/state.json"
            expected_meta = f"{group_id}/{topic.get('topic_slug')}/topic_meta.json"
            if topic.get("state_path") != expected_state:
                errors.append(
                    f"groups[{group_index}].topics[{topic_index}].state_path must equal {expected_state}"
                )
            if topic.get("topic_meta_path") != expected_meta:
                errors.append(
                    f"groups[{group_index}].topics[{topic_index}].topic_meta_path must equal {expected_meta}"
                )
    return errors


def test_project_manifest_schema_accepts_topic_layer_manifest() -> None:
    schema = load_json(REPO_ROOT / "schemas" / "project_manifest.schema.json")
    manifest = load_json(FIXTURES / "valid.json")

    assert validation_errors(manifest, schema) == []
    assert project_manifest_consistency_errors(manifest) == []


def test_project_manifest_rejects_invalid_state_path() -> None:
    schema = load_json(REPO_ROOT / "schemas" / "project_manifest.schema.json")
    manifest = load_json(FIXTURES / "invalid-state-path.json")

    errors = validation_errors(manifest, schema)

    assert any("does not match" in error for error in errors)


def test_project_manifest_rejects_state_path_that_points_to_another_group() -> None:
    schema = load_json(REPO_ROOT / "schemas" / "project_manifest.schema.json")
    manifest = load_json(FIXTURES / "valid.json")
    manifest["groups"][0]["topics"][0]["state_path"] = "group-b/topic-a/state.json"

    assert validation_errors(manifest, schema) == []
    assert project_manifest_consistency_errors(manifest) == [
        "groups[0].topics[0].state_path must equal group-a/opportunity-evaluation/state.json"
    ]


def test_group_manifest_schema_accepts_topic_list() -> None:
    schema = load_json(REPO_ROOT / "schemas" / "group_manifest.schema.json")
    manifest = load_json(GROUP_MANIFEST_FIXTURES / "valid.json")

    assert validation_errors(manifest, schema) == []
    assert group_manifest_consistency_errors(manifest) == []


def test_group_manifest_rejects_cross_group_state_path() -> None:
    schema = load_json(REPO_ROOT / "schemas" / "group_manifest.schema.json")
    manifest = load_json(GROUP_MANIFEST_FIXTURES / "invalid-state-path.json")

    errors = validation_errors(manifest, schema)

    assert any("does not match" in error for error in errors)


def test_topic_meta_schema_accepts_valid_topic() -> None:
    schema = load_json(REPO_ROOT / "schemas" / "topic_meta.schema.json")
    meta = load_json(TOPIC_META_FIXTURES / "valid.json")

    assert validation_errors(meta, schema) == []


def test_topic_meta_schema_rejects_non_kebab_case_slug() -> None:
    schema = load_json(REPO_ROOT / "schemas" / "topic_meta.schema.json")
    meta = load_json(TOPIC_META_FIXTURES / "invalid-slug.json")

    errors = validation_errors(meta, schema)

    assert any("does not match" in error for error in errors)


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
