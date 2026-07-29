# Canvas HTML 实现契约

本契约定义两种 Canvas 页面的 HTML 结构：

- **全局 Canvas 页面**：六板块汇总视图（`maau-global-canvas.html`）
- **模块详情 Canvas 页面**：M1-M6 各自专属结构（`module-N-canvas.html`）

两者共享头部、质量面板、本地批注区和内嵌数据区。区别在于 `<main>` 内部结构：全局页面用固定的六大板块，模块详情页面用该模块的专属 section。

数据源是 `modules/Mx-v{N}.md`（确认包，Markdown）；LLM 读取后按本章的 section 映射表，把内容映射到 HTML 锚点。映射的字段名沿用确认包 Markdown 的 section 标题（中文标题与 HTML 锚点 ID 之间的对应见下表）。

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

每个模块详情页面**不使用六板块结构**。它只展示该模块的专属 section，不留空白板块。

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
      <!-- 由 Mx-v{N}.md 的固定 section 驱动，见下方 M1-M6 专属结构 -->
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

`<section id="module-outputs">` 内部由 `Mx-v{N}.md` 的固定 section 驱动（参见 `../mvl-distill/references/workshop-canvas-map.md` 的"模块 Markdown 必填 section"表）。每个模块的专属 HTML 锚点如下：

### M1 模块详情

| HTML 锚点 | Mx-v{N}.md 的固定 section 标题 |
|---|---|
| `id="m1-goal"` | 目标（goal） |
| `id="m1-value"` | 价值（value） |
| `id="m1-success-metrics"` | 成功指标（success_metrics） |
| `id="m1-evidence"` | 证据（evidence） |
| `id="m1-boundary"` | 边界（boundary） |
| `id="m1-acceptance"` | 验收标准（acceptance） |
| `id="m1-grouping"` | 项目分组（grouping） |

### M2 模块详情

| HTML 锚点 | Mx-v{N}.md 的固定 section 标题 |
|---|---|
| `id="m2-users"` | 用户（users） |
| `id="m2-needs"` | 需求（needs） |
| `id="m2-pain-points"` | 痛点（pain_points） |
| `id="m2-most-important-outcomes"` | 最重要结果（most_important_outcomes） |
| `id="m2-current-workflow"` | 现状流程（current_workflow） |
| `id="m2-requirements"` | 需求（requirements） |

### M3 模块详情

| HTML 锚点 | Mx-v{N}.md 的固定 section 标题 |
|---|---|
| `id="m3-hmw"` | HMW 拆解（hmw） |
| `id="m3-loop-goal"` | 闭环目标（loop_goal） |
| `id="m3-capability-metrics"` | 能力指标（capability_metrics） |
| `id="m3-acceptance"` | 验收标准（acceptance） |
| `id="m3-boundary"` | 边界（boundary） |
| `id="m3-solution-direction"` | 方案方向（solution_direction） |
| `id="m3-workflow-draft"` | Workflow 草案（workflow_draft） |
| `id="m3-validation-dimensions"` | 验证维度（validation_dimensions） |

### M4 模块详情

| HTML 锚点 | Mx-v{N}.md 的固定 section 标题 |
|---|---|
| `id="m4-agent-team"` | Agent Team（agent_team） |
| `id="m4-collaboration"` | 协作模式（collaboration_mode） |
| `id="m4-workflow-final"` | Workflow 冻结（workflow_final） |
| `id="m4-knowledge"` | Context：知识（knowledge） |
| `id="m4-data-sources"` | Context：数据源（data_sources） |
| `id="m4-tools-skills"` | Context：工具与技能（tools_skills） |
| `id="m4-prototype-rounds"` | 两轮原型（prototype_rounds） |
| `id="m4-delivery-preparation"` | 交付准备（delivery_preparation） |

### M5 模块详情

| HTML 锚点 | Mx-v{N}.md 的固定 section 标题 |
|---|---|
| `id="m5-validation-rounds"` | 验证记录（validation_rounds） |
| `id="m5-can-execute"` | 能否执行（can_execute） |
| `id="m5-can-create-value"` | 能否创造价值（can_create_value） |
| `id="m5-trust-risk-controls"` | 信任与风控（trust_risk_controls） |
| `id="m5-issues-corrections"` | 问题与修正（issues_corrections） |

### M6 模块详情

| HTML 锚点 | Mx-v{N}.md 的固定 section 标题 |
|---|---|
| `id="m6-final-solution"` | 最终方案（final_solution） |
| `id="m6-solution-comparison"` | 三维对比（solution_comparison） |
| `id="m6-demo-summary"` | 演示结论（demo_summary） |
| `id="m6-validation-review"` | 验证回顾（validation_review） |
| `id="m6-capability-boundary"` | 能力边界（capability_boundary） |
| `id="m6-applicable-scenarios"` | 适用场景（applicable_scenarios） |
| `id="m6-optimization-space"` | 优化空间（optimization_space） |
| `id="m6-evolution-assets"` | 进化资产（evolution_assets） |
| `id="m6-next-step-plan"` | 后续计划（next_step_plan） |
| `id="m6-headline"` | 一句话价值（headline） |
| `id="m6-takeaway"` | 管理层 takeaway（takeaway） |

**关键规则**：

- 模块详情页面**没有空白板块**。只显示该模块专属的 section。
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
- 可编辑字段保存到浏览器 `localStorage` 时，必须标记为"本地批注"，不能覆盖已确认事实源。

## 数据完整性

- 输出页的 `data-version` 必须等于确认包版本 `v{N}`。
- 页面内嵌数据必须来自同一次读取，不允许手工复制后再改写。
- HTML 中的结论 ID、缺口 ID、引用标识与确认包 Markdown 保持一致。
- 内容变更后必须升版（vN → vN+1），并把状态退回 `draft` 或 `gaps_open`；旧 HTML 视为过期。
- 引用层级遵循 `../mvl-distill/SKILL.md` 的"不引用逐字稿段落"立场：仅引用 Key Points 与确认包自身的 section。

## 全局下钻

全局 Canvas 的板块使用普通链接，例如：

```html
<a href="./module-1-canvas.html#conclusion-M1-C01">查看 M1 依据</a>
```

不要使用 iframe。这样既避免 `file:` 唯一安全源问题，也允许用户本地双击打开。

## 打印与管理层阅读

- `@media print` 隐藏编辑控件，保留版本、确认和风险状态。
- 结论与关键指标优先，证据细节折叠但可打印附录。
- `blocker` 和 `major` 不应出现在正式页面；若历史记录需要展示，明确标记"已解决"及证据。

## 交付前自检

阶段一已移除 `scripts/audit_canvas_html.py`。结构审计由 `SKILL.md` 的"渲染自检"清单执行（数据源一致 / DOM 结构 / 共享结构 / 离线安全 / 打印规则 / 草稿标记 / 视觉系统单一 7 项）。审计通过仍不替代人工浏览器预览；二者都完成后才可交付正式 HTML。
