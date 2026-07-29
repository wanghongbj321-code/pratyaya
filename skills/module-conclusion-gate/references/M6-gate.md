# M6 闸门策略

> M6 模块（终极打磨、方案择优、成果演示与闭环总结）的最低可用结论与常见 blocker。本文件由 `module-conclusion-gate` 在 Gate 评估时读取。

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

满足以下全部条件才可放行：

1. 11 个必填 section 全部有内容或显式标为缺口；
2. final_solution 继承 M4 workflow_final，未引入 M5 验证未覆盖的假设；
3. solution_comparison 至少三维对比；
4. capability_boundary 含具体的"能做 / 不能做"清单（各 ≥ 3 项）；
5. evolution_assets 至少 3 项实际形成的资产（含 Owner + 可复用条件）；
6. next_step_plan 每项含动作 / Owner / 时间 / 验收标准；
7. headline + takeaway 与 validation_review 数据一致。
