"""SWOT optional state schema: structural validation only, not runtime authorization."""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / 'schemas/state.schema.json').read_text(encoding='utf-8'))
VALIDATOR = Draft202012Validator(SCHEMA)


def fixture(name):
    return json.loads((ROOT / 'tests/fixtures/state' / f'{name}.json').read_text(encoding='utf-8'))


@pytest.mark.parametrize('name', ['swot-draft', 'swot-gate-pass', 'swot-override', 'legacy-v24-without-swot'])
def test_valid_states(name):
    VALIDATOR.validate(fixture(name))


def test_schema_is_valid_and_stays_v24():
    Draft202012Validator.check_schema(SCHEMA)
    assert SCHEMA['properties']['schema_version']['const'] == '2.4'


def test_existing_topic_can_add_swot_without_other_changes():
    state = fixture('legacy-v24-without-swot')
    state['swot'] = fixture('swot-draft')['swot']
    VALIDATOR.validate(state)


@pytest.mark.parametrize('status', ['draft', 'gaps_open', 'review_ready', 'confirmed', 'rendered'])
def test_five_states(status):
    state = fixture('swot-gate-pass' if status in ('confirmed', 'rendered') else 'swot-draft')
    state['swot']['review-case']['status'] = status
    VALIDATOR.validate(state)


@pytest.mark.parametrize('mutation', [
    {'status': 'approved'}, {'version': -1}, {'slug': 'Bad Slug'},
    {'gate_recommendation': 'warn'}, {'render_authorized': True},
    {'confirmation_mode': 'gate_pass'},
])
def test_invalid_instance_cannot_hide_behind_valid_other_canvas(mutation):
    state = fixture('legacy-v24-without-swot')
    state['swot'] = fixture('swot-draft')['swot']
    state['swot']['review-case'].update(mutation)
    assert list(VALIDATOR.iter_errors(state))


@pytest.mark.parametrize('key', ['Bad Slug', '../escape', '', 'x' * 65])
def test_invalid_map_keys(key):
    state = fixture('legacy-v24-without-swot')
    state['swot'] = {key: fixture('swot-draft')['swot']['review-case']}
    assert list(VALIDATOR.iter_errors(state))


def test_missing_instance_slug():
    state = fixture('legacy-v24-without-swot')
    state['swot'] = fixture('swot-draft')['swot']
    del state['swot']['review-case']['slug']
    assert list(VALIDATOR.iter_errors(state))


@pytest.mark.parametrize('gate_id', ['SWOT-GATE-00', 'SWOT-GATE-09', 'SWOT-GATE-99', 'SWOT-GATE-6', 'HMW-GATE-06', 'SWOT-G-01'])
def test_invalid_override_id(gate_id):
    state = fixture('swot-override')
    state['swot']['review-case']['override_audit']['items'][0]['assessment_id'] = gate_id
    errors = list(VALIDATOR.iter_errors(state))
    assert any('assessment_id' in error.path for error in errors)


def test_information_integrity_override_rejected():
    errors = list(VALIDATOR.iter_errors(fixture('swot-invalid-override')))
    assert any('category' in error.path for error in errors)


@pytest.mark.parametrize('mutation', [
    {'gate_recommendation': 'pending'}, {'gate_recommendation': 'fail'},
    {'render_authorized': False},
])
def test_gate_pass_requires_pass_and_authorization(mutation):
    state = fixture('swot-gate-pass')
    state['swot']['review-case'].update(mutation)
    assert list(VALIDATOR.iter_errors(state))


@pytest.mark.parametrize('missing', ['override_audit', 'reason', 'confirmed_by', 'confirmed_at', 'items'])
def test_override_requires_audit_evidence(missing):
    state = fixture('swot-override')
    instance = state['swot']['review-case']
    if missing == 'override_audit':
        del instance[missing]
    else:
        del instance['override_audit'][missing]
    assert list(VALIDATOR.iter_errors(state))
