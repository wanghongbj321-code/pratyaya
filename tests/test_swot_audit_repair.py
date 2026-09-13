"""Regression coverage for SWOT review findings; no render generation."""
from pathlib import Path
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/canvas-render/scripts'))
from canvas_audit.audit_core import main
from canvas_audit.audit_helpers import audit_swot_content_mapping, parse_html


def test_agent_frontmatter_is_valid_yaml():
    doc = (ROOT / 'agents/pratyaya.md').read_text(encoding='utf-8')
    assert yaml.safe_load(doc.split('---', 2)[1])['name'] == 'pratyaya'


@pytest.mark.parametrize('omitted', ['--source', '--state', '--instance', '--template'])
def test_formal_audit_requires_context(omitted, capsys):
    fixture = ROOT / 'tests/fixtures/swot/formal'
    args = [str(fixture / 'output/swot-canvas-review-case--v1.html'), '--type', 'swot']
    options = {'--source': str(fixture / 'modules/SWOT-review-case-v1.md'),
               '--state': str(fixture / 'state.json'), '--instance': 'review-case',
               '--template': str(ROOT / 'skills/canvas-render/examples/swot-canvas.html')}
    for key, value in options.items():
        if key != omitted:
            args.extend([key, value])
    assert main(args) != 0
    assert 'SWOT_FORMAL_PARAMS' in capsys.readouterr().out


def test_empty_source_cannot_pass_mapping(tmp_path):
    """A package without the required SWOT sections must be rejected."""
    package = tmp_path / 'SWOT-review-case-v1.md'
    package.write_text('# SWOT 确认包 v1\n', encoding='utf-8')
    _, html = parse_html(ROOT / 'tests/fixtures/swot/formal/output/swot-canvas-review-case--v1.html')
    findings = audit_swot_content_mapping(html, package)
    assert findings
    assert any(f.code == 'SWOT_CONTENT' for f in findings)


def test_swot_mapping_rejects_legacy_factor_reference(tmp_path):
    package = ROOT / 'tests/fixtures/swot/formal/modules/SWOT-review-case-v1.md'
    broken = tmp_path / package.name
    broken.write_text(
        package.read_text(encoding='utf-8').replace('SWOT-F-S02', 'S-02'),
        encoding='utf-8',
    )
    _, html = parse_html(ROOT / 'tests/fixtures/swot/formal/output/swot-canvas-review-case--v1.html')
    findings = audit_swot_content_mapping(html, broken)
    assert any('稳定编号' in f.message for f in findings)


def test_swot_mapping_rejects_tampered_user_decision(tmp_path):
    package = ROOT / 'tests/fixtures/swot/formal/modules/SWOT-review-case-v1.md'
    broken = tmp_path / package.name
    broken.write_text(
        package.read_text(encoding='utf-8').replace('| 待决策 | 快速上线', '| 采用 | 快速上线'),
        encoding='utf-8',
    )
    _, html = parse_html(ROOT / 'tests/fixtures/swot/formal/output/swot-canvas-review-case--v1.html')
    findings = audit_swot_content_mapping(html, broken)
    assert any('用户决定' in f.message for f in findings)


def test_swot_mapping_rejects_missing_handover_item(tmp_path):
    package = ROOT / 'tests/fixtures/swot/formal/modules/SWOT-review-case-v1.md'
    broken = tmp_path / package.name
    broken.write_text(
        package.read_text(encoding='utf-8').replace('建立客户风险分级标准', '建立不存在的交接事项'),
        encoding='utf-8',
    )
    _, html = parse_html(ROOT / 'tests/fixtures/swot/formal/output/swot-canvas-review-case--v1.html')
    findings = audit_swot_content_mapping(html, broken)
    assert any('交接事项' in f.message for f in findings)


def test_current_fixture_does_not_hide_omitted_evidence():
    fixture = ROOT / 'tests/fixtures/swot/formal'
    _, html = parse_html(fixture / 'output/swot-canvas-review-case--v1.html')
    findings = audit_swot_content_mapping(html, fixture / 'modules/SWOT-review-case-v1.md')
    # Current fixture should pass all content mapping checks
    assert len(findings) == 0, f"Current fixture should pass, but got: {findings}"
