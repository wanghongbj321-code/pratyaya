# Canvas HTML 实现契约

本契约定义两种 Canvas 页面的 HTML 结构：

- **全局 Canvas 页面**：六板块汇总视图（`maau-global-canvas.html`）
- **模块详情 Canvas 页面**：M1-M6 各自专属结构（`module-N-canvas.html`）

**MAAU transcript-direct 分支**（`generation_path=transcript-direct`）：一次性六板块源包 `modules/MAAU-{slug}-v{N}.md` 渲染为 `output/maau-global-canvas-{slug}.html`。结构与全局 Canvas 页面一致（六大板块 + 共享头部/质量面板/批注/内嵌数据），但**不做 M1-M6 模块详情下钻**：transcript-direct 是单源一次性综合，无六模块详情页。与 Phase 2 全局页（`output/maau-global-canvas.html`）互斥。

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
      <div id="agent-team-collaboration"></div>
    </section>
    <section id="workflow">
      <div id="workflow-steps">...</div>
      <div id="workflow-automation">...</div>
      <div id="workflow-human-checkpoints"></div>
      <div id="workflow-human-agent-nodes"></div>
      <div id="workflow-rules"></div>
      <div id="workflow-flow">...</div>
    </section>
    <section id="context">
      <div id="context-knowledge">...</div>
      <div id="context-data-sources"></div>
      <div id="context-tools-skills"></div>
    </section>
    <section id="validation">
      <div id="validation-executable">...</div>
      <div id="validation-value">...</div>
      <div id="validation-evolution"></div>
    </section>
  </main>
  <aside id="quality-panel">...</aside>
  <section id="local-notes" contenteditable="true">...</section>
  <script type="application/json" id="canvas-data">...</script>
</body>
```

全局页面六大板块必须齐全，但板块内的小模块可以显示"未讨论"——不能为了填满而编造内容。

### A1. Workflow BPMN 流程图（`#workflow-flow`）

Workflow 板块在 `.maau-fields` 文本框之下必须包含一张**派生只读**的 BPMN 可视化流程图（`id="workflow-flow"`，全局页稳定锚点）。该契约适用于 MVL Phase 2 全局汇总页（`maau-global-canvas.html`）与 MAAU transcript-direct 实例页（`maau-global-canvas-{slug}.html`）。流程图是展示层派生视图：渲染时由 LLM 从确认包（`MAAU-{slug}-v{N}.md` / `Mx-v{N}.md`）Workflow section 按以下规则静态生成内联 SVG，不新增分析、不补写业务内容。

#### A1.1 DOM 结构

```html
<div class="maau-flow" id="workflow-flow" aria-label="Workflow BPMN 流程图">
  <div class="maau-flow-head">
    <span class="maau-flow-title">流程可视化（BPMN 2.0 风格）</span>
    <span class="maau-flow-meta">Workflow Flow · v{N}</span>
  </div>
  <div class="bpmn-flow-wrap">
    <svg class="bpmn-flow" role="img" aria-label="Workflow BPMN 流程图" viewBox="...">
      <defs>
        <marker id="flow-arrow" ...>...</marker>
        <marker id="flow-arrow-dash" ...>...</marker>
      </defs>
      <g class="bpmn-track" data-track="A">...</g>
      <g class="bpmn-node" data-node-type="agent_execution" data-node-id="w1" data-track="A">
        <rect class="bpmn-task" .../>
        <g class="bpmn-actor" data-actor="ai">...</g>
        <g class="bpmn-number">...</g>
      </g>
      <path class="bpmn-sequence" d="M...H...V..." marker-end="url(#flow-arrow)"/>
      <path class="bpmn-sequence bpmn-reflow" d="M...H...V..." marker-end="url(#flow-arrow-dash)"/>
    </svg>
  </div>
  <div class="bpmn-legend" aria-label="BPMN 图例">...</div>
  <div class="workflow-done" id="workflow-done">...</div>
</div>
```

