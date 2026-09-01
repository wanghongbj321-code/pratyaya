# Pratyaya 变更日志

> 本文件记录 Pratyaya 专家的正式版本变更。
> 完整 SemVer 与架构说明见 [`README.md`](./README.md) / [`DESIGN.md`](./DESIGN.md) / [docs/MVL-整体架构设计.md](./docs/MVL-整体架构设计.md)。

## [v3.1.1] - 2026-09-01

> v3.1.0 未发布（分支未合并即进入优化），Workflow BPMN 流程图功能与三项视觉/契约优化合并为 v3.1.1 一并发布。

### 新增功能（MINOR）

- **Workflow 板块 BPMN 可视化流程图**：MAAU 全局画布（Phase 2 M1-M6 汇总页与 MAAU transcript-direct 实例页）的 Workflow 板块在文本框下方新增派生只读的 BPMN 流程图（`#workflow-flow`）。采用 BPMN 图形语言子集（Start Event / Task / Exclusive Gateway / End Event / Sequence Flow），三类节点用 Service Task（齿轮，Agent 执行）/ User Task（小人头，人工操作/确认）/ 组合节点（人审 + Agent 执行）图标区分；桌面三泳道（Agent 执行 / 人工操作确认 / 人审 + Agent 执行）、窄屏单流横向滚动。
- **数据派生（Q1=A）**：流程图从确认包 Workflow section（`trigger` / `steps` / `completion_condition` + 三类节点 + `rules`）静态生成内联 SVG，**不改数据契约**（`maau-synth-spec.md` / `workshop-canvas-map.md` 不变）；`canvas-data` 顶层新增 `workflow.nodes` / `workflow.edges` 派生拓扑，供静态审计一致性校验。
- **渲染契约**：`render-contract.md` 新增 §A1「Workflow BPMN 流程图（`#workflow-flow`）」DOM 契约、BPMN 子集与元素映射、派生规则、泳道/响应式与拓扑数据约束；示例母版 `examples/mvl-canvas/maau-global-canvas.html` 新增三泳道示例 SVG 与图例（门店补货智能体）。
- **静态审计**：`GLOBAL_MAIN_IDS` 新增 `workflow-flow` 锚点；`audit_workflow_flow` 断言 Start/End Event 存在、`nodes` 覆盖三类节点、SVG `bpmn-node` 数量与 `nodes` 数量一致、`edges.from/to` 引用有效、传入 `--source` 时确认包含三类节点章节。
- **测试**：新增 `tests/test_workflow_flow.py`（7 项）；MAAU fixture `maau-global-canvas-retail-demo.html` 同步补 `#workflow-flow` 与拓扑。

### 优化（PATCH）

- **Sequence Flow 正交化**：所有连接线改为横 / 竖 / 肘型折线（禁止曲线 / 斜线）；所有端点对齐节点边中点（顶 / 底 / 左 / 右边缘中心）；静态审计新增"Sequence Flow 禁止曲线命令（`C`/`Q`/`S`/`A`）"断言。
- **节点编号徽标**：所有 BPMN 节点（含 Start / End）左上角显示流程序号徽标（白底黑色小字号，`01`–`07`，按 Start → End 拓扑序）；`canvas-data.workflow.nodes[]` 新增 `number` 字段；静态审计校验 `number` 存在且唯一。任务类型不使用 BPMN Task Marker 图标，由泳道（桌面）/ 节点在流程中的位置区分；图例只列 Start / Task / Gateway / End 四类图形符号。

### 兼容性与迁移边界

- 无 schema 变更；`state.schema.json` `schema_version` 仍 `"2.3"`。
- 渲染参数不变（仍 `canvas_type=mvl` + `page_type=global`），主 Agent 无需改动。
- 已渲染的旧全局页不包含流程图，需按流程重新渲染才套用新契约。

## [v3.0.0] - 2026-08-13

