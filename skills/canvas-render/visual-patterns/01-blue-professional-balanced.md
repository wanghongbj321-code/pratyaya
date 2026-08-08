---
id: blue-professional-balanced
zh_name: 蓝色专业·均衡
visual_system: Blue Professional
layout: balanced
formality: medium-high
density: medium
best_for: 内部方案、管理层均衡总览
---

# Blue Professional — 均衡总览版

## 色板 token

| 用途 | Hex / 表达式 | CSS 变量建议 |
|---|---|---|
| 页面背景 | `#f2f3f6` | `--page-bg` |
| Canvas 背景 | `#fdfae7` | `--canvas-bg` |
| Section 背景 | `#fffdf1` | `--section-bg` |
| 主色 | `#1e2bfa` | `--accent` |
| 标题渐变起点 | `#1727d8` | `--accent-deep` |
| 标题渐变终点 | `#2536ff` | `--accent-bright` |
| 柔和强调色 | `#f0f1ff` | `--accent-soft` |
| Section 标题柔和色 | `#eef0ff` | `--section-title-bg` |
| 主文字 | `#17233a` | `--ink` |
| 辅助文字 | `#667085` | `--muted` |
| 普通边框 | `#d6dce7` | `--line` |
| Canvas 边框 | `#c7ceda` | `--canvas-line` |
| 控件边框 | `#c9d1dd` | `--control-line` |
| Section 边框 | `color-mix(in srgb, var(--accent) 62%, #ccd4e1)` | `--section-line` |
| 工作流边框 | `color-mix(in srgb, var(--accent) 35%, #dddddd)` | `--step-line` |
| 成功背景 | `#eaf8ef` | `--success-soft` |
| 成功文字 | `#267044` | `--success-ink` |
| 成功边框 | `#9dcfb0` | `--success-line` |
| 风险背景 | `#fff4e5` | `--risk-soft` |
| 风险文字 | `#8a4b08` | `--risk-ink` |

实现时以 Blue Professional token 覆盖通用组件，不得混入 Signal 的灰棕色或咨询公司模板的强品牌色。

## 字体

- 主字体：`Inter, "Microsoft YaHei", Arial, sans-serif`；只使用系统可用字体，不加载网络字体。
- 页面 Hero：`clamp(26px, 3vw, 42px)`，字重 800。
- Canvas 主标题：`clamp(21px, 2.2vw, 34px)`，字重 800。
- Section 标题：18px，字重 800。
- 小标题：14px，字重 800。
- 正文与列表：12.5px，行高 1.5。
- 摘要：14px，行高 1.5。
- 表格：12px；表头字重 800；首列字重 800。
- Eyebrow / 标签：11px，字重 800，字距 `.14em`–`.18em`。
- 工作流标题：13px，字重 800；辅助文字使用 `--muted`。
- 页脚强调语：17px，字重 800。

## 网格

- 页面主容器：`max-width: 1500px; margin: auto; padding: 28px 18px 45px`。
- Hero：flex 横向布局，左右分布，底部间距 18px。
- Canvas：内边距 13px，圆角 12px。
- Balanced 主网格：`grid-template-columns: 1fr 1fr 1.4fr; gap: 9px`。
- Agent Team 使用较宽的第三列。
- Workflow 独占整行，距主网格 9px。
- 底部 Context / Validation：`grid-template-columns: 1fr 1fr; gap: 9px; margin-top: 9px`。
- Context / Validation 内部三列：`repeat(3, 1fr)`。
- 工作流：横向 flex，gap 25px；节点 `min-width: 150px; flex: 1`，允许横向滚动。
- 1000px 及以下：主网格两列，Agent Team 跨满两列。
- 700px 及以下：
  - 页面 padding 改为 `16px 9px`。
  - 主网格、底部网格和三列组件改为单列。
  - Agent Team 取消跨列。
  - 相邻三列组件改为顶部边框。
  - 标题带允许换行，操作按钮不再使用自动左外边距。
  - 表格容器横向滚动，表格最小宽度 620px。
  - 页脚改为纵向布局。

