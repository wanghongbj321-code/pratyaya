# Canvas 示例库

> 本目录存放 pratyaya 各画布类型的**一等公民示例**（静态骨架）。渲染任何画布前，`canvas-render` Skill 按 `canvas_type` 在此目录查找对应示例并参照生成最终画布（见 `skills/canvas-render/SKILL.md`「示例参照」）。

## 示例映射

| canvas_type | 示例文件 | 说明 |
|---|---|---|
| `golden-circle` | [`goden-circle-canvas.html`](./goden-circle-canvas.html) | 黄金圈单画布：WHY / HOW / WHAT 三层 + 跨层一致性 |
| `golden-circle`（索引） | [`gc-canvas-index.html`](./gc-canvas-index.html) | 黄金圈 instance 索引页 |
| `hmw` | [`hmw-canvas.html`](./hmw-canvas.html) | HMW：陈述四字段 + 质量鉴别 + 想法种子 |
| `hmw`（索引） | [`hmw-canvas-index.html`](./hmw-canvas-index.html) | HMW instance 索引页 |
| `persona` | [`user-persona-canvas.html`](./user-persona-canvas.html) | 用户画像：9 基本信息 + 6 宫格 |
| `persona`（索引） | [`persona-canvas-index.html`](./persona-canvas-index.html) | 用户画像 instance 索引页 |
| `journey` | [`user-journey-canvas.html`](./user-journey-canvas.html) | 用户旅程：动态阶段 × 5 行合并结构 + 断点摘要 + 质量鉴别 |
| `journey`（索引） | [`journey-canvas-index.html`](./journey-canvas-index.html) | 用户旅程 instance 索引页 |
| `v2c-vac` | [`v2c-value-attribution-canvas.html`](./v2c-value-attribution-canvas.html) | V2C 价值归因画布：Scenario → Capability → Change → Business Impact → Value 归因链 + 断点 + 质量鉴别 |
| `mvl` | [`mvl-canvas/maau-global-canvas.html`](./mvl-canvas/maau-global-canvas.html) | MVL 全局 Canvas：六大板块汇总视图 |
| `mvl`（模块详情） | [`mvl-canvas/module-1-canvas.html`](./mvl-canvas/module-1-canvas.html) … [`module-6-canvas.html`](./mvl-canvas/module-6-canvas.html) | MVL 六个模块各自的详情 Canvas |

> 新画布类型接入时，按上述惯例在本表追加一行，并参照对应 render-contract 补建示例文件。

## 共享主题

- [`shared/canvas-theme.css`](./shared/canvas-theme.css)：标准 pratyaya 黑灰单色主题（`data-theme="base"`，无配色切换），是主题的**单一事实源**。方案 A（2026-08-09）起，所有示例把该主题 **内联**进各自 HTML 的 `<style>`（单文件自包含、可独立传播），不再通过 `<link rel="stylesheet" href=".../shared/canvas-theme.css">` 外链。修改主题时须同步更新本文件与各示例的内联副本（或用一致性检查防漂移）。

## 职责划分

- **示例**：提供画布"长什么样"的版面与签名视觉事实源。
- **render-contract**（`skills/canvas-render/references/*.md`）：定义锚点与数据映射。
- **visual-patterns**（`skills/canvas-render/visual-patterns/`）：定义视觉模式 token / 候选。

## 定位说明

- 所有示例为**静态骨架**，业务内容以占位 / "未讨论"表示，不编造结论。
- 正式渲染由 `canvas-render` Skill 经"提炼 → 门禁 → 渲染"管线生成到 `output/*.html`。
- 示例可本地双击打开、按 Ctrl/Cmd + P 横版打印。