### 新增功能（MAJOR）

- **V2C Value Attribution Canvas（V2C VAC）一等公民画布**：新增 V2C 系列的 Value Attribution Canvas，来源于王鸿的 Value-to-Capability FDE 工作方法论，支持 `pipeline` 多阶段管道与 `transcript-direct` 一次性综合两种路径，确认包命名为 `V2C-VAC-{slug}-v{N}.md`。
- **V2C VAC 分析与治理 Skill**：新增 `v2c-vac-distill` 与 `v2c-vac-gate`；前者负责 Key Points、阶段提炼、一次性综合、补问清单与确认包，后者负责 `V2C-GATE-01~12`、信息完整性 / 业务风险分类，以及 `V2C-AGxx` 归因断点与 Gate ID 的边界。
- **V2C VAC 状态 schema**：新增 `state.v2c_vac.{slug}` instance map，记录 `generation_path`、`pipeline_stage`、`source_package_path`、`gate_report_path`、override、授权与渲染产物路径；`pipeline` 与 `transcript-direct` 在同一实例内保持互斥。
- **V2C VAC 渲染契约与审计**：新增 `render-contract-v2c-vac.md`、`v2c-value-attribution-canvas.html` 示例模板、`audit_canvas_html.py --type v2c-vac`、`--page-type v2c-vac-index` 与 `V2C-VAC-TPL-GATE-01..08` Template Gate。
- **V2C VAC fixtures 与契约一致性检查**：新增 V2C VAC 正常 / 异常 fixtures 和专项一致性规则，覆盖 Skill 路径、Gate 表、渲染契约、state schema、审计类型与 README / CHANGELOG 版本语义。
- **plugin metadata 升级**：`.codebuddy-plugin/plugin.json` 版本升至 `3.0.0`，description / displayDescription / quickPrompts 纳入 V2C VAC，并移除 MAAU 默认入口表述。

### 变更

- **显式画布路由**：只提供逐字稿或会议材料时不再默认进入任何画布；主 Agent 必须先追问画布类型。MAAU、V2C VAC、MVL M1-M6 与其他画布都必须显式选择。
- **M1-M6 Gate 表格式决策**：正式接受 5 列精简版（`ID / 条件 / 分类 / 风险等级 / 来源`），契约一致性检查器仍兼容历史 8 列详版。

### 兼容性与迁移边界

- `state.schema.json` 顶层 `schema_version` 仍保持 `"2.3"`；V2C VAC 通过 `_meta.v2c_vac_schema_version = "3.0-v2c-vac-1"` 标记派生子版本。
- 旧项目的 `state.json` 即使没有 `v2c_vac` 区块，也可以继续使用既有 MVL、MAAU、黄金圈、HMW、Persona、Journey 等流程；只有首次创建 V2C VAC 实例时才需要写入 `state.v2c_vac.{slug}`。
- 旧 quick prompt 或旧文档中“逐字稿默认进入 MAAU”的理解不再适用；v3.0.0 起逐字稿入口必须显式指定画布和生成路径。
- `v2c` 是 V2C 系列名；Value Attribution Canvas 的机器标识必须使用 `canvas_type=v2c-vac` 与 state key `v2c_vac`。
- 正式 V2C VAC 渲染只能基于已通过 Gate 并获得授权的 `V2C-VAC-{slug}-v{N}.md`；不得直接从逐字稿或未授权草稿渲染。

## [v2.9.1] - 2026-08-09

### 变更（PATCH）

