# M4 闸门策略

> M4 模块（闭环冻结、原型两轮迭代与开发筹备）的最低可用结论与常见 blocker。本文件由 `module-conclusion-gate` 在 Gate 评估时读取。

## 必填 section

参见 `../../mvl-distill/references/workshop-canvas-map.md` 中"M4 必填 section"：

- `agent_team`（人和 Agent 的角色职责、决策边界、协作模式）
- `collaboration_mode`（协作模式）
- `workflow_final`（冻结的 AI 应用工作流）
- `knowledge`（知识库）
- `data_sources`（数据源）
- `tools_skills`（工具与技能）
- `prototype_rounds`（两轮原型及修改）
- `delivery_preparation`（开发、场景测试、用户验证准备、团队分工、迭代节奏）

## 必须形成的结论

AI 应用 Workflow 已冻结，三类节点、流向和规则均明确；两轮原型有记录；Agent Team、Context、开发/测试/用户验证准备和迭代节奏已明确。

## 常见 blocker

- 只有普通业务流程、没有体现 AI（workflow_final 未含 AI 节点）
- 缺少任一节点类型（agent_execution_nodes / human_operation_confirmation_nodes / human_review_agent_execution_nodes）
- 工作流无起止或流向（缺 trigger 或 completion_condition）
- 两轮原型无结果（prototype_rounds 缺修改记录或测试结论）
- 角色决策边界不清（agent_team 未明确"谁拍板/谁认可"）
- 知识/数据/工具缺失（knowledge / data_sources / tools_skills 为空或来源不清）
- 筹备责任不清（delivery_preparation 未明确 Owner 与时间）

## 评估要点

- workflow_final 是否在 M3 草案基础上冻结（继承三类节点 + 加流向 + 加规则）？
- 角色决策边界是否明确（业务方 vs 技术方 vs Agent 各拍什么）？
- 两轮原型是否每轮都有：目标 / 实施 / 发现 / 修改？
- 知识/数据/工具的可获得性是否讨论过（能否在模拟环境中获得）？
- 开发/测试/用户验证准备是否明确（Owner + 时间）？

## 放行条件

满足以下全部条件才可放行：

1. 8 个必填 section 全部有内容或显式标为缺口；
2. workflow_final 继承 M3 草案并加流向/规则；
3. workflow_final 三类节点至少各 1 项；
4. agent_team 每角色含：名称 / 职责 / 是否 Agent / 决策边界 / 协作模式；
5. prototype_rounds 含两轮迭代记录（每轮：目标 / 实施 / 发现 / 修改）；
6. delivery_preparation 至少含开发 / 测试 / 用户验证三项的 Owner 与时间。