## 组件库

- **页面 Hero**：白底外的管理层说明区；包含 eyebrow、标题、副标题和成功状态胶囊。状态胶囊使用绿色成功 token。
  - **Pan-Mode Invariants（v2.3.5+）**：Hero 卡片白纸底（沿用 §色板 `--section-bg`/`Canvas` 系统），主色 `#1e2bfa` **仅作用于 eyebrow / 标题色 / 4px 主色底线 / 行动摘要 5px 左线 / pale 卡背景**；不得整片铺主色，更不得将标题带换为"蓝底白字渐变"（与 §反例 "不引入渐变 / 圆润胶囊" 强约束）。
- **Canvas**：`#fdfae7` 背景、1px Canvas 边框、12px 圆角、`0 18px 50px #22314c1f` 阴影。
- **标题带**：蓝色 110deg 渐变、白字、17px 20px 内边距、7px 圆角；左侧 47×47px 半透明 Logo，右侧可放打印按钮。
- **摘要**：`--accent-soft` 背景、左侧 4px 主色边框、12px 15px 内边距。
- **Section**：1.5px 混色边框、8px 圆角、`--section-bg` 背景；标题使用柔和蓝到 section 背景的横向渐变。
- **Section 编号**：25×25px 主色圆形、白字。
- **内容块**：11px 13px 内边距；相邻块以 1px `--line` 分隔。
- **表格**：宽度 100%、折叠边框；表头主色背景白字；单元格 9px 7px 内边距；首列主色加粗。窄屏必须放入可横向滚动容器。
- **工作流节点**：柔和蓝背景、1px 混色边框、8px 圆角、13px 内边距；编号为 27×27px 主色圆形；相邻节点使用主色箭头。
- **三列内容**：桌面为三列，使用竖向分隔线；窄屏改为纵向并使用横向分隔线。
- **质量面板**：沿用 section 语法；状态使用成功或风险 token，不新增另一套卡片语言。
- **本地批注**：浅色 section，明确标注“仅保存在本机，不修改确认事实”；focus 时使用主色 outline。
- **页脚**：主色到深蓝渐变、白字、14px 17px 内边距、7px 圆角。
- **隐私 / 原型说明**：虚线中灰边框、12px 字号；正式业务结论不得放入该说明。
- **交互**：只允许打印、展开/折叠和本地批注；交互 CSS/JS 全部内联。
- **打印**：
  - 页面背景改白。
  - 页面主容器去除外部 padding。
  - 隐藏页面 Hero、导航、隐私说明和编辑/打印控件。
  - Canvas 去阴影和外边框。
  - 保留版本、确认、风险状态、质量面板和结论。
  - 本地批注的编辑提示隐藏；批注内容可打印。

## 适用场景

- 内部方案评审和管理层均衡总览。
- 需要同时呈现 Intent、User、Agent Team、Workflow、Context 与 Validation 的完整全局 Canvas。
- 信息密度中等、需要蓝色专业感但不希望呈现强咨询品牌风格的场景。
- 需要离线打开、打印、窄屏阅读和本地批注的单文件交付。

## 反例

- 不与 Signal 灰棕色、McKinsey serif、Accenture 红灰或其他视觉系统混搭。
- 不把 flow 高密度模式的两列主网格强行套入本 balanced 模式。
- 不省略窄屏表格横向滚动和三列转单列规则。
- 不使用外部字体、CDN 图标、远程脚本、`fetch()` 或 iframe。
- 不复制原模板中的标题、角色、数字、指标、结论或脱敏示例文字。
- 不因页面留白而补写业务事实；缺失内容由 Gate 阻断或按契约显示。
- 不让本地批注覆盖确认包内容或 `canvas-data`。
