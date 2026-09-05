"""v3.6 current delivery: identity, anti-downgrade and final SVG regression."""
import copy
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/canvas-render/scripts"))
from canvas_audit.audit_core import audit
from canvas_audit.audit_helpers import parse_html

MAAU = ROOT / "tests/fixtures/maau/maau-global-canvas-retail-demo.html"
SOURCE = ROOT / "tests/fixtures/maau/MAAU-retail-demo-v1.md"
STATE = ROOT / "tests/fixtures/state/maau-gate-pass.json"
EXAMPLES = ROOT / "skills/canvas-render/examples/mvl-canvas"


def change_data(text, mutate):
    m = re.search(r'(<script[^>]*id="canvas-data"[^>]*>)(.*?)(</script>)', text, re.S)
    data = json.loads(m[2])
    mutate(data)
    return text[:m.start(2)] + json.dumps(data, ensure_ascii=False) + text[m.end(2):]


def check(tmp_path, text, variant="workflow", target=None):
    p = tmp_path / "candidate.html"
    p.write_text(text)
    return audit(p, source_path=SOURCE, state_path=STATE, instance_slug="retail-demo",
                 page_type_arg="global", generation_path_arg="transcript-direct",
                 workflow_variant=variant,
                 target_output=Path(target or f"maau-global-canvas-retail-demo--{variant}-v1.html"))


def test_current_maau_and_explicit_legacy(tmp_path):
    assert not check(tmp_path, MAAU.read_text())
    assert audit(MAAU, source_path=SOURCE, state_path=STATE, instance_slug="retail-demo")
    assert not audit(MAAU, source_path=SOURCE, state_path=STATE, instance_slug="retail-demo", artifact_policy="legacy")


@pytest.mark.parametrize("target", [
    "maau-global-canvas-retail-demo--workflow-v2.html",
    "maau-global-canvas-another--workflow-v1.html",
    "maau-global-canvas-retail-demo--noflow-v1.html",
    "maau-global-canvas-retail-demo.html",
    "maau-global-canvas.html",
])
def test_wrong_target_rejected(tmp_path, target):
    assert "ARTIFACT_IDENTITY" in {f.code for f in check(tmp_path, MAAU.read_text(), target=target)}


def test_missing_expected_form_rejected(tmp_path):
    assert check(tmp_path, MAAU.read_text(), variant=None)


def test_noflow_example_and_downgrade(tmp_path):
    text = (EXAMPLES / "maau-global-canvas-noflow.html").read_text()
    p = tmp_path / "candidate.html"
    p.write_text(text)
    assert not audit(p, workflow_variant="noflow", target_output=Path("maau-global-canvas.html"))
    assert audit(p, workflow_variant="workflow", target_output=Path("maau-global-canvas--workflow.html"))
    assert text.count('id="workflow-done"') == 1
    p.write_text(change_data(text, lambda d: d.update(workflow={})))
    assert audit(p, workflow_variant="noflow", target_output=Path("maau-global-canvas.html"))
    p.write_text(text.replace('id="intent"', 'id="removed"'))
    assert audit(p, workflow_variant="noflow", target_output=Path("maau-global-canvas.html"))


@pytest.mark.parametrize("mutation", [
    lambda t: change_data(t, lambda d: d.pop("workflow")),
    lambda t: re.sub(r'<svg[^>]*class="bpmn-flow".*?</svg>', '', t, flags=re.S),
    lambda t: t.replace('id="workflow-flow"', 'id="removed"'),
])
def test_workflow_omissions_fail(tmp_path, mutation):
    assert check(tmp_path, mutation(MAAU.read_text()))


def test_current_all_canvas_e2e_targets():
    spec = importlib.util.spec_from_file_location('e2e_cases', ROOT / 'tests/test_e2e_authorization.py')
    cases = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cases)
    for name, case in cases.E2E_CANVASES.items():
        base = cases.E2E / case["fixture"]
        command = [sys.executable, str(cases.AUDIT), str(base / case['html']),
                   '--source', str(base / case['source']), '--state', str(base / case['state'])]
        command += case['cli']
        if case.get('instance'):
            command += ['--instance', case['instance']]
        if case.get('template'):
            command += ['--template', str(ROOT / case['template'])]
        _, html = parse_html(base / case['html'])
        v = html.body_attrs['data-version'].removeprefix('v')
        if name == 'maau':
            target = f"maau-global-canvas-{case['instance']}--workflow-v{v}.html"
            command += ['--workflow-variant', 'workflow']
        elif name == 'mvl':
            target = f"module-{html.body_attrs['data-module'][1:]}-canvas--v{v}.html"
        else:
            target = f"{name}-canvas-{case['instance']}--v{v}.html"
        command += ['--target-output', target]
        result = subprocess.run(command, capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr


def test_versioned_paths_and_stale_sidecars(tmp_path):
    from skills._engine import paths, files
    names = set()
    for slug in ("sales", "sales-workflow", "sales-v1"):
        for variant in ("noflow", "workflow"):
            path = paths.html_file(tmp_path, "maau-global", slug, version=1, workflow_variant=variant)
            names.add(path)
            path.parent.mkdir(exist_ok=True)
            path.write_text("existing verified artifact")
            assert files.html_exists(tmp_path, "maau-global", slug, version=1, workflow_variant=variant)
            files.mark_html_stale(tmp_path, "maau-global", slug, stale_version=1, version=1, workflow_variant=variant)
            assert files.is_html_stale(tmp_path, "maau-global", slug, version=1, workflow_variant=variant)
            assert path.read_text() == "existing verified artifact"
    assert len(names) == 6
    with pytest.raises(ValueError):
        paths.html_file(tmp_path, "gc", "bad--slug", version=1)


def test_state_reentry_and_source_bump():
    from skills._engine import state
    assert state.can_transition("rendered", "rendered")
    assert not state.can_transition("rendered", "confirmed")
    original = {"version": 1, "status": "rendered", "render_authorized": True,
                "confirmation_mode": "gate_pass", "gate_recommendation": "pass",
                "output_file": "output/maau-global-canvas-sales--noflow-v1.html"}
    bumped = state.reset_for_bump(original)
    assert bumped["version"] == 2 and not bumped["render_authorized"]
    assert original["status"] == "rendered" and original["render_authorized"]


def test_index_uses_actual_output_file(tmp_path):
    from canvas_audit.audit_helpers import audit_index_page
    html = tmp_path / "index.html"
    html.write_text('<body data-page-type="golden-circle-index"><a href="gc-canvas-sales--v2.html">sales</a><script id="canvas-data" type="application/json">{"instances":[{"slug":"sales"}]}</script></body>')
    state = tmp_path / 'state.json'
    state.write_text(json.dumps({"golden_circle":{"sales":{"output_file":"output/gc-canvas-sales--v2.html"}}}))
    text, snapshot = parse_html(html)
    assert not audit_index_page(snapshot, text, state, 'gc')
    html.write_text(text.replace('gc-canvas-sales--v2.html','gc-canvas-sales.html'))
    text, snapshot = parse_html(html)
    assert audit_index_page(snapshot, text, state, 'gc')
