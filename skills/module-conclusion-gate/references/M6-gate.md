# M6 闸门策略

> M6 模块（终极打磨、方案择优、成果演示与闭环总结）的最低可用结论与常见 blocker。本文件由 `module-conclusion-gate` 在 Gate 评估时读取。

> **v3.2.0 更新**：每条放行条件增加稳定 ID、分类（`information_integrity` / `business_risk`）和风险等级，供 Gate 报告与 override 审计引用。

## 必填 section

参见 `../../mvl-distill/references/workshop-canvas-map.md` 中"M6 必填 section"：

- `final_solution`（最终方案）
- `solution_comparison`（多方案三维对比）
- `demo_summary`（演示结论）
- `validation_review`（三轮验证数据、问题整改和经验复盘）
- `capability_boundary`（能力边界）
- `applicable_scenarios`（适配场景）
- `optimization_space`（优化空间）
- `evolution_assets`（可复用资产：Prompt / Workflow / SOP / Knowledge / Agent / Template / Best Practice / 数据资产）
- `next_step_plan`（后续迭代、规模化复制、生产化建议与推进计划）
- `headline`（顶部一句话概括）
- `takeaway`（底部一句话总结）

## 必须形成的结论

最终方案、多方案三维择优、演示结论、验证复盘、能力边界、适配场景、优化空间、资产和后续计划均已确认。

## 常见 blocker

- 把未验证内容写成成果（final_solution 含 M5 验证未覆盖的假设）
- 边界不清（capability_boundary 仅写"通用"等无具体描述）
- 总结与证据冲突（takeaway / headline 与 validation_review 数据不一致）
- 后续建议不是讨论结论（next_step_plan 含"应该做 X"等讨论未涉及的内容）
- 资产未盘清（evolution_assets 为空或仅写"有 Prompt"等无具体内容）
- 适配场景与 M2 user 脱节（applicable_scenarios 未呼应 M2 的 users 描述）

## 评估要点

- final_solution 是否对应 M4 冻结的工作流（不是重新设计的方案）？
- solution_comparison 是否三维对比（如：业务价值 / 技术可行性 / 实施成本）？
- validation_review 是否对 M5 三轮验证数据做完整复盘？
- capability_boundary 是否含具体的"能做 / 不能做"清单？
- evolution_assets 是否盘清实际形成的资产（含 Owner 与可复用条件）？
- next_step_plan 是否每项含：动作 / Owner / 时间 / 验收标准？
- headline + takeaway 是否与 validation_review 数据一致？

## 放行条件

每条放行条件拥有稳定 ID、分类和风险等级，供 Gate 报告与 `override_audit.items` 引用。

| ID | 条件 | 分类 | 风险等级 | 来源 |
|---|---|---|---|---|
| `M6-GATE-01` | 11 个必填 section 全部有内容或显式标为缺口 | `information_integrity` | low | M6 必填 section 表 |
| `M6-GATE-02` | final_solution 继承 M4 workflow_final，未引入 M5 验证未覆盖的假设 | `information_integrity` | low | M6-final_solution, M4-workflow_final |
| `M6-GATE-03` | solution_comparison 至少三维对比 | `information_integrity` | low | M6-solution_comparison |
| `M6-GATE-04` | capability_boundary 含具体的"能做 / 不能做"清单（各 ≥ 3 项） | `information_integrity` | low | M6-capability_boundary |
| `M6-GATE-05` | evolution_assets 至少 3 项实际形成的资产（含 Owner + 可复用条件） | `business_risk` | medium | M6-evolution_assets |
| `M6-GATE-06` | next_step_plan 每项含动作 / Owner / 时间 / 验收标准 | `business_risk` | medium | M6-next_step_plan |
| `M6-GATE-07` | headline + takeaway 与 validation_review 数据一致 | `information_integrity` | low | M6-headline, M6-takeaway, M6-validation_review |

**详细说明**：

满足以下全部条件才可放行：

1. `M6-GATE-01`：11 个必填 section 全部有内容或显式标为缺口。
2. `M6-GATE-02`：final_solution 继承 M4 workflow_final，未引入 M5 验证未覆盖的假设。
3. `M6-GATE-03`：solution_comparison 至少三维对比。
4. `M6-GATE-04`：capability_boundary 含具体的"能做 / 不能做"清单（各 ≥ 3 项）。
5. `M6-GATE-05`：evolution_assets 至少 3 项实际形成的资产（含 Owner + 可复用条件）。
6. `M6-GATE-06`：next_step_plan 每项含动作 / Owner / 时间 / 验收标准。
7. `M6-GATE-07`：headline + takeaway 与 validation_review 数据一致。

> **分类说明**：
> - `M6-GATE-01` ~ `M6-GATE-04`、`M6-GATE-07` 均为 `information_integrity`，FAIL 时不可 override。
> - `M6-GATE-05` / `M6-GATE-06` 为 `business_risk`（资产盘点和未来推进计划在模拟环境下常常不完整），FAIL 时用户可显式 override 并填写理由；Gate 仍输出 `gate_recommendation=fail`，但 `override_eligible=true`。

## 来源 ID 约定

- `M6-{section}`：对应必填 section（如 `M6-final_solution`、`M6-next_step_plan`）。
- `M6-Gxx`：本模块缺口 ID。
- `M6-Ixx`：本模块推断 ID。
- `M6-Cxx`：本模块结论 ID。