- `#workflow-flow` 必须唯一；空数据时显示"未讨论"占位，结构与锚点仍存在。
- 现有 `#workflow-*` 文本框锚点保持不变（文本框是本地批注载体，流程图是派生只读视图）。
- SVG 必须使用内联样式与系统字体，禁止外链资源（沿用离线约束）。
- `#workflow-done` 是条件锚点：`completion_condition` 有内容时渲染，空内容时不占位，不加入 `GLOBAL_MAIN_IDS`。

#### A1.2 BPMN 子集与元素映射

| BPMN 元素 | 标准符号 | 数据映射 | SVG 标记 |
|---|---|---|---|
| Start Event | 单线空心圆 | `trigger` | `data-node-type="start"` |
| Task | 圆角矩形 | `steps` 中的步骤 | `data-node-type="agent_execution"` / `"human_operation"` / `"human_review"` |
| Exclusive Gateway | 菱形 | `rules` 中的分支（升级/停止/回退/如果→否则） | `data-node-type="gateway"` |
| Timer Event | 空心圆 + 时间符号 | 文本明确出现每日 / 定时 / 周期 | `data-node-type="timer"` |
| Message Event | 空心圆 + 消息符号 | 文本明确出现消息 / 推送 / 通知 | `data-node-type="message"` |
| Data Store | 圆柱 | 文本明确出现入库 / 知识库 / 经验库 / 存储，且有回流语义 | `data-node-type="data_store"` |
| End Event | 双线空心圆 | `completion_condition` | `data-node-type="end"` |
| Sequence Flow | 实线箭头，可带条件标签 | 步骤间流向；Gateway 流出线标注条件 | `<path class="bpmn-sequence">` + `marker-end="url(#flow-arrow)"` |
| Reflow / Feedback Flow | 虚线箭头 | 明确的回流 / 反馈 / 循环 | `<path class="bpmn-sequence bpmn-reflow">` + `marker-end="url(#flow-arrow-dash)"` |

三类任务节点必须呈现 actor 徽标（右上角小方片）：
- **Agent 执行** → `type="agent_execution"`，`actor="ai"` 或 `actor="system"`；
- **人工操作/确认** → `type="human_operation"`，`actor="human"`；
- **人审 + Agent 执行** → `type="human_review"`，`actor="hybrid"` 或 `actor="reviewer"`。

`actor` 使用稳定英文机器值：`human / ai / system / hybrid / reviewer`；显示文案固定映射为 `人 / AI / 系统 / 人+AI / 审核`。BPMN Manual Task 本轮不新增独立 `type`，映射为 `human_operation + actor="human"`。

每个 SVG 节点必须是 `<g class="bpmn-node" data-node-type="{type}" data-node-id="{id}" data-track="{track}">`，且 `data-node-type`、`data-track` 与 `canvas-data.workflow.nodes[]` 一致。所有节点（含 Start / End 事件）**左上角显示流程序号徽标**，徽标数字与 `canvas-data.workflow.nodes[].number` 一致。

#### A1.3 派生规则

1. **主干链**：`steps` 列表顺序 → 默认线性 Sequence Flow 链。
2. **轨道判定**：扫描 steps/三类节点文本中的阶段前缀或标题（如 `A1…A6` / `B1…B3` / `C1…C3`、"流水线 / 对话层 / 学习闭环"等语义）分组为业务阶段轨道带；无法解析阶段 → 固定单轨 `main`，不硬造多轨。
3. **起止**：`trigger` → Start；`completion_condition` → End。
4. **节点归类**：每个步骤按内容归入三类节点（与确认包三类节点章节一一对应），决定 `type` 与 `actor`；无法确定 `ai` 还是 `system` 时，Agent 执行节点优先 `ai`。
5. **可选事件/存储派生**：文本明确含"每日/定时/周期"→ `timer`；"消息/推送/通知"→ `message`；"入库/知识库/经验库/存储"且有回流语义 → `data_store`。语义不明确时不派生，宁可单轨直链。
6. **分支**：`rules` 含分支语义（升级/停止/回退/如果→否则/低置信升级）→ 对应位置插 Exclusive Gateway，流出线标注条件；无法确定性推断的拓扑 → 保守线性连接，不确定分支信息进缺口表承载，不编造。
7. **回流 / 闭环虚线**：文本明确表达"回流 / 次日循环 / 定期重复 / 反哺"且目标节点可定位时，画正交虚线回流；不确定就不画。
8. **缺类/缺字段**：按既有规则显示"未讨论"，不得补写；`completion_condition` 有内容才渲染 `#workflow-done` 清单。
9. **连接线正交**：Sequence Flow 只使用横线 / 竖线 / 肘型折线（SVG 路径命令仅 `M` / `H` / `V`），禁止曲线 / 斜线命令（`C` / `Q` / `S` / `A`）。

