---
name: canvas-render
description: 把已通过用户授权的 MVL 模块确认包（Mx-v{N}.md）按用户选定的 Markdown 视觉模式渲染为可编辑、可追溯、离线可打开的 HTML Canvas，并在六模块完成后生成可下钻的全局 Canvas。正式渲染前置条件：state.json 的 render_authorized=true 且 confirmation_mode ∈ {gate_pass, override}；override 时必须携带完整 override_audit。主 Agent 扫描 visual-patterns frontmatter、推荐候选并传递完整模式路径；本 Skill 不自动选模式。用户要求生成模块画布、全局画布或管理层汇报页面时使用。
---

# Canvas 渲染

本 Skill 是展示层，不是分析层。只把已确认的 Markdown 事实源转成 HTML；不得从转写直接提炼，不得为填满页面新增、润色或补齐业务结论。

执行前按需读取：

- `../mvl-distill/references/workshop-canvas-map.md`：全局 Canvas 大小模块映射。
- `../mvl-distill/references/mvl-canvas-spec.md`：模块产出规范。
- `references/render-contract.md`：DOM、共享结构、离线、数据完整性、打印和 caveat 契约。
- `visual-patterns/README.md`：视觉模式的发现、命名、字段、正文结构和阻断规则。

视觉候选只能来自 `visual-patterns/` 的 Markdown 规格；不得从集中登记册或预制 HTML 推断候选与视觉 token。

## 输入契约

正式渲染和模块详情渲染必须同时收到：

1. 确认包路径：按主 Agent 已确定的当前项目工作目录解析 `modules/Mx-v{N}.md`，不得跨项目搜索。
2. 用户授权（来自 `state.json`）：同模块 `render_authorized = true` 且 `confirmation_mode ∈ {gate_pass, override}`；override 时 `override_audit` 完整（含 items、reason、confirmed_by、confirmed_at）。
3. Gate 建议（来自同版本 Gate 报告）：`gate_recommendation`（pass / fail）。
4. 用户选定模式的完整仓库相对路径，例如：

   ```text
   skills/canvas-render/visual-patterns/01-blue-professional-balanced.md
   ```

草稿模式的数据源改为当前最新 `modules/Mx-keypoints.md`，但仍必须收到用户选定模式的完整路径。

收到模式路径后必须校验：

- 路径位于 `skills/canvas-render/visual-patterns/` 内。
- 文件存在，且文件名满足 `NN-{id}.md`。
- frontmatter 恰好包含 `id / visual_system / layout / formality / density / best_for`。
- 文件名 `{id}` 与 frontmatter `id` 一致。
- 正文按顺序包含"色板 token / 字体 / 网格 / 组件库 / 适用场景 / 反例"六节。

任一项失败时阻断并报告具体路径和失败项。不得猜测路径、拼接 ID、静默回退到其他模式或使用其他视觉资产替代。

## 正式渲染前置条件

1. 读取确认包文件，不以聊天上下文、Key Points 或转写作为正式事实源。
2. **模块状态为 `confirmed` 或 `rendered`**，且输出版本等于确认包 `v{N}`。
3. **用户授权**：`state.json` 中同模块 `render_authorized = true`。
4. **确认模式**：`confirmation_mode ∈ {gate_pass, override}`，且与确认包版本一致。
5. **override 审计完整性**（仅 `confirmation_mode=override` 时）：`override_audit.items` 非空、所有 `category=business_risk`、`reason` / `confirmed_by` / `confirmed_at` 必填。
6. 本 Skill 只读取上述状态，不重新评估 Gate，也不得把 `gate_recommendation=fail` 改成 `pass`。
7. 用户已在主 Agent 步骤 7 中明确选定视觉模式。
8. 条件不满足时返回阻断原因，不生成无水印正式页面。

## 三种模式

### 正式模式（全局 Canvas）

