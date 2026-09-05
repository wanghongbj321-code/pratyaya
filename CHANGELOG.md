# Pratyaya 变更日志

> 本文件记录 Pratyaya 专家的正式版本变更。
> 完整 SemVer 与架构说明见 [`README.md`](./README.md) / [`DESIGN.md`](./DESIGN.md) / [docs/MVL-整体架构设计.md](./docs/MVL-整体架构设计.md)。

## [v3.5.1] - 2026-09-05

### 修复（PATCH）

- **契约测试移除版本号绑定断言**：`tests/test_contract_consistency.py` 删除对 `plugin.json` 具体版本号的硬编码断言（技能注册测试尾部一处、入口语境测试内一处），入口语境测试更名为 `test_plugin_json_entry_context`。契约一致性测试只校验结构/入口契约，不绑定发布版本号——后续升版不再需要同步测试中的版本字面量（此前 v3.4.1 / v3.5.0 均需随升版同步）。

### 兼容性与迁移边界

- `plugin.json` `version` `3.5.0` → `3.5.1`（PATCH）；`state.schema.json` `schema_version` 保持 `"2.4"`。
- 纯测试与版本元数据改动，不影响渲染契约、审计断言与任何运行产物。

## [v3.5.0] - 2026-09-05

### 新增功能（MINOR）

- **Workflow 确定性布局器（语义 / 布局分离）**：新增官方几何展开资产 `skills/canvas-render/scripts/workflow_layout/workflow_layout.py`——LLM 只产 `canvas-data.workflow` 语义拓扑，布局器确定性生成内联 SVG 几何（轨道分行堆叠 + 轨内横流蛇形折返 + 跨轨 / 回流走行间空隙与 gutter，范式对齐示例母版，无泳道色块）；自带几何自检（节点不重叠 / 边正交 / 不穿节点 / 端点中点 / 边全集不丢），自检 0 问题才可交付；`VERSION` 版本化 + `layout_trace(fork_id?)` 溯源（写 `canvas-data.workflow.layout`，不改 schema_version）。
- **布局回归基线**：`tests/fixtures/workflow_layout/` 物化真实拓扑样本（hotel-revenue 新 / 旧 schema、suozhang 三轨含 gateway/timer/message/data_store 与 dashed 回流）；`tests/test_workflow_layout.py` 覆盖几何自检 / 边全集 / 宽度预算 / 确定性 / 旧 schema 回归（8 项通过）。
- **L1 布局配置层**：`layout_override`（渲染输入侧参数，不进 `canvas-data`）可调间距 / 卡宽预算 / 轨道基线 / gutter / 每行容量，支持 `--preset compact|roomy`；配置说明与可配 / 不可配对照清单见 `layout_override.schema.md`。
- **L2 布局分叉层**：显式触发 + 拷贝协议 + `layout_meta.json`（`derived_from: {baseline_version, baseline_sha}`）+ 自检验收门 + 漂移治理，见 `fork_guide.md`。
- **AGENTS.md 规则 3 边界修订**：禁止"内容渲染"脚本；`workflow_layout` 作为确定性几何展开官方资产可在 Skill 流程内执行（不承担业务内容渲染）；其他自动化渲染 / 注入入口仍须先按规则 2 提设计变更。
- **SKILL / render-contract 同步**：SKILL.md 新增「Workflow 流程图生成（确定性几何展开，3.5.0+）」小节；render-contract §A1 明确"布局器生成 / LLM 静态生成"两路径须满足同一 DOM / 元素 / 审计契约，§A1.5 增加可选 `workflow.layout` 溯源字段说明。

### 修复（PATCH）

- `tests/test_contract_consistency.py` 版本硬编码同步（3.4.1 → 3.5.0）。
- **布局器实施审查修复**（审查报告：`internal/…/全局画布Workflow确定性布局器设计方案-20260905-实施审查报告-ds-v4-flash.md`）：CLI `--override <file.json>` 取值不再被误收为拓扑输入（文档示范用法可正常 exit 0）；几何自检 FAIL → exit `1`（不产 `--svg`，禁止进入装配）、输入不合法 → exit `2`（自检门禁可编程化）；新增 `validate()` 正式输入契约校验（tracks 非空 / track 归属 / 任务类 actor 合法 / type 合法 / edges 引用存在且无重复同向边）；`selfcheck()` 补端点落边界中点、dashed 走 gutter、track 归属、边全集断言，dashed 回流一律强制走 gutter 通道；CLI 输出布局报告坐标表（§3.1）；文本折行 ≤3 行省略号截断（防溢出卡片 / 事件圆）；`--svg` 预览渲染轨道标签；SKILL / render-contract 措辞收敛"布局器 = 几何层，`#workflow-flow` DOM 由渲染回合按 §A1 装配"；`schema.md` / `fork_guide.md` 声明能力边界（单左 gutter、右 gutter / 线-线避让为 L0 演进项）。测试新增 8 项审查修复回归。