#### A1.4 轨道带与响应式

- 桌面：Pool = MVL/MAAU 全局 Workflow；轨道带 = 业务阶段（A/B/C... 或单轨 `main`），节点自左向右排列，跨轨道箭头表达人机交接或反馈闭环。
- 单轨：固定写 `tracks=[{"id":"main","label":"Workflow 主链"}]`，节点 `track="main"`。
- 窄屏（390px）：保留横向滚动容器（`.bpmn-flow-wrap { overflow-x:auto; }`），不把轨道语义改写成新的数据结构。
- MVL 全局页打印幅面为 A3 横版；M1-M6 模块详情页保持既有幅面，本节不适用。

#### A1.5 `canvas-data` 拓扑数据

`canvas-data` 顶层新增 `workflow` 对象（与 `sections.workflow` 并存）：

```json
"workflow": {
  "tracks": [
    { "id": "main", "label": "Workflow 主链" }
  ],
  "nodes": [
    { "id": "w0", "number": "01", "type": "start", "track": "main", "label": "触发条件（trigger）" },
    { "id": "w1", "number": "02", "type": "agent_execution", "track": "main", "actor": "ai", "label": "..." },
    { "id": "w2", "number": "03", "type": "gateway", "track": "main", "label": "关键规则分支" },
    { "id": "w3", "number": "04", "type": "human_operation", "track": "main", "actor": "human", "label": "..." },
    { "id": "w4", "number": "05", "type": "human_review", "track": "main", "actor": "hybrid", "label": "..." },
    { "id": "w5", "number": "06", "type": "end", "track": "main", "label": "完成条件（completion_condition）" }
  ],
  "edges": [
    { "from": "w0", "to": "w1" },
    { "from": "w2", "to": "w3", "label": "条件标签" },
    { "from": "w4", "to": "w1", "dashed": true, "label": "反馈回流" }
  ]
}
```

约束：
- `tracks` 必须为非空数组；多阶段时写 A/B/C 等业务阶段，单轨固定写 `main`；
- `nodes[].track` 必填且必须引用 `tracks[].id`；
- `nodes[].type ∈ {start, end, gateway, agent_execution, human_operation, human_review, timer, message, data_store}`；
- `nodes` 必须覆盖 `agent_execution / human_operation / human_review` 三类（与确认包三类节点一一对应）；
- 任务类节点必须有 `nodes[].actor ∈ {human, ai, system, hybrid, reviewer}`；
- `nodes[].number` 必填且唯一，`01` 起按 Start→End 主链阅读序递增；回流 / 反馈边不参与重新排序；
- `edges[].from / to` 必须引用存在的 node id；
- `edges[].dashed=true` 必须对应 SVG 中一条 `bpmn-reflow` 路径；
- SVG 中 `bpmn-node` 数量必须等于 `nodes` 数量；`data-node-type`、`data-track` 与 `nodes` 一致；
- Sequence Flow 只允许正交折线（`M` / `H` / `V`），禁止曲线命令（`C` / `Q` / `S` / `A`）。

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
| `id="m3-workflow-draft"` | Workflow 草案（workflow_draft） |
| `id="m3-solution-direction"` | 方案方向（solution_direction） |
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
- `#module-outputs` 内各模块专属稳定锚点的 DOM 相对顺序，必须与本节对应模块映射表的行顺序一致。
- 桌面和窄屏版的视觉阅读顺序必须与该 DOM 顺序一致；不得通过 CSS `order`、与 DOM 冲突的显式网格定位或 JavaScript 排序将两者解耦。
- 顺序约束只依赖 `#module-outputs` 与稳定锚点；不要求固定 HTML 标签、编号 class、连续兄弟节点或一致卡片宽度。
- 已讨论的字段正常展示内容；未讨论的字段显示"未讨论"并标为缺口。
- 质量面板（quality-panel）的锚点 ID 统一使用 `quality-*` 前缀，两种页面共享。
- 对齐状态放在 quality-panel 的 `alignment-section` 内，两种页面共享。

