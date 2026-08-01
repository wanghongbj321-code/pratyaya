# M4 闸门策略

> M4 模块（闭环冻结、原型两轮迭代与开发筹备）的最低可用结论与常见 blocker。本文件由 `module-conclusion-gate` 在 Gate 评估时读取。

> 每条放行条件包含稳定 ID、分类（`information_integrity` / `business_risk`）和风险等级，供 Gate 报告与 override 审计引用。

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

每条放行条件拥有稳定 ID、分类和风险等级，供 Gate 报告与 `override_audit.items` 引用。

| ID | 条件 | 分类 | 风险等级 | 来源 |
|---|---|---|---|---|
| `M4-GATE-01` | 8 个必填 section 全部有内容或显式标为缺口 | `information_integrity` | low | M4 必填 section 表 |
| `M4-GATE-02` | workflow_final 继承 M3 草案并加流向/规则 | `information_integrity` | low | M4-workflow_final, M3-workflow_draft |
| `M4-GATE-03` | workflow_final 三类节点至少各 1 项 | `information_integrity` | low | M4-workflow_final |
| `M4-GATE-04` | agent_team 每角色含：名称 / 职责 / 是否 Agent / 决策边界 / 协作模式 | `information_integrity` | low | M4-agent_team |
| `M4-GATE-05` | prototype_rounds 含两轮迭代记录（每轮：目标 / 实施 / 发现 / 修改） | `information_integrity` | low | M4-prototype_rounds |
| `M4-GATE-06` | delivery_preparation 至少含开发 / 测试 / 用户验证三项的 Owner 与时间 | `business_risk` | medium | M4-delivery_preparation |

**详细说明**：

满足以下全部条件才可放行：

1. `M4-GATE-01`：8 个必填 section 全部有内容或显式标为缺口。
2. `M4-GATE-02`：workflow_final 继承 M3 草案并加流向/规则。
3. `M4-GATE-03`：workflow_final 三类节点至少各 1 项。
4. `M4-GATE-04`：agent_team 每角色含：名称 / 职责 / 是否 Agent / 决策边界 / 协作模式。
5. `M4-GATE-05`：prototype_rounds 含两轮迭代记录（每轮：目标 / 实施 / 发现 / 修改）。
6. `M4-GATE-06`：delivery_preparation 至少含开发 / 测试 / 用户验证三项的 Owner 与时间。

> **分类说明**：
> - `M4-GATE-01` ~ `M4-GATE-05` 均为 `information_integrity`，FAIL 时不可 override。
> - `M4-GATE-06` 为 `business_risk`（交付准备中的 Owner / 时间在模拟环境下经常未完全确定），FAIL 时用户可显式 override 并填写理由；Gate 仍输出 `gate_recommendation=fail`，但 `override_eligible=true`。

## 来源 ID 约定

- `M4-{section}`：对应必填 section（如 `M4-workflow_final`、`M4-prototype_rounds`）。
- `M4-Gxx`：本模块缺口 ID。
- `M4-Ixx`：本模块推断 ID。
- `M4-Cxx`：本模块结论 ID。
