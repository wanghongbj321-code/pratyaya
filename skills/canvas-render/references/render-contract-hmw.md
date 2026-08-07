# HMW Canvas HTML 实现契约

本契约定义 HMW（How Might We，问题重构）Canvas 页面的 HTML 结构。

数据源是 `modules/HMW-v{N}.md`（确认包，Markdown）；LLM 读取后按本章的 section 映射表，把内容映射到 HTML 锚点。映射的字段名沿用确认包 Markdown 的 section 标题。

## A. HMW Canvas 页面结构

```html
<body data-mode="formal" data-page-type="hmw" data-version="1">
  <header id="canvas-header">
    <h1>How Might We 问题重构画布</h1>
    <div id="canvas-headline">一句话结论</div>
  </header>
  <main>
    <section id="hmw-statement">
      <h2>HMW 陈述</h2>
      <div id="hmw-situation">问题情境（谁 + 何时 + 卡住）</div>
      <div id="hmw-question">我们可以如何（问句本体）</div>
      <div id="hmw-for">为 / 给</div>
      <div id="hmw-sothat">以便</div>
    </section>
    <section id="hmw-quality">
      <h2>质量鉴别</h2>
      <div id="hmw-quality-preset">预设解法判定</div>
      <div id="hmw-quality-vague">含糊判定</div>
      <div id="hmw-quality-moment">用户时刻判定</div>
      <div id="hmw-quality-tension">张力判定</div>
    </section>
    <section id="hmw-ideas">
      <h2>想法种子（8 固定格，对齐 worksheet）</h2>
      <div id="hmw-idea-1">想法 1</div>
      <div id="hmw-idea-2">想法 2</div>
      <div id="hmw-idea-3">想法 3</div>
      <div id="hmw-idea-4">想法 4</div>
      <div id="hmw-idea-5">想法 5</div>
      <div id="hmw-idea-6">想法 6</div>
      <div id="hmw-idea-7">想法 7</div>
      <div id="hmw-idea-8">想法 8</div>
    </section>
    <section id="hmw-coherence">
      <h2>想法 ↔ HMW 对应</h2>
      <div id="hmw-coherence-map">想法与问句对应图（数据源：HMW-v{N}.md 第 6c 节）</div>
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
      "canvas_type": "hmw",
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
| `canvas-headline` | 必展项 → 一句话结论 |
| `hmw-situation` | 6：situation（问题情境） |
| `hmw-question` | 6：question（我们可以如何） |
| `hmw-for` | 6：for（为/给） |
| `hmw-sothat` | 6：so_that（以便） |
| `hmw-quality-preset` | 6a：preset_solution（预设解法） |
| `hmw-quality-vague` | 6a：vague（含糊） |
| `hmw-quality-moment` | 6a：user_moment（用户时刻） |
| `hmw-quality-tension` | 6a：tension（张力） |
| `hmw-idea-1` … `hmw-idea-8` | 6b：想法种子第 1–8 条 |
| `hmw-coherence-map` | 6c：想法 ↔ HMW 对应 |

**关键规则**：

- 已讨论的字段正常展示内容；未讨论的字段显示"未讨论"并标为缺口。
- `hmw-quality-*` 的数据源为 `HMW-v{N}.md` 第 6a 节，不由 canvas-render 推断。
- `hmw-coherence-map` 的数据源为 `HMW-v{N}.md` 第 6c 节，不由 canvas-render 推断。
- 想法锚点 `hmw-idea-1` … `hmw-idea-8` 固定 8 个，对齐 worksheet 的 8 想法格；空想法格渲染为占位（显示"未讨论"或空卡片），但**锚点必须存在**。
- HMW Canvas 是单画布，不存在子模块详情页和全局汇总页。

## 共享结构

与 MVL / GC Canvas 共享 quality-panel、local-notes、canvas-data 结构（见 `render-contract.md`）。差异：

- `data-page-type` 为 `hmw`（非 `global` / `module-detail` / `golden-circle`）。
- 无 `data-module` 属性。
- `canvas-data.module` 字段替换为 `canvas-data.canvas_type: "hmw"`。
- `canvas-data.auth` 字段对应 `state.json.hmw`。

### Caveat 状态标识

与 MVL / GC 一致：
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
- `canvas-data` 的 `auth` 字段必须与 `state.json.hmw` 完全一致。

## 打印与管理层阅读

- `@media print` 隐藏编辑控件，保留版本、确认、风险状态、结论和 override caveat。
- 结论与关键指标优先，证据细节折叠但可打印附录。
- override 画布必须保留 caveat 标识与风险详情。

## 模板结构 Profile（Template Gate 判定依据）

Template Gate（`audit_canvas_html.py --template examples/canvas-html/hmw-canvas.html --type hmw`）以本 profile 为判定依据，比较成品与模板的一级模块、稳定锚点与相对 DOM 顺序。**不比较**占位文本、业务文案、动态版本值或 CSS 逐字符内容。

### 一级模块必需性与 DOM 相对顺序（强制）

```text
canvas-header
  → hmw-statement
  → hmw-ideas
  → hmw-coherence
  → hmw-quality
  → quality-panel
  → local-notes
  → canvas-data