- **MAAU 全局画布母版五要素 3 行错落布局**：`skills/canvas-render/examples/mvl-canvas/maau-global-canvas.html` 的 `.maau-top-grid` 由 5 列并排改为 3 行错落排——Row1 = Intent / User / Agent Team（3 列）；Row2 = Workflow 全宽横贯、内部 5 个字段改 5 列横排；Row3 = Context 全宽横贯、内部 3 个字段改 3 列横排；`<1100px` 窄屏断点内 Workflow / Context 内部字段列同步回退单列，避免挤压。
- 该母版是 MVL 全局画布的"版面与签名视觉唯一事实源"（canvas-render「示例参照」），渲染时 Agent 参照它生成成品，故仅改母版即可让后续渲染套用新布局。
- `audit_canvas_html.py` / `render-contract*.md` / `visual-patterns/` 均不校验五要素网格列数（只校验 id 齐全），无需同步改文档；审计确认 `PASS`。

### 兼容性

- 无 schema 变更；`state.schema.json` `schema_version` 仍 `"2.3"`。
- 布局改动仅影响 MAAU 全局画布母版；已渲染旧产物需按流程重新渲染才套用新布局。

## [v2.9.0] - 2026-08-09

### 新增功能（MINOR）

- **project + group + topic 三层目录**：工作坊产物目录从 `project + group` 双层升级为 `workshop/{project_slug}/{group_id}/{topic_slug}/` 三层。`topic_slug`（kebab-case ASCII）是工作坊议题边界，不替代画布 `instance_slug`（同一 topic 下可有多个 GC/HMW/Persona/Journey/MAAU 画布实例）。
- **topic_meta 元数据**：新增 `topic_meta.json`（`schemas/topic_meta.schema.json`，schema_version=2.7-topic-meta-1），承载 `topic_name` / `topic_owner` / `contact` / `created_at` / `created_by`。
- **group manifest 派生视图**：新增 `workshop/{project_slug}/{group_id}/manifest.json`（`schemas/group_manifest.schema.json`，schema_version=2.7-group-manifest-1），汇总当前 group 的 topics；缺失或陈旧时可重建，不是业务真相源。
- **project manifest 升级**：`workshop/{project_slug}/manifest.json` 从 groups 列表升级为 groups + topics 嵌套视图（`schemas/project_manifest.schema.json` schema_version=2.7-project-manifest-1），`groups[].topics[].state_path` 必须为 `{group_id}/{topic_slug}/state.json`，禁止 `../` / 绝对路径 / 跨组跨 topic 路径。
- **state 下沉为 topic 级**：`state.schema.json` required 增加 `topic_slug` / `topic_name`（schema_version 仍 2.3）；`state.json` 从 group 级下沉为 topic 级状态真相源。
- **旧 project+group 自动迁移**：旧 `workshop/{project_slug}/{group_id}/state.json`（无 topic 子目录）自动迁移到 `workshop/{project_slug}/{group_id}/default/`；`default` 仅作为 legacy topic 占位，新建 topic 禁止使用。
- **Agent / Skill / 文档同步**：`agents/pratyaya.md`（每次对话开始、Phase 0、状态目录、状态查询、切换/新建 topic、legacy 迁移规则）、`skills/faq-answer`、`skills/canvas-render`、`README.md`、`DESIGN.md`、`DEVELOPMENT.md`、`docs/user-guide.md`、`docs/MVL-整体架构设计.md`、`docs/prompt-guide.html` 统一为 `workshop/{project_slug}/{group_id}/{topic_slug}/` 路径，并增加跨 topic 禁读规则。

### 变更（Canvas 单文件自包含 · 方案 A）

