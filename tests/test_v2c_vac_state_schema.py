"""state.schema.json 的 V2C VAC state.v2c_vac.{slug} schema 校验测试。"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "state.schema.json"


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def base_state() -> dict:
    return {
        "schema_version": "2.3",
        "project_slug": "demo-project",
        "project_name": "Demo 项目",
        "group_id": "group-a",
        "topic_slug": "v2c-vac-test",
        "topic_name": "V2C VAC Test",
        "_meta": {
            "instance_map_schema_version": "2.6-instance-map-1",
            "v2c_vac_schema_version": "3.0-v2c-vac-1",
        },
        "v2c_vac": {
            "store-replenishment": {
                "slug": "store-replenishment",
                "generation_path": "pipeline",
                "pipeline_stage": "scenario",
                "version": 1,
                "status": "draft",
                "gate_recommendation": "pending",
                "render_authorized": False,
                "confirmation_mode": None,
                "source_file": "modules/V2C-VAC-store-replenishment-v1.md",
                "output_file": None,
            }
        },
        "updated_at": "2026-08-13T14:00:00+08:00",
    }


def validate(state: dict, schema: dict) -> list[str]:
    errors: list[str] = []
    validator = jsonschema.Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(state), key=lambda e: list(e.path)):
        errors.append(f"{'.'.join(map(str, error.path))}: {error.message}")
    instances = state.get("v2c_vac")
    if isinstance(instances, dict):
        for slug, instance in instances.items():
            if isinstance(instance, dict) and instance.get("slug") != slug:
                errors.append(f"v2c_vac.{slug}.slug: must match map key")
    return errors


class TestValidV2CVacStates:
    def test_pipeline_draft_state_passes(self, schema: dict) -> None:
        assert validate(base_state(), schema) == []

    def test_transcript_direct_state_requires_null_stage_and_passes(self, schema: dict) -> None:
        state = base_state()
        instance = state["v2c_vac"]["store-replenishment"]
        instance["generation_path"] = "transcript-direct"
        instance["pipeline_stage"] = None

        assert validate(state, schema) == []

    def test_confirmed_pipeline_state_allows_null_stage(self, schema: dict) -> None:
        state = base_state()
        instance = state["v2c_vac"]["store-replenishment"]
        instance["status"] = "confirmed"
        instance["gate_recommendation"] = "pass"
        instance["render_authorized"] = True
        instance["confirmation_mode"] = "gate_pass"
        instance["pipeline_stage"] = None

        assert validate(state, schema) == []

    def test_override_state_with_v2c_gate_id_passes(self, schema: dict) -> None:
        state = base_state()
        instance = state["v2c_vac"]["store-replenishment"]
        instance["status"] = "confirmed"
        instance["pipeline_stage"] = None
        instance["gate_recommendation"] = "fail"
        instance["render_authorized"] = True
        instance["confirmation_mode"] = "override"
        instance["override_audit"] = {
            "version": 1,
            "items": [
                {
                    "assessment_id": "V2C-GATE-09",
                    "category": "business_risk",
                    "source_id": "V2C-AG03",
                    "original_result": "fail",
                    "risk_level": "medium",
                    "impact": "Value Anchor 尚未获得业务负责人确认",
                }
            ],
            "reason": "用户接受该业务风险并要求先出观察版画布",
            "confirmed_by": "业务负责人张三",
            "confirmed_at": "2026-08-13T14:00:00+08:00",
        }

        assert validate(state, schema) == []


class TestInvalidV2CVacStates:
    def test_default_slug_fails(self, schema: dict) -> None:
        state = base_state()
        state["v2c_vac"] = {
            "default": {
                "slug": "default",
                "generation_path": "pipeline",
                "pipeline_stage": "scenario",
                "version": 1,
                "status": "draft",
                "gate_recommendation": "pending",
                "render_authorized": False,
                "confirmation_mode": None,
            }
        }

        assert validate(state, schema) != []

    def test_map_key_slug_mismatch_fails(self, schema: dict) -> None:
        state = base_state()
        state["v2c_vac"]["store-replenishment"]["slug"] = "other-slug"

        errors = validate(state, schema)

        assert any("must match map key" in error for error in errors)

    def test_transcript_direct_with_pipeline_stage_fails(self, schema: dict) -> None:
        state = base_state()
        instance = state["v2c_vac"]["store-replenishment"]
        instance["generation_path"] = "transcript-direct"
        instance["pipeline_stage"] = "scenario"

        errors = validate(state, schema)

        assert any("pipeline_stage" in error for error in errors)

    def test_pipeline_draft_with_null_stage_fails(self, schema: dict) -> None:
        state = base_state()
        state["v2c_vac"]["store-replenishment"]["pipeline_stage"] = None

        errors = validate(state, schema)

        assert any("pipeline_stage" in error for error in errors)

    def test_invalid_generation_path_fails(self, schema: dict) -> None:
        state = base_state()
        state["v2c_vac"]["store-replenishment"]["generation_path"] = "maau"

        errors = validate(state, schema)

        assert any("generation_path" in error for error in errors)

    def test_override_with_v2c_gap_id_fails(self, schema: dict) -> None:
        state = base_state()
        instance = state["v2c_vac"]["store-replenishment"]
        instance["status"] = "confirmed"
        instance["pipeline_stage"] = None
        instance["gate_recommendation"] = "fail"
        instance["render_authorized"] = True
        instance["confirmation_mode"] = "override"
        instance["override_audit"] = {
            "version": 1,
            "items": [
                {
                    "assessment_id": "V2C-AG01",
                    "category": "business_risk",
                    "source_id": "V2C-AG01",
                    "original_result": "fail",
                    "risk_level": "medium",
                    "impact": "Primary Change 是否真实发生仍待验证",
                }
            ],
            "reason": "用户接受",
            "confirmed_by": "业务负责人张三",
            "confirmed_at": "2026-08-13T14:00:00+08:00",
        }

        errors = validate(state, schema)

        assert any("assessment_id" in error for error in errors)

    def test_override_with_information_integrity_fails(self, schema: dict) -> None:
        state = base_state()
        instance = state["v2c_vac"]["store-replenishment"]
        instance["status"] = "confirmed"
        instance["pipeline_stage"] = None
        instance["gate_recommendation"] = "fail"
        instance["render_authorized"] = True
        instance["confirmation_mode"] = "override"
        instance["override_audit"] = {
            "version": 1,
            "items": [
                {
                    "assessment_id": "V2C-GATE-01",
                    "category": "information_integrity",
                    "source_id": "state.v2c_vac.store-replenishment",
                    "original_result": "fail",
                    "risk_level": "high",
                    "impact": "确认包身份与 state 不一致",
                }
            ],
            "reason": "用户接受",
            "confirmed_by": "业务负责人张三",
            "confirmed_at": "2026-08-13T14:00:00+08:00",
        }

        errors = validate(state, schema)

        assert any("category" in error for error in errors)
