"""5W 根因分析画布 HTML 静态审计回归测试。

覆盖：正式 fixture 双 Gate 通过 / 缺 --template / 缺稳定锚点 / canvas_type
错误 / override assessment_id pattern / business_risk override 通过 / 索引页。
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT = REPO_ROOT / "skills" / "canvas-render" / "scripts" / "audit_canvas_html.py"
TEMPLATE = REPO_ROOT / "skills" / "canvas-render" / "examples" / "5w-canvas.html"
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "5w"
SAMPLE = FIXTURES / "5w-canvas-sample-5w.html"
PYTHON = sys.executable


def copy_fixture(tmp_path: Path, fixture_name: str, name: str | None = None) -> Path:
    out = tmp_path / (name or fixture_name)
    shutil.copyfile(FIXTURES / fixture_name, out)
    return out


def copy_sample(tmp_path: Path, name: str = "5w-canvas-sample-5w.html") -> Path:
    out = tmp_path / name
    shutil.copyfile(SAMPLE, out)
    return out


def write_source_and_state(tmp_path: Path) -> tuple[Path, Path]:
    source = copy_fixture(tmp_path, "5W-sample-5w-v1.md")
    state = copy_fixture(tmp_path, "state-gate-pass.json", "state.json")
    return source, state


def run_5w_audit(html: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    cmd = [PYTHON, str(AUDIT), str(html), "--type", "5w", *extra]
    return subprocess.run(cmd, capture_output=True, text=True)


def test_5w_formal_fixture_passes(tmp_path: Path) -> None:
    html = copy_sample(tmp_path)
    source, state = write_source_and_state(tmp_path)

    result = run_5w_audit(
        html,
        "--source",
        str(source),
        "--state",
        str(state),
        "--instance",
        "sample-5w",
        "--template",
        str(TEMPLATE),
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_5w_formal_delivery_requires_template(tmp_path: Path) -> None:
    html = copy_sample(tmp_path)
    source, state = write_source_and_state(tmp_path)

    result = run_5w_audit(
        html,
        "--source",
        str(source),
        "--state",
        str(state),
        "--instance",
        "sample-5w",
    )

    assert result.returncode != 0
    assert "5W-TPL-GATE-00" in result.stdout


def test_5w_missing_stable_anchor_fails(tmp_path: Path) -> None:
    html = copy_sample(tmp_path, "missing-anchor.html")
    html.write_text(
        html.read_text(encoding="utf-8").replace(
            'id="5w-why-5"',
            'id="5w-why-5-missing"',
        ),
        encoding="utf-8",
    )

    result = run_5w_audit(html, "--template", str(TEMPLATE))

    assert result.returncode != 0
    assert "MISSING_ANCHOR" in result.stdout or "5W-TPL-GATE-04" in result.stdout


def test_5w_wrong_canvas_type_fails(tmp_path: Path) -> None:
    html = copy_sample(tmp_path, "wrong-type.html")
    html.write_text(
        html.read_text(encoding="utf-8").replace(
            '"canvas_type": "5w"',
            '"canvas_type": "5W"',
        ),
        encoding="utf-8",
    )

    result = run_5w_audit(html, "--template", str(TEMPLATE))

    assert result.returncode != 0
    assert "CANVAS_TYPE" in result.stdout


def test_5w_override_assessment_id_must_use_gate_id(tmp_path: Path) -> None:
    html = copy_sample(tmp_path, "bad-override.html")
    text = html.read_text(encoding="utf-8")
    text = text.replace('"confirmation_mode": "gate_pass"', '"confirmation_mode": "override"')
    text = text.replace(
        '"override_audit": {\n      "items": []\n    }',
        '"override_audit": {"items": [{"assessment_id": "5W-AG01", "category": "business_risk"}]}',
    )
    text = text.replace('<div class="caveat" id="quality-caveat" hidden>', '<div class="caveat" id="quality-caveat">')
    html.write_text(text, encoding="utf-8")

    result = run_5w_audit(html, "--template", str(TEMPLATE))

    assert result.returncode != 0
    assert "5W_OVERRIDE" in result.stdout


def test_5w_override_business_risk_fixture_passes(tmp_path: Path) -> None:
    html = copy_sample(tmp_path, "override-pass.html")
    state = copy_fixture(tmp_path, "state-override-business-risk.json", "state.json")
    state_data = json.loads(state.read_text(encoding="utf-8"))
    override_audit = state_data["five_whys"]["sample-5w"]["override_audit"]
    text = html.read_text(encoding="utf-8")
    text = text.replace('"gate_recommendation": "pass"', '"gate_recommendation": "fail"')
    text = text.replace('"confirmation_mode": "gate_pass"', '"confirmation_mode": "override"')
    text = text.replace(
        '"override_audit": {\n      "items": []\n    }',
        f'"override_audit": {json.dumps(override_audit, ensure_ascii=False, separators=(",", ":"))}',
    )
    text = text.replace('<div class="caveat" id="quality-caveat" hidden>', '<div class="caveat" id="quality-caveat">')
    html.write_text(text, encoding="utf-8")
    source = copy_fixture(tmp_path, "5W-sample-5w-v1.md")

    result = run_5w_audit(
        html,
        "--source",
        str(source),
        "--state",
        str(state),
        "--instance",
        "sample-5w",
        "--template",
        str(TEMPLATE),
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_5w_index_fixture_passes(tmp_path: Path) -> None:
    html = copy_fixture(tmp_path, "5w-canvas-index.html")
    state = copy_fixture(tmp_path, "state-index.json", "state.json")

    result = run_5w_audit(
        html,
        "--state",
        str(state),
        "--index",
        "--page-type",
        "5w-index",
    )

    assert result.returncode == 0, result.stdout + result.stderr
