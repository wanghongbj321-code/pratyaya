"""state.schema.json 的 MAAU 一次性综合路径（maau.{slug}）schema 校验测试。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

SCHEMA_PATH = REPO_ROOT / "schemas" / "state.schema.json"


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def base_state() -> dict:
    """构造一个最小合法 state（含 project_slug / group_id / maau.retail-demo draft）。"""
    return {
        "schema_version": "2.3",
        "project_slug": "demo-project",
        "project_name": "Demo 项目",
        "group_id": "group-a",
        "maau": {
            "retail-demo": {
                "slug": "retail-demo",
                "generation_path": "transcript-direct",
                "version": 1,
                "status": "draft",
                "gate_recommendation": "pending",
                "render_authorized": False,
                "confirmation_mode": None,
                "source_file": "modules/MAAU-retail-demo-v1.md",
                "output_file": None,
            }
        },
        "updated_at": "2026-08-08T10:00:00+08:00",
    }


def validate(state: dict, schema: dict) -> list[str]:
    """返回校验错误信息列表；空列表表示通过。"""
    errors: list[str] = []
    validator = jsonschema.Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(state), key=lambda e: list(e.path)):
        errors.append(f"{'.'.join(map(str, error.path))}: {error.message}")
    instances = state.get("maau")
    if isinstance(instances, dict):
        for slug, instance in instances.items():
            if isinstance(instance, dict) and instance.get("slug") != slug:
                errors.append(f"maau.{slug}.slug: must match map key")
    return errors


class TestValidMaauStates:
    def test_draft_state_passes(self, schema: dict) -> None:
        errors = validate(base_state(), schema)
        assert errors == []

    def test_gate_pass_confirmed_state_passes(self, schema: dict) -> None:
        state = base_state()
        state["maau"]["retail-demo"]["status"] = "confirmed"
        state["maau"]["retail-demo"]["gate_recommendation"] = "pass"
        state["maau"]["retail-demo"]["render_authorized"] = True
        state["maau"]["retail-demo"]["confirmation_mode"] = "gate_pass"
        errors = validate(state, schema)
        assert errors == []

    def test_gate_pass_rendered_state_passes(self, schema: dict) -> None:
        state = base_state()
        state["maau"]["retail-demo"]["status"] = "rendered"
        state["maau"]["retail-demo"]["gate_recommendation"] = "pass"
        state["maau"]["retail-demo"]["render_authorized"] = True
        state["maau"]["retail-demo"]["confirmation_mode"] = "gate_pass"
        state["maau"]["retail-demo"]["output_file"] = "output/maau-global-canvas-retail-demo.html"
        errors = validate(state, schema)
        assert errors == []

    def test_override_state_with_maau_gate_id_passes(self, schema: dict) -> None:
        state = base_state()
        state["maau"]["retail-demo"]["status"] = "confirmed"
        state["maau"]["retail-demo"]["gate_recommendation"] = "fail"
        state["maau"]["retail-demo"]["render_authorized"] = True
        state["maau"]["retail-demo"]["confirmation_mode"] = "override"
        state["maau"]["retail-demo"]["override_audit"] = {
            "version": 1,
            "items": [
                {
                    "assessment_id": "MAAU-GATE-06",
                    "category": "business_risk",
                    "source_id": "MAAU Validation 板块",
                    "original_result": "fail",
                    "risk_level": "medium",
                    "impact": "Validation 证据不完整",
                }
            ],
            "reason": "用户接受该业务风险",
            "confirmed_by": "业务负责人张三",
            "confirmed_at": "2026-08-08T10:00:00+08:00",
        }
        errors = validate(state, schema)
        assert errors == []

    def test_slug_required_and_present(self, schema: dict) -> None:
        # generation_path 与 slug 都是必填
        state = base_state()
        del state["maau"]["retail-demo"]["generation_path"]
        errors = validate(state, schema)
        assert any("generation_path" in e for e in errors)


class TestInvalidMaauStates:
    def test_default_slug_fails(self, schema: dict) -> None:
        state = base_state()
        state["maau"] = {
            "default": {
                "slug": "default",
                "generation_path": "transcript-direct",
                "version": 1,
                "status": "draft",
                "gate_recommendation": "pending",
                "render_authorized": False,
                "confirmation_mode": None,
            }
        }
        errors = validate(state, schema)
        assert any("default" in e for e in errors)

    def test_map_key_slug_mismatch_fails(self, schema: dict) -> None:
        state = base_state()
        state["maau"]["retail-demo"]["slug"] = "other-slug"
        errors = validate(state, schema)
        assert any("must match map key" in e for e in errors)

    def test_non_kebab_slug_fails(self, schema: dict) -> None:
        state = base_state()
        state["maau"] = {
            "Bad_Slug": {
                "slug": "Bad_Slug",
                "generation_path": "transcript-direct",
                "version": 1,
                "status": "draft",
                "gate_recommendation": "pending",
                "render_authorized": False,
                "confirmation_mode": None,
            }
        }
        errors = validate(state, schema)
        assert errors != []

    def test_non_transcript_direct_generation_path_fails(self, schema: dict) -> None:
        state = base_state()
        state["maau"]["retail-demo"]["generation_path"] = "m1-m6"
        errors = validate(state, schema)
        assert any("generation_path" in e for e in errors)

    def test_override_with_information_integrity_fails(self, schema: dict) -> None:
        state = base_state()
        state["maau"]["retail-demo"]["status"] = "confirmed"
        state["maau"]["retail-demo"]["gate_recommendation"] = "fail"
        state["maau"]["retail-demo"]["render_authorized"] = True
        state["maau"]["retail-demo"]["confirmation_mode"] = "override"
        state["maau"]["retail-demo"]["override_audit"] = {
            "version": 1,
            "items": [
                {
                    "assessment_id": "MAAU-GATE-03",
                    "category": "information_integrity",
                    "source_id": "MAAU 六板块字段",
                    "original_result": "fail",
                    "risk_level": "high",
                    "impact": "字段不完整",
                }
            ],
            "reason": "用户接受",
            "confirmed_by": "业务负责人张三",
            "confirmed_at": "2026-08-08T10:00:00+08:00",
        }
        errors = validate(state, schema)
        assert any("category" in e for e in errors)

    def test_override_with_m1_gate_id_fails(self, schema: dict) -> None:
        state = base_state()
        state["maau"]["retail-demo"]["status"] = "confirmed"
        state["maau"]["retail-demo"]["gate_recommendation"] = "fail"
        state["maau"]["retail-demo"]["render_authorized"] = True
        state["maau"]["retail-demo"]["confirmation_mode"] = "override"
        state["maau"]["retail-demo"]["override_audit"] = {
            "version": 1,
            "items": [
                {
                    "assessment_id": "M1-GATE-01",
                    "category": "business_risk",
                    "source_id": "M1",
                    "original_result": "fail",
                    "risk_level": "medium",
                    "impact": "M1 目标字段",
                }
            ],
            "reason": "用户接受",
            "confirmed_by": "业务负责人张三",
            "confirmed_at": "2026-08-08T10:00:00+08:00",
        }
        errors = validate(state, schema)
        assert any("assessment_id" in e for e in errors)

    def test_override_with_hmw_gate_id_fails(self, schema: dict) -> None:
        state = base_state()
        state["maau"]["retail-demo"]["status"] = "confirmed"
        state["maau"]["retail-demo"]["gate_recommendation"] = "fail"
        state["maau"]["retail-demo"]["render_authorized"] = True
        state["maau"]["retail-demo"]["confirmation_mode"] = "override"
        state["maau"]["retail-demo"]["override_audit"] = {
            "version": 1,
            "items": [
                {
                    "assessment_id": "HMW-GATE-01",
                    "category": "business_risk",
                    "source_id": "HMW",
                    "original_result": "fail",
                    "risk_level": "medium",
                    "impact": "HMW 陈述字段",
                }
            ],
            "reason": "用户接受",
            "confirmed_by": "业务负责人张三",
            "confirmed_at": "2026-08-08T10:00:00+08:00",
        }
        errors = validate(state, schema)
        assert any("assessment_id" in e for e in errors)

    def test_generation_path_missing_fails(self, schema: dict) -> None:
        state = base_state()
        del state["maau"]["retail-demo"]["generation_path"]
        errors = validate(state, schema)
        assert any("generation_path" in e for e in errors)
