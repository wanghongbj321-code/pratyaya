# Pratyaya 变更日志

> 本文件记录 Pratyaya 专家的正式版本变更。
> 完整 SemVer 与架构说明见 [`README.md`](./README.md) / [`DESIGN.md`](./DESIGN.md) / [docs/MVL-整体架构设计.md](./docs/MVL-整体架构设计.md)。

## [v2.3.0] - 2026-08-07

### 新增功能（MINOR）

- **User Journey 画布**：新增完整用户旅程一等公民画布，独立于 MVL M2 `09-user-journey.md`，不写 `state.modules.M2`。
- **journey-distill Skill**：新增 Journey Key Points、确认包与补问产物，正式主表忠实保留动态阶段 × 5 行合并结构（行动 / 触点与系统 / 情绪 / 等待与返工 / 风险节点）。
- **journey-gate Skill**：新增 6 条 Journey 放行条件（3 条 `information_integrity` + 3 条 `business_risk`），仅 `business_risk` 可由用户显式 override。
- **状态模型升级**：`state.schema.json` 升级为 v2.3，新增可选 `persona` 与 `journey` 区块；Journey override 审计限定 `JOURNEY-GATE-*` 且 `category=business_risk`。
- **canvas-render 扩展**：`canvas_type` 新增 `journey`，新增 `render-contract-journey.md` 与示例映射 `journey` → `examples/canvas-html/user-journey-canvas.html`。
- **Journey 双 Gate 审计**：`audit_canvas_html.py` 新增 `--type journey`；正式交付需 `--template examples/canvas-html/user-journey-canvas.html`，检查动态阶段连续编号、每阶段 5 子锚点、质量锚点、断点摘要、授权与 caveat。
- **示例与测试资产**：新增 `examples/modules/JOURNEY-keypoints.md`、`JOURNEY-v1.md`、`JOURNEY-gaps.md` 与 `tests/fixtures/journey/`，覆盖正式、草稿、override 与故障场景。
- **契约检查器扩展**：新增 Journey 规则（`JOURNEY_SKILL_PATH` / `JOURNEY_GATE_FILE_SET` / `JOURNEY_ANCHOR_SYNC` / `JOURNEY_EXAMPLE_MISSING` / `JOURNEY_SEVEN_ELEMENTS`）。
- **文档同步**：README / DESIGN / DEVELOPMENT / 用户指南 / 安装指南 / MVL 专题文档同步 v2.3、五类画布、10 个 Skill（+ Persona/Journey）、10 个视觉模式和 Journey 独立边界。

### 兼容策略（非破坏性）

- 既有 MVL / GC / HMW 项目无需迁移；`persona` 与 `journey` 均为可选区块。
- 独立 Journey 结论可被用户人工引用回 MVL，但系统不自动同步，也不修改 MVL 内置方法文件。

## [v2.2.0] - 2026-08-07

### 新增功能（MINOR）

- **用户画像画布**：新增与 MVL、黄金圈、HMW 对等的 Persona 单画像画布，结构固定为 9 基本信息、6 宫格和 4 项质量鉴别；不生成全局汇总，也不改变 MVL M2 的内置用户画像方法。
- **Persona Skills**：新增 `persona-distill` 与 `persona-gate`，确认包命名为 `PERSONA-v{N}.md`，Gate 仅提出建议，只有 `PERSONA-GATE-03/04` 的 business_risk 允许用户显式 override。
- **渲染与审计**：新增 `render-contract-persona.md`、Persona 示例模板、`audit_canvas_html.py --type persona` 和不可 override 的 `PERSONA-TPL-GATE-01~06`。
- **状态模型**：state schema 升至 2.2；`persona` 与既有 `hmw` 都保持可选，Persona 正式授权读取 `state.persona`。

### 兼容策略

- Persona 与 MVL M2 `08-user-persona.md` 并存、可人工引用但不建立依赖。
- 渲染继续由 `canvas-render` Skill 完成，不新增渲染脚本；正式 Persona 输出须通过内容/授权 Gate 与 Template Gate。

## [v2.1.0] - 2026-08-06

### 新增功能（MINOR）