- **画布主题内联，禁止本地相对路径外链 CSS**：`canvas-render` 示例模板（HMW / GC / Persona / Journey / MVL 六模块 + MAAU 全局）与 `tests/fixtures/maau/maau-global-canvas-retail-demo.html` 由 `<link rel="stylesheet" href="shared/canvas-theme.css">` 外链改为**内联 `<style>`**（内容取自 `canvas-theme.css`，保留为单一事实源），成品 HTML 单文件自包含、可独立传播。
- **审计脚本收口**：`audit_canvas_html.py` 的 `TPL-GATE-06`（HMW/PERSONA `audit_template_gate` + JOURNEY `audit_journey_template_gate`）从「必须 `<link>` 外链」改为接受「内联 `<style>` 或本地外链」，且**正式产物禁止本地相对路径外链 CSS（应内联）**；通用 `OFFLINE` 检查同步拦截相对外链 CSS（覆盖 MVL/GC）。
- **测试同步**：`test_audit_canvas_html.py` / `test_journey_canvas_audit.py` / `test_audit_maau.py` 相应更新（`copy_template` 去 shared 复制、缺内联主题 token FAIL、外部 URL 注入测试、`add_instance_attr` 行首 `<body>` 匹配）；`canvas-theme.css` 注释改用 `body[data-theme="base"]` 写法避免干扰 `<body>` 匹配。
- **契约文档同步**：`render-contract.md` / `render-contract-hmw.md` / `render-contract-gc.md` / `render-contract-journey.md` / `render-contract-persona.md` / `SKILL.md` / `examples/README.md` 的离线约束升级为「必须内联、正式产物禁止相对外链 CSS、单文件自包含」。
- **内部参考模板单配色化**：`internal/pratyaya-internal/docs/refs/canvas-templates/` 下 6 个参考模板（01-05 + index）由多皮肤（base/mckinsey/accenture + theme-switch）改为**标准黑灰单配色**，内联主题、移除 theme-switch/`brand-bar`/mckinsey 与 accenture 覆盖规则及切换 JS（journey 保留情绪选择 JS）。

### 兼容性

- `state.schema.json` 顶层 `schema_version` 保持 `"2.3"`；新增 `topic_slug` / `topic_name` 为必填，旧 state 需在迁移时补齐。
- 旧 `project + group` 结构自动迁移到 `default` topic，迁移使用 `.migrating-default/` staging，校验后 rename；失败保留旧结构不动并阻断。
- 新建 topic 禁止使用 `default`；topic 重命名不原地改名，按"新建 topic + 迁移产物"处理。
- 全量 `tests/` = 238 passed；契约一致性 error=0, warning=6（GATE_TABLE_WIDTH 既有）。

## [v2.8.0] - 2026-08-08

### 变更（MINOR）

- MAAU 一次性综合（transcript-direct）提升为**默认生成路径**；M1-M6 六模块管线调整为**显式备选路径**。
- 主 Agent 步骤 -1 路由默认翻转：收到逐字稿且未声明画布类型时默认进入 MAAU 综合（Phase 3）。
- 文档（README / user-guide / DESIGN / DEVELOPMENT）同步默认/备选语境；`maau-synthesize` Skill 措辞同步。
- 互斥语义保持不变：MAAU transcript-direct 与 M1-M6 Phase 2 全局汇总同一 group 二选一。

### 兼容性

- `state.schema.json` 顶层 `schema_version` 保持 `"2.3"`，无字段变化。
- M1-M6 六模块管线保留原样可用，仅需显式声明触发；`module-conclusion-gate` / `canvas-render` / 各 distill / gate / `faq-answer` Skill 无契约变化。

## [v2.7.0] - 2026-08-08

### 新增功能（MINOR）