### 兼容性与迁移边界

- `plugin.json` `version` `3.4.1` → `3.5.0`（MINOR）；`state.schema.json` `schema_version` 保持 `"2.4"`，`canvas-data.workflow.layout` / `layout_override` 均不改 schema_version。
- 布局器为增量能力：新渲染可按 §A1 两路径生成，**不追溯重渲染**已交付画布；编排侧"受控几何注入（B）"留待后续版本启用（本版为 CLI 生成路径）。

## [v3.4.1] - 2026-09-05

### 修复（PATCH）

- **全局页示例母版 Workflow 视觉精调**：`examples/mvl-canvas/maau-global-canvas.html` 去除深灰整卡（A2–A6/C1 改浅色单色卡片）、移除三条横向泳道背景带、actor 徽章改白底黑灰描边并整体内移避免压任务框边框、事件符号改用 ⏱/✉、图例补为 7 类带图形符号、补 `#workflow-done` 完成条件条样式；SVG 文字样式改为 CSS 单点 + 直接子代选择器（`>`）控制，防止通用后代规则覆盖嵌套徽章 / 序号样式。打印幅面落地 A3 横版（`@page size: A3 landscape` + 页面文案同步）。
- **5W 画布示例标题精简**：`examples/5w-canvas.html` 标题去除中文"5W 五个为什么"前缀。

### 兼容性与迁移边界

- `plugin.json` `version` `3.4.0` → `3.4.1`（PATCH）；本轮仅示例母版与文案修订，不影响渲染契约、审计断言与 `state.schema.json` `schema_version`（仍 `"2.4"`）。

## [v3.4.0] - 2026-09-05

### 新增功能（MINOR）

- **MVL/MAAU 全局页 Workflow 双轨 BPMN 可视化**：`render-contract.md` §A1 从旧三泳道（按节点类型）模型升级为 MVL 全局页通用的轨道带模型，Phase 2 全局汇总页与 MAAU transcript-direct 实例页共享同一契约；支持业务阶段轨道（A/B/C…）或单轨 `main`，并用 actor 徽标表达 `human / ai / system / hybrid / reviewer` 执行语义。
- **扩展 BPMN 结构签名**：Workflow 派生拓扑新增 `workflow.tracks`、`nodes[].track`、`nodes[].actor` 与 `edges[].dashed`，合法节点类型扩展为 `start / end / gateway / agent_execution / human_operation / human_review / timer / message / data_store`；回流/反馈边使用 `bpmn-reflow` 虚线，完成条件可渲染为 `#workflow-done` 条。
- **A3 全局页打印与示例母版升级**：MVL 全局页示例母版 `examples/mvl-canvas/maau-global-canvas.html` 改为 A3 横版、浅色单色轨道带 Workflow；M1-M6 模块详情页继续保持既有 A4 口径。
- **审计与 L2 smoke 升级**：`audit_workflow_flow` 新增 tracks、actor、dashed reflow、扩展节点类型与 DOM/data 一致性断言；`canvas-smoke.mjs` 为 `mvl` 增加 Workflow 结构签名和滚动豁免，窄屏横向滚动限制在 `.bpmn-flow-wrap` 内。
- **测试与 fixtures**：`tests/test_workflow_flow.py` 扩展到 18 条，覆盖 MAAU transcript-direct 三轨、Phase 2 单轨、actor/track/reflow 反向用例；新增 Phase 2 全局页 fixture，MAAU fixtures 与 demo 输出同步重渲染为新轨道带模型。

### 兼容性与迁移边界

- `state.schema.json` `schema_version` 保持 `"2.4"` 不变；本轮只扩展 HTML `canvas-data.workflow` 渲染/审计契约。
- 已交付旧 `maau-global-canvas*.html` 不追溯重渲染；之后新渲染的 Phase 2 全局页与 MAAU transcript-direct 实例页按新 §A1 输出。

