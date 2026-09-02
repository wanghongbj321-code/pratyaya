"""跨模块 caveat 浮现与对齐总检数据收集测试（§8）。"""

from skills._engine import reconcile


def _state():
    return {
        "modules": {
            "M1": {"status": "rendered", "confirmation_mode": "gate_pass"},
            "M2": {"status": "rendered", "confirmation_mode": "override"},
        },
        "maau": {"s1": {"status": "rendered", "confirmation_mode": "gate_pass"}},
        "golden_circle": {"g1": {"status": "confirmed", "confirmation_mode": "gate_pass"}},
    }


def test_collect_all_instances():
    keys = [f"{i['root']}.{i['key']}" for i in reconcile.collect_all_instances(_state())]
    assert "modules.M1" in keys
    assert "modules.M2" in keys
    assert "maau.s1" in keys
    assert "golden_circle.g1" in keys


def test_collect_override_caveats():
    keys = [f"{c['root']}.{c['key']}" for c in reconcile.collect_override_caveats(_state())]
    assert keys == ["modules.M2"]


def test_has_override():
    assert reconcile.has_override(_state()) is True
    assert reconcile.has_override({"modules": {"M1": {"confirmation_mode": "gate_pass"}}}) is False


def test_all_rendered():
    assert reconcile.all_rendered(_state()) is False  # g1 为 confirmed
    assert reconcile.all_rendered({"modules": {"M1": {"status": "rendered"}}}) is True
    assert reconcile.all_rendered({}) is False


def test_render_status_summary():
    summary = reconcile.render_status_summary(_state())
    assert summary["all_rendered"] is False
    assert "golden_circle.g1" in summary["unrendered"]
    assert summary["counts"]["rendered"] == 3