## 共享结构

两种页面都包含以下共享部分：

```html
<aside id="quality-panel">
  <h3>质量与对齐</h3>
  <div id="quality-version">v{N}</div>
  <div id="quality-approval">
    <!-- gate_recommendation / render_authorized / confirmation_mode -->
  </div>
  <div id="quality-gaps">缺口摘要</div>
  <div id="quality-risks">风险摘要</div>
  <div id="quality-caveat" hidden>
    <!-- 仅 override 时显示，含 override 项数量、高风险项数量、风险详情 -->
  </div>
  <section id="alignment-section">
    <h4>对齐状态</h4>
    <div id="alignment-consensus">...</div>
    <div id="alignment-divergences">...</div>
    <div id="alignment-decisions">...</div>
  </section>
</aside>
<section id="local-notes" contenteditable="true">...</section>
<script type="application/json" id="canvas-data">
  {
    "version": "v{N}",
    "module": "M{N}",
    "sections": { ...确认包 section 映射... },
    "generation_path": "m1-m6 | transcript-direct",
    "instance": "{slug}",   // 仅 instance 化输出（非 MVL / MAAU transcript-direct）
    "source_file": "modules/Mx-v{N}.md | modules/MAAU-{slug}-v{N}.md",
    "workflow": { "nodes": [ { "id": "w0", "type": "start", "label": "..." }, ... ], "edges": [ { "from": "w0", "to": "w1" }, ... ] },  // 全局页 Workflow 流程图派生拓扑（见 §A1.5）
    "auth": {
      "gate_recommendation": "pass | fail",
      "render_authorized": true,
      "confirmation_mode": "gate_pass | override",
      "override_audit": { ...完整 override_audit 数据，仅 override 时存在... }
    }
  }
</script>
```

**MAAU transcript-direct 标头**：`generation_path=transcript-direct` 的实例页必须含 `[来源: transcript-direct]` 标头；`canvas-data.generation_path`、`instance`、`source_file`、`auth` 四项均须写全，`auth` 与 `state.maau.{slug}` 完全一致。

### Caveat 状态标识

模块详情页头部必须根据 `confirmation_mode` 显示对应状态：

- `confirmation_mode=gate_pass`：显示"已确认"。
- `confirmation_mode=override`：显示"**已确认 · 带保留意见**"。

`#quality-caveat` 仅在 `confirmation_mode=override` 时可见（移除 `hidden`），内容必须包含：

- Gate 建议（pass / fail）
- 最终渲染授权（true）
- override 项数量
- 高风险项数量
- override 理由、确认人、确认时间、补救措施
- 每项的 Gate 项 ID、来源 ID、影响、风险等级

caveat 内容在任何视图下都必须保留，不得隐藏。

## 本地离线约束

