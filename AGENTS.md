# AGENTS.md

> 面向在本项目内工作的 AI Agent。先读 [README.md](./README.md) 再开始。

## 规则

### 1. 动手前先读 README

先读 [README.md](./README.md) 了解项目全貌，再按任务类型读对应文档（`SKILL.md` / `DEVELOPMENT.md` / `DESIGN.md` / `docs/user-guide.md` 等）。术语不确定先查证，不要凭模型先验推断。

### 2. 遇到设计问题必须先问用户

涉及状态机、数据源、Skill/Agent 边界、字段定义、Gate 规则、模板、SemVer、文档边界或任何"按惯例/默认"的选择时，**先停下来**列方案与影响，等用户拍板再实现。不确定是不是设计问题，按"是"处理，先问再做。

### 3. 渲染必须通过 canvas-render Skill，禁止内容渲染脚本

- **禁止新增或使用"内容渲染"脚本**（如 `scripts/render_canvas.py` 等任何把已确认业务事实写成 HTML/撰写业务内容的脚本）；渲染统一通过调用 `canvas-render` Skill 完成，参照 `skills/canvas-render/examples/` 对应画布示例模板生成画布。
- **几何展开工具为官方资产**：`skills/canvas-render/scripts/workflow_layout/` 可执行几何展开与 §A1 SVG 内部结构生成，产出可嵌入 `#workflow-flow` 的最终 `<svg>`（`--fragment`）；`--svg` 保留目检预览。工具不撰写业务内容、不渲染整页 HTML；HTML 外层、图例、完成条件由 `canvas-render` Skill 负责，完整页面仍须通过 L1/L2 及按需 L3。
- `skills/canvas-render/scripts/audit_canvas_html.py` 是**审计**工具（校验产物结构与授权元数据），不是渲染工具；渲染后必须用它做静态审计。
- 画布类型判定（`canvas_type`）、渲染契约（`render-contract-*.md`）、视觉模式（`visual-patterns/`）以 `skills/canvas-render/` 为准，不另起渲染实现。
- 除上述官方几何展开工具外，若未来确需其他自动化渲染 / 注入入口，先按规则 2 提出设计变更，经用户确认后再实现。
