---
id: signal-balanced
visual_system: Signal
layout: balanced
formality: high
density: medium-high
best_for: 领导审阅、正式机构型总览
---

# Signal — 均衡总览版

## 色板 token

| 用途 | Hex / 表达式 | CSS 变量建议 |
|---|---|---|
| 页面背景 | `#d9d6cf` | `--page-bg` |
| Canvas 背景 | `#f0ece3` | `--canvas-bg` |
| Section 背景 | `#f5f1e8` | `--section-bg` |
| 主色 | `#334261` | `--accent` |
| 标题深色 | `#1c2644` | `--accent-deep` |
| 标题渐变终点 | `#2a3658` | `--accent-mid` |
| 柔和灰棕 | `#eee9df` | `--accent-soft` |
| Section 标题柔和色 | `#e6e0d4` | `--section-title-bg` |
| 暖金信号 | `#c8a870` | `--signal-gold` |
| 主文字 | `#17233a` | `--ink` |
| 辅助文字 | `#667085` | `--muted` |
| 普通边框 | `#d6dce7` | `--line` |
| Canvas 边框 | `#b8b1a4` | `--canvas-line` |
| Section 边框 | `#65708a` | `--section-line` |
| 流程节点边框 | `#cac4b4` | `--step-line` |
| 成功状态 | `#eaf8ef` / `#267044` / `#9dcfb0` | `--success-*` |
| 风险状态 | `#f4eadb` / `#765021` / `#c8a870` | `--risk-*` |

灰棕页面、纸张色 Canvas、深海军蓝标题和克制暖金信号构成单一 Signal 系统；暖金只用于摘要边线、控制点和风险提示。

## 字体

- 主字体：`Inter, "Microsoft YaHei", Arial, sans-serif`；不使用外部字体。
- 页面 Hero：`clamp(26px, 3vw, 42px)`，字重 800，颜色 `--accent-deep`。
- Canvas 主标题：`clamp(21px, 2.2vw, 34px)`，字重 800。
- Section 标题：18px，字重 800，颜色 `--accent-deep`。
- 小标题：14px，字重 800。
- 正文与列表：12.5px，行高 1.5。
- 表格：12px；表头字重 800；首列使用深色加粗。
- Eyebrow：11px，字重 800，字距 `.18em`，呈机构档案感。
- 页脚强调语：17px，字重 800。

## 网格

- 页面容器：`max-width: 1500px; margin: auto; padding: 28px 18px 45px`。
- Canvas：13px 内边距、12px 圆角。
- Balanced 主网格：`grid-template-columns: 1fr 1fr 1.4fr; gap: 9px`，第三列用于 Agent Team。
- Workflow 独占整行，横向节点 `gap: 25px; min-width: 150px`。
- Context / Validation：`grid-template-columns: 1fr 1fr; gap: 9px`。
- 两个底部 section 内部均使用三等分网格。
- 1000px 及以下：主网格两列，Agent Team 跨满。
- 700px 及以下：主网格、底部和三联块改为单列；表格与流程保留局部横向滚动；标题带和页脚纵向换行。

## 组件库

- **页面 Hero**：灰棕底上的正式说明区，状态胶囊保持克制，不使用大面积亮色。
- **Canvas**：纸张色背景、`#b8b1a4` 边框、轻阴影，形成正式机构档案感。
- **标题带**：`linear-gradient(110deg, #1c2644, #2a3658)`，白字、7px 圆角；暖金不得作为大面积标题底色。
- **摘要**：`--accent-soft` 背景，4px `--signal-gold` 左边框。
- **Section**：`#f5f1e8` 背景、`#65708a` 边框；标题从 `#e6e0d4` 过渡到 section 背景。
- **编号与小标题**：编号圆点、表头、首列和小标题统一使用 `--accent-deep`。
- **表格**：深海军蓝表头、纸张色单元格、细灰边框；宽表格必须在自身容器滚动。
- **工作流节点**：纸张柔和底、灰棕边框；编号使用深海军蓝，箭头保持克制。
- **质量面板**：使用纸张色卡片和深色标题；风险卡可用暖金边框，但不使用品牌外红色。
- **本地批注**：与档案纸张一致，虚线边框和明确的本地保存提示。
- **页脚**：深海军蓝渐变、白字，保持制度文件式收束。
- **打印**：A3 横向优先，页面背景改白、去阴影；隐藏交互控件，保留版本、确认、风险、质量面板、结论和批注内容。

## 适用场景

- 领导审阅、正式机构型总览、治理方案或政策关联度高的 Canvas。
- 需要同时呈现六大板块，且信息密度中高、阅读语气稳重。
- 读者更看重依据、责任、风险和可审计性，而非视觉活跃度。
- 需要纸张感打印输出和克制的管理层视觉。

## 反例

- 不混入 Blue Professional 的高饱和亮蓝或咨询模板的强品牌红绿橙。
- 不把暖金扩展为大面积背景或装饰渐变。
- 不用过度圆角、玻璃拟态、霓虹阴影或娱乐化图标。
- 不把 flow 两列主网格用于本 balanced 模式。
- 不复制旧模板中的机构标题、流程、角色、数字或结论。
- 不隐藏共享质量面板、本地批注或确认状态。
- 不使用外部资源、CDN 字体、iframe 或网络请求。
