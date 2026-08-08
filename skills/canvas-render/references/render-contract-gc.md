# GC Canvas HTML 实现契约

本契约定义黄金圈（Golden Circle）Canvas 页面的 HTML 结构。

数据源是 `modules/GC-{slug}-v{N}.md`（确认包，Markdown）；LLM 读取后按本章的 section 映射表，把内容映射到 HTML 锚点。映射的字段名沿用确认包 Markdown 的 section 标题。`{slug}` 必须等于 `state.json.golden_circle.{slug}.slug`，正式输出为 `output/gc-canvas-{slug}.html`；`output/gc-canvas.html` 仅作为多 instance 索引页。

## A. 黄金圈 Canvas 页面结构

```html
<body data-mode="formal" data-page-type="golden-circle" data-version="1" data-instance="{slug}">
  <header id="canvas-header">
    <h1>黄金圈法则 Golden Circle Canvas</h1>
    <div id="canvas-headline">一句话结论</div>
  </header>
  <section id="gc-diagram">
    <!-- 3 圈同心圆图示（WHY / HOW / WHAT）——签名视觉，必须参照 examples/goden-circle-canvas.html 实现（见 §C） -->
  </section>
  <main>
    <section id="why">
      <h2>WHY — 信念、目标与使命</h2>
      <div id="why-belief">信念</div>
      <div id="why-purpose">存在目的</div>
      <div id="why-mission">使命/愿景</div>
    </section>
    <section id="how">
      <h2>HOW — 核心差异化与方法</h2>
      <div id="how-principles">做事原则</div>
      <div id="how-differentiation">差异化</div>
      <div id="how-methods">方法/流程</div>
    </section>
    <section id="what">
      <h2>WHAT — 产品与服务</h2>
      <div id="what-products">产品</div>
      <div id="what-services">服务</div>
      <div id="what-evidence">市场证据</div>
    </section>
    <section id="cross-layer-alignment">
      <h2>跨层一致性</h2>
      <div id="alignment-why-how">WHY→HOW 推导链（数据源：GC-{slug}-v{N}.md 第 6a 节）</div>
      <div id="alignment-how-what">HOW→WHAT 推导链（数据源：GC-{slug}-v{N}.md 第 6a 节）</div>
    </section>
  </main>
  <aside id="quality-panel">
    <h3>质量与对齐</h3>
    <div id="quality-version">v{N}</div>
    <div id="quality-approval">
      <!-- gate_recommendation / render_authorized / confirmation_mode -->
    </div>
    <div id="quality-gaps">缺口摘要</div>
    <div id="quality-risks">风险摘要</div>
    <div id="quality-caveat" hidden>
      <!-- 仅 override 时显示，含 Gate 建议、override 项数量、高风险项数量、风险详情 -->
    </div>
  </aside>
  <section id="local-notes" contenteditable="true">...</section>
  <script type="application/json" id="canvas-data">
    {
      "version": "v{N}",
      "instance": "{slug}",
      "canvas_type": "golden-circle",
      "sections": { ...确认包 section 映射... },
      "auth": {
        "gate_recommendation": "pass | fail",
        "render_authorized": true,
        "confirmation_mode": "gate_pass | override",
        "override_audit": { ...完整 override_audit 数据，仅 override 时存在... }
      }
    }
  </script>
</body>
```

## B. 稳定锚点映射

| HTML 锚点 | 确认包 section |
|---|---|
| `canvas-headline` | 必展项 → 一句话�论 |
| `why-belief` | 6：WHY / belief（领导信念） |
| `why-purpose` | 6：WHY / purpose（存在目的） |
| `why-mission` | 6：WHY / mission（使命/愿景） |
| `how-principles` | 6：HOW / principles（做事原则） |
| `how-differentiation` | 6：HOW / differentiation（差异化） |
| `how-methods` | 6：HOW / methods（方法/流程） |
| `what-products` | 6：WHAT / products（产品） |
| `what-services` | 6：WHAT / services（服务） |
| `what-evidence` | 6：WHAT / evidence（市场证据） |
| `alignment-why-how` | 6a：跨层一致性 / WHY→HOW 推导链 |
| `alignment-how-what` | 6a：跨层一致性 / HOW→WHAT 推导链 |

