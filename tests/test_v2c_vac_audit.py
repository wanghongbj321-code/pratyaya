"""V2C VAC HTML 静态审计回归测试。"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT = REPO_ROOT / "skills" / "canvas-render" / "scripts" / "audit_canvas_html.py"
TEMPLATE = REPO_ROOT / "skills" / "canvas-render" / "examples" / "v2c-value-attribution-canvas.html"
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "v2c-vac"
PYTHON = sys.executable


def copy_fixture(tmp_path: Path, fixture_name: str, name: str | None = None) -> Path:
    out = tmp_path / (name or fixture_name)
    shutil.copyfile(FIXTURES / fixture_name, out)
    return out


def copy_template(tmp_path: Path, name: str = "v2c-vac-canvas-sample-vac.html") -> Path:
    out = tmp_path / name
    shutil.copyfile(TEMPLATE, out)
    return out


def write_source_and_state(tmp_path: Path) -> tuple[Path, Path]:
    source = copy_fixture(tmp_path, "V2C-VAC-sample-vac-v1.md")
    state = copy_fixture(tmp_path, "state-gate-pass.json", "state.json")
    return source, state


def run_v2c_audit(html: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    cmd = [PYTHON, str(AUDIT), str(html), "--type", "v2c-vac", *extra]
    return subprocess.run(cmd, capture_output=True, text=True)


def test_v2c_vac_formal_fixture_passes(tmp_path: Path) -> None:
    html = copy_template(tmp_path)
    source, state = write_source_and_state(tmp_path)

    result = run_v2c_audit(
        html,
        "--source",
        str(source),
        "--state",
        str(state),
        "--instance",
        "sample-vac",
        "--template",
        str(TEMPLATE),
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_v2c_vac_formal_delivery_requires_template(tmp_path: Path) -> None:
    html = copy_template(tmp_path)
    source, state = write_source_and_state(tmp_path)

    result = run_v2c_audit(
        html,
        "--source",
        str(source),
        "--state",
        str(state),
        "--instance",
        "sample-vac",
    )

    assert result.returncode != 0
    assert "V2C-VAC-TPL-GATE-00" in result.stdout


def test_v2c_vac_missing_stable_anchor_fails(tmp_path: Path) -> None:
    html = copy_template(tmp_path, "missing-anchor.html")
    html.write_text(
        html.read_text(encoding="utf-8").replace(
            'id="v2c-vac-gap-V2C-AG06"',
            'id="v2c-vac-gap-missing"',
        ),
        encoding="utf-8",
    )

    result = run_v2c_audit(html, "--template", str(TEMPLATE))

    assert result.returncode != 0
    assert "MISSING_ANCHOR" in result.stdout or "V2C-VAC-TPL-GATE-04" in result.stdout


def test_v2c_vac_wrong_canvas_type_fails(tmp_path: Path) -> None:
    html = copy_template(tmp_path, "wrong-type.html")
    html.write_text(
        html.read_text(encoding="utf-8").replace(
            '"canvas_type":"v2c-vac"',
            '"canvas_type":"v2c"',
        ),
        encoding="utf-8",
    )

    result = run_v2c_audit(html, "--template", str(TEMPLATE))

    assert result.returncode != 0
    assert "CANVAS_TYPE" in result.stdout


def test_v2c_vac_wrong_generation_path_fails(tmp_path: Path) -> None:
    html = copy_template(tmp_path, "wrong-generation.html")
    source, state = write_source_and_state(tmp_path)
    html.write_text(
        html.read_text(encoding="utf-8").replace(
            '"generation_path":"transcript-direct"',
            '"generation_path":"not-a-path"',
        ),
        encoding="utf-8",
    )

    result = run_v2c_audit(
        html,
        "--source",
        str(source),
        "--state",
        str(state),
        "--instance",
        "sample-vac",
        "--template",
        str(TEMPLATE),
    )

    assert result.returncode != 0
    assert "V2C_GENERATION" in result.stdout


def test_v2c_vac_wrong_source_file_fails(tmp_path: Path) -> None:
    html = copy_template(tmp_path, "wrong-source-file.html")
    source, state = write_source_and_state(tmp_path)
    html.write_text(
        html.read_text(encoding="utf-8").replace(
            '"source_file":"modules/V2C-VAC-sample-vac-v1.md"',
            '"source_file":"modules/WRONG-v1.md"',
        ),
        encoding="utf-8",
    )

    result = run_v2c_audit(
        html,
        "--source",
        str(source),
        "--state",
        str(state),
        "--instance",
        "sample-vac",
        "--template",
        str(TEMPLATE),
    )

    assert result.returncode != 0
    assert "V2C_SOURCE_FILE" in result.stdout


def test_v2c_vac_override_assessment_id_must_use_gate_id(tmp_path: Path) -> None:
    html = copy_template(tmp_path, "bad-override.html")
    text = html.read_text(encoding="utf-8")
    text = text.replace('"confirmation_mode":"gate_pass"', '"confirmation_mode":"override"')
    text = text.replace(
        '"override_audit":{"items":[]}',
        '"override_audit":{"items":[{"assessment_id":"V2C-AG01","category":"business_risk"}]}',
    )
    text = text.replace('<p id="quality-caveat" hidden>', '<p id="quality-caveat">')
    html.write_text(text, encoding="utf-8")

    result = run_v2c_audit(html, "--template", str(TEMPLATE))

    assert result.returncode != 0
    assert "V2C_OVERRIDE" in result.stdout


def test_v2c_vac_override_business_risk_fixture_passes(tmp_path: Path) -> None:
    html = copy_template(tmp_path, "override-pass.html")
    state = copy_fixture(tmp_path, "state-override-business-risk.json", "state.json")
    state_data = json.loads(state.read_text(encoding="utf-8"))
    override_audit = state_data["v2c_vac"]["sample-vac"]["override_audit"]
    text = html.read_text(encoding="utf-8")
    text = text.replace('"gate_recommendation":"pass"', '"gate_recommendation":"fail"')
    text = text.replace('"confirmation_mode":"gate_pass"', '"confirmation_mode":"override"')
    text = text.replace(
        '"override_audit":{"items":[]}',
        f'"override_audit":{json.dumps(override_audit, ensure_ascii=False, separators=(",", ":"))}',
    )
    text = text.replace('<p id="quality-caveat" hidden>', '<p id="quality-caveat">')
    html.write_text(text, encoding="utf-8")
    source = copy_fixture(tmp_path, "V2C-VAC-sample-vac-v1.md")

    result = run_v2c_audit(
        html,
        "--source",
        str(source),
        "--state",
        str(state),
        "--instance",
        "sample-vac",
        "--template",
        str(TEMPLATE),
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_v2c_vac_index_fixture_passes(tmp_path: Path) -> None:
    html = copy_fixture(tmp_path, "v2c-vac-canvas-index.html")
    state = copy_fixture(tmp_path, "state-index.json", "state.json")

    result = run_v2c_audit(
        html,
        "--state",
        str(state),
        "--index",
        "--page-type",
        "v2c-vac-index",
    )

    assert result.returncode == 0, result.stdout + result.stderr
