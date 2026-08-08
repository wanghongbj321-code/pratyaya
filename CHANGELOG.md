# Pratyaya 变更日志

> 本文件记录 Pratyaya 专家的正式版本变更。
> 完整 SemVer 与架构说明见 [`README.md`](./README.md) / [`DESIGN.md`](./DESIGN.md) / [docs/MVL-整体架构设计.md](./docs/MVL-整体架构设计.md)。

## [v2.3.2] - 2026-08-08

### 重构（PATCH）

- **User Journey 一等公民画布语义对齐**：将 `journey-frame.md` / `journey-spec.md` 5 行主表的第 4 行从 `wait_rework` / 「等待与返工」切换为 `pain_point` / 「痛点」，第 5 行从 `risk` / 「风险节点」切换为 `opportunity` / 「机会」。6a 质量鉴别维度键从 `friction_visible` 切换为 `pain_opportunity_visible`，6b 节标题从「关键断点与机会」切换为「痛点与机会」。`JOURNEY-Fxx` ID 前缀含义由「断点 / 机会」切换为「痛点 / 机会条目」，仍保留该 ID 前缀；6b 数据列新增「来源」列（取值 `user_stated` / `inferred_from_pain_point` / `inferred_from_quality`）。
- **canvas-render 一等公民模板与契约切换**：`user-journey-canvas.html` 与 `render-contract-journey.md` 同步切换：DOM 子锚点从 `journey-stage-{n}-wait-rework` / `-risk` 切换为 `journey-stage-{n}-pain-point` / `-opportunity`；6b section id 从 `journey-frictions` 切换为 `journey-pain-opportunities`；6a / 6b 摘要锚点分别切换为 `journey-quality-pain-opportunity-visible` / `journey-pain-opportunity-summary`。`canvas-data.stages[]` 必填 snake_case 字段从 `wait_rework` / `risk` 切换为 `pain_point` / `opportunity`。
- **audit / 契约检查器同步**：`audit_canvas_html.py` 与 `check_contract_consistency.py` 的 `JOURNEY_STAGE_FIELDS` / `JOURNEY_STAGE_DATA_FIELDS` / `JOURNEY_QUALITY_KEYS` / `JOURNEY_QUALITY_ANCHORS` / `JOURNEY_ANCHORS` / `JOURNEY_MAIN_IDS` / `JOURNEY_TPL_MAIN_IDS` / `required_anchors` 全部切换；反向白名单落地：审计任意产品不再接受旧 anchor / 旧 data 字段，2 个新增故障夹具（`legacy_dom_anchors_rejected` / `legacy_quality_dimension_rejected`）覆盖旧契约拒绝。
- **JOURNEY-gate 6 条放行条件同步**：`JOURNEY-GATE-03` 的覆盖要求由「至少 2 个等待 / 返工信息、1 个风险节点」切换为「至少 2 个痛点、1 个机会」；GATE-03 / GATE-06 的来源字段由 `friction_visible` 切到 `pain_opportunity_visible`；来源 ID `JOURNEY-friction` 切到 `JOURNEY-pain-opportunity`。
- **示例 / fixtures / 测试资产同步**：`examples/modules/JOURNEY-{keypoints,v1,gaps}.md` 与 `tests/fixtures/journey/` 全部按新字段重写；新增 `JOURNEY-Inf01` 推断（用于支撑 F04 `inferred_from_pain_point` 机会）。
- **离线工作表重构**：`internal/.../docs/refs/canvas-templates/02-用户旅程画布.html`（worksheet）的第 4 / 5 行文案与及格线同步切到新字段；保持 5 行结构、配色切换、emoji 情绪选择、`.mood` 行为不变；不进入运行时模板事实源。
- **plugin.json 升 version**：2.3.1 → **2.3.2**（PATCH）。
- **plugin quickPrompt 切到新口径**：Journey quick prompt 英文与中文文案同步从 `friction points` / 「关键断点」切换为 `pain points and opportunities` / 「痛点与机会」。
- **顶层文档兜底**：`README.md` / `DESIGN.md` / `DEVELOPMENT.md` / `docs/user-guide.md` / `agents/pratyaya.md` 中 5 行主表 / 关键断点 / 痛点与机会摘要措辞同步切换。

### 兼容性

