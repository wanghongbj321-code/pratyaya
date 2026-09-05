# -*- coding: utf-8 -*-
"""Workflow 0.2.0: deterministic geometry and final SVG internals.
--svg retains geometric HTML preview; --fragment output.svg emits final SVG.
HTML wrappers, legend and completion conditions belong to canvas-render.
Exit 0: geometry PASS; 1: geometry FAIL; 2: invalid input/arguments.
"""
import json
import math
import os
import sys

_Version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "VERSION")
__version__ = open(_Version_file, encoding="utf-8").read().strip()

# ---- 几何常量默认值（§3.3；可被 layout_override 覆盖，见 LAYOUT_OVERRIDE_KEYS）----
DEFAULT = {
    "card_h": 58.0,
    "card_w_min": 150.0,
    "card_w_max": 260.0,
    "row_h": 96.0,            # 轨道内行中心距
    "track_gap": 60.0,        # 相邻轨道带间距
    "track_pad_top": 44.0,    # 轨道标签行高（首行起始）
    "margin_x": 60.0,
    "gutter_w": 70.0,         # 左 gutter 走廊宽（跨轨 / 回流绕行）
    "max_per_row": 6,
    "max_page_w": 1400.0,     # 整页宽度预算（A3 打印可读）
}
# 可配置项白名单（其余键忽略并告警）：本清单同时是 L1 对照清单的事实源
LAYOUT_OVERRIDE_KEYS = tuple(DEFAULT.keys())
COMPACT_PRESETS = {
    "compact": {"row_h": 84.0, "track_gap": 44.0, "margin_x": 48.0,
                "gutter_w": 60.0, "card_w_max": 230.0},
    "roomy": {"row_h": 110.0, "track_gap": 80.0, "margin_x": 76.0,
              "gutter_w": 86.0, "card_w_max": 300.0},
}

COL_CHAR_W_CJK = 9.0
COL_CHAR_W_LATIN = 5.6
NODE_PAD_X = 30.0
EVENT_TYPES = {"start", "end", "timer", "message"}
TASK_TYPES = {"agent_execution", "human_operation", "human_review"}
VALID_TYPES = EVENT_TYPES | TASK_TYPES | {"gateway", "data_store"}
ACTORS = {"human", "ai", "system", "hybrid", "reviewer"}


def text_width(s):
    return sum(COL_CHAR_W_CJK if ord(ch) > 0x2E7F else COL_CHAR_W_LATIN for ch in s)


def wrap_lines(s, max_w, max_lines=None):
    """按最大宽折行；max_lines 给定时超限行以省略号截断（P2-4：防溢出卡片/圆）。"""
    lines, cur = [], ""
    for ch in s:
        if text_width(cur + ch) <= max_w:
            cur += ch
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    if not lines:
        lines = [""]
    if max_lines is not None and len(lines) > max_lines:
        keep = lines[:max_lines]
        ell = "…"
        while keep[-1] and text_width(keep[-1] + ell) > max_w:
            keep[-1] = keep[-1][:-1]
        if keep:
            keep[-1] += ell
        lines = keep
    return lines or [""]


class Item:
    __slots__ = ("id", "type", "track", "x", "y", "w", "h", "order")

    def __init__(self, node, order, w, h):
        self.id = node["id"]
        self.type = node.get("type", "agent_execution")
        self.track = node.get("track") or "main"
        self.order = order
        self.w, self.h = w, h
        self.x = self.y = 0.0

    @property
    def cx(self):
        return self.x + self.w / 2

    @property
    def cy(self):
        return self.y + self.h / 2

    def rect(self):
        return (self.x, self.y, self.x + self.w, self.y + self.h)


