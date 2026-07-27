# Canvas HTML 实现契约

本契约定义两种 Canvas 页面的 HTML 结构：

- **全局 Canvas 页面**：六板块汇总视图（`maau-global-canvas.html`）
- **模块详情 Canvas 页面**：M1-M6 各自专属结构（`module-N-canvas.html`）

两者共享头部、质量面板、本地批注区和内嵌数据区。区别在于 `<main>` 内部结构：全局页面用固定的六大板块，模块详情页面用该模块的专属章节。

## A. 全局 Canvas 页面结构

```html
<body data-mode="formal" data-page-type="global" data-version="1">
  <header id="canvas-header">...</header>
  <main>
    <section id="intent">
      <div id="intent-goal">...</div>
      <div id="intent-value">...</div>
      <div id="intent-success-metrics"></div>
    </section>
    <section id="user">
      <div id="user-users">...</div>
      <div id="user-needs">...</div>
      <div id="user-pain-points">...</div>
      <div id="user-most-important-outcomes"></div>
    </section>
    <section id="agent-team">
      <div id="agent-team-roles">...</div>
      <div id="agent-team-collaboration">...</div>
    </section>
    <section id="workflow">
      <div id="workflow-steps">...</div>
      <div id="workflow-automation">...</div>
      <div id="workflow-human-checkpoints">...</div>
      <div id="workflow-human-agent-nodes">...</div>
      <div id="workflow-rules">...</div>
    </section>
    <section id="context">
      <div id="context-knowledge">...</div>
      <div id="context-data-sources">...</div>
      <div id="context-tools-skills">...</div>
    </section>
    <section id="validation">
      <div id="validation-executable">...</div>
      <div id="validation-value">...</div>
      <div id="validation-evolution">...</div>
    </section>
  </main>
  <aside id="quality-panel">...</aside>
  <section id="local-notes" contenteditable="true">...</section>
  <script type="application/json" id="canvas-data">...</script>
</body>
```

全局页面六大板块必须齐全，但板块内的小模块可以显示"未讨论"——不能为了填满而编造内容。

## B. 模块详情 Canvas 页面结构

每个模块详情页面**不使用六板块结构**。它只展示该模块的专属章节，不留空白板块。

```html
<body data-mode="formal" data-page-type="module-detail" data-module="M3" data-version="1">
  <header id="canvas-header">...</header>
  <main>
    <section id="module-summary">
      <h2>M3：闭环目标定义、HMW 拆解与方案方向锁定</h2>
      <div id="module-summary-headline">一句话结论</div>
      <div id="module-summary-overview">模块概览</div>
    </section>
    <section id="module-outputs">
      <!-- 由 canvas_fields 的固定字段驱动，见下方 M1-M6 专属结构 -->
    </section>
    <section id="module-conclusions">
      <h3>结论登记表</h3>
      <div id="conclusions-table">...</div>
    </section>
    <section id="module-evidence">
      <h3>证据索引</h3>
      <div id="evidence-list">...</div>
    </section>
    <section id="module-gaps">
      <h3>缺口与推断</h3>
      <div id="gaps-table">...</div>
      <div id="inferences-table">...</div>
    </section>
  </main>
  <aside id="quality-panel">...</aside>
  <section id="local-notes" contenteditable="true">...</section>
  <script type="application/json" id="canvas-data">...</script>
</body>
```

`<section id="module-outputs">` 内部由 `canvas_fields` 的固定字段驱动。每个模块的专属结构如下：

### M1 模块详情

| 专属 section | 对应 canvas_fields |
|---|---|
| `id="m1-goal"` | `goal` |
| `id="m1-value"` | `value` |
| `id="m1-success-metrics"` | `success_metrics` |
| `id="m1-evidence"` | `evidence` |
| `id="m1-boundary"` | `boundary` |
| `id="m1-acceptance"` | `acceptance` |
| `id="m1-grouping"` | `grouping` |

### M2 模块详情

| 专属 section | 对应 canvas_fields |
|---|---|
| `id="m2-users"` | `users` |
| `id="m2-needs"` | `needs` |
| `id="m2-pain-points"` | `pain_points` |
| `id="m2-most-important-outcomes"` | `most_important_outcomes` |
| `id="m2-current-workflow"` | `current_workflow` |
| `id="m2-requirements"` | `requirements` |

### M3 模块详情

| 专属 section | 对应 canvas_fields |
|---|---|
| `id="m3-hmw"` | `hmw` |
| `id="m3-loop-goal"` | `loop_goal` |
| `id="m3-capability-metrics"` | `capability_metrics` |
| `id="m3-acceptance"` | `acceptance` |
| `id="m3-boundary"` | `boundary` |
| `id="m3-solution-direction"` | `solution_direction` |
| `id="m3-workflow-draft"` | `workflow_draft` |
| `id="m3-validation-dimensions"` | `validation_dimensions` |

