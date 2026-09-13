"""画布注册表一致性测试（§8.3）。

锁定 `skills/_engine/canvas_registry.py` 的 CANVASES 为九个注册项的唯一事实源，
其参数与 `agents/pratyaya.md` 注册表表格一致。
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from skills._engine import canvas_registry as reg


def test_nine_canvas_ids():
    assert {c.canvas_id for c in reg.CANVASES} == {
        "mvl", "maau", "gc", "hmw", "persona", "journey", "v2c-vac", "5w", "swot",
    }


def test_eight_audit_types():
    # maau 复用 mvl，去重后 8 种。
    assert set(reg.audit_types()) == {
        "mvl", "gc", "hmw", "persona", "journey", "v2c-vac", "5w", "swot",
    }
    assert len(reg.audit_types()) == 8


def test_swot_spec_and_lookups():
    expected = reg.CanvasSpec(
        canvas_id="swot", canvas_type="swot", audit_type="swot",
        state_key="swot.{slug}", file_prefix="SWOT", output_prefix="swot",
        distill_skill="swot-distill", gate_skill="swot-gate",
        gate_id_prefix="SWOT-GATE-", page_type="swot-index",
        template="skills/canvas-render/examples/swot-canvas.html",
        generation_path=None, is_instance_map=True,
    )
    assert reg.by_id("swot") == expected
    assert reg.get("swot") == expected
    assert reg.by_audit_type("swot") == expected
    assert reg.by_prefix("SWOT") == expected
    assert reg.by_id("swot").state_key_root == "swot"


def test_eight_canvas_types():
    assert set(reg.canvas_types()) == {
        "mvl", "golden-circle", "hmw", "persona", "journey", "v2c-vac", "5w", "swot",
    }
    assert len(reg.canvas_types()) == 8


def test_engine_roots_match_schema():
    import json

    schema = json.loads((REPO_ROOT / "schemas/state.schema.json").read_text(encoding="utf-8"))
    canvas_roots = {root for branch in schema["anyOf"] for root in branch["required"]}
    assert {spec.state_key_root for spec in reg.CANVASES} == canvas_roots


def test_maau_reuses_mvl():
    maau = reg.by_id("maau")
    assert maau.canvas_type == "mvl"
    assert maau.audit_type == "mvl"
    assert maau.generation_path == "transcript-direct"


def test_gc_has_distinct_type_and_audit():
    gc = reg.by_id("gc")
    assert gc.canvas_type == "golden-circle"
    assert gc.audit_type == "gc"
    assert gc.canvas_type != gc.audit_type


def test_state_key_roots():
    assert reg.by_id("mvl").state_key_root == "modules"
    assert reg.by_id("maau").state_key_root == "maau"
    assert reg.by_id("gc").state_key_root == "golden_circle"
    assert reg.by_id("5w").state_key_root == "five_whys"
    assert reg.by_id("v2c-vac").state_key_root == "v2c_vac"


def test_mvl_is_not_instance_map():
    assert reg.by_id("mvl").is_instance_map is False
    for cid in ("maau", "gc", "hmw", "persona", "journey", "v2c-vac", "5w", "swot"):
        assert reg.by_id(cid).is_instance_map is True


def test_validate_clean():
    assert reg.validate() == []