- 输入只能是全部 M1–M6 都已 `rendered`，且均指向最新确认版本。
- 输出 `output/maau-global-canvas.html`。
- 展示 Intent / User / Agent Team / Workflow / Context / Validation 六大板块。
- 显示版本、确认人、时间、剩余 minor 缺口、风险、override caveat 与最后更新时间。
- 保留结论 ID，并用普通相对链接下钻到模块详情 Canvas。
- **全局 caveat 浮现**：扫描六模块 `confirmation_mode`，对 `override` 模块在全局页和管理层摘要中显式标注 caveat 与风险摘要。

### 模块详情模式

- 模块 `confirmed` 或 `rendered` 且同版本用户授权后立即生成。
- 输出 `output/module-N-canvas.html`；只有静态自检和浏览器预览都通过后才算成功，并将状态改为 `rendered`。
- 展示该模块在 `render-contract.md` 中规定的全部专属 section，不复刻全局六板块。
- 显示版本、确认、缺口、风险、结论 ID、证据摘要和 caveat 状态。

### 草稿模式

- 仅在用户明确要求"用草稿辅助继续讨论"时生成。
- 数据源只能是当前最新 `modules/Mx-keypoints.md`。
- 页面顶部和打印版永久显示"草稿 / 未确认 / 禁止用于管理层决策"。
- 空字段显示"未讨论"或"待确认"，不得补写。
- 不进入全局 Canvas、管理层报告，也不改变模块状态。

## 视觉模式实现

本 Skill 不选择模式，只实现主 Agent 传入的已选路径。

1. 读取模式 frontmatter 和六节正文。
2. 按"色板 token / 字体 / 网格 / 组件库"实现内联 CSS 与组件。
3. 用"适用场景"校准信息层级，用"反例"检查禁用混搭和错误实现。
4. 按 `render-contract.md` 把确认包 section 映射到稳定 HTML 锚点。
5. 模式未单独描述的业务 section 仍必须补齐，但只复用同一模式的 token 和组件语法。
6. 一个输出只允许一个 `visual_system`。

视觉模式只提供设计语法，不提供业务内容。不得复制模式文档之外的示例标题、角色、数字、指标、结论和品牌内容。

## 内容与数据契约

- 正式页面内容只来自同版本 `modules/Mx-v{N}.md`。
- 全局页只使用规定的六大板块；过程材料留在模块详情页并提供下钻入口。
- Workflow 必须分别呈现 Agent 执行、人工操作 / 确认、人审 + Agent 执行三类节点。
- 内嵌 `<script type="application/json" id="canvas-data">`，内容包含同版本确认包 + 授权元数据（`render_authorized` / `confirmation_mode` / `override_audit`）。
- 每个模块、结论、缺口和共享区域使用 `render-contract.md` 规定的稳定锚点。
- 必须区分事实、决策、假设和建议；推断不得伪装成确认事实。
- 不使用 `fetch()`、iframe、外部字体、外部脚本或外部网络资源。
- 全局下钻只使用普通相对链接。

## Caveat 显式呈现（v4.0.0 新增）

`confirmation_mode=override` 时，本 Skill 必须在模块详情页和全局页显式呈现 caveat：

1. **模块页顶部状态标识**："已确认 · 带保留意见"（caveat 页面仍是正式输出，不使用"草稿 / 未确认"水印）。
2. **`quality-panel`** 显示：Gate 建议、最终渲染授权、override 项数量、高风险项数量。
3. **风险详情**列出：Gate 项 ID、来源 ID、影响、override 理由、确认人、确认时间、补救措施。
4. **打印版**保留以上 caveat 状态和风险，不因打印而隐藏。
5. **`canvas-data`** 内嵌同版本 `override_audit` 全量数据，供前端查询与审计。
6. 正常通过（`confirmation_mode=gate_pass`）时只显示"已确认"，不得出现 override 提示。

## 编辑边界

- 只有明确标记的"本地批注"可编辑。
- 编辑内容只写入浏览器 `localStorage`，不得覆盖确认包内容、稳定锚点或 `canvas-data`。
- 筛选、展开 / 折叠和打印可以使用内联 JavaScript；不得引入幻灯片分页或演示运行时。