- **HMW 画布**：新增完整的 HMW（How Might We，问题重构）画布支持，作为与 MVL、黄金圈同级的第三类一等公民画布。
- **hmw-distill Skill**：HMW 提炼（Key Points + 确认包生成），含陈述四字段、质量鉴别（第 6a 节）、想法种子（第 6b 节）、想法↔HMW 对应（第 6c 节）。
- **hmw-gate Skill**：HMW 门禁（6 条放行条件：4 info_integrity + 2 business_risk）。
- **canvas-render 扩展**：`canvas_type` 新增 `hmw`，新增 `render-contract-hmw.md`（8 固定想法锚点 `hmw-idea-1`…`hmw-idea-8`）；示例映射表新增 `hmw` → `examples/canvas-html/hmw-canvas.html`。
- **一等公民示例模板**：新增 `examples/canvas-html/hmw-canvas.html`（与 user-persona / goden-circle 同款黑灰骨架 + HMW 签名 4 字段陈述 + 2×4 八想法格 + 独立质量鉴别 / 想法对应 / 治理面板，占位内容规范 `data-state="placeholder"`）。
- **双 Gate 审计模型**：`audit_canvas_html.py` 新增 `--type hmw` 与 `--template` 参数，HMW 正式交付走两个独立检查面——`[CONTENT/AUTH GATE]`（版本/事实源/授权/锚点/canvas-data）+ `[TEMPLATE GATE]`（`HMW-TPL-GATE-01~06` 结构完整性，**不可 override**）；模板自身先通过结构自审计才放行成品；`--template` 缺失时 FAIL（`HMW-TPL-GATE-00`）。
- **渲染 smoke 脚本**：新增 `scripts/render_canvas.py`（确认包 → 模板骨架 → 临时 HTML），供集成验证。
- **测试基础设施入库**：`tests/` 从 `.gitignore` 移除，测试作为发布 Gate 随专家包发布（§14 完成定义）；新增 state v2.1 fixtures、HMW 结构一致性测试与双 Gate 审计测试（59 用例）。
- **状态模型升级**：`state.schema.json` 从 v2.0 升级到 v2.1——新增**可选**顶层 `hmw` 区块（向后兼容，无破坏性变更）；`override_audit.assessment_id` 正则扩展为 `^(M[1-6]|GC|HMW)-GATE-[0-9]+$`。
- **Agent 多画布路由**：步骤 -1 增加 HMW 分支，新增 Phase HMW（8 步工作流），指令卡新增 HMW 行；Phase 0 新项目三区块（mvl/golden_circle/hmw）初始化，旧项目按需追加 hmw。
- **契约检查器扩展**：新增 5 条 HMW 规则（`HMW_SKILL_PATH` / `HMW_GATE_FILE_SET` / `HMW_TEMPLATE_MISSING` / `HMW_INF_ID` / `HMW_TPL_GATE_UNIQUE`），规则族 31 → 37 条。
- **视觉模式**：复用现有 10 个候选（不新增），默认 `10-black-gray-professional`。
- **与 M3 的关系**：HMW 为完全独立画布；MVL 的 M3 hmw 子模块保持不变（两套并存，可引用不依赖）。

### 兼容策略（非破坏性）

- 既有 v2.0 项目无需迁移：`hmw` 区块为可选，旧 `state.json` 不含该区块仍合法；进入 HMW 流程时按需追加。
- 既有 MVL / 黄金圈渲染与审计命令不变（默认 `--type mvl`；GC 用 `--type gc`）。

### 迁移说明（新增项目）

- 新项目在 Phase 0 同时建 `modules` / `golden_circle` / `hmw` 三区块（见 [agents/pratyaya.md](./agents/pratyaya.md) Phase 0）。
- HMW 正式渲染必须携带 `--template examples/canvas-html/hmw-canvas.html`（双 Gate 前置条件）。

### 变更文件

- 新增：`skills/hmw-distill/`、`skills/hmw-gate/`、`render-contract-hmw.md`、`examples/canvas-html/hmw-canvas.html`、`scripts/render_canvas.py`、`tests/`（fixtures + 3 个测试文件）
- 修改：`plugin.json`（v2.1.0）、`agents/pratyaya.md`、`canvas-render/SKILL.md`、`audit_canvas_html.py`、`check_contract_consistency.py`、`schemas/state.schema.json`（v2.1）、`schemas/README.md`、`README.md`、`DESIGN.md`、`DEVELOPMENT.md`、`docs/user-guide.md`、`docs/installation.md`、`docs/MVL-整体架构设计.md`、`examples/state-v2-sample.json`、`.gitignore`

### 后续修正（不升版）

