"""state.schema.json v2.3 校验测试（HMW / Persona / Journey + 向后兼容）。"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "state.schema.json"
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "state"


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def validate(state: dict, schema: dict) -> list[str]:
    """返回校验错误信息列表；空列表表示通过。"""
    errors: list[str] = []
    validator = jsonschema.Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(state), key=lambda e: list(e.path)):
        errors.append(f"{'.'.join(map(str, error.path))}: {error.message}")
    return errors


class TestSchemaVersion:
    def test_schema_version_is_2_3(self, schema: dict) -> None:
        assert schema["properties"]["schema_version"]["const"] == "2.3"

    def test_single_canvas_blocks_are_present(self, schema: dict) -> None:
        for key in ("modules", "golden_circle", "hmw", "persona", "journey"):
            assert key in schema["properties"]


class TestValidHmwStates:
    @pytest.mark.parametrize(
        "fixture",
        ["hmw-draft.json", "hmw-gate-pass.json", "hmw-override.json"],
    )
    def test_valid_states_pass(self, fixture: str, schema: dict) -> None:
        state = load_fixture(fixture)
        state["schema_version"] = "2.3"
        errors = validate(state, schema)
        assert errors == []

    def test_agent_initialized_hmw_block_passes(self, schema: dict) -> None:
        state = load_fixture("legacy-v2-without-hmw.json")
        state["schema_version"] = "2.3"
        state["hmw"] = {
            "version": 0,
            "status": "draft",
            "gate_recommendation": "pending",
            "render_authorized": False,
            "confirmation_mode": None,
        }
        errors = validate(state, schema)
        assert errors == []


class TestValidPersonaStates:
    @pytest.mark.parametrize(
        "fixture",
        ["persona-draft.json", "persona-gate-pass.json", "persona-override.json"],
    )
    def test_valid_states_pass(self, fixture: str, schema: dict) -> None:
        errors = validate(load_fixture(fixture), schema)
        assert errors == []

    def test_agent_initialized_persona_block_passes(self, schema: dict) -> None:
        state = load_fixture("legacy-v2.1-without-persona.json")
        state["schema_version"] = "2.3"
        state["persona"] = {
            "version": 0,
            "status": "draft",
            "gate_recommendation": "pending",
            "render_authorized": False,
            "confirmation_mode": None,
        }
        errors = validate(state, schema)
        assert errors == []


class TestValidJourneyStates:
    @pytest.mark.parametrize(
        "fixture",
        ["journey-draft.json", "journey-gate-pass.json", "journey-override.json"],
    )
    def test_valid_states_pass(self, fixture: str, schema: dict) -> None:
        errors = validate(load_fixture(fixture), schema)
        assert errors == []

    def test_agent_initialized_journey_block_passes(self, schema: dict) -> None:
        state = load_fixture("legacy-v22-without-journey.json")
        state["schema_version"] = "2.3"
        state["journey"] = {
            "version": 0,
            "status": "draft",
            "gate_recommendation": "pending",
            "render_authorized": False,
            "confirmation_mode": None,
        }
        errors = validate(state, schema)
        assert errors == []


class TestInvalidHmwStates:
    def test_override_with_information_integrity_fails(self, schema: dict) -> None:
        state = load_fixture("hmw-invalid-override.json")
        state["schema_version"] = "2.3"
        errors = validate(state, schema)
        assert any("category" in error for error in errors)

    def test_override_without_audit_fails(self, schema: dict) -> None:
        state = load_fixture("hmw-override.json")
        state["schema_version"] = "2.3"
        del state["hmw"]["override_audit"]
        errors = validate(state, schema)
        assert any("override_audit" in e for e in errors)

    def test_override_with_wrong_gate_id_fails(self, schema: dict) -> None:
        state = load_fixture("hmw-override.json")
        state["schema_version"] = "2.3"
        state["hmw"]["override_audit"]["items"][0]["assessment_id"] = "GC-GATE-01"
        errors = validate(state, schema)
        assert any("assessment_id" in e for e in errors)

    def test_conflicting_auth_fields_fail(self, schema: dict) -> None:
        state = load_fixture("hmw-gate-pass.json")
        state["schema_version"] = "2.3"
        state["hmw"]["gate_recommendation"] = "fail"
        errors = validate(state, schema)
        assert any("gate_recommendation" in e for e in errors)

    def test_gate_pass_with_render_not_authorized_fails(self, schema: dict) -> None:
        state = load_fixture("hmw-gate-pass.json")
        state["schema_version"] = "2.3"
        state["hmw"]["render_authorized"] = False
        errors = validate(state, schema)
        assert any("render_authorized" in e for e in errors)

    def test_unknown_status_fails(self, schema: dict) -> None:
        state = load_fixture("hmw-draft.json")
        state["schema_version"] = "2.3"
        state["hmw"]["status"] = "shipped"
        errors = validate(state, schema)
        assert any("status" in e for e in errors)


class TestInvalidPersonaStates:
    def test_override_with_information_integrity_fails(self, schema: dict) -> None:
        state = load_fixture("persona-invalid-override.json")
        errors = validate(state, schema)
        assert any("category" in error for error in errors)

    def test_override_without_audit_fails(self, schema: dict) -> None:
        state = load_fixture("persona-override.json")
        del state["persona"]["override_audit"]
        errors = validate(state, schema)
        assert any("override_audit" in e for e in errors)

    def test_override_with_wrong_gate_id_fails(self, schema: dict) -> None:
        state = load_fixture("persona-override.json")
        state["persona"]["override_audit"]["items"][0]["assessment_id"] = "HMW-GATE-01"
        errors = validate(state, schema)
        assert any("assessment_id" in e for e in errors)

    def test_conflicting_auth_fields_fail(self, schema: dict) -> None:
        state = load_fixture("persona-gate-pass.json")
        state["persona"]["gate_recommendation"] = "fail"
        errors = validate(state, schema)
        assert any("gate_recommendation" in e for e in errors)

    def test_gate_pass_with_render_not_authorized_fails(self, schema: dict) -> None:
        state = load_fixture("persona-gate-pass.json")
        state["persona"]["render_authorized"] = False
        errors = validate(state, schema)
        assert any("render_authorized" in e for e in errors)

    def test_unknown_status_fails(self, schema: dict) -> None:
        state = load_fixture("persona-draft.json")
        state["persona"]["status"] = "shipped"
        errors = validate(state, schema)
        assert any("status" in e for e in errors)


class TestInvalidJourneyStates:
    def test_override_with_information_integrity_fails(self, schema: dict) -> None:
        state = load_fixture("journey-invalid-override.json")
        errors = validate(state, schema)
        assert any("category" in error for error in errors)

    def test_override_without_audit_fails(self, schema: dict) -> None:
        state = load_fixture("journey-override.json")
        del state["journey"]["override_audit"]
        errors = validate(state, schema)
        assert any("override_audit" in e for e in errors)

    def test_override_with_wrong_gate_id_fails(self, schema: dict) -> None:
        state = load_fixture("journey-override.json")
        state["journey"]["override_audit"]["items"][0]["assessment_id"] = "HMW-GATE-02"
        errors = validate(state, schema)
        assert any("assessment_id" in e for e in errors)

    def test_conflicting_auth_fields_fail(self, schema: dict) -> None:
        state = load_fixture("journey-gate-pass.json")
        state["journey"]["gate_recommendation"] = "fail"
        errors = validate(state, schema)
        assert any("gate_recommendation" in e for e in errors)

    def test_draft_with_render_authorized_fails(self, schema: dict) -> None:
        state = load_fixture("journey-draft.json")
        state["journey"]["render_authorized"] = True
        errors = validate(state, schema)
        assert any("render_authorized" in e for e in errors)


class TestBackwardCompatibility:
    def test_legacy_v2_without_hmw_passes_non_hmw_shape(self, schema: dict) -> None:
        errors = validate(load_fixture("legacy-v2-without-hmw.json"), schema)
        assert all("hmw" not in e for e in errors)

    def test_legacy_v2_1_without_persona_passes_non_persona_shape(self, schema: dict) -> None:
        errors = validate(load_fixture("legacy-v2.1-without-persona.json"), schema)
        assert all("persona" not in e for e in errors)

    def test_legacy_v22_without_journey_passes_non_journey_shape(self, schema: dict) -> None:
        errors = validate(load_fixture("legacy-v22-without-journey.json"), schema)
        assert all("journey" not in e for e in errors)
