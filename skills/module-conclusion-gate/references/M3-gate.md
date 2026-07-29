# M3 闸门策略

> M3 模块（闭环目标定义、HMW 拆解与方案方向锁定）的最低可用结论与常见 blocker。本文件由 `module-conclusion-gate` 在 Gate 评估时读取。

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

满足以下全部条件才可放行：

1. 8 个必填 section 全部有内容或显式标为缺口；
2. workflow_draft 含 trigger / steps / completion_condition 三个核心要素；
3. workflow_draft 三类节点至少各 1 项；
4. 闭环目标 loop_goal 由业务方与技术方共同确认；
5. solution_direction 已锁定（无悬而未决的备选方向）。
