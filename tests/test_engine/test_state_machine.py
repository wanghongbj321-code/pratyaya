"""5 态机、if/then 约束、升版边界测试（§8.3）。"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from skills._engine import state
from skills._engine.state import StateMachineError


# ---- 5 态机 ----


@pytest.mark.parametrize("from_s,to_s", [
    ("draft", "gaps_open"),
    ("draft", "review_ready"),
    ("gaps_open", "review_ready"),
    ("review_ready", "gaps_open"),
    ("review_ready", "confirmed"),
    ("confirmed", "rendered"),
])
def test_legal_transitions(from_s, to_s):
    assert state.can_transition(from_s, to_s)
    state.assert_transition(from_s, to_s)  # 不应 raise


@pytest.mark.parametrize("from_s,to_s", [
    ("draft", "confirmed"),       # 跳过 Gate
    ("draft", "rendered"),        # 跳过一切
    ("gaps_open", "confirmed"),   # 缺口未关就确认
    ("gaps_open", "rendered"),
    ("review_ready", "rendered"),  # 未确认就渲染
    ("confirmed", "review_ready"),  # 未经升版回退
    ("rendered", "confirmed"),      # 渲染后回退
])
def test_illegal_transitions_raise(from_s, to_s):
    assert not state.can_transition(from_s, to_s)
    with pytest.raises(StateMachineError):
        state.assert_transition(from_s, to_s)


def test_unknown_status_is_invalid():
    assert not state.can_transition("bogus", "draft")
    with pytest.raises(StateMachineError):
        state.assert_transition("bogus", "draft")


# ---- if/then 约束 ----


def _instance(**kw):
    base = {
        "version": 1,
        "status": "review_ready",
        "gate_recommendation": "pending",
        "render_authorized": False,
        "confirmation_mode": None,
    }
    base.update(kw)
    return base


def test_if_then_override_requires_audit():
    bad = _instance(status="confirmed", gate_recommendation="fail",
                    render_authorized=True, confirmation_mode="override")
    assert state.validate_if_then(bad) != []  # 缺 override_audit

    ok = _instance(status="confirmed", gate_recommendation="fail",
                   render_authorized=True, confirmation_mode="override",
                   override_audit={"version": 1, "items": [], "reason": "r",
                                   "confirmed_by": "u", "confirmed_at": "t"})
    assert state.validate_if_then(ok) == []


def test_if_then_gate_pass():
    bad = _instance(status="confirmed", gate_recommendation="fail",
                    render_authorized=True, confirmation_mode="gate_pass")
    assert state.validate_if_then(bad) != []  # gate_pass 却 fail

    ok = _instance(status="confirmed", gate_recommendation="pass",
                   render_authorized=True, confirmation_mode="gate_pass")
    assert state.validate_if_then(ok) == []


def test_if_then_unconfirmed_must_not_authorize():
    bad = _instance(status="review_ready", gate_recommendation="pass",
                    render_authorized=True, confirmation_mode="gate_pass")
    assert state.validate_if_then(bad) != []


# ---- 升版边界 ----


def test_reset_for_bump_resets_four_fields_and_clears_override():
    before = {
        "version": 3,
        "status": "rendered",
        "gate_recommendation": "pass",
        "render_authorized": True,
        "confirmation_mode": "gate_pass",
        "override_audit": {"version": 1, "items": [], "reason": "x"},
    }
    after = state.reset_for_bump(before, new_status="draft")
    assert after["version"] == 4
    assert after["gate_recommendation"] == "pending"
    assert after["render_authorized"] is False
    assert after["confirmation_mode"] is None
    assert "override_audit" not in after
    assert after["status"] == "draft"
    # 不改入参
    assert before["version"] == 3


def test_reset_for_bump_rejects_bad_target():
    with pytest.raises(StateMachineError):
        state.reset_for_bump({"version": 1}, new_status="rendered")