- **CSS、JavaScript、图标和字体必须内联或使用系统字体；正式产物禁止依赖本地相对路径外链 CSS**（如 `<link rel="stylesheet" href="shared/canvas-theme.css">`），否则单独传播 HTML 时样式丢失。方案 A（2026-08-09）已把示例模板主题内联，成品须与其一致。
- 禁止通过 `fetch("file.json")` 加载本地数据；浏览器会因 file origin 拦截。
- 禁止用 iframe 打开兄弟 HTML；使用普通相对链接。
- **成品 HTML 必须单文件自包含（CSS 内联），独立传播时无需任何伴随文件**；无网络时仍可展开、筛选、打印和编辑。
- 可编辑字段保存到浏览器 `localStorage` 时，必须标记为"本地批注"，不能覆盖已确认事实源。

## 数据完整性

- 输出页的 `data-version` 必须等于确认包版本 `v{N}`。
- 页面内嵌数据必须来自同一次读取，不允许手工复制后再改写。
- HTML 中的结论 ID、缺口 ID、引用标识与确认包 Markdown 保持一致。
- `canvas-data` 的 `auth` 字段必须与 `state.json` 同模块记录完全一致；不得手工改写。
- 内容变更后必须升版（vN → vN+1），并把状态退回 `draft` 或 `gaps_open`；旧 HTML 视为过期。
- 引用层级遵循 `../mvl-distill/SKILL.md` 的"不引用逐字稿段落"立场：仅引用 Key Points 与确认包自身的 section。

## 全局下钻

全局 Canvas 的板块使用普通链接，例如：

```html
<a href="./module-1-canvas.html#conclusion-M1-C01">查看 M1 依据</a>
```

不要使用 iframe。这样既避免 `file:` 唯一安全源问题，也允许用户本地双击打开。

### 无模块详情时的链接 / 说明规则

MAAU transcript-direct 实例页是**单源一次性综合**，没有 M1-M6 模块详情页：

- 不得生成指向 `module-{1-6}-canvas.html` 的下钻链接（这些文件在 transcript-direct 下不存在）。
- 六板块内容直接展示在实例页内；如需补充依据，用普通相对链接指向源包 `modules/MAAU-{slug}-v{N}.md` 或直接展示在对应板块，不伪造模块详情页。
- 全局下钻章节仅适用于 Phase 2（M1-M6）全局汇总；transcript-direct 实例页不适用。

### 可选索引页与 Phase 2 全局页冲突规则

- transcript-direct 下可生成可选索引页 `output/maau-global-canvas.html`（聚合全部 `maau.{slug}` 实例的链接列表），此时它**不是** M1-M6 Phase 2 全局页。
- **冲突规则**：同一 group 的 MAAU 输出只能二选一——transcript-direct 实例页（可配可选索引）或 M1-M6 Phase 2 全局页。不得把两者同时作为正式输出，也不得把 transcript-direct 实例混入 M1-M6 Phase 2 全局页的六模块下钻。
- 索引页为派生视图，不写任一 instance 的 `output_file`；生成后运行对应 audit 的 `--index` 检查。

## 管理层阅读

- 正常确认的模块（`confirmation_mode=gate_pass`）不显示 caveat 标识。
- override 模块（`confirmation_mode=override`）必须保留 caveat 标识与风险详情。
- 全局 Canvas 管理层摘要分开呈现：无保留确认结论 / 带保留意见的结论 / 未验证假设 / 关键风险 / 补救动作（Owner + 日期）。

## 交付前自检

交付采用两阶段校验：

1. **Python 静态审计**：运行 `skills/canvas-render/scripts/audit_canvas_html.py`，检查页面/版本元数据、契约结构、稳定锚点存在性与顺序、`canvas-data`、授权一致性、离线安全及 caveat 必需结构。模块锚点顺序由脚本直接读取本契约的 M1–M6 映射表，不维护第二份清单。
2. **精简浏览器视觉验收**：只检查 Python 无法可靠判断的桌面、窄屏实际布局，包括阅读顺序、溢出、遮挡、堆叠、caveat 可见性与选定视觉模式的呈现结果。

Python 审计或浏览器视觉验收任一失败均阻断交付；二者全部通过后才可把模块标记为 `rendered`。浏览器验收不重复检查锚点、JSON、授权字段或离线字符串。
