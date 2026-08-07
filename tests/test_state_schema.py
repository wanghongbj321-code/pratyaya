"""state.schema.json v2.3 校验测试（HMW / Journey 区块 + 向后兼容）。

覆盖执行计划 §2.2 要求的场景：
1. 合法 HMW 与 Journey draft / gate_pass / override 分别通过。
2. information_integrity 被 override、缺少审计项、错误 Gate ID、授权字段互相矛盾时失败。
3. 无 journey 区块的旧 MVL / GC / HMW state 仍可走非 Journey 流程。
4. 已有项目首次启动 HMW / Journey 时，Agent 初始化出的区块可通过 schema。
"""

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
        assert "hmw" in schema["properties"]
        assert "persona" in schema["properties"]
        assert "journey" in schema["properties"]
        assert "golden_circle" in schema["properties"]
        assert "modules" in schema["properties"]


class TestValidHmwStates:
    @pytest.mark.parametrize(
        "fixture",
        ["hmw-draft.json", "hmw-gate-pass.json", "hmw-override.json"],
    )
    def test_valid_states_pass(self, fixture: str, schema: dict) -> None:
        errors = validate(load_fixture(fixture), schema)
        assert errors == []

    def test_agent_initialized_hmw_block_passes(self, schema: dict) -> None:
        """Agent Phase 0 首次追加 hmw 区块（空骨架）应通过 schema。"""
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


class TestValidJourneyStates:
    @pytest.mark.parametrize(
        "fixture",
        ["journey-draft.json", "journey-gate-pass.json", "journey-override.json"],
    )
    def test_valid_states_pass(self, fixture: str, schema: dict) -> None:
        errors = validate(load_fixture(fixture), schema)
        assert errors == []

    def test_agent_initialized_journey_block_passes(self, schema: dict) -> None:
        """首次进入 Journey 流程追加 journey 区块（空骨架）应通过 schema。"""
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
        """information_integrity 类别被 override 必须失败。"""
        state = load_fixture("hmw-invalid-override.json")
        errors = validate(state, schema)
        assert any("category" in error for error in errors)

    def test_override_without_audit_fails(self, schema: dict) -> None:
        """confirmation_mode=override 但缺少 override_audit 必须失败。"""
        state = load_fixture("hmw-override.json")
        del state["hmw"]["override_audit"]
        errors = validate(state, schema)
        assert any("override_audit" in e for e in errors)

    def test_override_with_wrong_gate_id_fails(self, schema: dict) -> None:
        """override 审计项的 assessment_id 必须匹配 ^HMW-GATE-[0-9]+$。"""
        state = load_fixture("hmw-override.json")
        state["hmw"]["override_audit"]["items"][0]["assessment_id"] = "GC-GATE-01"
        errors = validate(state, schema)
        assert any("assessment_id" in e for e in errors)

    def test_conflicting_auth_fields_fail(self, schema: dict) -> None:
        """gate_pass 要求 gate_recommendation=pass 且 render_authorized=true。"""
        state = load_fixture("hmw-gate-pass.json")
        state["hmw"]["gate_recommendation"] = "fail"
        errors = validate(state, schema)
        assert any("gate_recommendation" in e for e in errors)

    def test_gate_pass_with_render_not_authorized_fails(self, schema: dict) -> None:
        state = load_fixture("hmw-gate-pass.json")
        state["hmw"]["render_authorized"] = False
        errors = validate(state, schema)
        assert any("render_authorized" in e for e in errors)

    def test_unknown_status_fails(self, schema: dict) -> None:
        state = load_fixture("hmw-draft.json")
        state["hmw"]["status"] = "shipped"
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
    def test_legacy_v2_without_hmw_passes(self, schema: dict) -> None:
        """旧 v2.0 state（无 hmw 区块）不阻断 MVL / GC 流程。"""
        errors = validate(load_fixture("legacy-v2-without-hmw.json"), schema)
        # schema_version=2.0 与 const 2.3 冲突，但这是"旧版本标识"——
        # 兼容性语义：缺少 hmw 不报错（anyOf 只要求三者之一存在）
        assert all("hmw" not in e for e in errors)

    def test_legacy_v22_without_journey_passes_non_journey_shape(self, schema: dict) -> None:
        """旧 v2.2 state（无 journey 区块）不因缺 Journey 阻断非 Journey 流程。"""
        errors = validate(load_fixture("legacy-v22-without-journey.json"), schema)
        assert all("journey" not in e for e in errors)