- **MAAU 一次性综合路径（`transcript-direct`）**：新增 `maau-synthesize` Skill，把用户直接提供的一次性逐字稿综合提炼为 MVL 全局画布的六板块源包（Intent / User / Agent Team / Workflow / Context / Validation），产出 `modules/MAAU-{slug}-v{N}.md`。MAAU 综合不是新增画布类型，而是 MVL 全局画布的**平行一次性生成路径**，与 M1-M6 Phase 2 全局汇总互斥（同一 group 的 MAAU 输出只能二选一）。
- **MAAU 独立闸门 ID 空间**：`module-conclusion-gate` 新增 `references/MAAU-gate.md`，`MAAU-GATE-01~09`；`information_integrity` 类 FAIL 不接受 override，`business_risk` 类可 override。
- **MAAU 渲染契约与审计**：`canvas-render` 新增 MAAU transcript-direct 正式模式（实例页 `output/maau-global-canvas-{slug}.html` + `[来源: transcript-direct]` 标头 + 不伪造 M1-M6 下钻）；`audit_canvas_html.py` 新增 `--page-type` / `--generation-path` 与 MAAU 校验（`MAAU_GENERATION` / `MAAU_HEADER` / `MAAU_OVERRIDE` / `MAAU_STATE`）。
- **主 Agent Phase 3**：`agents/pratyaya.md` 新增 Phase 3「逐字稿 → MAAU 源包」编排（冲突分流 / 提炼 / Gate / 授权 / 渲染）+ MAAU 专用指令卡。
- **MAAU schema**：`state.schema.json` 新增顶层 `maau` 区块（`maau.{slug}` instance map，`generation_path` 固定 `transcript-direct`，显式禁 `default`）。

### 兼容性

- `state.schema.json` 的顶层 `schema_version` 仍保持 `"2.3"`；`maau` 为可选区块，无 `maau` 的旧 state 不阻断其他流程（懒加载）。
- MAAU 走独立 `MAAU-GATE-*` ID 空间，不改动 M1-M6 的 Gate 条件与稳定 ID。
- `check_contract_consistency.py` 的 M1-M6 GATE 检查范围调整为 `M?-gate.md`，另增 `MAAU_GATE_TABLE` 专项 Rule 校验 `MAAU-gate.md`。

## [v2.6.0] - 2026-08-08

### 新增功能（MINOR）

- **非 MVL 一等公民画布 instance map**：黄金圈 / HMW / Persona / Journey 从单实例 state 升级为 `state.{state_key}.{slug}`，同一 project/group 可持有多张并列 instance；MVL M1-M6 固定模块结构不变。
- **instance slug 治理**：新增 kebab-case slug 约束；新建 instance 禁止使用 `default`，旧单字段 state 自动迁移时使用 legacy `default` 并触发 `force_consent=true` 提示。
- **多 instance 文件命名**：非 MVL 确认包、Key Points、补问与 Gate 报告采用 `PREFIX-{slug}-...` 命名；正式 HTML 输出采用 `output/{canvas}-canvas-{slug}.html`，原 `output/{canvas}-canvas.html` 转为索引页。
- **legacy 迁移工具**：新增 `scripts/legacy_migration_v2_6_0.py`，把旧单画布 state 迁移为 instance map，并在 `group_meta.json.legacy_migrations.v2_6_0_instance_map` 写入回溯记录。
- **audit instance 支持**：`skills/canvas-render/scripts/audit_canvas_html.py` 新增 `--instance` 与 `--index`，正式非 MVL 审计按 `state.{state_key}.{slug}` 校验授权与 HTML `data-instance` / `canvas-data.instance` 一致性。
- **索引页模板**：新增 GC / HMW / Persona / Journey 四个 instance index 示例模板。

### 兼容性

- `state.schema.json` 的顶层 `schema_version` 仍保持 `"2.3"`，新增 `_meta.instance_map_schema_version = "2.6-instance-map-1"` 作为派生子版本信号。
- 旧单字段 state 必须先迁移；新流程不再把 `state.persona.render_authorized` 等单字段路径作为正式授权来源。
- `default` 只作为 legacy 迁移逃生口存在；用户确认前不得让 legacy `default` instance 进入正式渲染。

## [v2.5.0] - 2026-08-08

### 新增功能（MINOR）

