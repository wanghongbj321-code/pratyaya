# -*- coding: utf-8 -*-
"""Workflow 确定性布局器测试（阶段 0/1 基线 + 实施审查修复项回归）。

覆盖设计 §3.2 / §3.5：
- 每个真实/合成 fixture 的几何自检 0 问题（不重叠 / 正交 / 不穿节点 / 端点中点 /
  dashed 走 gutter / track 归属 / 边全集不丢）；
- 确定性：相同输入两次布局坐标一致；
- 宽度预算（A3 打印可读，§3.3 整页宽度约束）；
- 边集合完整性：布局器为每条输入边产出路径（节点/边全集不丢，Q3 几何降级语义）；
- 审查修复回归：CLI `--override` 不误收拓扑（P1-1）/ 自检 FAIL exit 1（P1-2）/
  输入不合法 exit 2 与 validate（P1-4）/ 折行上限（P2-4）/ 轨道标签（P2-5）。
"""
import json
import multiprocessing as mp
import pathlib
import queue
import subprocess
import sys

import pytest

sys.path.insert(
    0,
    str(pathlib.Path(__file__).resolve().parents[1] / "skills" / "canvas-render" / "scripts"),
)

from workflow_layout import workflow_layout as wl  # noqa: E402
from workflow_layout.workflow_layout import layout_of  # noqa: E402

FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures" / "workflow_layout"
WL_PY = pathlib.Path(wl.__file__).resolve()
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


# ---- 实施审查修复回归（P1/P2）----

def _run_cli(*args):
    return subprocess.run(
        [sys.executable, str(WL_PY), *args],
        capture_output=True,
        text=True,
        cwd=str(FIXTURES.parents[2]),
    )


def _wrap_lines_worker(text, max_w, max_lines, out):
    try:
        out.put(("ok", wl.wrap_lines(text, max_w, max_lines=max_lines)))
    except BaseException as exc:  # pragma: no cover - 仅用于跨进程回传诊断
        out.put(("err", repr(exc)))


def _wrap_lines_with_timeout(text, max_w, max_lines, timeout=2.0):
    """避免 wrap_lines 回归为死循环时拖挂整份测试文件。"""
    ctx = mp.get_context("spawn")
    out = ctx.Queue()
    proc = ctx.Process(target=_wrap_lines_worker, args=(text, max_w, max_lines, out))
    proc.start()
    proc.join(timeout)
    if proc.is_alive():
        proc.terminate()
        proc.join()
        pytest.fail(f"wrap_lines(text, {max_w}, max_lines={max_lines}) 超时，疑似死循环")
    if proc.exitcode != 0:
        pytest.fail(f"wrap_lines 子进程异常退出: exitcode={proc.exitcode}")
    try:
        status, payload = out.get_nowait()
    except queue.Empty:
        pytest.fail("wrap_lines 子进程未返回结果")
    if status == "err":
        pytest.fail(f"wrap_lines 抛出异常: {payload}")
    return payload


def test_cli_override_file_not_treated_as_topology():
    """P1-1：--override <file.json> 取值不得被误收为拓扑输入（schema.md 示范用法）。"""
    topo = FIXTURES / "workflow_hotel_revenue_new.json"
    ex = pathlib.Path(wl.__file__).parent / "layout_override.example.json"
    res = _run_cli(str(topo), "--override", str(ex))
    assert res.returncode == 0, f"rc={res.returncode}\nstdout={res.stdout}\nstderr={res.stderr}"
    assert "layout_override 生效" in res.stdout
    assert "Traceback" not in res.stderr and "KeyError" not in res.stderr
    assert "== 坐标表" in res.stdout


def test_cli_geometry_failure_exits_nonzero():
    """P1-2：几何自检 FAIL → exit 1，且不写 --svg 产物（门禁可编程化）。"""
    topo = FIXTURES / "workflow_hotel_revenue_new.json"
    # row_h=10 远小于卡高 58 → 相邻行重叠 → 自检 FAIL
    res = _run_cli(str(topo), "--override-json", '{"row_h": 10}', "--svg", "/tmp/wl_bad_out")
    assert res.returncode == 1, f"rc={res.returncode}\nstdout={res.stdout}"
    assert "自检 FAIL" in res.stdout


