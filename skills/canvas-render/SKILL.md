---
name: canvas-render
description: 把已通过 Gate 评估的 MVL 模块确认包（Mx-v{N}.md）渲染为可编辑、可追溯、离线可打开的 HTML Canvas，并在六模块完成后生成可下钻的全局 Canvas。模板选择由 LLM 基于 index.json 自行决定推荐后用户拍板，渲染数据源是 Markdown 而非 JSON。用户要求生成模块画布、全局画布或管理层汇报页面时使用。
---

# Canvas 渲染

这个 Skill 是展示层，不是分析层。只把已确认的 Markdown 事实源（`modules/Mx-v{N}.md`）转成 HTML，不从转写直接提炼，也不为了填满页面新增、润色或补齐业务结论。

渲染前读取 `../mvl-distill/references/workshop-canvas-map.md` 和 `../mvl-distill/references/mvl-canvas-spec.md`。它们定义唯一允许的全局 Canvas 大/小模块及模块详情产出。

同时读取 `references/html-slides-adaptation.md` 和仓库 `html-templates/index.json`。前者把 `html-slides` 中适用于 Canvas 的能力收敛为模板选择、设计系统继承、浏览器预览、打印和离线交付规则；后者登记批准使用的全部视觉外壳清单。

## 正式渲染前置条件

1. 读取 `modules/Mx-v{N}.md`（确认包），不要以聊天上下文或转写作为事实源。
2. 该模块当前状态必须是 `confirmed`，且渲染的版本与确认包 `v{N}` 一致。
3. 该模块必须已经通过 `module-conclusion-gate` 评估（`render_allowed = true`）。
   - Gate 评估由主 agent 步骤 6 调用 `module-conclusion-gate` 后完成，输出 Markdown 格式的 Gate 判定报告。
   - 本 skill 不重新执行 Gate，只读取其结论。
4. 模板已由用户在主 agent 步骤 7 中选定（见下文"视觉外壳选择"）。
5. 条件不满足时返回阻断原因，不得生成没有水印的正式页面。

## 三种模式

### 正式模式（全局 Canvas）

- 输入只能是全部 M1-M6 都已 `rendered`，且所有版本与各模块 `Mx-v{N}.md` 一致。
- 输出 `output/maau-global-canvas.html`。
- 展示六大板块（Intent / User / Agent Team / Workflow / Context / Validation）的汇总视图。
- 页面显示版本、确认人/时间、剩余 minor 缺口和最后更新时间。
- 保留结论 ID，支持从结论下钻到证据摘要（链接到各模块详情 Canvas）。
- 通过 `<a href="./module-N-canvas.html">` 链接下钻到各模块详情 Canvas。

### 模块详情模式（单模块产物）

- **每个模块确认后必须立即生成**，不是等全局汇总时才出。
- 输入只能是该模块 `confirmed` 状态或已通过 Gate 的同版本确认包 `modules/Mx-v{N}.md`。
- 输出 `output/module-N-canvas.html`，完成后该模块状态改为 `rendered`。
- 展示该模块的**全部讨论产出**（M1-M6 各自的固定 section，对照 `render-contract.md` 的字段映射表），不是全局 Canvas 的子板块。
- 页面显示版本、确认人/时间、剩余 minor 缺口和最后更新时间。
- 保留结论 ID，支持从结论下钻到证据摘要。
- 用户说"查看 Mx 产物"或"生成 Mx 模块画布"时，应该生成/展示这个页面。

### 草稿模式

- 仅在用户明确要求"用草稿辅助继续讨论"时生成。
- 数据源：当前最新 Key Points 文件 `modules/Mx-keypoints.md`（**非确认包**，因为尚未确认）。
- 页面顶部和打印版都必须显示"草稿 / 未确认 / 禁止用于管理层决策"。
- 空字段显示"未讨论"或"待确认"，不得自动补写。
- 草稿不得进入全局 Canvas、演示报告或领导汇报。
- 草稿生成不改变模块状态（仍为 `draft` 或 `gaps_open`）。

## 视觉外壳选择（用户驱动）

正式模式与模块详情模式的模板由用户从主 agent 步骤 7 给出的候选中选择。**本 skill 不自动选择模板**。

**主 agent 步骤 7 的选择流程**（本 skill 仅依赖其结果）：

1. 读取 `html-templates/index.json` 获取全部候选模板。
2. LLM 基于以下字段自行判断内容特征，**自行决定**向用户推荐 1-2 个最匹配的模板：
   - `visual_system`（Blue Professional / Signal / McKinsey Blue / Accenture Red-Grey / Bain Red / BCG Green / Roland Berger Orange）
   - `layout`（balanced / flow）
   - `formality`（medium-high / high）
   - `density`（medium / medium-high / high）
   - `best_for`（文字描述）
