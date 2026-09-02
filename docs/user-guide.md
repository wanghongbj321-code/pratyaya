# 用户指南

> 适用版本：以 `.codebuddy-plugin/plugin.json` `version` 字段为权威
> 配套文档：[安装指南](./installation.md) / [DEVELOPMENT.md](../DEVELOPMENT.md) / [DESIGN.md](../DESIGN.md)

> **TL;DR**：5 步快速开始（见 §1），遇到问题查 §6 异常处理指引。

## 1. 快速开始

1. 确认专家已安装并验证（详见 [安装指南 §5](./installation.md#5-如何找到并验证专家)）
2. 在"我的专家"中找到 “Pratyaya Canvas Expert”
3. 点击进入主 Agent 对话
4. 选择画布类型（MAAU 综合 / MVL / 黄金圈 / HMW / 用户画像 / 用户旅程 / V2C VAC / 5W，见 §2）与模式（A / B / C）
5. 按 §3 决策分支逐模块推进

新工作坊会创建在 `workshop/{project_slug}/{group_id}/{topic_slug}/` 下。`project_slug` / `group_id` / `topic_slug` 是目录短名（kebab-case ASCII，如 `zhongruan-power`、`group-a`、`opportunity-evaluation`）；中文项目名、组名和议题名会作为 `project_name` / `group_name` / `topic_name` 显示，不直接作为目录键。同一组可围绕多个议题（topic）并行推进，`topic_slug` 是议题边界，不替代画布实例 `instance_slug`。

如果遇到使用、状态或异常问题，可以直接问 FAQ，例如"为什么当前画布不能正式渲染？"、"请解释 Gate fail 后我有哪些选择"或"我遇到使用问题了，请根据当前项目状态帮我解释原因并建议下一步"。FAQ 只解释依据和下一步，不会替你确认、override 或渲染。

## 2. 模式选择

主 Agent 启动时会先确认**画布类型**，再问你"想用哪种模式"。只给逐字稿或会议材料时也必须先指定画布类型；系统不会默认进入 MAAU、V2C VAC、5W 或任何其他画布。

启动时还会确认项目与组：

| 信息 | 示例 | 用途 |
|---|---|---|
| 项目名称 `project_name` | 中软国际 Power 商机评估 | 人类显示名，可中文 |
| 项目目录短名 `project_slug` | `zhongruan-power` | `workshop/{project_slug}/` 目录键 |
| 组号短名 `group_id` | `group-a` / `team-3` | `workshop/{project_slug}/{group_id}/` 目录键 |
| 组显示名 `group_name` | 战略组 | 写入 `group_meta.json` |
| 议题短名 `topic_slug` | `opportunity-evaluation` | `workshop/{project_slug}/{group_id}/{topic_slug}/` 目录键 |
| 议题显示名 `topic_name` | 商机评估 | 写入 `topic_meta.json` |

**画布类型**（对应 `state.json` 多个区块）：

| 画布 | 说 | 工作流 |
|---|---|---|
| **MAAU 综合** | "用这份逐字稿生成 MAAU" / "直接生成 maau" | 一次性逐字稿 → MVL 全局画布六板块源包，单实例（见 §4.6） |
| **MVL** | "M1 战略对齐" / "MVL 六模块管线" | 六模块（M1-M6），见 §4.1 |
| **黄金圈** | "开始黄金圈画布" / "Golden Circle" | WHY/HOW/WHAT 三层，单画布 |
| **HMW** | "开始 HMW 画布" / "How Might We" | 问题陈述四字段 + 想法种子，单画布 |
| **用户画像** | "开始用户画像画布" / "Persona" | 9 基本信息 + 6 宫格 + 4 质量鉴别，单画布 |
| **用户旅程** | "开始用户旅程画布" / "Journey" | 动态阶段 × 5 行合并结构，单画布 |
| **V2C VAC** | "开始 V2C VAC" / "价值归因画布" / "Value Attribution Canvas" | Scenario → Capability → Change → Business Impact → Value 归因链，支持多阶段管道和一次性综合 |
| **5W** | "开始 5W 画布" / "丰田 5W" / "根因分析" / "五问法" | 问题陈述 + 五层因果链（制造层 Why 1-2 / 检验层 Why 3-4 / 体系层 Why 5）+ 根本原因 + 对策四要素，单画布（见 §4.8） |

> V2C 系列画布的思路来源于王鸿的 Value-to-Capability FDE 工作方法论。V2C VAC 用来观察和审查价值归因假设，不把尚未验证的业务收益包装成确定结论。
> 5W 默认采用丰田自身推荐的根因分析思考模型（三层面追问框架）：先确认问题陈述是事实，再逐层追问"为什么"直到体系层，最后用"因此"检验根本原因并落实可行动对策。

**模式**（各画布共用；具体字段由对应 Skill 定义）：

| 模式 | 适用场景 | 数据源 |
|---|---|---|
| **A 引导模式** | 第一次做 MVL 工作坊 | 聊天对话（无转写稿） |
| **B 转写模式** | 有会议录音/转写稿 | `transcripts/module-N-TXX-raw.md` |
| **C 覆盖检查模式** | 旧项目材料迁移 | 旧的 `module-N.json`（已弃用） |

> **不推荐 C**：当前版本不再读取 `module-N.json`。如需迁移，请用 B 模式重新提炼。

## 3. 用户决策分支

每次模块完成后，主 Agent 会问你"下一步"；Gate 在确认前自动运行：

| 你说 | 主 Agent 做 |
|---|---|
| **提炼** | 把 Key Points 提炼成 `Mx-v{N}.md` 确认包 |
| **补问** | 列出待补问的 minor/major 缺口 |
| **先看个样子** | 生成草稿 Canvas（仅当前模块） |
| **确认 vN** | 在 Gate 报告基础上作最终确认（Gate 全 PASS 时 `confirmation_mode=gate_pass`） |
| **override / 我接受这个风险** | 仅 Gate 报告含 `business_risk` FAIL 时生效；`confirmation_mode=override` + 填写 override 审计；HTML 显示 caveat 标识 |
| **补问 / 修订** | 存在 `information_integrity` FAIL 或需修订时；不提供 override 路径 |

## 4. 工作坊使用流程

### 4.1 MVL（3 天工作坊）

#### 第 1 天（M1-M2）

- **M1 闭环目标定义**：goal、value、success_metrics
- **M2 用户与需求**：users、needs、pain_points

主 Agent 引导：M1 → M2 顺序执行，每完成一节给出"提炼/补问/先看个样子"。

### 第 2 天（M3-M4）

- **M3 拆解到方案方向**：hmw、loop_goal、solution_direction
- **M4 Agent Team 与 Context**：agent_team、knowledge、tools_skills

主 Agent 引导：M3 拆解结果驱动 M4 方案选择。

### 第 3 天（M5-M6）

- **M5 验证与修正**：validation_rounds、can_execute、can_create_value
- **M6 收尾与价值判断**：final_solution、headline、takeaway

主 Agent 引导：M5 验证后生成 M6 收尾，再生成全局 Canvas。

### 4.2 黄金圈（多 instance 画布）

一次引导完成 WHY / HOW / WHAT 三层：

1. **WHY**：信念 / 目的 / 使命
2. **HOW**：原则 / 差异化 / 方法
3. **WHAT**：产品 / 服务 / 证据

主 Agent 引导三层讨论 → 提炼 `GC-{slug}-v{N}.md` → Gate → 确认 → 生成 `gc-canvas-{slug}.html`。同一 group 可有多个黄金圈 instance；`gc-canvas.html` 是索引页。

### 4.3 HMW（多 instance 画布）

问题重构工作坊，一次完成四步：

1. **陈述四字段**：situation（问题情境）/ question（我们可以如何）/ for（为谁）/ so_that（以便达到什么结果）
2. **质量鉴别**：四维度（预设解法 / 含糊 / 用户时刻 / 张力）各判通过或不通过
3. **想法种子**：三分支（落地 / 抽象 / 重构）各产出想法，填 8 固定想法格
4. **想法↔HMW 对应**：每条想法回应问句、对应质量维度、一致性判断

主 Agent 引导讨论 → 提炼 `HMW-{slug}-v{N}.md` → Gate → 确认 → 生成 `hmw-canvas-{slug}.html`。HMW 正式渲染走**双 Gate**（内容/授权 + 结构 Template Gate），结构问题不能自行豁免（详见 [DEVELOPMENT.md §3.1](../DEVELOPMENT.md#31-python-静态审计)）。`hmw-canvas.html` 是索引页。

### 4.4 用户画像（多 instance 画布）

用户画像固定覆盖 9 基本信息、6 宫格和 4 项质量鉴别。主 Agent 引导讨论 → 提炼 `PERSONA-{slug}-v{N}.md` → Persona Gate → 用户确认或合规 override → 生成 `persona-canvas-{slug}.html`。正式渲染同样经过内容/授权与 Template 双 Gate；只有 `PERSONA-GATE-03/04` 的业务风险可以显式 override。`persona-canvas.html` 是索引页。

### 4.5 用户旅程（多 instance 画布）

当前旅程工作坊，一次完成四步：

1. **阶段地图**：阶段按实际旅程动态生成，最低 3 个有效阶段，不固定 7 个槽位。
2. **5 行主表**：行动 / 触点与系统 / 情绪 / 痛点 / 机会。
3. **痛点与机会**：痛点、机会与情绪低点形成的痛点与机会摘要（v2.3.2 起）。
4. **质量鉴别**：用户视角 / 到达业务结果 / 痛点与机会可见 / 未预设方案，正式画布外显，但不进入主表成为第 6 行。

主 Agent 引导讨论 → 提炼 `JOURNEY-{slug}-v{N}.md` → Journey Gate → 确认 / override → 生成 `journey-canvas-{slug}.html`。Journey 正式渲染走**双 Gate**（内容/授权 + 动态阶段 Template Gate），结构问题不能自行豁免。`journey-canvas.html` 是索引页。

非 MVL 画布开始时请提供 instance slug，例如 `decision-maker` / `frontline-operator`。slug 必须是小写英文、数字和连字符组成的 kebab-case；新建时不能使用 `default`。

> 独立 Journey Canvas 不修改 MVL M2 的 `09-user-journey.md`，不写 `state.modules.M2`；如需把 Journey 结论带入 MVL，只能由用户人工引用。

### 4.6 MAAU 一次性综合（transcript-direct）

MAAU 一次性综合适合把**明确指定给 MAAU 的一次性逐字稿**（会议录音转写、规划材料等）综合生成 MVL 全局画布六板块源包。只给逐字稿但不说画布类型时，主 Agent 会先追问，不会默认进入 MAAU。

1. 提供逐字稿（文本或文件路径），并指定 `project_slug` / `group_id` 与一个 instance `slug`（kebab-case，如 `retail-demo` / `power-market`）。
2. 主 Agent 调用 `maau-synthesize` 综合为六板块源包：**Intent** / **User** / **Agent Team** / **Workflow** / **Context** / **Validation**，产出 `modules/MAAU-{slug}-v{N}.md`。
3. 运行 MAAU Gate（`MAAU-GATE-01~09`）并展示报告，等你在"确认 vN / override / 补问"中选择。
4. 授权后渲染为 `output/maau-global-canvas-{slug}.html`（含 `[来源: transcript-direct]` 标头）。

**关键点**：

- **slug**：每个 MAAU 综合是一个独立实例，同一 group 可并列多个（`maau.{slug}`）。slug 必须为小写英文、数字和连字符组成的 kebab-case；**新建时不能使用 `default`**。
- **Gate / override**：`MAAU-GATE-*` 中 `information_integrity` 类 FAIL **不接受 override**，必须补问或升版；`business_risk` 类可 override（填写理由、确认人、时间）。
- **多实例输出**：每个 slug 生成一个实例页 `maau-global-canvas-{slug}.html`；可选生成索引页 `maau-global-canvas.html` 汇总全部实例。
- **互斥**：MAAU 一次性综合与 M1-M6 Phase 2 全局汇总互斥——同一 group 的 MAAU 输出只能二选一，不把逐字稿综合实例混入六模块汇总。

### 4.7 V2C VAC 价值归因画布（多 instance 画布）

V2C VAC 用于审查一个具体业务场景中，AI-enabled Capability 是否可能贡献于可观察变化，并进一步影响 Business Impact 与 Value。它不是价值证明页，而是观察类画布：未知、假设、断点和验证计划必须外显。

你可以选择两种生成路径：

| 路径 | 适用场景 | 产物 |
|---|---|---|
| `pipeline` 多阶段管道 | 需要逐步澄清 Scenario / Capability / Change / Impact / Value | `V2C-VAC-{slug}-stage-{stage}.md` 阶段草稿 + 最终 `V2C-VAC-{slug}-v{N}.md` |
| `transcript-direct` 一次性综合 | 已有完整逐字稿，希望一次性形成归因画布源包 | `V2C-VAC-{slug}-keypoints.md` + `V2C-VAC-{slug}-v{N}.md` |

主链按 `Scenario → Capability → Change → Business Impact → Value` 展示。每张 VAC 只允许一个 Primary Change 进入一条 Business Impact Chain；其他可观察变化可以记录，但默认不连入主链。

证据状态固定为 `F / H / ? / E`：

| 状态 | 含义 | 使用边界 |
|---|---|---|
| `F` | Fact | 有当前项目材料、访谈、业务记录或明确来源线索 |
| `H` | Hypothesis | 可保留为假设，但必须有验证计划或风险说明 |
| `?` | Question / Gap | 必须登记为 `V2C-AGxx` 或推断，不能静默放行 |
| `E` | Evidence-supported | 必须有 Pilot、业务数据、现场观察或对照验证支持 |

V2C VAC Gate 使用 `V2C-GATE-01..12`。只有 `business_risk` 类 Gate FAIL 可由用户显式 override；`information_integrity` FAIL 必须补问或修订。override 审计项的 `assessment_id` 必须使用 `V2C-GATE-*`，不能使用 `V2C-AGxx`。

### 4.8 5W 根因分析画布（多 instance 画布）

5W（Five Whys）用于对一个**问题陈述**做根因分析，默认采用丰田自身推荐的思考模型（三层面追问框架）。它不是头脑风暴工具，而是约束性追问工具：每个"Why"必须基于事实回答，根本原因必须通过"因此"检验，对策必须可行动、可验证。

| 环节 | 说明 |
|---|---|
| 问题陈述 | 必须是事实（时间 / 地点 / 现象 / 影响），不是结论或个人归因 |
| 五层因果链 | 制造层 Why 1-2（为什么会发生）→ 检验层 Why 3-4（为什么没发现）→ 体系层 Why 5（为什么没预防） |
| 根本原因 | 用"因此"检验三连问确认因果链成立 |
| 对策四要素 | 对策 / 负责人 / 截止日期 / 验证方式，缺一不可 |
| 其他原因分支 | 非主链原因单独记录，不强行并入五层链 |

每个 instance 对应一个问题（`instance_slug`，kebab-case，拒绝 `default`）。产物：`5W-{slug}-keypoints.md`（6 节 Key Points）→ `5W-{slug}-v{N}.md`（17 节确认包，唯一事实源）→ `5W-{slug}-gate-report-v{N}.md` → `5w-canvas-{slug}.html`（A3 横版，1-5 卡片横向并排 + 三层面标注）。

5W Gate 使用 `5W-GATE-01..07`：`5W-GATE-01~04`（事实陈述 / 五层有内容 / 证据 / 无个人归因）为 `information_integrity`，不可 override；`5W-GATE-05~07`（"因此"检验 / 根因可行动 + 对策四要素 / 预防性回应）为 `business_risk`，可由用户显式 override（`assessment_id` 必须为 `5W-GATE-*`）。

## 5. 常用指令速查

按使用阶段组织。完整指令集见 `agents/pratyaya.md` 的指令卡章节。

**启动阶段**：

- "开始 A 引导模式，项目名中软国际 Power 商机评估，项目短名 zhongruan-power，组号 group-a，议题短名 opportunity-evaluation，议题显示名商机评估"
- "开始 B 转写模式"
- "开始黄金圈画布" / "开始 HMW 画布" / "开始用户画像画布" / "开始用户旅程画布" / "开始 V2C VAC" / "开始 5W 画布"
- "检查本组所有 topic" / "本组议题进度"（读取 group 级 manifest，按 topic 汇总）
- "检查所有组状态" / "跨组对比"（读取项目级 manifest，按 group × topic 汇总）
- "切换 topic"（切换到当前组下另一个议题，不复制状态；目标不存在时进入初始化）
- "新建 topic"（在当前 project + group 下创建新议题目录）
- "我遇到使用问题了，请根据当前项目状态帮我解释原因并建议下一步"
- "为什么当前画布不能正式渲染？"
- "请解释 Gate fail 后我有哪些选择"

**模块阶段（MVL）**：

- "M1 提炼" / "M1 补问" / "M1 先看个样子" / "M1 确认 v1" / "M1 override（已阅读影响）"
- "切换到 M2" / "M2 当前状态"

**HMW 阶段**：

- "HMW 提炼" / "HMW 补问" / "HMW 先看个样子" / "HMW 确认 v1" / "HMW override（已阅读影响）"
- "生成 HMW 画布" / "HMW 状态"

**用户画像阶段**：

- "用户画像提炼" / "用户画像补问" / "用户画像先看个样子" / "用户画像确认 v1" / "用户画像 override（已阅读影响）"
- "生成用户画像画布" / "用户画像状态"

**用户旅程阶段**：

- "用户旅程提炼" / "用户旅程补问" / "用户旅程先看个样子" / "用户旅程确认 v1" / "用户旅程 override（已阅读影响）"
- "生成用户旅程画布" / "Journey 状态"

**MAAU 综合阶段**：

- "用这份逐字稿生成 MAAU" / "直接生成 maau"（提供逐字稿 + slug，如 `retail-demo`）
- "MAAU 确认 v1" / "MAAU override（已阅读影响）"
- "MAAU 状态" / "列出 MAAU 实例" / "生成 MAAU 索引页"

**V2C VAC 阶段**：

- "根据这份逐字稿生成 V2C VAC，路径 transcript-direct，instance store-replenishment"
- "开始 V2C VAC pipeline，先做 scenario 阶段"
- "V2C VAC 提炼" / "V2C VAC 补问" / "V2C VAC 先看个样子" / "V2C VAC 确认 v1"
- "V2C VAC override（已阅读 V2C-GATE-09 的影响）" / "生成 V2C VAC 画布" / "V2C VAC 状态"

**5W 阶段**：

- "开始 5W 画布，instance qc-issue，问题陈述：XX 批次产品检验漏检率上升"
- "5W 转写" / "5W 提炼" / "5W 补问" / "5W 先看个样子" / "5W 确认 v1"
- "5W override（已阅读 5W-GATE-06 的影响）" / "生成 5W 画布" / "5W 状态"
- "5W 门禁" / "5W 质量检查"（重跑 `5w-gate` 评估当前确认包）

### Journey 画布迁移边界（v2.3.2 PATCH 起）

> 详细说明见 [skills/canvas-render/references/render-contract-journey.md 兼容性边界段](../skills/canvas-render/references/render-contract-journey.md)；本节为用户视角摘要。

不兼容产物：

- v2.3.1 及更早的 `output/journey-canvas.html` 仅作阅读用，不能直接复用为 v2.3.2 渲染产物。
- v2.3.1 及更早的 `JOURNEY-v{N}.md` 确认包不得按新契约直接渲染；需重新提炼。
- 旧字段 `wait_rework` / `risk` / `friction_visible` 等已退场；audit 必填检查会 FAIL 含旧字段的产物。

迁移验收（必要步骤）：

1. 用 v2.3.2 的 `journey-distill` 重新提炼确认包（或在新版本下追加修订）。
2. 重跑 `python scripts/check_contract_consistency.py`，error 必须为 0。
3. 重跑 `journey-gate` 的 6 条放行条件（`JOURNEY-GATE-01` 至 `JOURNEY-GATE-06`），必须 PASS。
4. 渲染前 audit 必须通过（`JOURNEY-TPL-GATE-*` 不可 override；只有 6 条中 `business_risk` 类 Gate 可在 override 时接受，且填写理由）。

**关键约束**：

- `JOURNEY-Fxx` ID 前缀保留（含义切到「痛点 / 机会条目」，但不需要替换 ID）。
- `state.schema.json` `schema_version` 当前为 2.4（v3.2.0 新增 5W 时由 2.3 升版）。
- **不要沿用旧 Gate 结论**：v2.3.2 重构后 `journey-gate` 的覆盖要求已切到「至少 2 个痛点、1 个机会」，旧 Gate 的「等待 / 返工 + 风险节点」结论不适用于新契约。

**全局阶段**：

- "开始用户画像 instance decision-maker，项目名中软国际 Power 商机评估，项目短名 zhongruan-power，组号 group-a"
- "列举 Persona instances" / "切到 Persona instance decision-maker" / "生成 Persona 全部 instance 画布"
- "生成全局 Canvas" / "M5 验证" / "M6 收尾"

> **快速指令（quickPrompts）**：plugin.json 中 `quickPrompts` 字段定义的 3 个推荐入口指令，可一键触发。本指南不复制具体指令，统一以 plugin.json 为权威来源。

## 6. 异常处理指引

### 6.1 模糊回答

如主 Agent 回"我不太理解"或答非所问：

- 重述问题，使用更具体的关键词
- 参考 §5 指令速查，使用固定指令
- 必要时切换模式

### 6.2 Gate 冲突

如 Gate 报告含 FAIL 项（`gate_recommendation = fail`）：

- **仅 `business_risk` FAIL（`override_eligible = true`）**：可选择"override / 我接受这个风险"（填写理由、确认人、确认时间）；HTML 显示"已确认 · 带保留意见" caveat 标识
- **含 `information_integrity` FAIL（`override_eligible = false`）**：不接受 override，必须"补问"或"升版到 vN+1"重做
- **未通过项摘要**：在 Gate 报告中列出 blocker / major 缺口与分类

### 6.3 视觉模式资源异常

如 Canvas 渲染时报“视觉模式目录缺失”“模式未选择”或“文件名与 ID 不一致”：

- 检查 `skills/canvas-render/visual-patterns/` 是否包含 10 个编号 Markdown 模式
- 回到主 Agent 步骤 7，重新扫描候选并选择视觉模式
- 选择时使用主 Agent 给出的候选名称；主 Agent 会向渲染 Skill 传递完整路径

### 6.4 状态回退

如 `confirmed` → `draft` 回退：

- 检查 `Mx-v{N}.md` 是否被修改
- 用 `git diff` 确认改动
- 必要时升版到 v{N+1}

### 6.5 多用户并行

如两人同时编辑：

- 避免同时编辑同一模块
- 必要时用 `git pull` 拉取最新版本
- 主 Agent 会按最后拉取时间决定数据源

## 7. 草稿 Canvas 与正式 Canvas 的区别

| 特征 | 草稿 Canvas | 正式 Canvas |
|---|---|---|
| 顶部字样 | 草稿 / 未确认 / 禁止用于管理层决策 | 画布名 + 版本号（MVL Canvas / Golden Circle / HMW Canvas / Persona Canvas / Journey Canvas / V2C Value Attribution Canvas / 5W Canvas） |
| 数据源 | 对应 Key Points 或阶段草稿（非确认包） | 对应确认包（`Mx-v{N}.md` / `GC-{slug}-v{N}.md` / `HMW-{slug}-v{N}.md` / `PERSONA-{slug}-v{N}.md` / `JOURNEY-{slug}-v{N}.md` / `MAAU-{slug}-v{N}.md` / `V2C-VAC-{slug}-v{N}.md` / `5W-{slug}-v{N}.md`） |
| 视觉来源 | 用户选定的 `visual-patterns/NN-{id}.md` | 用户选定的 `visual-patterns/NN-{id}.md` |
| 视觉系统 | 用户选定 | 用户选定 |
| 状态变化 | 不改变画布状态 | 画布状态改为 `rendered` |
| 适用范围 | 辅助继续讨论 | 演示报告 + 领导汇报 |

---

**版本**：以 `.codebuddy-plugin/plugin.json` 为权威
**反馈**：在本仓库开 issue
