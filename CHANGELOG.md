# Pratyaya 变更日志

> 本文件记录 Pratyaya 专家的正式版本变更。
> 完整 SemVer 与架构说明见 [`README.md`](./README.md) / [`DESIGN.md`](./DESIGN.md) / [docs/MVL-整体架构设计.md](./docs/MVL-整体架构设计.md)。

## [v2.1.0] - 2026-08-06

### 新增功能（MINOR）

- **HMW 画布**：新增完整的 HMW（How Might We，问题重构）画布支持，作为与 MVL、黄金圈同级的第三类一等公民画布。
- **hmw-distill Skill**：HMW 提炼（Key Points + 确认包生成），含陈述四字段、质量鉴别（第 6a 节）、想法种子（第 6b 节）、想法↔HMW 对应（第 6c 节）。
- **hmw-gate Skill**：HMW 门禁（6 条放行条件：4 info_integrity + 2 business_risk）。
- **canvas-render 扩展**：`canvas_type` 新增 `hmw`，新增 `render-contract-hmw.md`（8 固定想法锚点 `hmw-idea-1`…`hmw-idea-8`）。
- **审计脚本扩展**：`audit_canvas_html.py` 新增 `--type hmw`，支持 HMW 画布校验。
- **状态模型升级**：`state.schema.json` 从 v2.0 升级到 v2.1——新增**可选**顶层 `hmw` 区块（向后兼容，无破坏性变更）；`override_audit.assessment_id` 正则扩展为 `^(M[1-6]|GC|HMW)-GATE-[0-9]+$`。
- **Agent 多画布路由**：步骤 -1 增加 HMW 分支，新增 Phase HMW（8 步工作流），指令卡新增 HMW 行。
- **视觉模式**：复用现有 10 个候选（不新增），默认 `10-black-gray-professional`。
- **与 M3 的关系**：HMW 为完全独立画布；MVL 的 M3 hmw 子模块保持不变（两套并存，可引用不依赖）。

### 变更文件

- 新增：`skills/hmw-distill/`、`skills/hmw-gate/`、`render-contract-hmw.md`
- 修改：`plugin.json`（v2.1.0）、`agents/pratyaya.md`、`canvas-render/SKILL.md`、`audit_canvas_html.py`、`schemas/state.schema.json`（v2.1）、`schemas/README.md`

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