### M4 模块详情

| 专属 section | 对应 canvas_fields |
|---|---|
| `id="m4-agent-team"` | `agent_team` |
| `id="m4-collaboration"` | `collaboration_mode` |
| `id="m4-workflow-final"` | `workflow_final` |
| `id="m4-knowledge"` | `knowledge` |
| `id="m4-data-sources"` | `data_sources` |
| `id="m4-tools-skills"` | `tools_skills` |
| `id="m4-prototype-rounds"` | `prototype_rounds` |
| `id="m4-delivery-preparation"` | `delivery_preparation` |

### M5 模块详情

| 专属 section | 对应 canvas_fields |
|---|---|
| `id="m5-validation-rounds"` | `validation_rounds` |
| `id="m5-can-execute"` | `can_execute` |
| `id="m5-can-create-value"` | `can_create_value` |
| `id="m5-trust-risk-controls"` | `trust_risk_controls` |
| `id="m5-issues-corrections"` | `issues_corrections` |

### M6 模块详情

| 专属 section | 对应 canvas_fields |
|---|---|
| `id="m6-final-solution"` | `final_solution` |
| `id="m6-solution-comparison"` | `solution_comparison` |
| `id="m6-demo-summary"` | `demo_summary` |
| `id="m6-validation-review"` | `validation_review` |
| `id="m6-capability-boundary"` | `capability_boundary` |
| `id="m6-applicable-scenarios"` | `applicable_scenarios` |
| `id="m6-optimization-space"` | `optimization_space` |
| `id="m6-evolution-assets"` | `evolution_assets` |
| `id="m6-next-step-plan"` | `next_step_plan` |
| `id="m6-headline"` | `headline` |
| `id="m6-takeaway"` | `takeaway` |

**关键规则**：

- 模块详情页面**没有空白板块**。只显示该模块专属的章节。
- 每个 section 的 ID 以模块前缀开头（`m1-`、`m2-`…`m6-`），避免与全局页面的 ID 冲突。
- 已讨论的字段正常展示内容；未讨论的字段显示"未讨论"并标为缺口。
- 质量面板（quality-panel）的锚点 ID 统一使用 `quality-*` 前缀，两种页面共享。
- 对齐状态放在 quality-panel 的 `alignment-section` 内，两种页面共享。

## 共享结构

两种页面都包含以下共享部分：

```html
<aside id="quality-panel">
  <h3>质量与对齐</h3>
  <div id="quality-version">...</div>
  <div id="quality-approval">...</div>
  <div id="quality-gaps">...</div>
  <div id="quality-risks">...</div>
  <section id="alignment-section">
    <h4>对齐状态</h4>
    <div id="alignment-consensus">...</div>
    <div id="alignment-divergences">...</div>
    <div id="alignment-decisions">...</div>
  </section>
</aside>
<section id="local-notes" contenteditable="true">...</section>
<script type="application/json" id="canvas-data">...</script>
```

## 本地离线约束

- CSS、JavaScript、图标和字体优先内联或使用系统字体。
- 禁止通过 `fetch("file.json")` 加载本地数据；浏览器会因 file origin 拦截。
- 禁止用 iframe 打开兄弟 HTML；使用普通相对链接。
- 所有交互在单文件内工作，无网络时仍可展开、筛选、打印和编辑。
- 可编辑字段保存到浏览器 `localStorage` 时，必须标记为“本地批注”，不能覆盖已确认事实源。

## 数据完整性

- 输出页的 `data-version` 必须等于模块记录版本。
- 页面内嵌数据必须来自同一次读取，不允许手工复制后再改写。
- HTML 中的结论 ID、缺口 ID、证据引用与 JSON 保持一致。
- 内容变更后必须升版，并把状态退回 `draft` 或 `gaps_open`；旧 HTML 视为过期。

## 全局下钻

全局 Canvas 的板块使用普通链接，例如：

```html
<a href="./module-1-canvas.html#conclusion-M1-C01">查看 M1 依据</a>
```

不要使用 iframe。这样既避免 `file:` 唯一安全源问题，也允许用户本地双击打开。

## 打印与管理层阅读

- `@media print` 隐藏编辑控件，保留版本、确认和风险状态。
- 结论与关键指标优先，证据细节折叠但可打印附录。
- `blocker` 和 `major` 不应出现在正式页面；若历史记录需要展示，明确标记“已解决”及证据。

## 交付前审计

```powershell
python skills/canvas-render/scripts/audit_canvas_html.py output/module-1-canvas.html
```

审计必须确认：六大模块及规定小模块锚点齐全、质量面板与本地批注存在、同版本 JSON 已内嵌、包含打印规则，并且没有 iframe、`fetch()` 或外部网络资源。退出码 `0` 表示结构与离线安全检查通过；它不替代人工浏览器预览。