3. 展示时给出推荐理由（哪条 `best_for` / 视觉系统与当前内容匹配）。
4. 用户选定后主 agent 调用本 skill 渲染。
5. 用户未回应风格选择时，**主 agent**（非本 skill）按主 agent 步骤 7 的安全默认处理。

**本 skill 收到模板选定后的职责**：

1. 读取选定的 HTML 模板 `html-templates/{template-file}.html`。
2. 提取其视觉系统（字体、色板、网格、间距、组件语法），不复制其示例内容。
3. 按 `render-contract.md` 的"Mx-v{N}.md 固定 section → HTML 锚点"映射表，把确认包中的 section 映射到 HTML 锚点。
4. 模板缺少当前规范的 section 时，**在同一视觉系统内补齐**，不删减正式 Canvas 的结构。
5. 完成后做浏览器预览（桌面/窄屏/打印），并执行渲染自检（见下文）。

## 内容与数据契约

- 页面数据来自 `modules/Mx-v{N}.md`（确认包）；不得把业务内容硬编码进组件逻辑。
- 全局页面只能使用映射文件规定的六个大模块及其小模块，不得增加其他方法板块。
- Workflow 必须呈现 AI 应用的完整流向，并分别展示自动化节点（Agent 执行）、人工操作/确认节点、人审 + Agent 执行节点；不能把普通业务流程直接当成最终 Workflow。
- 模块详情页展示该次日程的固定产出（见 `render-contract.md` 的 M1-M6 section 映射）；全局页不塞入 HMW、原型记录、验证明细等过程材料，只提供下钻入口。
- 在 HTML 中嵌入 `<script type="application/json" id="canvas-data">` 保存同版本结构化数据（从确认包 Markdown 提取并整理为 JSON）。
- 每个模块和结论使用稳定锚点，如 `module-M1`、`conclusion-M1-C01`。
- 必须保留事实、决策、假设、建议的视觉区分；推断不能伪装成已确认事实。
- 无外部网络依赖，双击 `file://` 即可打开；不要用 `fetch()` 读取本地文件，不要用 iframe 串联本地 HTML。
- 详细实现契约见 `references/render-contract.md`。

## 渲染自检（替代旧 audit 脚本）

阶段一已移除 `scripts/audit_canvas_html.py`，结构审计职责转为本 skill 的 LLM 自检步骤。正式交付前按以下清单逐项确认：

1. **数据源一致**：HTML 内嵌的 `canvas-data` 与 `modules/Mx-v{N}.md` 内容一致（同版本号、同 section 标题）。
2. **DOM 结构**：对照 `render-contract.md` 章节 A/B 与 M1-M6 section 映射表，全部规定锚点存在。
3. **共享结构**：质量面板 `quality-panel`、对齐 section `alignment-section`、本地批注 `local-notes` 均存在。
4. **离线安全**：无 `fetch("file...")`、无 iframe、无外部网络资源。
5. **打印规则**：`@media print` 隐藏编辑控件，保留版本、确认和风险状态。
6. **草稿标记**：草稿模式下页面顶部与打印版均含"草稿 / 未确认 / 禁止用于管理层决策"字样。
7. **视觉系统单一**：仅继承一种 `visual_system`，不混搭。

任一检查不通过则阻断交付，输出未通过项与建议。

## 全局 Canvas

全局汇总前：

1. M1-M6 全部是 `rendered`，并且指向各自最新确认版本。
2. 按主 agent 阶段 2（全局汇总）的跨模块一致性清单检查目标、用户、流程、能力、数据和验证是否闭合。
3. 若有冲突，回到对应模块升版、重新确认并重新渲染。
4. 全局页面通过普通 `<a href="./module-N-canvas.html#module-MN">` 下钻，不用 iframe。
5. 管理层摘要只呈现已确认结论；未知项与风险单独列出。
6. 标题统一使用"MVL Canvas"；页面明确"模拟环境概念验证原型，非生产级系统"。

## 视觉要求

采用专业商务风，蓝色或低饱和机构色为主，避免大面积高反差色块。信息优先级为：

1. 核心结论与价值判断；
2. 验证状态与关键指标；
3. 决策边界、风险和缺口；
4. 证据与追溯详情。

可以参考仓库 `html-templates/` 的布局和组件，但必须遵守事实源、闸门和离线打开约束。完整适配边界见 `references/html-slides-adaptation.md`。