## [v3.3.2] - 2026-09-03

### 重构（PATCH）

- **主 Agent 规则优先级体系（INV + P0-P6）**：`agents/pratyaya.md` 重构为"不变式优先"规则架构——顶部声明 **INV-01..13 不变式**（未指定画布不处理 / Key Points 仅草稿 / 只读已确认确认包 / Gate 只建议 / 人确认的是版本 / 升版重置 / `information_integrity` 不可 override / override 审计完整 / 视觉模式列全候选并需用户确认 / 验收失败保持 `confirmed` / 逐字稿不可信 / FAQ 只读 / 默认只读当前 topic）与 **P0-P6 优先级层**（安全>授权>状态机>注册表>pipeline>指令卡>表达），INV 恒高于 P0-P6；正文由 ~400 行收敛至 ~189 行，路由与治理规则以表格化、可校验形式沉淀。
- **入口决策树（步骤 -1）**：改为结构化判定链（明确流程指令 → FAQ/状态解释 → 画布类型关键词路由 → 元数据完整 → state 存在 → 三元一致），未指定画布时追问、不进入默认画布。
- **结构与下沉**：路径/资源解析、Phase 0 迁移、Phase 1-3 与下沉 pipeline 引用、画布注册表、标准管线骨架、状态机与升版、δ 差异、实例管理、指令卡、异常处理表统一收敛；渲染细节继续指向 canvas-render SKILL.md「分级渲染验收」与 references pipeline。
- **测试**：全量 pytest **469 passed**（契约一致性 / 画布注册表 / 薄控制面门禁全绿，agent ≤ 400 行门禁保持）。

## [v3.3.1] - 2026-09-03

### 优化（PATCH）

- **渲染成本预防（提示词补丁）**：`skills/canvas-render/SKILL.md` 新增"审计脚本是裁判，不是规格书"审计定位（§资源清单 + §Python 静态审计双落点）；§「精简浏览器视觉验收」改写为**分级渲染验收**三级体系（L1 Python 静态审计必做 / L2 DOM 双视口度量断言必做 / L3 截图目检按需），8 处画布输出句与 10 处 `references/*-pipeline.md` 成功句统一替换，主 Agent 提示词改薄引用 + 渲染成本护栏。
- **L2 冒烟断言脚本**：新增 `skills/canvas-render/scripts/canvas-smoke.mjs`（canvas_type 参数化 + 断点期望表 + 滚动豁免清单 + 环境自检降级；exit 0=PASS / 1=FAIL / 2=DEGRADED），降低浏览器全量截图目检成本。
- **渲染路径自报**：§渲染自检新增"路径自报"（读哪三类依据 / 跑哪几级验收 / 工具往返量级）与"模式与确认自报"，使低成本默认路径可复盘可核验。
- **视觉模式选择确认（T1）**：模式选择环节必须列出全部 10 个候选并**默认预选 `10-black-gray-professional`（黑灰专业）**，每次渲染均需用户确认（可一键接受默认或改选），Agent 不得隐式选定。
- **视觉模式公司名中性化（T2）**：`visual-patterns/` 05-09 五个模式去除咨询公司专名——`05-mckinsey-blue-conclusion`→`05-ink-blue`（墨蓝）、`06-accenture-purple-institutional`→`06-bright-purple`（亮紫）、`07-bain-red-action`→`07-true-red`（正红）、`08-bcg-green-matrix`→`08-teal-green`（青绿）、`09-roland-berger-dark-blue-gray`→`09-dark-blue-gray`（深蓝灰）；正文公司引用、色板 token 公司出处归因句与公司缩写 CSS 变量建议同步中性化；`examples/hmw-canvas.html` 示例同步。
- **测试**：全量 pytest **469 passed**；hmw / 5W 模板审计与 L2 smoke 双视口 PASS。

### 破坏性变更说明（按内部约定记录，SemVer 号位由发布流程定）

- **T2 模式 id 改名属不向后兼容**：`visual-patterns/` 05-09 模式文件名与 frontmatter `id` 已变更，渲染产物 `data-visual-mode` / canvas-data JSON `visual_mode.{id,zh_name,visual_system}` 使用旧 id 的既有 HTML 需按新 id 重新渲染。`schemas/` 无 visual_mode id 枚举，非 schema 破坏；序号 01-10 与候选总数 10 不变。

## [v3.3.0] - 2026-09-02

### 新增功能（MINOR）

