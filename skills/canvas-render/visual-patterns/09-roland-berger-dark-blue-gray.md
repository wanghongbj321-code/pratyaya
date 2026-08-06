---
id: roland-berger-dark-blue-gray
zh_name: 罗兰贝格深蓝灰
visual_system: Roland Berger Dark Blue-Gray
layout: balanced
formality: high
density: medium
best_for: 欧洲机构风格、深蓝灰品牌识别、简洁商务汇报
---

# Roland Berger Dark Blue-Gray — 欧洲机构版

## 色板 token

| 用途 | Hex | CSS 变量建议 |
|---|---|---|
| 页面背景 | `#eff0f1` | `--rb-light` |
| 纸张 / Canvas | `#ffffff` | `--paper` |
| Dark Blue（结构主色） | `#004775` | `--rb-dark-blue` |
| Dark Grey（机构中性色） | `#8d9399` | `--rb-dark-grey` |
| Turquoise（克制强调） | `#00aac9` | `--rb-turquoise` |
| 浅蓝灰 | `#e8f6f8` | `--rb-pale` |
| 主文字 | `#1a1a1a` | `--ink` |
| 辅助文字 | `#65747d` | `--muted` |
| 蓝灰边框 | `#ced2d5` | `--line` |
| 青色强调 | `#00aac9` | `--accent` |
| 成功背景 / 文字 | `#eef5f0` / `#315d46` | `--success-soft` / `--success-ink` |
| 风险背景 / 文字 | `#e8f6f8` / `#004775` | `--risk-soft` / `--risk-ink` |

`#004775` 是标题、section、规则线和结论的唯一结构主色；`#8d9399` 只作为机构中性色，`#00aac9` 只作单个连接或重点信号。三者在 Roland Berger 当前官网生产 CSS 中分别标为 `darkblue`、`darkgrey` 和 `turquoise`；不再使用无法证明为当前独占主色的 Orange。

## 字体

- 主字体：`"Helvetica Neue", Arial, "PingFang SC", "Microsoft YaHei", sans-serif`。
- 页面 Hero：`clamp(28px, 3.2vw, 44px)`，字重 700，行高 1.2，颜色 `--rb-dark-blue`。
- Eyebrow：10px，字重 700，字距 `.2em`，Dark Blue。
- Executive summary：16px，行高 1.6；标签 11px、字重 700、Dark Blue。
- Section 标题：14px，字重 700。
- 小标题：12px，字重 700，字距 `.03em`，Dark Blue。
- 正文与列表：13px，行高 1.55。
- 表格：12px，表头字重 700。
- 指标：24px，字重 700，Dark Blue；标签 10px。
- 工作流标题：13px，字重 700。
- 页脚结论：15px，字重 700。

## 网格

- 页面容器：`max-width: 1400px; margin: auto; padding: 36px 32px 48px`。
- Hero 底部使用 4px Dark Blue 规则线；摘要位于 Canvas 前。
- Canvas：`padding: 28px 32px 32px`。
- Balanced 主网格：`grid-template-columns: 1fr 1fr 1.4fr; gap: 22px`。
- 底部网格：`grid-template-columns: 1fr 1fr; gap: 22px`。
- Workflow：`gap: 16px; padding: 16px`；节点 `min-width: 140px`。
- 三联内容：`repeat(3, 1fr)`。
- 1100px 及以下：主网格两列，Agent Team 跨满。
- 720px 及以下：页面 padding `20px 16px`；主要网格与三联内容单列；flow 纵向并隐藏箭头。

## 组件库

- **Hero**：Dark Blue 大标题、同色 eyebrow 和 4px 规则线，保持简洁商务语气。
- **Executive summary**：浅蓝灰背景、5px Dark Blue 左边框；标签使用 Dark Blue。
- **Canvas**：白纸、1px 蓝灰边框、宽松留白。
- **Section**：白底、蓝灰细边框；标题为 Dark Blue 实底白字；编号为白底 Dark Blue 圆点。
- **表格**：浅蓝灰表头、Dark Blue 文字、2px Dark Blue 底线；正文保持深灰。
- **工作流**：浅蓝灰容器、白色节点、3px Dark Blue 顶边；Turquoise 箭头表示推进。
- **指标**：24px Dark Blue 数字与 10px 灰色标签；避免同屏出现过多大号数字。
- **脚注**：10px 辅助文字、蓝灰顶部规则线，来源标签使用 Dark Blue。
- **质量面板**：浅蓝灰背景、Dark Blue 标题和蓝灰边框；完整呈现共享质量与 alignment 字段。
- **本地批注**：白底、蓝灰虚线边框、Dark Blue focus outline。
- **页脚**：Dark Grey 实底白字，通过 Turquoise 短标签连接下一步。
- **打印**：页面背景改白、Canvas 去边框；隐藏编辑控件，保留版本、确认、风险、质量面板、结论和批注内容。

## 适用场景

- 欧洲机构风格、简洁商务汇报、需要深蓝灰识别的管理层 Canvas。
- 信息密度中等，要求 Dark Blue 结构、Dark Grey 中性层级与克制 Turquoise 强调之间取得平衡。
- 适合方案总览、转型议题、行动路线和正式会议材料。
- 需要打印、离线和窄屏阅读的一页式结构化交付。

## 反例

- 不把 Dark Grey 或 Turquoise 升级为第二结构主色。
- 不混入 Orange、红、绿或彩色图表库默认配色。
- 不使用复杂渐变、玻璃拟态、过度圆角或厚重阴影。
- 不把所有普通数字升级为大号橙色指标。
- 不复制旧模板中的标题、指标、结论、角色或脚注内容。
- 不隐藏质量面板、本地批注、确认或风险状态。
- 不加载外部字体、Logo、图标、脚本、iframe 或网络资源。