- 旧字段体系（v2.3.1 期）所有相关概念在 v2.3.2 已退场；audit 不再接受旧 anchor / 旧 stage data 字段为合法输入。具体退场概念类别：阶段 5 行主表第 4 / 5 行文本 → 「痛点 / 机会」；6b 节标题 → 「痛点与机会」；6a 质量维度英文键 / 质量鉴别四维度 → 切换为 `pain_opportunity_visible` 统一字段；6b section id / 摘要锚点 / 6a 维度锚点 → pain-opportunity 系列；阶段 DOM 子锚点 / stage data snake_case 字段 → pain_point / opportunity 系列；Gate 来源 ID → `JOURNEY-pain-opportunity` 系列。
- `JOURNEY-Fxx` ID 前缀保留；其内部含义已切换为「痛点 / 机会条目」，但前缀继续指向同一类条目，迁移期不需要替换。
- `state.schema.json` `schema_version` 保持 2.3 不动；现有 MVL / GC / HMW / Persona 业务结论无需迁移。

### 不兼容边界与迁移验收

- **旧 Journey HTML**：v2.3.1 及更早的 `output/journey-canvas.html` 与 `user-journey-canvas.html` 不做就地兼容；如需新语义，必须用新确认包重渲染。旧 HTML 仅作阅读用。
- **旧 JOURNEY-v{N}.md 确认包**：不得直接按新契约渲染；必须迁移为新版本或重新提炼（见 `render-contract-journey.md` 兼容性边界段）。
- **旧 JOURNEY-keypoints.md**：可作为 Stage 2 的背景输入，但 Stage 2 必须按新列头生成确认包。
- **旧 canvas-data.stages[]**：`wait_rework` / `risk` 不再是 v2.3.2 必填字段；audit 一旦发现产物只含旧字段，将报 `JOURNEY-TPL-GATE-04` 并 FAIL。
- **迁移验收硬要求**：迁移后的确认包必须重新跑 `journey-gate`，**不能沿用旧 Gate 结论**。具体三步验收：① `python scripts/check_contract_consistency.py`；② 在 agent 中按 `skills/journey-gate/SKILL.md` 流程跑 6 条放行条件（`JOURNEY-GATE-01` 至 `JOURNEY-GATE-06`）；③ 渲染前 audit 必填检查（`audit_canvas_html.py --type journey --template skills/canvas-render/examples/user-journey-canvas.html --source ... --state ...`）。3 条命令全部 PASS 后方可视为 v2.3.2 新契约产物。audit 中的任何 `JOURNEY-TPL-GATE-*` FAIL 都属于**不可 override** 的 Template Gate 错误。

## [v2.3.1] - 2026-08-08

### 修复（PATCH）

- **示例库与审计脚本随 skill 安装**：解决 WorkBuddy 安装专家时 `examples/canvas-html/` 与 `scripts/audit_canvas_html.py` 未随 `canvas-render` skill 打包、安装态下 SKILL.md / render-contract 的相对路径引用悬空的问题。`examples/canvas-html/` 整体迁入 `skills/canvas-render/examples/`、`scripts/audit_canvas_html.py` 迁入 `skills/canvas-render/scripts/`，使渲染管线依赖随 skill 子树随装。
- **audit 脚本自身常量同步**：`Path(__file__).resolve().parents[1]` 迁入后变为 skill 根，对应契约常量（5 处）与 HMW/Journey Template 常量改为 skill 相对（`references/...`、`examples/...`）。
- **路径基准区分**：`SKILL.md` / render-contract 中正文描述性引用统一改为 skill 内相对（`examples/...`），可执行命令行保留"以专家包根目录为 cwd"的语义并加 `skills/canvas-render/` 前缀（`scripts/audit_canvas_html.py` / `--template skills/canvas-render/examples/...`）。
- **tests / check 脚本同步**：5 个测试文件（含 `test_persona_audit.py` 的 importlib 加载）与 `scripts/check_contract_consistency.py` 对 audit 脚本与示例模板的路径常量、字符串断言（HMW/Persona/Journey）一并更新。
- **文档同步**：`DEVELOPMENT.md` / `AGENTS.md` / `DESIGN.md` / `docs/installation.md` / `agents/pratyaya.md` 中所有 `examples/canvas-html/` 与 `scripts/audit_canvas_html.py` 引用改为仓库根相对 `skills/canvas-render/...`；历史 design/debugs 方案文档与 `CHANGELOG.md` v2.3.0 及之前条目保持原路径不动。
- **保留内容**：`examples/modules/` / `examples/output/` / `examples/state-v2-sample.json` / `scripts/check_contract_consistency.py`（D4=② 仅同步内部路径常量，不随装）保留原地。

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