- **主 Agent 薄控制面重构（P1+P2+P3）**：`agents/pratyaya.md` 由 1360 行收敛至 397 行。修复 4 项 defect（Journey 指令块未闭合 / 指令卡重复错位 / 路径约定重复 / `approval` 术语残留）并重排 Phase 编号；引入**画布注册表**（8 画布 × 12 字段，含 `canvas_type` / `audit_type` 双列——GC 为唯一 `golden-circle` ≠ `gc` 的画布）与参数化标准 8 步管线，6 份同构 Phase 合并为 1 份；8 类画布执行细节下沉到各 `{canvas}-distill/references/{PREFIX}-pipeline.md`（9 个文件），各 distill SKILL.md 新增"先读 pipeline reference"强制读取契约。治理不变式（Gate 只建议 / 人确认版本 / 升版边界 / override 规则）保留在控制面。
- **共享画布引擎（P4）**：新增 `skills/_engine/` 13 模块（canvas_registry / paths / session / state / executor / gate / authorization / contract / files / reconcile / migration / manifest）。引擎只做**规则型判定**（5 态机合法跃迁、Gate 三态汇总、升版重置、授权 if-then、override 完整性、确认包文件名/版本/instance 一致性），不做语义判定、不渲染 HTML、不替人拍板（`authorization.grant()` 强制携带 `confirmed_by` / `confirmed_at` / `user_confirmation_text`）。依赖方向单向：`canvas_registry`（零副作用、标准库 only）← `canvas_audit` ← `audit_canvas_html.py`；audit `--type` choices 改为从注册表读取，消除第二份清单。
- **规则一致性防线（R14）**：9 个 pipeline references 顶部加入 `<!-- rule:{id}: ... -->` 确定性规则注释块（升版重置 / 授权 if-then / Gate 汇总），由 CI 测试校验 references 声明与引擎实现一致。
- **测试与门禁**：新增 `tests/test_engine/`（15 个文件，含绕过检测、导入边界、禁 HTML 写出、规则块防线）；新增注册表三方交叉断言（audit choices / state schema / plugin skills）；新增 B 组正式授权链路审计 `tests/test_e2e_authorization.py`——`36cd94c` 起为 5w / v2c-vac / maau 三段式 fixture + 未授权反向用例，`afc51dc` 按 canvas-render Skill（LLM 渲染）补全 gc / hmw / persona / journey / mvl 五类成品 fixture，八类全覆盖 25 passed。全量测试 **469 passed**。
- **GC examples 模板契约合规修复**：`examples/goden-circle-canvas.html` 补齐 `canvas-header` id、`canvas-data.sections` 扁平锚点键与 `auth` 字段（视觉零改动），A 组 GC 模板自审计（`--type gc`）由 rc=1 → PASS，八类模板自审计全绿。

### 兼容性与迁移边界

- `state.schema.json` `schema_version` 保持 `"2.4"` 不变。
- `_engine` 不加入 plugin.json `skills` 数组（共享库，非 skill，由各 SKILL.md 以相对路径调用）。
- e2e 八类 fixture 均含已授权 `state.json` 与正式成品 HTML（由 canvas-render Skill 产出）；正式渲染仍走 canvas-render Skill，不以 fixture 代替。

## [v3.2.0] - 2026-09-02

### 新增功能（MINOR）

- **丰田 5W 根因分析画布（一等公民）**：新增 5W（Five Whys）独立画布，与 GC / HMW / V2C VAC 对称。默认采用**丰田自身推荐的根因分析思考模型**（三层面追问框架：制造层 Why 1-2 → 检验层 Why 3-4 → 体系层 Why 5），问题陈述 + 五层因果链 + 根本原因 + 对策四要素 + 其他原因分支 + 判别记录。以离线工作表 `internal/pratyaya-internal/docs/refs/canvas-templates/06-5W画布.html` 为版面原型（A3 横版、1-5 卡片横向并排、三层面标注、黑灰单配色）。
- **5W 分析与治理 Skill**：新增 `5w-distill`（Stage 1 Key Points 抽取 + Stage 2 原子提炼，17 节确认包）与 `5w-gate`（`5W-GATE-01~07`，其中 `01~04` 为 `information_integrity` 不可 override，`05~07` 为 `business_risk` 可 override）。机器标识三套分离：文件前缀 / Gate ID `5W-`、`canvas_type=5w`、state 键 `five_whys`。
- **5W 渲染契约与审计**：新增 `render-contract-5w.md`、契约化示例 `examples/5w-canvas.html`、`audit_canvas_html.py --type 5w`、`--page-type 5w-index` 与 `5W-TPL-GATE-00..06` Template Gate（正式交付必须传 `--template`）；五层锚点 `5w-why-1` ~ `5w-why-5` 必须全部存在（层数弹性暂不支持）。
- **状态 schema v2.4**：`state.schema.json` `schema_version` 升至 `"2.4"`，新增 `state.five_whys.{slug}` instance map（`assessment_id` pattern `^5W-GATE-[0-9]+$`），anyOf 追加第 8 分支。
- **Agent 与文档同步**：`agents/pratyaya.md` 新增 Phase 5W 八步流程、5W 指令卡、强制执行指令与状态目录；`README.md` / `DESIGN.md`（§14）/ `DEVELOPMENT.md`（§3.5 调试 + 命令速查）/ `docs/user-guide.md`（§4.8）/ `docs/installation.md` 同步画布清单与流程。