- **FAQ Q/A 支持能力**：新增 `faq-answer` Skill，回答 pratyaya 使用、当前 group 状态、Gate / override / 渲染异常与下一步建议。
- **主 Agent FAQ 路由**：`agents/pratyaya.md` 增加 FAQ / 问答 / 当前状态 / 不能渲染 / Gate fail / override 等只读解释入口；明确流程指令（提炼 / 补问 / 确认 / override / 生成画布）仍优先进入原画布流程。
- **WorkBuddy 元数据同步**：`plugin.json` 注册 `./skills/faq-answer`，版本升至 `2.5.0`，第三条 quickPrompt 改为 FAQ 入口；`tags` 仍保持 3 个，专家身份字段不变。
- **文档同步**：README、DESIGN、DEVELOPMENT 与用户指南补充 FAQ 是支持型 Skill，不进入画布状态机、不新增 Gate、不新增渲染契约、不写业务产物。

### 不变项

- `expertType` 保持 `agent`，不转 Team。
- 五类画布列表、确认包命名空间、Gate 与 Canvas 渲染契约不变。
- `schemas/state.schema.json` 与 `state.schema_version` 不变，不新增 `state.faq`。

## [v2.4.0] - 2026-08-08

### 新增功能（MINOR）

- **project + group 双层目录隔离**：工作坊产物目录从项目平层升级为 `workshop/{project_slug}/{group_id}/`；`project_slug` / `group_id` 为 kebab-case ASCII 目录键，`project_name` / `group_name` 保留为人类显示名。
- **项目级 manifest 派生视图**：新增 `workshop/{project_slug}/manifest.json` 作为可重建缓存，用于跨组状态汇总；业务真相仍为各 group 的 `state.json` 与确认包 Markdown。
- **group_meta 元数据**：新增 `group_meta.json` 与 `schemas/group_meta.schema.json`，承载 `group_name / group_lead / contact / created_at / created_by` 等显示元数据。
- **Schema 路径约束**：`state.schema.json` 新增必填 `project_slug`，并将 `group_id` 收紧为 kebab-case ASCII；新增 `project_manifest.schema.json`，限制 `groups[].state_path` 为 `{group_id}/state.json`，避免跨 group 路径。
- **Agent 与文档路径同步**：`agents/pratyaya.md`、`README.md`、`DEVELOPMENT.md`、`DESIGN.md`、`docs/user-guide.md`、`docs/MVL-整体架构设计.md`、`docs/prompt-guide.html` 与 `skills/canvas-render/SKILL.md` 同步新路径；审计命令改为从专家包根显式传入 group 子目录路径。
- **旧项目迁移策略**：旧 `workshop/{project_slug}/state.json`、`workshop/{project_name}/state.json`、`mvl-workshop/{project_slug}/state.json` 与 `mvl-workshop/{project_name}/state.json` 自动迁移到 `workshop/{project_slug}/default/`；迁移使用 `.migrating-*` 临时目录，校验后 rename，失败保留旧根不动。

### 兼容性

- `state.schema.json` 的 `schema_version` 仍保持 `"2.3"`；本次只收紧路径字段和目录约束。
- 旧平层项目首次进入时迁移到 `default` group；迁移成功后旧根只保留 `.workshop-legacy-stamp`，不创建软链接。
- 同项目不同 group 的 `state.json` 与产物禁止互相引用；只有项目级状态汇总可读取 manifest 或 enumerate 各 group state。

## [v2.3.5] - 2026-08-08

### 重构（PATCH）

