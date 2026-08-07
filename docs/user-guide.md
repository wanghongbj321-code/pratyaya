# 用户指南

> 适用版本：以 `.codebuddy-plugin/plugin.json` `version` 字段为权威
> 配套文档：[安装指南](./installation.md) / [DEVELOPMENT.md](../DEVELOPMENT.md) / [DESIGN.md](../DESIGN.md)

> **TL;DR**：5 步快速开始（见 §1），遇到问题查 §6 异常处理指引。

## 1. 快速开始

1. 确认专家已安装并验证（详见 [安装指南 §5](./installation.md#5-如何找到并验证专家)）
2. 在"我的专家"中找到 “Pratyaya Canvas Expert”
3. 点击进入主 Agent 对话
4. 选择画布类型（MVL / 黄金圈 / HMW / 用户画像 / 用户旅程，见 §2）与模式（A / B / C）
5. 按 §3 决策分支逐模块推进

## 2. 模式选择

主 Agent 启动时会先确认**画布类型**，再问你"想用哪种模式"：

**画布类型**（对应 `state.json` 的 MVL / 单画布区块）：

| 画布 | 说 | 工作流 |
|---|---|---|
| **MVL** | "开始 MVL 工作坊" / "M1 战略对齐" | 六模块（M1-M6），见 §4.1 |
| **黄金圈** | "开始黄金圈画布" / "Golden Circle" | WHY/HOW/WHAT 三层，单画布 |
| **HMW** | "开始 HMW 画布" / "How Might We" | 问题陈述四字段 + 想法种子，单画布 |
| **用户画像** | "开始用户画像画布" / "Persona" | 独立画布占位状态区块 |
| **用户旅程** | "开始用户旅程画布" / "Journey" | 动态阶段 × 5 行合并结构，单画布 |

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

### 4.2 黄金圈（单画布）

一次引导完成 WHY / HOW / WHAT 三层：

1. **WHY**：信念 / 目的 / 使命
2. **HOW**：原则 / 差异化 / 方法
3. **WHAT**：产品 / 服务 / 证据

主 Agent 引导三层讨论 → 提炼 `GC-v{N}.md` → Gate → 确认 → 生成 `gc-canvas.html`。

### 4.3 HMW（单画布）

问题重构工作坊，一次完成四步：

1. **陈述四字段**：situation（问题情境）/ question（我们可以如何）/ for（为谁）/ so_that（以便达到什么结果）
2. **质量鉴别**：四维度（预设解法 / 含糊 / 用户时刻 / 张力）各判通过或不通过
3. **想法种子**：三分支（落地 / 抽象 / 重构）各产出想法，填 8 固定想法格
4. **想法↔HMW 对应**：每条想法回应问句、对应质量维度、一致性判断

主 Agent 引导讨论 → 提炼 `HMW-v{N}.md` → Gate → 确认 → 生成 `hmw-canvas.html`。HMW 正式渲染走**双 Gate**（内容/授权 + 结构 Template Gate），结构问题不能自行豁免（详见 [DEVELOPMENT.md §3.1](../DEVELOPMENT.md#31-python-静态审计)）。

### 4.4 用户旅程（单画布）

当前旅程工作坊，一次完成四步：

1. **阶段地图**：阶段按实际旅程动态生成，最低 3 个有效阶段，不固定 7 个槽位。
2. **5 行主表**：行动 / 触点与系统 / 情绪 / 等待与返工 / 风险节点。
3. **关键断点与机会**：等待、返工、风险、情绪低点形成的断点摘要。
4. **质量鉴别**：用户视角 / 到达业务结果 / 断点可见 / 未预设方案，正式画布外显，但不进入主表成为第 6 行。

主 Agent 引导讨论 → 提炼 `JOURNEY-v{N}.md` → Journey Gate → 确认 / override → 生成 `journey-canvas.html`。Journey 正式渲染走**双 Gate**（内容/授权 + 动态阶段 Template Gate），结构问题不能自行豁免。

> 独立 Journey Canvas 不修改 MVL M2 的 `09-user-journey.md`，不写 `state.modules.M2`；如需把 Journey 结论带入 MVL，只能由用户人工引用。

## 5. 常用指令速查

按使用阶段组织。完整指令集见 `agents/pratyaya.md` 的指令卡章节。

**启动阶段**：

- "开始 A 引导模式" / "开始 B 转写模式"
- "开始黄金圈画布" / "开始 HMW 画布" / "开始用户旅程画布"

**模块阶段（MVL）**：

- "M1 提炼" / "M1 补问" / "M1 先看个样子" / "M1 确认 v1" / "M1 override（已阅读影响）"
- "切换到 M2" / "M2 当前状态"

**HMW 阶段**：

- "HMW 提炼" / "HMW 补问" / "HMW 先看个样子" / "HMW 确认 v1" / "HMW override（已阅读影响）"
- "生成 HMW 画布" / "HMW 状态"

**用户旅程阶段**：

- "用户旅程提炼" / "用户旅程补问" / "用户旅程先看个样子" / "用户旅程确认 v1" / "用户旅程 override（已阅读影响）"
- "生成用户旅程画布" / "Journey 状态"

**全局阶段**：

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
| 顶部字样 | 草稿 / 未确认 / 禁止用于管理层决策 | 画布名 + 版本号（MVL Canvas / Golden Circle / HMW Canvas / Journey Canvas） |
| 数据源 | 对应 Key Points（非确认包） | 对应确认包（`Mx-v{N}.md` / `GC-v{N}.md` / `HMW-v{N}.md` / `JOURNEY-v{N}.md`） |
| 视觉来源 | 用户选定的 `visual-patterns/NN-{id}.md` | 用户选定的 `visual-patterns/NN-{id}.md` |
| 视觉系统 | 用户选定 | 用户选定 |
| 状态变化 | 不改变画布状态 | 画布状态改为 `rendered` |
| 适用范围 | 辅助继续讨论 | 演示报告 + 领导汇报 |

---

**版本**：以 `.codebuddy-plugin/plugin.json` 为权威
**反馈**：在本仓库开 issue
