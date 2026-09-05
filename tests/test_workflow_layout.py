# -*- coding: utf-8 -*-
"""Workflow 确定性布局器测试（阶段 0/1 基线）。

覆盖设计 §3.2 / §3.5：
- 每个真实/合成 fixture 的几何自检 0 问题（不重叠 / 正交 / 不穿节点 / 端点中点）；
- 确定性：相同输入两次布局坐标一致；
- 宽度预算（A3 打印可读，§3.3 整页宽度约束）；
- 边集合完整性：布局器为每条输入边产出路径（节点/边全集不丢，Q3 几何降级语义）。
"""
import json
import pathlib
import sys

sys.path.insert(
    0,
    str(pathlib.Path(__file__).resolve().parents[1] / "skills" / "canvas-render" / "scripts"),
)

from workflow_layout import workflow_layout as wl  # noqa: E402
from workflow_layout.workflow_layout import layout_of  # noqa: E402

FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures" / "workflow_layout"
MAX_PAGE_W = 1400.0  # 屏幕/打印宽度预算（§3.3）


def _cases():
    out = []
    for fn in sorted(FIXTURES.glob("workflow_*.json")):
        data = json.loads(fn.read_text(encoding="utf-8"))
        out.append((fn.name, data))
    return out


def test_all_fixtures_geometrically_clean():
    for name, data in _cases():
        lay = layout_of(data)
        problems = lay.selfcheck()
        assert not problems, f"{name} 几何自检失败: {problems[:10]}"


def test_all_edges_rendered_and_budget():
    for name, data in _cases():
        lay = layout_of(data)
        assert len(lay.paths) == len(data.get("edges", [])), \
            f"{name}: 布局边数 {len(lay.paths)} != 输入边数 {len(data.get('edges', []))}"
        x0, _y0, x1, _y1 = lay.bounds()
        assert (x1 - x0) <= MAX_PAGE_W, f"{name}: 全图宽 {x1 - x0:.0f} 超出预算 {MAX_PAGE_W}"


def test_layout_is_deterministic():
    for name, data in _cases():
        a = layout_of(data)
        b = layout_of(data)
        ga = [(i.id, i.x, i.y, i.w, i.h) for i in a.items.values()]
        gb = [(i.id, i.x, i.y, i.w, i.h) for i in b.items.values()]
        assert ga == gb, f"{name}: 布局不确定（两次运行坐标不一致）"


def test_old_schema_regression_not_crash():
    """无 tracks 旧 schema 仅作鲁棒性输入：不崩溃、仍产出 0 问题几何。"""
    fn = FIXTURES / "workflow_hotel_revenue_old.json"
    data = json.loads(fn.read_text(encoding="utf-8"))
    lay = layout_of(data)
    assert not lay.selfcheck()


def test_layout_override_affects_geometry():
    """L1 override：几何常量生效且不改变节点全集。"""
    data = json.loads((FIXTURES / "workflow_hotel_revenue_new.json").read_text(encoding="utf-8"))
    base = layout_of(data)
    compact = layout_of(data, wl.resolve_override(preset="compact"))
    assert sorted(i.id for i in base.items.values()) == sorted(i.id for i in compact.items.values())
    # compact 收紧行距 → 图高变小或至少非全等
    assert compact.page_w() <= base.page_w() + 1e-6
    assert not compact.selfcheck()
    # 显式 override：row_h 更大 → 高度变化
    wide = layout_of(data, wl.resolve_override(override_json={"row_h": 140.0}))
    y0b = base.bounds()[1]
    y0w = wide.bounds()[1]
    assert abs(y0w - y0b) > 20.0 or wide.bounds()[3] != base.bounds()[3]


def test_override_unknown_keys_ignored():
    override = wl.resolve_override(override_json={"row_h": 90.0, "not_a_key": 1})
    assert "not_a_key" not in override
    assert override["row_h"] == 90.0


def test_example_override_file_parses():
    ex = json.loads((pathlib.Path(wl.__file__).parent / "layout_override.example.json")
                    .read_text(encoding="utf-8"))
    data = json.loads((FIXTURES / "workflow_hotel_revenue_new.json").read_text(encoding="utf-8"))
    lay = layout_of(data, wl.resolve_override(override_json=ex))
    assert not lay.selfcheck()


def test_version_and_layout_trace():
    """L2 溯源：版本号合法，layout_trace 输出稳定结构。"""
    v = wl.__version__
    assert v.count(".") == 2 and all(p.isdigit() for p in v.split("."))
    assert wl.layout_trace() == {"engine": "workflow_layout", "baseline_version": v}
    assert wl.layout_trace("fork-01")["fork_id"] == "fork-01"