- **视觉模式 Pan-Mode Calibration**：HMW 一等公民画布示例（`examples/hmw-canvas.html`）Bain Red 视觉系统落地 —— Hero 区整片铺红 → 白纸底卡 + 主红 eyebrow + 4px 主红规则线 + 浅红 `#fff0f0` 行动摘要卡 + 5px 主红左边框；同时将 `body` 上新增 `data-visual-mode="bain-red-action"` 与 canvas-data JSON 新增 `visual_mode` 字段，与方案 §6.2 / §14.4 表对齐。
- **Pan-Mode Invariants 13 条不变量**：`skills/canvas-render/visual-patterns/README.md` 新增 §Pan-Mode Invariants 段，沉淀跨 10 视觉模式的 13 条通用规则（Hero 永远白纸底 / 主色仅作信号元素 / 行动摘要公式 / Section 标题公式 / 表格三段式 / 禁用渐变阴影 / 质量判定仅字重 + 下划线 + 灰度等），并明确 §10 默认模式为锚定基准、§03/04 Signal 与 §05 McKinsey / §09 Roland Berger 各自获批的例外清单。
- **10 模式规格 §Hero 补 Pan-Mode Invariants**：`01-blue-professional-balanced.md` / `02-blue-professional-flow.md` / `03-signal-balanced.md` / `04-signal-flow.md` / `05-mckinsey-blue-conclusion.md` / `06-accenture-purple-institutional.md` / `07-bain-red-action.md` / `08-bcg-green-matrix.md` / `09-roland-berger-dark-blue-gray.md` / `10-black-gray-professional.md` 各在 §组件库 · Hero 段追加一行 `Pan-Mode Invariants (v2.3.5+)`，明确本模式对 §14.5 不变量的兑现方式与例外清单；§10 作为锚定基准自身标注"唯一已默认正确实现模式"。
- **示例库元数据补全**：4 个一等公民示例（`goden-circle-canvas.html` / `hmw-canvas.html` / `user-persona-canvas.html` / `user-journey-canvas.html`）与 7 个 MVL 子画布（`mvl-canvas/maau-global-canvas.html` + `module-1~6-canvas.html`）全部在 `<body>` 声明 `data-visual-mode` 属性，并在 `<script id="canvas-data">` JSON 中追加 `visual_mode.{id, zh_name, visual_system}` 字段。本次范围**仅加 metadata 不重排 CSS**（Q-α "一画布一模式" 推迟到 v2.4.0 PATCH 升级版）。
- **plugin.json 升 version**：2.3.4 → **2.3.5**（PATCH；v2.3.3 编号历史上被跳过，下一位 PATCH 用 2.3.5）。

### 设计决策点落地

- **Q-α（MVL 子画布一画布一模式映射）**：本次保守方案 —— 11 示例全部 `data-visual-mode="black-gray-professional"`（默认黑灰），按 §14.6 推荐 α "一画布一模式" 的多色映射推迟到 v2.4.0 MINOR。
- **Q-β（一等公民默认视觉模式）**：默认黑灰方案 —— 仅 HMW demo 演示 Bain Red，其他一等公民示例保持黑灰。
- **Q-γ（`data-visual-mode` 进 schema）**：HTML 属性权威 + canvas-data JSON `visual_mode` 字段可选（11 示例同步实施）。
- **Q-δ（行动摘要是否 10 模式必备）**：仅在 Bain Red 行动型语义落地，其他 9 模式 §组件库 · 行动摘要 段保留模式专属描述；统一公式由 §14.5 Invariant #5/#6 约束。

### 不变项

- 全部 render-contract-*.md spec 文档与 schema 不动（视觉层变化不影响契约层）。
- `scripts/audit_canvas_html.py` 与 `scripts/check_contract_consistency.py` 不动（视觉 token 不在审计范围）。
- `examples/shared/canvas-theme.css` 不动（共享主题层维持默认黑灰基线）。
- 6 个仓库根文档（README / DEVELOPMENT / DESIGN / docs/installation / docs/MVL-整体架构设计 / docs/user-guide）按 v2.3.4 同款原则不写 v2.3.5 字样；权威版本以 `plugin.json` `version` 字段为准。

### 兼容性

- v2.3.4 及更早产物的 `<body data-visual-mode>` 缺失不视为兼容性问题（属性为可选，canvas-data JSON `visual_mode` 字段亦可选）。
- 视觉模式规格 §Hero 新增的"Pan-Mode Invariants"注释行**为规范层补强**，不影响运行时模板或 Gate 行为。
- 下次升 PATCH 用 `2.3.6`，下次升 MINOR 从 `2.4.0` 起。

