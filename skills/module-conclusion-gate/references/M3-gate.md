# M3 闸门策略

> M3 模块（闭环目标定义、HMW 拆解与方案方向锁定）的最低可用结论与常见 blocker。本文件由 `module-conclusion-gate` 在 Gate 评估时读取。

> **v4.0.0 更新**：每条放行条件增加稳定 ID、分类（`information_integrity` / `business_risk`）和风险等级，供 Gate 报告与 override 审计引用。

## 必填 section

参见 `../../mvl-distill/references/workshop-canvas-map.md` 中"M3 必填 section"：

- `hmw`（HMW 提问）
- `loop_goal`（闭环目标）
- `capability_metrics`（能力指标）
- `acceptance`（验收标准）
- `boundary`（边界）
- `solution_direction`（AI 方案方向）
- `workflow_draft`（从触发到结果的 AI 应用工作流草案）
- `validation_dimensions`（分层验证维度）

## 必须形成的结论

HMW、闭环目标、能力指标、验收标准、边界、AI 方案方向、从触发到结果的 AI 应用工作流草案、三类节点、分层验证维度已明确。

## 常见 blocker

- HMW 与核心问题无关（提问停留在表象，未触及 M1/M2 暴露的关键 gap）
- 闭环无起止（workflow_draft 缺少 trigger 或 completion_condition）
- 方案方向未锁定（多个方向并存，无明确取舍）
- 验收标准未锁定（仅说"效果好"等不可验证描述）
- workflow_draft 缺少三类节点之一（agent_execution_nodes、human_operation_confirmation_nodes、human_review_agent_execution_nodes）

## 评估要点

- HMW 是否可追溯到 M1/M2 暴露的关键问题？
- 闭环目标是否含明确的起点（触发条件）与终点（完成条件）？
- AI 方案方向是否在讨论中已锁定（无悬而未决的"再考虑下"）？
- workflow_draft 是否满足三类节点齐全的契约（参见 `workshop-canvas-map.md` 的 AI 工作流结构契约）？
- 能力指标与 M1 的 success_metrics 是否对齐？
- 验证维度是否分层（自治流程 / 交互 / 信任）？

## 放行条件

每条放行条件拥有稳定 ID、分类和风险等级，供 Gate 报告与 `override_audit.items` 引用。

| ID | 条件 | 分类 | 风险等级 | 来源 |
|---|---|---|---|---|
| `M3-GATE-01` | 8 个必填 section 全部有内容或显式标为缺口 | `information_integrity` | low | M3 必填 section 表 |
| `M3-GATE-02` | workflow_draft 含 trigger / steps / completion_condition 三个核心要素 | `information_integrity` | low | M3-workflow_draft |
| `M3-GATE-03` | workflow_draft 三类节点至少各 1 项 | `information_integrity` | low | M3-workflow_draft |
| `M3-GATE-04` | 闭环目标 loop_goal 由业务方与技术方共同确认 | `information_integrity` | low | M3-loop_goal |
| `M3-GATE-05` | solution_direction 已锁定（无悬而未决的备选方向） | `information_integrity` | low | M3-solution_direction |

**详细说明**：

满足以下全部条件才可放行：

1. `M3-GATE-01`：8 个必填 section 全部有内容或显式标为缺口。
2. `M3-GATE-02`：workflow_draft 含 trigger / steps / completion_condition 三个核心要素。
3. `M3-GATE-03`：workflow_draft 三类节点至少各 1 项。
4. `M3-GATE-04`：闭环目标 loop_goal 由业务方与技术方共同确认。
5. `M3-GATE-05`：solution_direction 已锁定（无悬而未决的备选方向）。

> **分类说明**：M3 五条放行条件均为 `information_integrity`，任一 FAIL 均不可 override；用户必须返回补问或修订。

## 来源 ID 约定

- `M3-{section}`：对应必填 section（如 `M3-loop_goal`、`M3-workflow_draft`）。
- `M3-Gxx`：本模块缺口 ID。
- `M3-Ixx`：本模块推断 ID。
- `M3-Cxx`：本模块结论 ID。
