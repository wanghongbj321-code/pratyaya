---
id: blue-professional-flow
zh_name: 蓝色专业·流程
visual_system: Blue Professional
layout: flow
formality: medium-high
density: medium-high
best_for: 流程评审、职责与决策边界展示
---

# Blue Professional — 流程决策版

## 色板 token

| 用途 | Hex / 表达式 | CSS 变量建议 |
|---|---|---|
| 页面背景 | `#f2f3f6` | `--page-bg` |
| Canvas 背景 | `#fdfae7` | `--canvas-bg` |
| Section 背景 | `#fffdf1` | `--section-bg` |
| 主色 | `#1e2bfa` | `--accent` |
| 标题渐变 | `linear-gradient(110deg, #1727d8, #2536ff)` | `--title-gradient` |
| 柔和强调色 | `#f0f1ff` | `--accent-soft` |
| Section 标题背景 | `linear-gradient(90deg, #eef0ff, #fffdf1)` | `--section-title-bg` |
| 主文字 | `#17233a` | `--ink` |
| 辅助文字 | `#667085` | `--muted` |
| 普通边框 | `#d6dce7` | `--line` |
| Canvas 边框 | `#c7ceda` | `--canvas-line` |
| 流程节点边框 | `color-mix(in srgb, var(--accent) 35%, #dddddd)` | `--step-line` |
| 成功状态 | `#eaf8ef` / `#267044` / `#9dcfb0` | `--success-*` |
| 风险状态 | `#fff4e5` / `#8a4b08` | `--risk-*` |

色板与 01 保持同一 Blue Professional 家族；差异只能来自 flow 网格、流程密度和决策边界组件，不得另引入第二套视觉系统。

## 字体

- 主字体：`Inter, "Microsoft YaHei", Arial, sans-serif`，不得加载网络字体。
- 页面 Hero：`clamp(26px, 3vw, 42px)`，字重 800，行高 1.12。
- Canvas 主标题：`clamp(21px, 2.2vw, 34px)`，字重 800。
- Section 标题：18px，字重 800；流程区标题保持同级。
- 正文与列表：12.5px，行高 1.5。
- 表格：12px；表头与首列字重 800。
- 流程节点标题：13px，字重 800；节点类型和责任边界：11px，行高 1.4。
- Eyebrow：11px，字重 800，字距 `.14em`–`.18em`。
- 页脚强调语：17px，字重 800。

## 网格

- 页面容器：`max-width: 1500px; margin: auto; padding: 28px 18px 45px`。
- Canvas：13px 内边距、12px 圆角。
- Flow 主网格：`grid-template-columns: 1fr 1fr; gap: 9px`；Intent 与 User 并排。
- Agent Team：`grid-column: 1 / -1`，横跨主网格，给职责与决策边界表留足宽度。
- Workflow：独占整行；内部 flow 使用横向 flex，`gap: 25px; padding: 22px 18px; overflow-x: auto`。
- 流程节点：`min-width: 150px; min-height: 118px; flex: 1`，保证标题、执行主体和确认类型三层信息可读。
- 底部 Context / Validation：`grid-template-columns: 1.15fr .85fr; gap: 9px`，让上下文依赖获得更多宽度。
- 三联内容仍使用 `repeat(3, 1fr)`。
- 1000px 及以下：主网格保持两列，Agent Team 继续跨满。
- 700px 及以下：主网格、底部和三联内容全部单列；表格与流程各自在自身容器横向滚动；标题带和页脚允许换行。

## 组件库

- **页面 Hero / Canvas 标题带**：复用 Blue Professional 的成功胶囊、蓝色渐变标题带、半透明 47×47px Logo 和白色标题体系。
  - **Pan-Mode Invariants（v2.3.5+）**：Hero 卡片白纸底，主色仅作 eyebrow / 4px 主色底线 / 行动摘要 5px 左线；蓝渐变标题带是本模式视觉标识，pan-mode 不消除此差异，但**禁止 hero 整片铺主色 / 禁止将 eyebrow / 标题 / 底线三者同时改为品牌色非信号元素**。
- **摘要**：柔和蓝背景、4px 主色左边框；文案应突出流程目标与决策边界，不填入模式示例数据。
- **Section / card**：暖白底、1.5px 蓝色混合边框、8px 圆角、编号圆点。
- **职责表格**：Agent Team 横跨全宽；首列为角色，末列为决策边界。窄屏使用最小宽度 620px 的滚动表格。
- **工作流节点**：节点顶部先显示编号，再显示动作标题和执行类型；节点间使用蓝色箭头。人工确认、Agent 执行、人审 + Agent 三类节点用同一节点语法，通过文字标签和轻量状态边框区分，不另造颜色系统。
- **控制点**：在流程节点内或紧邻节点放置短标签，明确授权、退回、升级或异常停止；风险标签使用既有 `--risk-*`。
- **质量面板**：状态卡沿用蓝色 section 语法；版本、确认、缺口、风险与 alignment 内容必须可见。
- **本地批注**：暖白卡片内的虚线编辑区；focus 使用主色 outline，批注只写 localStorage。
- **页脚**：与标题带同源的蓝色渐变，用于收束结论与下一步。
- **打印**：A3 横向优先；隐藏导航、编辑提示和打印控件，去除 Canvas 阴影；保留版本、确认、风险、质量面板、结论和批注内容，关键节点与控制点使用 `break-inside: avoid`。

## 适用场景

- 流程评审、职责划分、授权边界和人工确认点较多的管理层讨论。
- 工作流是页面主叙事，且需要同时保留 Intent、User、Agent Team、Context 与 Validation。
- 信息密度中高，但仍需要中性、专业、非强品牌化的蓝色系统。
- 需要横向打印或在桌面宽屏上逐节点阅读的场景。

## 反例

- 不把 balanced 的三列均衡总览当作本模式主网格。
- 不把所有节点压缩到不可读宽度；空间不足时必须使用局部横向滚动。
- 不用额外红、绿、橙色给每类节点建立第二套编码；状态优先使用标签、边框和既有状态 token。
- 不混入 Signal 灰棕、咨询 serif 或其他品牌视觉系统。
- 不复制旧模板中的流程名称、角色、指标、结论或示例数字。
- 不隐藏质量面板、确认状态或风险信息来换取版面紧凑。
- 不使用外部字体、图标、脚本、iframe 或 `fetch()`。