## 浏览器预览

正式交付前必须完成人工可见的浏览器检查：

1. 桌面 `1440 × 900`：阅读顺序清晰，无溢出、遮挡、断链。
2. 窄屏 `390 × 844`：卡片合理堆叠，表格和高密度 flow 在自身容器滚动，文字不裁切。
3. 打印：保留结论、版本、确认、风险、质量状态和 override caveat，隐藏编辑提示与操作控件。
4. 离线：本地打开不产生业务网络请求，不使用 `fetch()` 或 iframe。
5. 编辑：本地批注写入、刷新恢复，不影响确认事实。
6. **Caveat 视觉**（仅 override 模块）：caveat 标识与风险详情在桌面、窄屏、打印下均可见。

浏览器检查不能被静态自检替代；两者都通过后才能交付正式 HTML。

## 渲染自检

正式交付前逐项确认：

1. **数据源一致**：`canvas-data` 与确认包同版本、同 section、同 ID。
2. **授权元数据**：`canvas-data` 含 `render_authorized` / `confirmation_mode` / `override_audit`（override 时），与 `state.json` 完全一致。
3. **DOM 结构**：规定的大模块、模块详情 section 和稳定锚点齐全。
4. **共享结构**：`quality-panel`、`alignment-section`、`local-notes`、`canvas-data` 齐全。
5. **离线安全**：无 `fetch()`、iframe 和外部网络资源。
6. **打印规则**：隐藏编辑控件，保留版本、确认、风险、质量状态、结论和 override caveat。
7. **草稿标记**：草稿页面及打印版包含永久未确认标记。
8. **视觉系统单一**：只实现选定模式的 `visual_system`。
9. **模式一致**：实际色板、字体、网格、组件及专属组件符合选定模式，未触发其反例。
10. **Caveat 显示**（仅 override）：页面顶部状态标识、`quality-panel`、风险详情、打印版均含 override 信息。

任一项失败时阻断交付，列出失败项、证据和修订建议。模块状态保持 `confirmed`；不得提前标记为 `rendered`。

## 渲染失败时状态保持规则

静态自检或浏览器验证失败时：

- 模块状态**保持 `confirmed`**（不得回退到 `gaps_open` 或 `review_ready`，业务授权与 HTML 校验是两层问题）；
- `confirmation_mode` 保持原值（`gate_pass` 或 `override`），不修改；
- `gate_recommendation` 不修改（仍是 Gate 的原始建议）；
- 修订同一版本 HTML 后重新执行全部校验；只有全部通过才把状态改为 `rendered`；
- 若修订涉及业务内容，必须按"状态回退"升版并重新确认与 Gate。

## 全局 Canvas

全局汇总前：

1. 确认 M1–M6 全部为 `rendered` 且版本最新。
2. 检查目标、用户、流程、能力、数据和验证的跨模块闭合。
3. **扫描 caveat**：识别 `confirmation_mode=override` 模块；收集 `override_audit.items`；检查下游模块是否依赖被 override 的假设或未验证项。
4. 有冲突时回到对应模块升版、确认和重新渲染，不在全局页静默修正。
5. 管理层摘要**分开呈现**：无保留确认结论 / 带保留意见的结论 / 未验证假设 / 关键风险 / 补救动作（Owner + 日期）。
6. 不得把 override 结论混入"已完全验证"或"无风险"的成果表述。
7. 标题统一使用"MVL Canvas"，并标明"模拟环境概念验证原型，非生产级系统"。

## 明确排除

- 不读取预制 HTML 作为运行时视觉来源。
- 不使用集中模板登记册进行推荐。
- 不要求候选标题页、幻灯片分页、键盘翻页或演示运行时。
- 不以页数替代 Canvas 的完整模块覆盖。
- 不因视觉适配改变工作坊映射、结论状态、版本或质量 Gate。
- 不把 `gate_recommendation=fail` 改写为 `pass`；不擅自重置 `confirmation_mode` 或 `override_audit`。
