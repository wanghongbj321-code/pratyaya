---
id: accenture-purple-institutional
visual_system: Accenture Purple
layout: balanced
formality: high
density: medium-high
best_for: 机构审阅、正式机构风格、紫色品牌识别
---

# Accenture Purple — 机构版

## 色板 token

| 用途 | Hex | CSS 变量建议 |
|---|---|---|
| 页面背景 | `#f2f2f2` | `--page-bg` |
| 纸张 / Canvas | `#ffffff` | `--paper` |
| Accenture Purple（结构主色） | `#a100ff` | `--ac-purple` |
| 深紫 | `#460073` | `--ac-dark` |
| 辅助紫 | `#7500c0` | `--ac-secondary` |
| 浅紫 | `#f4e8ff` | `--ac-light` |
| 斑马纹紫灰 | `#eee0ff` | `--ac-stripe` |
| 主文字 | `#1a1a1a` | `--ink` |
| 辅助文字 | `#666666` | `--muted` |
| 边框 | `#d0d0d0` | `--line` |
| 克制深色信号 | `#460073` | `--accent` |
| 成功背景 / 文字 | `#edf5f0` / `#2d6247` | `--success-soft` / `--success-ink` |
| 风险背景 / 文字 | `#f4e8ff` / `#460073` | `--risk-soft` / `--risk-ink` |

`#a100ff` 是 brand bar、section、规则线和页脚的唯一结构主色；`#460073` 与 `#7500c0` 只承担深浅层级。三者来自 Accenture 当前官网生产样式，不再沿用无法成立的红灰品牌归因。

## 字体

- 主字体：`Arial, "Microsoft YaHei", "PingFang SC", sans-serif`。
- 页面 Hero：`clamp(26px, 3vw, 40px)`，字重 700，行高 1.2，字距 `-.02em`。
- Eyebrow：10px，字重 700，字距 `.2em`，主紫。
- Executive summary：15px，行高 1.6；标签 11px、字距 `.12em`。
- Section 标题：13px，字重 700，字距 `.04em`。
- 小标题：12px，字重 700。
- 正文与列表：12.5px，行高 1.55。
- 表格：11.5px，表头字重 700。
- 指标：26px，字重 700；标签 10px。
- 页脚结论：15px，字重 700；说明文字 12.5px。

## 网格

- 页面容器：`max-width: 1400px; margin: auto; padding: 34px 30px 48px`。
- 顶部 6px 主紫 brand bar，Hero 底部使用 1px 灰色规则线。
- Executive summary 位于 Canvas 前，`padding: 18px 22px; margin-bottom: 26px`。
- Canvas：无内部留白外圈，模块直接组成机构表单式整体。
- 主网格：`grid-template-columns: 1fr 1fr 1.4fr; gap: 0`，以共享边框连接。
- 底部网格：`grid-template-columns: 1fr 1fr; gap: 0`。
- Workflow：`padding: 20px 22px; gap: 16px`；节点 `min-width: 130px`。
- Footer：`grid-template-columns: 220px 1fr`，左侧标签 / 责任信息，右侧结论 / 下一步。
- 1100px 及以下：主网格两列，Agent Team 跨满。
- 720px 及以下：页面 padding `18px 14px`；主网格、底部、三联块和 footer 单列；flow 纵向，连接箭头隐藏。

## 组件库

- **Brand bar / Hero**：6px 主紫顶条；Hero 使用黑灰标题、紫色 eyebrow 和右对齐元信息，形成机构公文感。
- **Executive summary**：浅紫背景、5px 主紫左边框；左右可分为固定标签列与结论正文。
- **Canvas**：白底、1px 灰边框、无圆角、无卡片间隙。
- **Section**：相邻区块共享边框；标题为主紫实底白字；编号使用白色方形线框，不用圆点。
- **表格**：浅紫表头、2px 主紫底线、偶数行 `--ac-stripe` 斑马纹。
- **工作流**：浅紫容器；白色节点、1px 灰边框、3px 主紫顶边；连接符用辅助紫线性箭头。
- **数据指标**：26px 主紫数字，配 10px 灰色标签。
- **机构型页脚**：主紫实底双栏；左栏与右栏用半透明白线分隔，适合责任、结论和下一步。
- **脚注**：位于 Canvas 底部，浅灰背景、10px 字号和顶部细边框。
- **质量面板**：浅紫背景、主紫标题与细边框；在机构网格内或其后保持明确版面，不隐藏共享字段。
- **本地批注**：白底或浅紫底、主紫 focus 边线；必须明确“本地保存”。
- **打印**：保留缩至 4px 的 brand bar；页面背景改白、Canvas 去外边框；隐藏编辑控件，保留质量、确认、风险、结论和批注。

## 适用场景

- 机构审阅、正式治理材料、责任与审批链较强的 Canvas。
- 信息密度中高，需要紧凑表格、共享边框和紫色制度感。
- 读者关注角色、流程、控制与正式交付，而非轻量探索。
- 适合 A3 横向打印和归档式阅读。

## 反例

- 不使用圆润卡片、玻璃拟态、柔和大渐变或大量阴影。
- 不把主紫扩展为整页背景；紫色集中在规则线、section 和页脚。
- 不混入旧模板红色或另设第二结构主色。
- 不把零间隙机构网格改成松散卡片墙。
- 不复制旧模板中的机构标题、指标、结论、责任信息或脚注内容。
- 不在打印时隐藏现行契约要求保留的版本、确认和风险状态。
- 不使用外部字体、Logo 图片、CDN 图标、iframe 或网络脚本。
