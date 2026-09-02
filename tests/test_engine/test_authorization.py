"""授权与 override 完整性测试（§8.3）。"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from skills._engine import authorization as auth
from skills._engine.authorization import AuthorizationError


def _valid_override_audit():
    return {
        "version": 1,
        "items": [
            {
                "assessment_id": "HMW-GATE-03",
                "category": "business_risk",
                "source_id": "hmw-gate",
                "original_result": "fail",
                "risk_level": "high",
                "impact": "方案方向偏保守",
            }
        ],
        "reason": "用户拍板接受该业务风险",
        "confirmed_by": "alice",
        "confirmed_at": "2026-09-02T12:00:00",
    }


def test_valid_override_audit_clean():
    assert auth.validate_override_audit(_valid_override_audit()) == []


def test_missing_top_field_detected():
    bad = _valid_override_audit()
    del bad["reason"]
    problems = auth.validate_override_audit(bad)
    assert any("reason" in p for p in problems)


def test_empty_items_rejected():
    bad = _valid_override_audit()
    bad["items"] = []
    assert any("items" in p for p in auth.validate_override_audit(bad))


def test_item_category_must_be_business_risk():
    bad = _valid_override_audit()
    bad["items"][0]["category"] = "information_integrity"
    assert any("category" in p for p in auth.validate_override_audit(bad))


def test_grant_gate_pass_requires_evidence():
    with pytest.raises(AuthorizationError):
        auth.grant(
            canvas_type="hmw", slug="hmw-1", version=1,
            confirmation_mode="gate_pass",
            confirmed_by="", confirmed_at="", user_confirmation_text="",
        )


def test_grant_gate_pass_ok():
    result = auth.grant(
        canvas_type="hmw", slug="hmw-1", version=1,
        confirmation_mode="gate_pass",
        confirmed_by="alice", confirmed_at="2026-09-02T12:00:00",
        user_confirmation_text="确认 v1 通过",
    )
    assert result["gate_recommendation"] == "pass"
    assert result["render_authorized"] is True
    assert result["confirmation_mode"] == "gate_pass"


def test_grant_override_requires_complete_audit():
    with pytest.raises(AuthorizationError):
        auth.grant(
            canvas_type="hmw", slug="hmw-1", version=1,
            confirmation_mode="override",
            confirmed_by="alice", confirmed_at="2026-09-02T12:00:00",
            user_confirmation_text="接受业务风险",
            override_audit=None,
        )


def test_grant_override_ok():
    result = auth.grant(
        canvas_type="hmw", slug="hmw-1", version=1,
        confirmation_mode="override",
        confirmed_by="alice", confirmed_at="2026-09-02T12:00:00",
        user_confirmation_text="接受业务风险",
        override_audit=_valid_override_audit(),
    )
    assert result["gate_recommendation"] == "fail"
    assert result["render_authorized"] is True
    assert result["override_audit"] is not None