## [v2.3.4] - 2026-08-08

### 重构（PATCH）

- **删除冗余「痛点与机会」独立 section**：Journey 一等公民画布的独立 6b 视觉 section（`<section id="journey-pain-opportunities">` 与摘要锚点 `journey-pain-opportunity-summary`）已合并入 5 行主表的第 4 / 5 行（`pain-point` / `opportunity` 子锚点）；6b 独立 visual section 不再渲染。痛点 / 机会条目登记（`JOURNEY-Fxx`）仍保留在 `JOURNEY-v{N}.md` 确认包第 6b 节（Markdown 层，不进运行时模板）。
- **契约 / audit / 示例同步**：`render-contract-journey.md` 移除对应一级模块、锚点映射、Template Gate Profile、稳定锚点集合、隐藏检测清单；`audit_canvas_html.py` 中 `JOURNEY_TPL_MAIN_IDS` / `JOURNEY_MAIN_IDS` / `JOURNEY_ANCHORS` 与 2 处隐藏检测循环同步切；`examples/user-journey-canvas.html` 同步删除冗余 section、CSS（`.pain-opportunities` / `.pain-opportunity-list` / `.pain-opportunity-item`）、响应式 grid 与 canvas-data 引用。
- **契约检查器与测试同步**：`scripts/check_contract_consistency.py` 的 `required_anchors` 移除被删锚点；`tests/test_contract_consistency.py` 同步 `JOURNEY_PAIN_OPPORTUNITY_ANCHORS_V232`（重定义为 4 个质量锚点）、`assert plugin["version"] == "2.3.4"`、示例模板锚点白名单；`tests/test_journey_canvas_audit.py` 中 `test_missing_quality_or_pain_opportunity_anchor_fails` 改为 `test_missing_quality_anchor_fails`（仅覆盖 6a 四锚点），`test_swap_main_order_fails_template_gate` 主序交换目标改为 `journey-map` ↔ `journey-quality`，`test_legacy_only_template_fails` 中的 dead-code 替换同步移除；`tests/fixtures/journey/fault-cases.json` 删除 `missing_pain_opportunity_summary` 故障用例。
- **Spec / Agent 文档同步**：`skills/journey-distill/references/journey-spec.md` 移除 Canvas 映射表中 6b 独立锚点行，并新增 v2.3.4 PATCH 说明段；`agents/pratyaya.md` 高层描述将"动态阶段 × 5 行合并结构 + 质量鉴别 + 断点摘要"精简为"动态阶段 × 5 行合并结构 + 质量鉴别（5 行分别为行动 / 触点与系统 / 情绪 / 痛点 / 机会）"。
- **plugin.json 升 version**：2.3.2 → **2.3.4**（PATCH）。

### 不变项

- 字段语义（`pain_point` / `opportunity` / `pain_opportunity_visible`、6b 数据列「类型 / 来源」）保持 v2.3.2。
- `state.schema.json` `schema_version` 保持 2.3。
- `JOURNEY-Fxx` 条目 ID 含义与前缀含义保持 v2.3.2。
- Gate 来源 ID `JOURNEY-pain-opportunity` 与 6 条放行条件（`JOURNEY-GATE-01` ~ `06`）保持不变。
- 6 个仓库根文档（README / DEVELOPMENT / DESIGN / docs/installation / docs/MVL-整体架构设计 / docs/user-guide）按「文档版本号去重原则」不写 v2.3.4 字样；权威版本以 `plugin.json` `version` 字段为准。

### 兼容性

- v2.3.2 / v2.3.1 / v2.3.0 产物 HTML 若仍含独立 6b visual section，新 audit 反向 FAIL（**预期行为**，与原方案一致）。
- v2.3.3 编号本次跳过（PATCH 升 1 号位未占用），下次升 PATCH 用 `2.3.5`，下次升 MINOR 从 `2.4.0` 起。

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
