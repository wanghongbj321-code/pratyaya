# 用户指南

> 适用版本：v1.0.0
> 配套文档：[安装指南](./installation.md) / [DEVELOPMENT.md](../DEVELOPMENT.md) / [DESIGN.md](../DESIGN.md)

> **TL;DR**：5 步快速开始（见 §1），遇到问题查 §6 异常处理指引。

## 1. 快速开始

1. 确认专家已安装并验证（详见 [安装指南 §5](./installation.md#5-如何找到并验证专家)）
2. 在"我的专家"中找到 “Pratyaya MVL Expert”
3. 点击进入主 Agent 对话
4. 选择模式（A / B / C，见 §2）
5. 按 §3 决策分支逐模块推进

## 2. 模式选择

主 Agent 启动时会问你"想用哪种模式"：

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

## 4. 3 天工作坊使用流程

### 第 1 天（M1-M2）

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

## 5. 常用指令速查

按使用阶段组织。完整指令集见 `agents/pratyaya.md` 的指令卡章节。

**启动阶段**：

- "开始 A 引导模式" / "开始 B 转写模式"

**模块阶段**：

- "M1 提炼" / "M1 补问" / "M1 先看个样子" / "M1 确认 v1" / "M1 override（已阅读影响）"
- "切换到 M2" / "M2 当前状态"

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

- 检查 `skills/canvas-render/visual-patterns/` 是否包含 9 个编号 Markdown 模式
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
| 顶部字样 | 草稿 / 未确认 / 禁止用于管理层决策 | MVL Canvas + 版本号 |
| 数据源 | `Mx-keypoints.md`（非确认包） | `Mx-v{N}.md`（确认包） |
| 视觉来源 | 用户选定的 `visual-patterns/NN-{id}.md` | 用户选定的 `visual-patterns/NN-{id}.md` |
| 视觉系统 | 用户选定 | 用户选定 |
| 状态变化 | 不改变模块状态 | 模块状态改为 `rendered` |
| 适用范围 | 辅助继续讨论 | 演示报告 + 领导汇报 |

---

**版本**：v1.0.0
**反馈**：在本仓库开 issue
