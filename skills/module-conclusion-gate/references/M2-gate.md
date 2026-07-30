# M2 闸门策略

> M2 模块（需求发现、用户与真实流程拆解）的最低可用结论与常见 blocker。本文件由 `module-conclusion-gate` 在 Gate 评估时读取。

> **v3.2.0 更新**：每条放行条件增加稳定 ID、分类（`information_integrity` / `business_risk`）和风险等级，供 Gate 报告与 override 审计引用。

## 必填 section

参见 `../../mvl-distill/references/workshop-canvas-map.md` 中"M2 必填 section"：

- `users`（用户）
- `needs`（需求）
- `pain_points`（痛点）
- `most_important_outcomes`（最重要结果）
- `current_workflow`（真实现状流程）
- `requirements`（需求，含 AI 刚需/增值需求及优先级）

## 必须形成的结论

用户、核心诉求、使用场景和行为链路、需求、痛点、最重要结果、真实现状流程、AI 刚需/增值需求及优先级已明确。

## 常见 blocker

- 用假想流程代替真实流程（讨论中未提供真实业务流程）
- 痛点无依据（仅说"用户觉得麻烦"等无证据描述）
- 核心需求未排序（多个需求平铺，未明确优先级）
- 用户画像不清（无具体角色/场景/行为链路）
- 现状流程与 AI 刚需脱节（流程描述完整但未指出 AI 在哪个环节创造价值）

## 评估要点

- 用户画像是否具体（角色 + 场景 + 行为链路）？
- 痛点是否可追溯到讨论中描述的具体场景？
- 需求是否按优先级排序（AI 刚需 vs 增值）？
- 真实现状流程是否含具体步骤、责任人、痛点环节？
- 最重要结果是否由业务方明确认可？

## 放行条件

每条放行条件拥有稳定 ID、分类和风险等级，供 Gate 报告与 `override_audit.items` 引用。

| ID | 条件 | 分类 | 风险等级 | 来源 |
|---|---|---|---|---|
| `M2-GATE-01` | 6 个必填 section 全部有内容或显式标为缺口 | `information_integrity` | low | M2 必填 section 表 |
| `M2-GATE-02` | users 至少包含一个具体用户角色 + 场景 + 行为链路 | `information_integrity` | low | M2-users |
| `M2-GATE-03` | pain_points 每项痛点可追溯到 current_workflow 中的具体环节 | `information_integrity` | low | M2-pain_points, M2-current_workflow |
| `M2-GATE-04` | requirements 明确区分 AI 刚需与增值需求，并标注优先级 | `information_integrity` | low | M2-requirements |
| `M2-GATE-05` | most_important_outcomes 由业务方明确认可（共识状态非"待确认"） | `information_integrity` | low | M2-most_important_outcomes |

**详细说明**：

满足以下全部条件才可放行：

1. `M2-GATE-01`：6 个必填 section 全部有内容或显式标为缺口。
2. `M2-GATE-02`：users 至少包含一个具体用户角色 + 场景 + 行为链路。
3. `M2-GATE-03`：pain_points 每项痛点可追溯到 current_workflow 中的具体环节。
4. `M2-GATE-04`：requirements 明确区分 AI 刚需与增值需求，并标注优先级。
5. `M2-GATE-05`：most_important_outcomes 由业务方明确认可（共识状态非"待确认"）。

> **分类说明**：M2 五条放行条件均为 `information_integrity`，任一 FAIL 均不可 override；用户必须返回补问或修订。

## 来源 ID 约定

- `M2-{section}`：对应必填 section（如 `M2-users`、`M2-requirements`）。
- `M2-Gxx`：本模块缺口 ID。
- `M2-Ixx`：本模块推断 ID。
- `M2-Cxx`：本模块结论 ID。
