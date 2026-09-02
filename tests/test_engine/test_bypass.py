"""绕过检测测试（§8.3）：拦截「跳过 Gate / 未确认即渲染 / 违规 override」。"""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from skills._engine import gate, state
from skills._engine.gate import Assessment
from skills._engine.state import StateMachineError


def test_cannot_skip_straight_to_rendered():
    # 未经 confirmed 直接渲染即绕过。
    with pytest.raises(StateMachineError):
        state.assert_transition("draft", "rendered")
    with pytest.raises(StateMachineError):
        state.assert_transition("review_ready", "rendered")
    with pytest.raises(StateMachineError):
        state.assert_transition("gaps_open", "rendered")


def test_cannot_confirm_with_open_gaps():
    with pytest.raises(StateMachineError):
        state.assert_transition("gaps_open", "confirmed")


def test_information_integrity_fail_blocks_override():
    summary = gate.evaluate([
        Assessment("GC-GATE-02", "fail", "information_integrity"),
    ])
    assert summary.gate_recommendation == "fail"
    assert summary.override_eligible is False
    assert summary.has_information_integrity_fail is True


def test_only_business_risk_fail_allows_override():
    summary = gate.evaluate([
        Assessment("HMW-GATE-03", "fail", "business_risk"),
        Assessment("HMW-GATE-01", "pass", "business_risk"),
    ])
    assert summary.gate_recommendation == "fail"
    assert summary.override_eligible is True
    assert summary.has_information_integrity_fail is False


def test_all_pass_is_clean():
    summary = gate.evaluate([
        Assessment("HMW-GATE-01", "pass", "business_risk"),
        Assessment("HMW-GATE-02", "pass", "information_integrity"),
    ])
    assert summary.gate_recommendation == "pass"
    assert summary.override_eligible is False