> v2.1.0 曾引入的渲染脚本 `scripts/render_canvas.py` 违背 AGENTS.md 规则 3「渲染必须通过 canvas-render Skill，禁止渲染脚本」，已移除。渲染回归 canvas-render Skill 人工完成；双 Gate 审计测试改为直接以 `examples/canvas-html/hmw-canvas.html` 模板做结构审计，不再有运行时渲染的正式产物。相关 `DEVELOPMENT.md` 命令与内部执行计划已同步改写。

## [v2.0.0] - 2026-08-06

### 破坏性变更（MAJOR）

- **项目目录迁移**：新项目使用 `workshop/{项目名}/`（旧 `mvl-workshop/{项目名}/` 仍可识别）。
- **状态模型升级**：`state.schema.json` 从 v1.0 升级到 v2.0——`current_module` 和 `modules` 降为可选字段，新增顶层 `golden_circle` 对象。
- **专家身份变更**：`displayName` 从 `Pratyaya MVL Expert` 改为 `Pratyaya Canvas Expert`。

### 新增功能

- **黄金圈画布**：新增完整的 Golden Circle 画布支持（WHY/HOW/WHAT 三层，四阶段管线）。
- **gc-distill Skill**：黄金圈提炼（Key Points + 确认包生成），含跨层一致性（第 6a 节）。
- **gc-gate Skill**：黄金圈门禁（6 条放行条件：4 info_integrity + 2 business_risk）。
- **视觉模式 10**：`10-black-gray-professional`（黑灰专业·打印版），作为默认配色方案。
- **中文展示名**：所有 10 个视觉模式新增 `zh_name` 字段（模式选择时优先展示）。
- **canvas-render 扩展**：支持 `canvas_type` 参数（`mvl` / `golden-circle`），`render-contract-gc.md`。
- **审计脚本扩展**：`audit_canvas_html.py` 新增 `--type gc`，支持 GC 画布校验。
- **通用画布入口**：`defaultInitPrompt` 改为询问画布类型，`quickPrompts` 新增黄金圈入口。
- **Agent 多画布路由**：步骤 -1 先判定画布类型，Phase GC 独立 8 步工作流。

### 变更文件

- 新增：`skills/gc-distill/`、`skills/gc-gate/`、`render-contract-gc.md`、`10-black-gray-professional.md`、`schemas/state.schema.json`（v2.0）
- 修改：`plugin.json`（v2.0.0）、`agents/pratyaya.md`、`canvas-render/SKILL.md`、`visual-patterns/README.md`、`audit_canvas_html.py`、`check_contract_consistency.py`、`README.md`、`schemas/README.md`、测试文件

## [v1.0.2] - 2026-08-01

### 字段对齐

- `profession` 的中英文值改为与 `displayName` 一致（统一为 `Pratyaya MVL Expert`），影响 `.codebuddy-plugin/plugin.json` 与 `agents/pratyaya.md` frontmatter。

### 文档去重

- 6 个文档（README / DEVELOPMENT / DESIGN / docs/installation / docs/MVL-整体架构设计 / docs/user-guide）删除重复的"版本：v1.0.X"行，改为指向 `.codebuddy-plugin/plugin.json` `version` 字段为权威。后续升版仅需改 `plugin.json` 与本文件。

## [v1.0.1] - 2026-08-01

### 措辞调整

- 精简 `displayDescription.zh` 至开发指导要求的 40-50 字区间。原 49 字符的"AI 原生的 MVL（Minimum Verifiable Loop，最小可验证自治闭环）工作坊引导专家包"过长，按 `workbuddy-expert-开发指导.md` §10.1 硬约束改为 30 字符的"AI 原生的 MVL 工作坊引导专家，蒸馏转写、卡模块结论、生成画布"。仅一处文件一处字段的措辞变更，不影响功能与契约。

## [v1.0.0] - 2026-08-01

### 初始版本

- 初始化 `pratyaya` 专家身份，展示名称统一为 `Pratyaya MVL Expert`。
- 提供 MVL 工作坊引导、转写提炼、模块 Gate 建议与 Canvas 渲染能力。
- 建立 Key Points → 提炼 → Gate → 渲染四阶段管线。
- 建立 `draft → gaps_open ↔ review_ready → confirmed → rendered` 五态生命周期。
- Gate 仅提供建议，用户是最终决策者。
- 正式渲染要求 `render_authorized=true` 且 `confirmation_mode ∈ {gate_pass, override}`。
- 提供 9 个 Markdown Canvas 视觉模式及离线 HTML 渲染契约。
