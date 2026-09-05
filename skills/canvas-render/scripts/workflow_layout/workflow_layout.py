# -*- coding: utf-8 -*-
"""
workflow_layout —— Workflow 确定性布局器（v0.1，阶段 0/1/3 基线）
================================================================
范式锚定（设计 §3.2，Q2 已确认）：以 examples/mvl-canvas/maau-global-canvas.html
母版 workflow 图为对齐基准——轨道分行堆叠、轨内横流（多行蛇形折返）、
跨轨 / 回流虚线走行间空隙 + 左侧 gutter 绕行，无泳道色块。
约束（Q3 已确认）：仅几何降级——节点 / 边全集必须全部渲染（L1 契约不破）。
L1（阶段 3）：`layout_override` 为渲染输入侧可选配置，只调节几何常量，
不改变节点 / 边集合、轨道结构与任何审计契约。
零第三方依赖。输入：workflow 拓扑 JSON（§A1.5 新 schema）。不修改输入数据。

CLI：
    python3 workflow_layout.py <topo.json> [more.json] [--svg out_dir] [--override override.json|--override-json '{...}']
"""
import json
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


def text_width(s):
    return sum(COL_CHAR_W_CJK if ord(ch) > 0x2E7F else COL_CHAR_W_LATIN for ch in s)


def wrap_lines(s, max_w):
    lines, cur = [], ""
    for ch in s:
        if text_width(cur + ch) <= max_w:
            cur += ch
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
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
        self.tracks = [t["id"] for t in data.get("tracks", [])] or ["main"]
        self.items = {}
        for i, n in enumerate(data["nodes"]):
            self.items[n["id"]] = Item(n, i, *self._node_dims(n))
        self.edges = data.get("edges", [])
        self.paths = {}
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
            if self._direct_ok(u, v, rects):
                if abs(u.cy - v.cy) < 1e-6:
                    pts = [(u.x + u.w, u.cy), (v.x, v.cy)]
                else:
                    pts = [(u.x + u.w, u.cy), (v.x, u.cy), (v.x, v.cy)]
                self.paths[(u.id, v.id)] = pts
            else:
                self.paths[(u.id, v.id)] = self._gutter(u, v)

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

    def selfcheck(self):
        probs = []
        rects = [(it.id, it.rect()) for it in self.items.values()]
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                a, ra = rects[i]
                b, rb = rects[j]
                if ra[0] < rb[2] and rb[0] < ra[2] and ra[1] < rb[3] and rb[1] < ra[3]:
                    probs.append(f"节点重叠 {a}∩{b}")
        for (u, v), pts in self.paths.items():
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
        gw = self.cfg["gutter_w"]
        xs0 = min(it.x for it in self.items.values())
        xs1 = max(it.x + it.w for it in self.items.values())
        ys0 = min(it.y for it in self.items.values())
        ys1 = max(it.y + it.h for it in self.items.values())
        return xs0 - gw, ys0 - 60, xs1 + gw, ys1 + 40

    def page_w(self):
        x0, _y0, x1, _y1 = self.bounds()
        return x1 - x0


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
    if override_json:
        merged.update(override_json)
    unknown = [k for k in merged if k not in LAYOUT_OVERRIDE_KEYS]
    if unknown:
        print("警告：忽略未知 layout_override 键:", unknown)
        merged = {k: v for k, v in merged.items() if k in LAYOUT_OVERRIDE_KEYS}
    return merged or None


