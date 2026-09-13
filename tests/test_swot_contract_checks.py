from pathlib import Path

from scripts.contract_consistency.runner import RULES, run_checks


SWOT_RULES = {
    "SWOT_SKILL_SYNC",
    "SWOT_GATE_TABLE",
    "SWOT_SECTION_SYNC",
    "SWOT_TEMPLATE_PROFILE",
    "SWOT_STATE_SCHEMA",
}


def test_swot_rules_are_registered_and_baseline_clean():
    assert SWOT_RULES <= {rule.code for rule in RULES}
    findings = run_checks(Path(__file__).resolve().parents[1], selected=sorted(SWOT_RULES))
    assert findings == []
