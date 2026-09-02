"""画布注册表一致性测试（§8.3）。

锁定 `skills/_engine/canvas_registry.py` 的 CANVASES 为八类画布唯一事实源，
其参数与 `agents/pratyaya.md` 注册表表格一致。
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from skills._engine import canvas_registry as reg


def test_eight_canvas_ids():
    assert {c.canvas_id for c in reg.CANVASES} == {
        "mvl", "maau", "gc", "hmw", "persona", "journey", "v2c-vac", "5w",
    }


def test_seven_audit_types():
    # maau 复用 mvl，去重后 7 种。
    assert set(reg.audit_types()) == {
        "mvl", "gc", "hmw", "persona", "journey", "v2c-vac", "5w",
    }
    assert len(reg.audit_types()) == 7


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
    for cid in ("maau", "gc", "hmw", "persona", "journey", "v2c-vac", "5w"):
        assert reg.by_id(cid).is_instance_map is True


def test_validate_clean():
    assert reg.validate() == []