class Layout:
    def __init__(self, data, override=None):
        self.data = data
        cfg = dict(DEFAULT)
        if override:
            for k in LAYOUT_OVERRIDE_KEYS:
                if k in override:
                    cfg[k] = float(override[k]) if k != "max_per_row" else int(override[k])
        self.cfg = cfg
        tracks = data.get("tracks", [])
        self.tracks = [t["id"] for t in tracks] or ["main"]
        self.track_labels = {t.get("id"): t.get("label", "") for t in tracks if isinstance(t, dict)}
        self.items = {}
        for i, n in enumerate(data["nodes"]):
            self.items[n["id"]] = Item(n, i, *self._node_dims(n))
        self.edges = data.get("edges", [])
        # dashed 边集合（(from_id, to_id) 键，供路由分流与自检断言）
        self._dashed_keys = set()
        for e in self.edges:
            if isinstance(e, dict) and e.get("dashed"):
                self._dashed_keys.add((e["from"], e["to"]))
        self.paths = {}
        self.path_kind = {}   # (u_id, v_id) -> "direct" | "gutter"
        self.track_y0 = {}    # 轨道 id -> 首行节点 y（供轨道标签/报告）
        self.issues = []

    # ---- 节点尺寸（受 override 影响）----
    def _node_dims(self, node):
        t = node.get("type", "agent_execution")
        cw_min, cw_max, ch = self.cfg["card_w_min"], self.cfg["card_w_max"], self.cfg["card_h"]
        if t in EVENT_TYPES:
            d = 56.0 if t == "end" else 46.0
            return d, d
        if t == "gateway":
            return max(160.0, min(cw_max + 40.0, text_width(node["label"]) + NODE_PAD_X)), 76.0
        if t == "data_store":
            return max(240.0, min(340.0, text_width(node["label"]) + 2 * NODE_PAD_X)), 64.0
        return max(cw_min, min(cw_max, text_width(node["label"]) + NODE_PAD_X)), ch

    # ---- 阶段 A：每轨内节点横排（蛇形折返多行）----
    def place(self):
        cfg = self.cfg
        by_track = {}
        for it in self.items.values():
            by_track.setdefault(it.track, []).append(it)
        for group in by_track.values():
            group.sort(key=lambda it: it.order)
        y = cfg["track_pad_top"]
        for tid in self.tracks:
            group = by_track.get(tid, [])
            if group:
                self.track_y0[tid] = y
            mpr = cfg["max_per_row"]
            rows = max(1, (len(group) + mpr - 1) // mpr)
            per = max(1, -(-len(group) // rows))
            for r in range(rows):
                seg = group[r * per:(r + 1) * per]
                seq = seg if r % 2 == 0 else list(reversed(seg))
                cx = cfg["margin_x"]
                for it in seq:
                    it.x = cx
                    it.y = y + r * cfg["row_h"]
                    cx += it.w + 24.0
            y += rows * cfg["row_h"] + cfg["track_gap"]
        return self

    # ---- 阶段 B：路由（可直连短肘 / gutter 空隙通道）----
    @staticmethod
    def _y_overlap(a, b):
        return not (a.y + a.h <= b.y or b.y + b.h <= a.y)

    def route(self):
        rects = [(it.id, it.rect()) for it in self.items.values()]
        for e in self.edges:
            u, v = self.items[e["from"]], self.items[e["to"]]
            key = (u.id, v.id)
            if key in self._dashed_keys:
                # dashed 回流/反馈一律走 gutter 走廊（§3.2 step6），不与主线流混行
                self.paths[key] = self._gutter(u, v)
                self.path_kind[key] = "gutter"
            elif self._direct_ok(u, v, rects):
                if abs(u.cy - v.cy) < 1e-6:
                    pts = [(u.x + u.w, u.cy), (v.x, v.cy)]
                else:
                    pts = [(u.x + u.w, u.cy), (v.x, u.cy), (v.x, v.cy)]
                self.paths[key] = pts
                self.path_kind[key] = "direct"
            else:
                self.paths[key] = self._gutter(u, v)
                self.path_kind[key] = "gutter"

    def _direct_ok(self, u, v, rects):
        if u.track != v.track:
            return False
        if u.x + u.w > v.x + 1e-6:
            return False
        if not self._y_overlap(u, v):
            return False
        seg_y0 = min(u.y, v.y)
        seg_y1 = max(u.y + u.h, v.y + v.h)
        for nid, rect in rects:
            if nid in (u.id, v.id):
                continue
            if rect[0] < v.x and rect[2] > u.x + u.w and rect[1] < seg_y1 and rect[3] > seg_y0:
                return False
        return True

    def _gutter(self, u, v):
        L_gut = self.cfg["margin_x"] - self.cfg["gutter_w"]
        rh = self.cfg["row_h"]
        bot_gap = u.y + u.h + min(19.0, rh / 2 - u.h / 2)
        top_air = v.y - max(19.0, (rh - v.h) / 2)
        if top_air < 0:
            top_air = 10.0
        x0 = u.cx
        return [(x0, u.y + u.h), (x0, bot_gap), (L_gut, bot_gap),
                (L_gut, top_air), (v.cx, top_air), (v.cx, v.y)]

    # ---- 阶段 C：几何自检 ----
    @staticmethod
    def _seg_hit(rect, a, b):
        x0, y0, x1, y1 = rect
        if a[0] == b[0]:
            x = a[0]
            if x <= x0 or x >= x1:
                return False
            lo, hi = sorted((a[1], b[1]))
            return lo < y1 and hi > y0
        if a[1] == b[1]:
            y = a[1]
            if y <= y0 or y >= y1:
                return False
            lo, hi = sorted((a[0], b[0]))
            return lo < x1 and hi > x0
        return False

    @staticmethod
    def _midpoints(it):
        return [(it.x + it.w / 2, it.y), (it.x + it.w / 2, it.y + it.h),
                (it.x, it.cy), (it.x + it.w, it.cy)]

    def selfcheck(self):
        probs = []
        rects = [(it.id, it.rect()) for it in self.items.values()]
        # 1. 节点矩形两两不重叠
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                a, ra = rects[i]
                b, rb = rects[j]
                if ra[0] < rb[2] and rb[0] < ra[2] and ra[1] < rb[3] and rb[1] < ra[3]:
                    probs.append(f"节点重叠 {a}∩{b}")
        # 2. 轨道归属合法（nodes[].track 必须 ∈ tracks，tracks 一致性）
        for it in self.items.values():
            if it.track not in self.tracks:
                probs.append(f"节点 {it.id} track={it.track!r} 不在 tracks {self.tracks} 内")
        # 3. 边全集不丢：每条输入边都产出了路径（含 dashed）
        if len(self.paths) != len(self.edges):
            probs.append(f"路径数 {len(self.paths)} != 输入边数 {len(self.edges)}（存在未渲染/重复 from→to 的边）")
        # 4. 路径断言：正交 / 不穿节点 / 端点落边界中点 / dashed 走 gutter
        for (u, v), pts in self.paths.items():
            su, sv = self.items[u], self.items[v]
            eps = 1e-6
            if not any(abs(pts[0][0] - mx) < eps and abs(pts[0][1] - my) < eps
                       for mx, my in self._midpoints(su)):
                probs.append(f"连线 {u}->{v} 起点 {pts[0]} 不落源节点边界中点")
            if not any(abs(pts[-1][0] - mx) < eps and abs(pts[-1][1] - my) < eps
                       for mx, my in self._midpoints(sv)):
                probs.append(f"连线 {u}->{v} 终点 {pts[-1]} 不落目标节点边界中点")
            if (u, v) in self._dashed_keys and self.path_kind.get((u, v)) != "gutter":
                probs.append(f"dashed 回流边 {u}->{v} 未走 gutter 通道（kind={self.path_kind.get((u, v))}）")
            for k in range(len(pts) - 1):
                a, b = pts[k], pts[k + 1]
                if not (a[0] == b[0] or a[1] == b[1]):
                    probs.append(f"非正交段 {u}->{v}")
                for nid, rect in rects:
                    if nid in (u, v):
                        continue
                    if self._seg_hit(rect, a, b):
                        probs.append(f"连线 {u}->{v} 穿节点 {nid} @ seg {a}->{b}")
                        break
        return probs

    def bounds(self):
        if not self.items:
            return 0.0, 0.0, 0.0, 0.0
        gw = self.cfg["gutter_w"]
        xs0 = min(it.x for it in self.items.values())
        xs1 = max(it.x + it.w for it in self.items.values())
        ys0 = min(it.y for it in self.items.values())
        ys1 = max(it.y + it.h for it in self.items.values())
        return xs0 - gw - 12, ys0 - 60, xs1 + gw, ys1 + 40

    def page_w(self):
        x0, _y0, x1, _y1 = self.bounds()
        return x1 - x0


def validate(data):
    """正式输入契约校验（§3.1，P1-4）：返回错误清单，空列表 = 合法。

    正式输入仅接受 §A1.5 新 schema：tracks 非空、nodes 非空、nodes[].track 必填
    且 ∈ tracks[].id、任务类节点 actor 必填合法、type ∈ 合法集、edges.from/to 引用
    存在且无重复同向边。缺 tracks/actor 的旧 schema 数据不属于正式输入（仅测试/回归用）。
    """
    errs = []
    if not isinstance(data, dict):
        return ["workflow 拓扑必须是 JSON 对象"]
    nodes = data.get("nodes")
    edges = data.get("edges", [])
    tracks = data.get("tracks")
    if not isinstance(nodes, list) or not nodes:
        errs.append("nodes 必须是非空数组")
    if not isinstance(tracks, list) or not tracks:
        errs.append("tracks 必须是非空数组（§A1.5 正式输入要求）")
    if not isinstance(edges, list):
        errs.append("edges 必须是数组")
    track_ids = []
    if isinstance(tracks, list):
        for t in tracks:
            if not isinstance(t, dict) or not t.get("id"):
                errs.append("tracks 元素必须是含 id 的对象")
            elif t["id"] in track_ids:
                errs.append(f"tracks 存在重复 id: {t['id']!r}")
            else:
                track_ids.append(t["id"])
    ids = []
    if isinstance(nodes, list):
        seen = {}
        for n in nodes:
            if not isinstance(n, dict):
                errs.append("nodes 元素必须是对象")
                continue
            nid = n.get("id")
            if not nid:
                errs.append(f"nodes 元素缺 id: {n!r}")
                continue
            if nid in seen:
                errs.append(f"nodes 存在重复 id: {nid!r}")
            seen[nid] = True
            ids.append(nid)
            ntype = n.get("type")
            if ntype not in VALID_TYPES:
                errs.append(f"node {nid!r} type={ntype!r} 不在合法集 {sorted(VALID_TYPES)}")
            track = n.get("track")
            if not track:
                errs.append(f"node {nid!r} 缺少 track 字段（正式输入要求）")
            elif track_ids and track not in track_ids:
                errs.append(f"node {nid!r} track={track!r} 不在 tracks {track_ids} 内")
            if ntype in TASK_TYPES:
                actor = n.get("actor")
                if actor not in ACTORS:
                    errs.append(f"node {nid!r} actor={actor!r} 必须 ∈ {sorted(ACTORS)}")
    if isinstance(edges, list) and edges:
        seen_edges = set()
        for e in edges:
            if not isinstance(e, dict):
                errs.append("edges 元素必须是对象")
                continue
            ef, et = e.get("from"), e.get("to")
            if ef not in ids:
                errs.append(f"edge from={ef!r} 引用不存在的 node")
            if et not in ids:
                errs.append(f"edge to={et!r} 引用不存在的 node")
            key = (ef, et)
            if key in seen_edges:
                errs.append(f"edges 存在重复同向边 {ef}->{et}")
            seen_edges.add(key)
    return errs


def layout_of(data, override=None):
    L = Layout(data, override)
    L.place().route()
    return L


def resolve_override(override_json=None, preset=None):
    """合并 preset + 显式 override；返回 override dict 或 None。"""
    merged = {}
    if preset:
        if preset not in COMPACT_PRESETS:
            raise ValueError(f"未知 preset: {preset}（可选 {sorted(COMPACT_PRESETS)}）")
        merged.update(COMPACT_PRESETS[preset])
    if override_json is not None:
        if not isinstance(override_json, dict):
            raise ValueError("layout_override must be an object")
        merged.update(override_json)
    unknown = [k for k in merged if k not in LAYOUT_OVERRIDE_KEYS]
    if unknown:
        print("警告：忽略未知 layout_override 键:", unknown)
        merged = {k: v for k, v in merged.items() if k in LAYOUT_OVERRIDE_KEYS}
    for key, value in merged.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError(f"layout_override {key} must be positive and finite")
        if key == "max_per_row" and int(value) != value:
            raise ValueError("max_per_row must be an integer")
    return merged or None


def _esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def svg_preview(L, data, title=""):
    """目检预览页（几何层产物，非 §A1 最终 DOM；装配在渲染回合/注入器侧）。"""
    x0, y0, x1, y1 = L.bounds()
    W, H = x1 - x0, y1 - y0
    labels = {n["id"]: n["label"] for n in data["nodes"]}
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.0f} {y0:.0f} {W:.0f} {H:.0f}" font-family="Helvetica,Arial,sans-serif">']
    out.append('<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#000"/></marker></defs>')
    # 轨道标签（P2-5：与母版轨道带观感同构；几何层仅占位，正式样式在装配侧）
    for tid in L.tracks:
        lab = L.track_labels.get(tid, tid)
        ty = L.track_y0.get(tid)
        if ty is None:
            continue
        out.append(f'<text x="{x0 + 10:.0f}" y="{ty - 24:.0f}" font-size="12" font-weight="bold" fill="#333">[{_esc(tid)}] {_esc(lab)}</text>')
    for it in L.items.values():
        x, y, w, h = it.x, it.y, it.w, it.h
        cx, cy = it.cx, it.cy
        label = labels.get(it.id, "")
        if it.type in EVENT_TYPES:
            out.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{w/2:.0f}" fill="#fff" stroke="#000" stroke-width="1.6"/>')
            for i, ln in enumerate(wrap_lines(label, max(40.0, w * 1.3), max_lines=2)):
                out.append(f'<text x="{cx:.0f}" y="{cy + (i - 0.4) * 11:.0f}" text-anchor="middle" font-size="8.5">{_esc(ln)}</text>')
        elif it.type == "gateway":
            out.append(f'<polygon points="{cx:.0f},{y:.0f} {x+w:.0f},{cy:.0f} {cx:.0f},{y+h:.0f} {x:.0f},{cy:.0f}" fill="#fff" stroke="#000" stroke-width="1.8"/>')
            for i, ln in enumerate(wrap_lines(label, w - 16, max_lines=3)):
                out.append(f'<text x="{cx:.0f}" y="{cy + (i - 0.3) * 11:.0f}" text-anchor="middle" font-size="9">{_esc(ln)}</text>')
        elif it.type == "data_store":
            out.append(f'<rect x="{x:.0f}" y="{y+8:.0f}" width="{w:.0f}" height="{h-8:.0f}" rx="6" fill="#fff" stroke="#000" stroke-width="2"/>')
            for i, ln in enumerate(wrap_lines(label, w - 16, max_lines=3)):
                out.append(f'<text x="{cx:.0f}" y="{cy + (i - 0.2) * 12:.0f}" text-anchor="middle" font-size="10">{_esc(ln)}</text>')
        else:
            out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="8" fill="#fff" stroke="#000" stroke-width="1.5"/>')
            lines = wrap_lines(label, w - 12, max_lines=3)
            for i, ln in enumerate(lines):
                out.append(f'<text x="{cx:.0f}" y="{cy + (i - (len(lines) - 1) / 2) * 13:.0f}" text-anchor="middle" font-size="10">{_esc(ln)}</text>')
    for (u, v), pts in L.paths.items():
        d = "M" + " ".join(f"{p[0]:.1f} {p[1]:.1f}" for p in pts)
        dash = ' stroke-dasharray="6,4"' if (u, v) in L._dashed_keys else ""
        out.append(f'<path d="{d}" fill="none" stroke="#000" stroke-width="1.5" marker-end="url(#arr)"{dash}/>')
    out.append('</svg>')
    return "".join(out)


def validate_fragment(data):
    """Final SVG needs the labels and reading numbers of §A1.5."""
    if not isinstance(data, dict) or not isinstance(data.get("nodes"), list):
        return ["fragment requires nodes"]
    errors, numbers = [], []
    for node in data["nodes"]:
        if not isinstance(node, dict):
            continue
        if not isinstance(node.get("label"), str) or not node.get("label"):
            errors.append("fragment node requires nonempty label")
        number = node.get("number")
        if not isinstance(number, (str, int)) or isinstance(number, bool) or not str(number):
            errors.append("fragment node requires number")
        numbers.append(str(number))
        if "note" in node and not isinstance(node["note"], str):
            errors.append("fragment note must be text")
    if len(numbers) != len(set(numbers)):
        errors.append("fragment node numbers must be unique")
    return errors


def svg_fragment(L, data):
    """Emit only SVG; every coordinate comes from the checked layout."""
    errors = validate(data) + validate_fragment(data) + L.selfcheck()
    if errors:
        raise ValueError("; ".join(errors))
    x0, y0, x1, y1 = L.bounds()
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" class="bpmn-flow" role="img" aria-label="Workflow BPMN 流程图" viewBox="{x0:g} {y0:g} {x1-x0:g} {y1-y0:g}">']
    out.append('<defs>')
    for marker in ("flow-arrow", "flow-arrow-dash"):
        out.append(f'<marker id="{marker}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path class="bpmn-arrow" d="M0 0 L10 5 L0 10 Z"/></marker>')
    out.append('</defs>')
    for tid in L.tracks:
        ty = L.track_y0.get(tid, y0 + 40)
        out.append(f'<g class="bpmn-track" data-track="{_esc(tid)}"><text class="bpmn-track-label" x="{L.cfg["margin_x"]:g}" y="{ty-24:g}">{_esc(L.track_labels.get(tid, tid))}</text></g>')
    for e in data["edges"]:
        pts = L.paths[(e["from"], e["to"])]
        d = f'M{pts[0][0]:g} {pts[0][1]:g}'
        for a, b in zip(pts, pts[1:]):
            d += f' H{b[0]:g}' if a[1] == b[1] else f' V{b[1]:g}'
        dashed = e.get("dashed") is True
        cls = "bpmn-sequence bpmn-reflow" if dashed else "bpmn-sequence"
        marker = "flow-arrow-dash" if dashed else "flow-arrow"
        out.append(f'<path class="{cls}" data-from="{_esc(e["from"])}" data-to="{_esc(e["to"])}" d="{d}" marker-end="url(#{marker})"><title>{_esc(e.get("label", ""))}</title></path>')
        if e.get("label"):
            a, b = max(zip(pts, pts[1:]), key=lambda ab: abs(ab[0][0]-ab[1][0])+abs(ab[0][1]-ab[1][1]))
            out.append(f'<text class="bpmn-flow-label" x="{(a[0]+b[0])/2:g}" y="{(a[1]+b[1])/2-5:g}" text-anchor="middle">{_esc(e["label"])}</text>')
    for node in data["nodes"]:
        it = L.items[node["id"]]
        x, y, w, h, cx, cy = it.x, it.y, it.w, it.h, it.cx, it.cy
        out.append(f'<g class="bpmn-node" data-node-type="{it.type}" data-node-id="{_esc(it.id)}" data-track="{_esc(it.track)}">')
        out.append(f'<title>{_esc(node["label"] + (" — " + node["note"] if node.get("note") else ""))}</title>')
        if it.type in EVENT_TYPES:
            out.append(f'<circle class="bpmn-event" cx="{cx:g}" cy="{cy:g}" r="{w/2:g}"/>')
            if it.type == "end":
                out.append(f'<circle class="bpmn-event" cx="{cx:g}" cy="{cy:g}" r="{w/2-4:g}"/>')
            if it.type in {"timer", "message"}:
                symbol = "◷" if it.type == "timer" else "✉"
                out.append(f'<text class="bpmn-symbol" x="{cx:g}" y="{y+14:g}" text-anchor="middle">{symbol}</text>')
        elif it.type == "data_store":
            out.append(f'<rect class="bpmn-task" x="{x:g}" y="{y+8:g}" width="{w:g}" height="{h-16:g}"/>')
            out.append(f'<ellipse class="bpmn-task" cx="{cx:g}" cy="{y+h-8:g}" rx="{w/2:g}" ry="8"/>')
            out.append(f'<ellipse class="bpmn-task" cx="{cx:g}" cy="{y+8:g}" rx="{w/2:g}" ry="8"/>')
        elif it.type == "gateway":
            out.append(f'<polygon class="bpmn-gateway" points="{cx:g},{y:g} {x+w:g},{cy:g} {cx:g},{y+h:g} {x:g},{cy:g}"/>')
        else:
            out.append(f'<rect class="bpmn-task" x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="6"/>')
        out.append(f'<g class="bpmn-number"><rect x="{x:g}" y="{y:g}" width="24" height="14" rx="3"/><text x="{x+12:g}" y="{y+10:g}" text-anchor="middle">{_esc(str(node["number"]))}</text></g>')
        if it.type in TASK_TYPES:
            actor = node["actor"]
            actor_label = {"human":"人", "ai":"AI", "system":"系统", "hybrid":"人+AI", "reviewer":"审核"}[actor]
            out.append(f'<g class="bpmn-actor" data-actor="{actor}"><rect x="{x+w-50:g}" y="{y:g}" width="48" height="14" rx="3"/><text x="{x+w-26:g}" y="{y+10:g}" text-anchor="middle">{actor_label}</text></g>')
        # Full label stays accessible in title; visible wrapping fits each shape.
        width = w * (.60 if it.type in EVENT_TYPES or it.type == "gateway" else .90)
        lines = wrap_lines(node["label"], width, max_lines=2)
        for i, line in enumerate(lines):
            out.append(f'<text class="bpmn-label" x="{cx:g}" y="{cy+2+i*11:g}" text-anchor="middle">{_esc(line)}</text>')
        if node.get("note"):
            out.append(f'<text class="note" x="{cx:g}" y="{y+h-3:g}" text-anchor="middle">{_esc(wrap_lines(node["note"], w-12, max_lines=1)[0])}</text>')
        out.append('</g>')
    out.append('</svg>')
    return "\n".join(out)


def layout_trace(fork_id=None):
    """产物溯源字段（写进 `canvas-data.workflow.layout`，可选；不改 schema_version）。
    engine / baseline_version 标识生成该 SVG 的布局器版本；fork_id 仅在 L2 分叉产物存在。"""
    trace = {"engine": "workflow_layout", "baseline_version": __version__}
    if fork_id:
        trace["fork_id"] = fork_id
    return trace


def _parse(argv):
    """CLI 解析（P1-1 修复）：--flag 的取值从 positional 输入中摘除，
    避免 `--override <file.json>` 被误收为拓扑输入。"""
    opts = {"override": None, "override_json": None, "preset": None, "svg": None, "fragment": None}
    files = []
    valued = {"--override", "--override-json", "--preset", "--svg", "--fragment"}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in valued and (i + 1 >= len(argv) or argv[i + 1].startswith("--")):
            raise ValueError(f"missing value for {a}")
        if a in valued and i + 1 < len(argv):
            opts[a[2:].replace("-", "_")] = argv[i + 1]
            i += 2
            continue
        if a.endswith(".json") and not a.startswith("--"):
            files.append(a)
        else:
            raise ValueError(f"unknown argument: {a}")
        i += 1
    return opts, files


def main(argv):
    if "--version" in argv:
        print("workflow_layout", __version__)
        return
    try:
        opts, files = _parse(argv)
        if opts["fragment"] and len(files) != 1:
            raise ValueError("--fragment requires exactly one topology input")
    except ValueError as exc:
        print("错误:", exc)
        sys.exit(2)
    if not files:
        print("用法: workflow_layout.py <topo.json> [more.json] "
              "[--override file.json|--override-json '{...}'] [--preset compact|roomy] [--svg out_dir] [--fragment new.svg]")
        sys.exit(2)
    try:
        override_json = None
        if opts["override"]:
            with open(opts["override"], encoding="utf-8") as f:
                override_json = json.load(f)
        elif opts["override_json"]:
            override_json = json.loads(opts["override_json"])
        override = resolve_override(preset=opts["preset"], override_json=override_json)
    except ValueError as exc:
        print("错误:", exc)
        sys.exit(2)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"错误: layout_override 读取/解析失败: {exc}")
        sys.exit(2)
    if override:
        print("layout_override 生效:", override)
    exit_code = 0
    for fn in files:
        try:
            with open(fn, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"错误: 无法读取/解析 {fn}: {exc}")
            exit_code = max(exit_code, 2)
            continue
        try:
            errs = validate(data)
            if opts["fragment"]:
                errs.extend(validate_fragment(data))
        except (TypeError, ValueError, KeyError) as exc:
            errs = [f"invalid topology: {exc}"]
        if errs:
            print(f"\n== {os.path.basename(fn)} == 输入不合法（{len(errs)} 项）：")
            for e in errs:
                print("  -", e)
            exit_code = max(exit_code, 2)
            continue
        try:
            L = layout_of(data, override)
            probs = L.selfcheck()
        except (TypeError, ValueError, KeyError) as exc:
            print("错误:", exc)
            exit_code = max(exit_code, 2)
            continue
        print(f"\n== {os.path.basename(fn)} ==")
        print(f"nodes={len(L.items)} edges={len(L.edges)} tracks={L.tracks} page_w≈{L.page_w():.0f}")
        # 布局报告：坐标表（§3.1，P2-3）
        print("== 坐标表（node id / type / track / x / y / w / h）==")
        for it in sorted(L.items.values(), key=lambda i: i.order):
            print(f"  {it.id}\t{it.type}\t{it.track}\tx={it.x:.0f}\ty={it.y:.0f}\t"
                  f"w={it.w:.0f}\th={it.h:.0f}")
        print(f"== 边路径（{len(L.paths)} 条，kind: direct/gutter）==")
        for (u, v), pts in L.paths.items():
            kind = L.path_kind.get((u, v))
            tag = "  dashed" if (u, v) in L._dashed_keys else ""
            print(f"  {u}->{v} [{kind}]{tag} " + " ".join(f"{p[0]:.0f},{p[1]:.0f}" for p in pts))
        print("自检问题:", len(probs))
        for p in probs[:25]:
            print("  -", p)
        if probs:
            exit_code = max(exit_code, 1)
            print("  → 自检 FAIL：禁止进入装配，不写 --svg 产物")
            continue
        if opts["fragment"]:
            try:
                fragment = svg_fragment(L, data)
                with open(opts["fragment"], "x", encoding="utf-8") as out:
                    out.write(fragment)
                print("fragment ->", opts["fragment"])
            except (OSError, ValueError) as exc:
                print("错误:", exc)
                exit_code = max(exit_code, 2)
        if opts["svg"]:
            outd = opts["svg"]
            os.makedirs(outd, exist_ok=True)
            html = ("<!doctype html><meta charset=utf-8><title>" + os.path.basename(fn) + "</title>"
                    "<body style=margin:24px>" + svg_preview(L, data))
            with open(os.path.join(outd, os.path.basename(fn) + ".html"), "w", encoding="utf-8") as g:
                g.write(html)
            print("svg ->", outd)
    if exit_code:
        print(f"\n总体结果: {'几何自检 FAIL' if exit_code == 1 else '输入/参数不合法'}（exit {exit_code}）")
    sys.exit(exit_code)


if __name__ == "__main__":
    main(sys.argv[1:])