```

> **顺序依据**：以 `examples/canvas-html/hmw-canvas.html` 模板实际 DOM 顺序为准（质量鉴别 `hmw-quality` 与质量与对齐 `quality-panel` 同属质量总结，置于想法与对应关系之后、相邻成组）。Template Gate 以本 profile 与模板为比对基准。

任一一级模块缺失、重复或相对顺序偏离本 profile，Template Gate FAIL（`HMW-TPL-GATE-02` / `HMW-TPL-GATE-03`）。

### 稳定锚点集合（Template Gate 校验）

- 页面：`data-page-type="hmw"`（`HMW-TPL-GATE-01`）
- 陈述 4 字段：`hmw-situation` / `hmw-question` / `hmw-for` / `hmw-sothat`（`HMW-TPL-GATE-04`）
- 质量 4 维度：`hmw-quality-preset` / `hmw-quality-vague` / `hmw-quality-moment` / `hmw-quality-tension`（`HMW-TPL-GATE-04`）
- 想法 8 固定格：`hmw-idea-1` … `hmw-idea-8`（锚点不可缺失；未讨论格用 `data-state="placeholder"`）（`HMW-TPL-GATE-04`）
- 对应关系：`hmw-coherence-map`（`HMW-TPL-GATE-04`）
- 治理面板：`quality-panel` 含 `quality-version` / `quality-approval` / `quality-gaps` / `quality-risks` / `quality-caveat` 插槽（`HMW-TPL-GATE-05`）
- 批注与数据：`local-notes`、`canvas-data`（`HMW-TPL-GATE-02`）
- 共享主题 / 窄屏布局 / `@media print` 钩子存在，无外部网络依赖（`HMW-TPL-GATE-06`）

### 隐藏检测（Template Gate 与内容/授权 Gate 共用）

质量鉴别（`hmw-quality`）、想法对应（`hmw-coherence`）与治理面板（`quality-panel`）不得以任何方式隐藏。四种隐藏方式任一命中即 FAIL：

1. `hidden` HTML 属性（`hidden` 属性存在）
2. `style="display:none"` 或计算后 `display` 为 `none`
3. `style="visibility:hidden"` 或计算后 `visibility` 为 `hidden`
4. `class="hidden"`（约定 `.hidden { display:none; }`）

### 参考样例

- `internal/pratyaya-internal/docs/refs/how-might-we-canvas.html`：内部静态 worksheet（设计参考，仅作视觉/语义映射参考，非运行时模板事实源）。
- `examples/canvas-html/hmw-canvas.html`：HMW 一等公民**版面与签名视觉事实源**（Template Gate 的比对模板）。

## 交付前自检

同 MVL / GC：Python 静态审计（`audit_canvas_html.py --type hmw`，正式交付追加 `--template examples/canvas-html/hmw-canvas.html` 触发双 Gate）+ 浏览器视觉验收。两阶段都通过后才把状态改为 `rendered`。
