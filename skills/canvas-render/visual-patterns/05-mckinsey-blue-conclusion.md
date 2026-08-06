---
id: mckinsey-blue-conclusion
zh_name: 麦肯锡蓝·结论驱动
visual_system: McKinsey Blue
layout: balanced
formality: high
density: medium
best_for: 高管汇报、结论先行、数据驱动的 Storyline
---

# McKinsey Blue — 结论驱动版

## 色板 token

| 用途 | Hex | CSS 变量建议 |
|---|---|---|
| 页面背景 | `#f4f7f8` | `--page-bg` |
| 纸张 / Canvas | `#ffffff` | `--paper` |
| 企业深蓝（结构主色） | `#051c2c` | `--mc-blue` |
| Electric Blue（辅助） | `#2251ff` | `--mc-electric` |
| Cyan（克制强调） | `#00a9f4` | `--mc-cyan` |
| 浅蓝 | `#e8f2f7` | `--mc-light` |
| 极浅蓝 | `#f4f7f8` | `--mc-pale` |
| 主文字 | `#1a1a1a` | `--ink` |
| 辅助文字 | `#5a6573` | `--muted` |
| 边框 | `#d9e2ec` | `--line` |
| 重点信号 | `#00a9f4` | `--accent` |
| 成功背景 / 文字 | `#edf6f1` / `#245c43` | `--success-soft` / `--success-ink` |
| 风险背景 / 文字 | `#fff3e8` / `#8a4818` | `--risk-soft` / `--risk-ink` |

`#051c2c` 是标题、section、规则线和结论的唯一结构主色；`#2251ff` 与 `#00a9f4` 只用于连接、次级提示和单个重点信号，不形成第二套主色。三者均来自 McKinsey 官方公开 Design System。

## 字体

- 主字体：`Georgia, "Noto Serif SC", "Songti SC", serif`；只使用系统回退，不请求网络字体。
- 页面 Hero：`clamp(28px, 3.2vw, 44px)`，字重 700，行高 1.2，颜色 `--mc-blue`。
- Executive summary：正文 16px，行高 1.6；标签 11px、字重 700、字距 `.12em`。
- Canvas / section 标题：14px，字重 700，字距 `.04em`。
- 小标题：12px，字重 700，字距 `.03em`，可使用短英文大写标签。
- 正文与列表：13px，行高 1.55。
- 表格：12px，表头和首列字重 700。
- 数据指标：24px，字重 700；标签 10px、字距 `.08em`。
- 工作流标题：13px，字重 700；节点序号 / 类型：11px。
- 页脚结论：15px，字重 700。

## 网格

- 页面容器：`max-width: 1400px; margin: auto; padding: 36px 32px 48px`。
- Hero 与 executive summary 位于 Canvas 之前，形成“结论先行 → 结构展开”的阅读顺序。
- Canvas：`padding: 28px 32px 32px`。
- Balanced 主网格：`grid-template-columns: 1fr 1fr 1.4fr; gap: 24px; margin-bottom: 24px`。
- 底部 Context / Validation：`grid-template-columns: 1fr 1fr; gap: 24px`。
- Workflow：横向 flow，`gap: 18px; padding: 18px 16px`；节点 `min-width: 140px`。
- 三联内容：`repeat(3, 1fr)`。
- 1100px 及以下：主网格两列，Agent Team 跨满。
- 720px 及以下：页面 padding 改为 `20px 16px`；主网格、底部和三联内容单列；flow 改为纵向，隐藏连接箭头。

## 组件库

- **Hero**：无大面积色块；标题直接使用主蓝，底部用 4px 主蓝规则线建立 Storyline 起点。
- **Executive summary**：极浅蓝背景、5px 主蓝左边框；必须先给结论，再由 Canvas 展开依据。
- **Canvas**：白色纸张、1px 蓝灰边框、宽松 28–32px 内边距。
- **Section**：1px 蓝灰边框；标题为主蓝实底白字；编号为白底主蓝圆点。
- **内容块**：14px 16px 内边距，块间使用细边框；避免装饰性圆角和阴影。
- **表格**：浅蓝表头、主蓝文字、2px 主蓝底线；行间只保留轻量横线。
- **工作流**：极浅蓝容器；白色节点、3px 主蓝顶边、轻阴影；天蓝箭头只负责顺序。
- **数据指标**：大号深蓝数字配小号大写标签；Cyan 只用于一个需要行动或风险关注的指标。
- **脚注 / 证据**：10px 辅助文字、顶部细线；不得塞入无法追溯的来源。
- **质量面板**：极浅蓝背景、1px 边框、主蓝标题；版本、确认、缺口、风险和 alignment 完整呈现。
- **本地批注**：白底、蓝灰虚线边框，focus 使用主蓝细 outline；与正式事实有明确视觉分隔。
- **页脚**：主蓝实底白字，使用“标签 + 结论”两级结构。
- **打印**：页面背景改白，Hero 规则线缩至 2px，Canvas 去边框和阴影；隐藏编辑控件但保留质量、确认、风险、结论和批注内容。

## 适用场景

- 高管汇报、结论先行、数据驱动 Storyline。
- 信息密度中等，要求先看到一句话结论、关键指标和行动含义。
- 需要正式 serif 语气、宽松留白和清晰证据层级的 Canvas。
- 适合管理层打印审阅或作为讨论材料的第一页式总览。

## 反例

- 不与 Blue Professional 的高饱和渐变标题带或 Signal 灰棕纸张混搭。
- 不把所有数字都做成大号指标；只突出真正影响结论的少量指标。
- 不用旧模板的非官方蓝色或橙色代替本规格中的官方核心色。
- 不使用密集卡片墙、过多圆角、胶囊或娱乐化插图。
- 不把 executive summary 写成事实堆叠；它只承担结论先行。
- 不复制旧模板中的标题、示例指标、结论、脚注或角色内容。
- 不隐藏质量状态和本地批注来保持“演示页”外观。
- 不依赖外部 serif 字体、图标、脚本或网络资源。
