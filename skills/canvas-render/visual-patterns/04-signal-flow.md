---
id: signal-flow
zh_name: Signal·流程
visual_system: Signal
layout: flow
formality: high
density: high
best_for: 管理层流程决策、风险与控制点展示
---

# Signal — 流程决策版

## 色板 token

| 用途 | Hex / 表达式 | CSS 变量建议 |
|---|---|---|
| 页面背景 | `#d9d6cf` | `--page-bg` |
| Canvas 背景 | `#f0ece3` | `--canvas-bg` |
| Section 背景 | `#f5f1e8` | `--section-bg` |
| 主色 | `#334261` | `--accent` |
| 标题深色 | `#1c2644` | `--accent-deep` |
| 标题渐变 | `linear-gradient(110deg, #1c2644, #2a3658)` | `--title-gradient` |
| 柔和灰棕 | `#eee9df` | `--accent-soft` |
| 暖金控制信号 | `#c8a870` | `--signal-gold` |
| 主文字 | `#17233a` | `--ink` |
| 辅助文字 | `#667085` | `--muted` |
| 普通边框 | `#d6dce7` | `--line` |
| Canvas 边框 | `#b8b1a4` | `--canvas-line` |
| Section 边框 | `#65708a` | `--section-line` |
| 流程节点边框 | `#cac4b4` | `--step-line` |
| 风险背景 / 文字 | `#f4eadb` / `#765021` | `--risk-soft` / `--risk-ink` |
| 成功背景 / 文字 | `#e7efe9` / `#315c42` | `--success-soft` / `--success-ink` |

暖金只承担控制点、风险和摘要信号；正式机构感仍由灰棕纸张与深海军蓝主导。

## 字体

- 主字体：`Inter, "Microsoft YaHei", Arial, sans-serif`。
- 页面 Hero：`clamp(26px, 3vw, 42px)`，字重 800。
- Canvas 主标题：`clamp(21px, 2.2vw, 34px)`，字重 800。
- Section 标题：18px，字重 800。
- 正文与列表：12.5px，行高 1.5。
- 表格：12px；职责、决策边界和控制列可使用 11.5px，但行高不得低于 1.4。
- 流程节点标题：13px，字重 800；执行主体、风险级别和控制方式：11px。
- 控制点标签：10px–11px，字重 800，字距 `.04em`，不得用全大写长句。
- 页脚强调语：17px，字重 800。

## 网格

- 页面容器：`max-width: 1500px; margin: auto; padding: 28px 18px 45px`。
- Flow 主网格：`grid-template-columns: 1fr 1fr; gap: 9px`。
- Agent Team：跨满两列，职责表必须容纳角色、执行方式、决策边界和升级路径。
- Workflow：独占整行；`padding: 22px 18px`，横向 flow 的 `gap: 25px`。
- 节点：`min-width: 150px; min-height: 118px; flex: 1`；高密度时允许增加宽度，不得缩小字体压入。
- Context / Validation：`grid-template-columns: 1.15fr .85fr; gap: 9px`。
- 流程下方允许使用四列控制摘要：自动化、人工确认、人审 + Agent、关键规则；窄屏转单列。
- 1000px 及以下：主网格两列，Agent Team 跨满。
- 700px 及以下：全部主网格单列；职责表、流程和控制摘要在各自容器内滚动或堆叠，不产生页面级横向溢出。

## 组件库

- **Hero / 标题带**：沿用 Signal 深海军蓝渐变、灰棕纸张和正式状态胶囊。
  - **Pan-Mode Invariants（v2.3.5+）**：Hero 灰棕纸张底（沿用 03 Signal 例外），主海军蓝 `#334261` 仅作用于 eyebrow / 标题色 / 4px 底线 / 摘要 5px 左线 / pale 卡背景；禁止主色整片涂底。
- **摘要**：暖金左边框；一句话只陈述流程治理结论，不堆叠证据细节。
- **Section**：纸张色、深色边框、低圆角；编号和标题使用 `--accent-deep`。
- **职责与决策表**：Agent Team 全宽；末列突出不可授权事项、升级路径和例外处理。
- **高密度流程**：每个节点固定包含序号、动作、执行主体三层；需要时增加风险/控制短标签。节点间用深色箭头，禁止用多色泳道取代单一视觉系统。
- **人工控制点**：使用暖金左边线或顶部短条，配合“人工确认 / 升级 / 停止”等文本；不得只依赖颜色表达含义。
- **风险卡**：使用 `--risk-soft`、`--risk-ink` 和暖金边框，适合 blocker/major 已解决记录或已接受风险。
- **表格**：深海军蓝表头、纸张色单元格、紧凑行距；窄屏横向滚动。
- **质量面板**：以机构档案语法呈现版本、确认、缺口、风险和 alignment；不得隐藏。
- **本地批注**：纸张卡片、虚线编辑区、深海军蓝 focus outline。
- **页脚**：深海军蓝渐变，收束决策、责任人与下一步。
- **打印**：A3 横向；流程节点、控制点、风险卡和质量状态 `break-inside: avoid`；隐藏编辑控件但保留所有治理状态。

## 适用场景

- 管理层流程决策、风险审阅、内控设计和责任边界确认。
- 节点多、控制点多、需要同时解释自动化与人工授权的高密度 Canvas。
- 强调正式性、审计性和异常路径，而非轻量创意讨论。
- 适合横向大屏或 A3 横向打印阅读。

## 反例

- 不把高密度理解为缩小字体或取消留白。
- 不用仅靠红黄绿颜色表达风险与控制；必须有文本标签。
- 不混入亮蓝、咨询品牌红绿橙或玻璃拟态组件。
- 不把 Agent Team 收窄到普通第三列；flow 模式必须给职责与边界足够宽度。
- 不复制旧模板中的流程、角色、风险、指标或结论内容。
- 不在打印中隐藏版本、确认、风险、质量面板或 alignment。
- 不使用外部字体、脚本、图标、iframe 或 `fetch()`。
