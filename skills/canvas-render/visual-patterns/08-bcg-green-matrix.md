---
id: bcg-green-matrix
zh_name: 波士顿绿·战略矩阵
visual_system: BCG Green
layout: balanced
formality: high
density: medium
best_for: 战略汇报、增长矩阵风格、结构化战略分析
---

# BCG Green — 增长矩阵版

## 色板 token

| 用途 | Hex | CSS 变量建议 |
|---|---|---|
| 页面背景 | `#f5f8f7` | `--bcg-light` |
| 纸张 / Canvas | `#ffffff` | `--paper` |
| BCG Green（结构主色） | `#197a56` | `--bcg-green` |
| 深绿 | `#0e3e1b` | `--bcg-dark` |
| 亮绿 | `#21bf61` | `--bcg-bright` |
| 浅绿 | `#e7f4ec` | `--bcg-pale` |
| 主文字 | `#1a1a1a` | `--ink` |
| 辅助文字 | `#5c6b65` | `--muted` |
| 边框 | `#d5e0db` | `--line` |
| 克制深绿信号 | `#0e3e1b` | `--accent` |
| 成功背景 / 文字 | `#e7f4ec` / `#0e3e1b` | `--success-soft` / `--success-ink` |
| 风险背景 / 文字 | `#fff5db` / `#765100` | `--risk-soft` / `--risk-ink` |

`#197a56` 是标题、section、规则线和结论的唯一结构主色；`#0e3e1b` 负责深色层级，`#21bf61` 只用于方向和连接。精确色值取自 BCG 当前 Careers 生产样式。

## 字体

- 主字体：`Georgia, "Noto Serif SC", "Songti SC", serif`，不加载网络字体。
- 页面 Hero：`clamp(28px, 3.2vw, 44px)`，字重 700，行高 1.2，颜色 `--bcg-green`。
- Eyebrow：10px，字重 700，字距 `.2em`，亮绿。
- 战略摘要：16px，行高 1.6；标签 11px、字重 700。
- Section 标题：14px，字重 700。
- 小标题：12px，字重 700，字距 `.03em`。
- 正文与列表：13px，行高 1.55。
- 表格：12px，表头字重 700。
- 指标：24px，字重 700；标签 10px。
- Matrix 单元：12px；象限标题字重 700。
- 页脚结论：15px，字重 700。

## 网格

- 页面容器：`max-width: 1400px; margin: auto; padding: 36px 32px 48px`。
- Hero 底部使用 4px 深绿规则线，战略摘要位于 Canvas 前。
- Canvas：`padding: 28px 32px 32px`。
- Balanced 主网格：`grid-template-columns: 1fr 1fr 1.4fr; gap: 22px`。
- 底部 Context / Validation：`grid-template-columns: 1fr 1fr; gap: 22px`。
- Workflow：`gap: 16px; padding: 16px`；节点 `min-width: 140px`。
- Matrix：`grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px`。
- 三联内容：`repeat(3, 1fr)`。
- 1100px 及以下：主网格两列，Agent Team 跨满。
- 720px 及以下：页面 padding `20px 16px`；主网格、底部、三联内容和 matrix 全部单列；flow 纵向。

## 组件库

- **Hero**：深绿 serif 标题、亮绿 eyebrow 和 4px 深绿规则线。
- **战略摘要**：浅绿背景、5px 深绿左边框；只陈述战略结论和选择逻辑。
- **Canvas**：白纸、1px 绿灰边框、宽松内边距。
- **Section**：白底、细绿灰边框；标题为深绿实底白字；编号为白底深绿圆点。
- **表格**：浅绿表头、深绿文字、2px 深绿底线。
- **工作流**：浅绿容器、白色节点、3px 深绿顶边；亮绿箭头表示推进方向。
- **2×2 Matrix**：四个单元使用浅绿底和 3px 深绿左边线；必须同时提供横轴、纵轴和象限标题，不能只放四张无坐标卡片。单元内容来自确认包，不得由视觉模式生成。
- **指标**：24px BCG Green 数字；可用单个深绿信号标注需要战略关注的项。
- **质量面板**：浅绿背景、深绿标题，完整显示版本、确认、缺口、风险和 alignment。
- **本地批注**：白底、绿灰虚线边框、深绿 focus outline。
- **页脚**：深绿实底白字，以“战略含义 + 下一步”收束。
- **打印**：页面背景改白、Canvas 去边框；Matrix、节点、质量卡和结论 `break-inside: avoid`；隐藏编辑控件但保留状态与批注内容。

## 适用场景

- 战略汇报、增长矩阵、组合优先级和结构化战略分析。
- 需要把对象放入二维坐标或四象限，同时保留完整六板块 Canvas。
- 信息密度中等，读者关注方向选择、组合关系和长期价值。
- 适合 A3 横向打印和管理层共同标注。

## 反例

- 不为凑齐四象限而编造对象、坐标或战略结论。
- 不把 matrix 当作四张普通卡片；轴、维度和象限语义必须明确。
- 不与 McKinsey 蓝、Bain 红或其他品牌系统混色。
- 不大面积使用亮绿，避免荧光化；不混入旧模板的非官方绿色或金色信号。
- 不复制旧模板中的矩阵内容、指标、结论、角色或脚注。
- 不隐藏共享质量面板、本地批注、确认和风险状态。
- 不使用外部字体、图表库、脚本、iframe 或远程资源。