**关键规则**：

- 已讨论的字段正常展示内容；未讨论的字段显示"未讨论"并标为缺口。
- `alignment-*` 的数据源为 `GC-{slug}-v{N}.md` 第 6a 节，不由 canvas-render 推断。
- GC Canvas 是独立一等公民画布；同一 group 可有多个 instance，不存在子模块详情页和全局汇总页。
- **`gc-diagram`（3 圈同心圆图示）是 GC 画布的签名视觉元素，渲染时必须参照 `examples/goden-circle-canvas.html` 实现**，见 §C。

## C. 3 圈同心圆图示（签名视觉，必须参照示例）

`gc-diagram` 区块展示黄金圈的标志性**三同心圆**（由内到外：WHY / HOW / WHAT），是 GC 画布区别于其他画布的核心视觉标识。

**硬性要求（渲染时必须遵守）**：

1. **必须参照** `examples/goden-circle-canvas.html`（仓库内一等公民示例）实现 `gc-diagram` 区块，包括：三同心圆的 SVG 结构（`<circle r="150/100/50">`）、WHY / HOW / WHAT 环带标签、`viewBox="0 0 340 340"` 及 pratyaya 黑灰配色。
2. 该示例是 `gc-diagram` 的**唯一视觉事实源**；渲染时不得省略该图示，不得用其他图形（如三个并列圆、三层卡片）替代。
3. 图示配色沿用 pratyaya 标准黑灰（`10-black-gray-professional`），不引入彩色、不做配色切换。
4. 图示本身是纯视觉元素，不承载业务数据；业务内容仍写入下方 WHY / HOW / WHAT 三层 section 的对应锚点。

> 说明：`gc-diagram` 不在 §B 锚点映射表内（不参与 anchor 顺序审计），但**渲染产物必须包含该元素**；交付前浏览器视觉验收时按示例比对。本要求是 `canvas-render/SKILL.md`「示例参照」全局规则（任何画布都必须查找并参照 `examples/` 对应示例）在 GC 的具体化。

## 共享结构

与 MVL Canvas 共享 quality-panel、local-notes、canvas-data 结构（见 `render-contract.md`）。差异：

- `data-page-type` 为 `golden-circle`（非 `global` / `module-detail`）。
- 无 `data-module` 属性。
- `canvas-data.module` 字段替换为 `canvas-data.canvas_type: "golden-circle"`。
- `canvas-data.auth` 字段对应 `state.json.golden_circle.{slug}`，且 `canvas-data.instance` 必须等于同一 `{slug}`。

### Caveat 状态标识

与 MVL 一致：
- `confirmation_mode=gate_pass`：显示"已确认"。
- `confirmation_mode=override`：显示"**已确认 · 带保留意见**"。

## 本地离线约束

- CSS、JavaScript、图标和字体优先内联或使用系统字体。
- 禁止通过 `fetch("file.json")` 加载本地数据。
- 禁止用 iframe 打开兄弟 HTML；使用普通相对链接。
- 所有交互在单文件内工作，无网络时仍可展开、筛选、打印和编辑。

## 数据完整性

- 输出页的 `data-version` 必须等于确认包版本 `v{N}`。
- 页面内嵌数据必须来自同一次读取。
- 结论 ID、缺口 ID 与确认包 Markdown 保持一致。
- `canvas-data` 的 `auth` 字段必须与 `state.json.golden_circle.{slug}` 完全一致。
- `body[data-instance]`、`canvas-data.instance`、确认包文件名 `{slug}` 与 `state.json.golden_circle.{slug}.slug` 必须一致。

## 打印与管理层阅读

- `@media print` 隐藏编辑控件，保留版本、确认、风险状态、结论和 override caveat。
- 结论与关键指标优先，证据细节折叠但可打印附录。
- override 模块必须保留 caveat 标识与风险详情。

## 交付前自检

同 MVL：Python 静态审计（`audit_canvas_html.py --type gc --instance {slug}`）+ 浏览器视觉验收。两阶段都通过后才把当前 instance 状态改为 `rendered`。