def svg_preview(L, data, title=""):
    x0, y0, x1, y1 = L.bounds()
    W, H = x1 - x0, y1 - y0
    labels = {n["id"]: n["label"] for n in data["nodes"]}
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.0f} {y0:.0f} {W:.0f} {H:.0f}" font-family="Helvetica,Arial,sans-serif">']
    out.append('<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#000"/></marker></defs>')
    for it in L.items.values():
        x, y, w, h = it.x, it.y, it.w, it.h
        cx, cy = it.cx, it.cy
        label = labels.get(it.id, "")
        if it.type in EVENT_TYPES:
            out.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{w/2:.0f}" fill="#fff" stroke="#000" stroke-width="1.6"/>')
            for i, ln in enumerate(wrap_lines(label, 150)):
                out.append(f'<text x="{cx:.0f}" y="{cy + (i - 0.4) * 11:.0f}" text-anchor="middle" font-size="8.5">{ln}</text>')
        elif it.type == "gateway":
            out.append(f'<polygon points="{cx:.0f},{y:.0f} {x+w:.0f},{cy:.0f} {cx:.0f},{y+h:.0f} {x:.0f},{cy:.0f}" fill="#fff" stroke="#000" stroke-width="1.8"/>')
            for i, ln in enumerate(wrap_lines(label, w - 16)):
                out.append(f'<text x="{cx:.0f}" y="{cy + (i - 0.3) * 11:.0f}" text-anchor="middle" font-size="9">{ln}</text>')
        elif it.type == "data_store":
            out.append(f'<rect x="{x:.0f}" y="{y+8:.0f}" width="{w:.0f}" height="{h-8:.0f}" rx="6" fill="#fff" stroke="#000" stroke-width="2"/>')
            for i, ln in enumerate(wrap_lines(label, w - 16)):
                out.append(f'<text x="{cx:.0f}" y="{cy + (i - 0.2) * 12:.0f}" text-anchor="middle" font-size="10">{ln}</text>')
        else:
            out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="8" fill="#fff" stroke="#000" stroke-width="1.5"/>')
            lines = wrap_lines(label, w - 12)
            for i, ln in enumerate(lines):
                out.append(f'<text x="{cx:.0f}" y="{cy + (i - (len(lines) - 1) / 2) * 13:.0f}" text-anchor="middle" font-size="10">{ln}</text>')
    for (u, v), pts in L.paths.items():
        d = "M" + " ".join(f"{p[0]:.1f} {p[1]:.1f}" for p in pts)
        out.append(f'<path d="{d}" fill="none" stroke="#000" stroke-width="1.5" marker-end="url(#arr)"/>')
    out.append('</svg>')
    return "".join(out)


def layout_trace(fork_id=None):
    """产物溯源字段（写进 `canvas-data.workflow.layout`，可选；不改 schema_version）。
    engine / baseline_version 标识生成该 SVG 的布局器版本；fork_id 仅在 L2 分叉产物存在。"""
    trace = {"engine": "workflow_layout", "baseline_version": __version__}
    if fork_id:
        trace["fork_id"] = fork_id
    return trace


def main(argv):
    if "--version" in argv:
        print("workflow_layout", __version__)
        return
    files = [a for a in argv if a.endswith(".json") and not a.startswith("--")]
    override = None
    if "--override" in argv:
        with open(argv[argv.index("--override") + 1], encoding="utf-8") as f:
            override = resolve_override(override_json=json.load(f))
    elif "--override-json" in argv:
        override = resolve_override(override_json=json.loads(argv[argv.index("--override-json") + 1]))
    elif "--preset" in argv:
        override = resolve_override(preset=argv[argv.index("--preset") + 1])
    if override:
        print("layout_override 生效:", override)
    for fn in files:
        with open(fn, encoding="utf-8") as f:
            data = json.load(f)
        L = layout_of(data, override)
        probs = L.selfcheck()
        print(f"\n== {os.path.basename(fn)} ==")
        print(f"nodes={len(L.items)} edges={len(L.edges)} tracks={L.tracks} page_w≈{L.page_w():.0f}")
        print("自检问题:", len(probs))
        for p in probs[:25]:
            print("  -", p)
        if "--svg" in argv:
            outd = argv[argv.index("--svg") + 1]
            os.makedirs(outd, exist_ok=True)
            html = ("<!doctype html><meta charset=utf-8><title>" + os.path.basename(fn) + "</title>"
                    "<body style=margin:24px>" + svg_preview(L, data))
            with open(os.path.join(outd, os.path.basename(fn) + ".html"), "w", encoding="utf-8") as g:
                g.write(html)
            print("svg ->", outd)


if __name__ == "__main__":
    main(sys.argv[1:])