### 兼容性与迁移边界

- 纯新增非破坏性升级；旧 state 无 `five_whys` 区块不阻断既有 MVL / MAAU / GC / HMW / Persona / Journey / V2C VAC 流程。
- 5W 是独立单画布：不生成 MVL 全局 Canvas，不读取或写入 `state.modules` / `state.maau`。

## [v3.1.1] - 2026-09-01

> v3.1.0 未发布（分支未合并即进入优化），Workflow BPMN 流程图功能与三项视觉/契约优化合并为 v3.1.1 一并发布。

### 新增功能（MINOR）

- **Workflow 板块 BPMN 可视化流程图**：MAAU 全局画布（Phase 2 M1-M6 汇总页与 MAAU transcript-direct 实例页）的 Workflow 板块在文本框下方新增派生只读的 BPMN 流程图（`#workflow-flow`）。采用 BPMN 图形语言子集（Start Event / Task / Exclusive Gateway / End Event / Sequence Flow），三类节点由泳道（桌面）/ 节点在流程中的位置区分；桌面三泳道（Agent 执行 / 人工操作确认 / 人审 + Agent 执行）、窄屏单流横向滚动。
- **数据派生（Q1=A）**：流程图从确认包 Workflow section（`trigger` / `steps` / `completion_condition` + 三类节点 + `rules`）静态生成内联 SVG，**不改数据契约**（`maau-synth-spec.md` / `workshop-canvas-map.md` 不变）；`canvas-data` 顶层新增 `workflow.nodes` / `workflow.edges` 派生拓扑，供静态审计一致性校验。
- **渲染契约**：`render-contract.md` 新增 §A1「Workflow BPMN 流程图（`#workflow-flow`）」DOM 契约、BPMN 子集与元素映射、派生规则、泳道/响应式与拓扑数据约束；示例母版 `examples/mvl-canvas/maau-global-canvas.html` 新增三泳道示例 SVG 与图例（门店补货智能体）。
- **静态审计**：`GLOBAL_MAIN_IDS` 新增 `workflow-flow` 锚点；`audit_workflow_flow` 断言 Start/End Event 存在、`nodes` 覆盖三类节点、SVG `bpmn-node` 数量与 `nodes` 数量一致、`edges.from/to` 引用有效、传入 `--source` 时确认包含三类节点章节。
- **测试**：新增 `tests/test_workflow_flow.py`（10 项，覆盖 PASS 与 8 种 FAIL 场景）；MAAU fixture `maau-global-canvas-retail-demo.html` 同步补 `#workflow-flow` 与拓扑。

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

## 归档说明（v1.0.0 – v2.9.1）

> 早期版本明细已于 2026-09-05 归档移除。v1.0.0 ~ v2.9.1（2026-08-01 ~ 2026-08-09，共 18 个版本）为「MVL Expert → 多画布平台」演进期的历史记录，其语义与当前 v3.x（显式画布路由 + 多画布一等公民）差异较大，继续陈列会干扰对本文件当前内容的阅读。
> 完整历史明细可回溯 **git 历史**：`git log --oneline --all -- CHANGELOG.md` 查看各版本变更提交；带 tag 的版本（v1.0.2、v2.3.x、v2.4.0、v2.7.0 ~ v2.9.1 等）亦可查看对应 GitHub Releases（https://github.com/wanghongbj321-code/pratyaya/releases）或执行 `git show <tag>:CHANGELOG.md`。