def test_cli_invalid_input_exits_2():
    """P1-4：输入不满足 §A1.5 正式 schema → exit 2 并列出错误。"""
    bad = {"nodes": [{"id": "w0", "type": "start", "label": "x"}]}
    p = pathlib.Path("/tmp/wl_bad_schema.json")
    p.write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
    try:
        res = _run_cli(str(p))
        assert res.returncode == 2, f"rc={res.returncode}\nstdout={res.stdout}"
        assert "输入不合法" in res.stdout
        assert "tracks" in res.stdout and "actor" not in res.stdout or "缺少 track" in res.stdout
    finally:
        p.unlink(missing_ok=True)


def test_validate_rejects_incomplete_schema():
    """P1-4：validate 对 tracks 缺失 / track 悬空 / actor 非法 / edge 悬空逐项报错。"""
    data = json.loads((FIXTURES / "workflow_hotel_revenue_new.json").read_text(encoding="utf-8"))
    assert wl.validate(data) == []
    no_tracks = {"nodes": data["nodes"]}
    errs = wl.validate(no_tracks)
    assert any("tracks" in e for e in errs)
    bad_actor = json.loads(json.dumps(data))
    bad_actor["nodes"][1]["actor"] = "humanoid"
    assert any("actor" in e for e in wl.validate(bad_actor))
    bad_edge = json.loads(json.dumps(data))
    bad_edge["edges"][0]["to"] = "nope"
    assert any("引用不存在" in e for e in wl.validate(bad_edge))
    dup = json.loads(json.dumps(data))
    dup["edges"].append({"from": dup["edges"][0]["from"], "to": dup["edges"][0]["to"]})
    assert any("重复同向边" in e for e in wl.validate(dup))


def test_selfcheck_covers_dashed_and_midpoints():
    """P2-1：自检含 dashed 走 gutter / 端点中点 / 边全集断言，fixture 全 0。"""
    data = json.loads((FIXTURES / "workflow_suozhang_three_track.json").read_text(encoding="utf-8"))
    lay = layout_of(data)
    assert not lay.selfcheck()
    for key, kind in lay.path_kind.items():
        if key in lay._dashed_keys:
            assert kind == "gutter", f"dashed {key} 应走 gutter，实际 {kind}"
    assert len(lay.paths) == len(data["edges"])


def test_dashed_reflow_forced_to_gutter():
    """P2-1：同轨 dashed 回流也强制走 gutter（不混主线流 direct）。"""
    data = json.loads((FIXTURES / "workflow_hotel_revenue_new.json").read_text(encoding="utf-8"))
    # 构造一条同轨 dashed 回流 w4 -> w1（跨节点、同轨）
    data["edges"].append({"from": "w4", "to": "w1", "label": "反馈", "dashed": True})
    lay = layout_of(data)
    assert not lay.selfcheck(), lay.selfcheck()
    assert lay.path_kind[("w4", "w1")] == "gutter"


def test_wrap_lines_max_lines():
    """P2-4：折行带行数上限（≤3 行），超限末行省略号截断。"""
    text = "超长标签" * 30
    lines = _wrap_lines_with_timeout(text, 150, max_lines=3)
    assert wl.wrap_lines(text, 150) != lines
    assert len(lines) <= 3
    assert lines[-1].endswith("…")


def test_track_labels_rendered():
    """P2-5：--svg 预览含轨道标签（轨道 id + label）。"""
    data = json.loads((FIXTURES / "workflow_suozhang_three_track.json").read_text(encoding="utf-8"))
    lay = layout_of(data)
    svg = wl.svg_preview(lay, data)
    assert "[A] 数据采集与自动化流水线" in svg
    assert "[B] 人机协作对话层" in svg
    assert "[C] 学习闭环" in svg
    assert "stroke-dasharray" in svg  # dashed 边以虚线呈现
