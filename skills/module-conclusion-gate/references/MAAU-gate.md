# MAAU 闸门策略

> MAAU 全局画布一次性综合提炼源包（`generation_path=transcript-direct`）的最低可用结论与常见 blocker。本文件由 `module-conclusion-gate` 在 Gate 评估时读取（`gate_reference=references/MAAU-gate.md`）。
>
> 状态指针：`state.maau.{slug}`。Gate 对六板块源包**整体评估**，输出一份 Gate 报告；ID 使用 `MAAU-GATE-01` 起始，**不得复用 `M1-GATE-*` 到 `M6-GATE-*`**。

> 每条放行条件包含稳定 ID、分类（`information_integrity` / `business_risk`）和风险等级，供 Gate 报告与 override 审计引用。`information_integrity` 不可 override，`business_risk` 可 override。

## 必填板块

参见 `../../maau-synthesize/references/maau-synth-spec.md` 六板块字段契约：

- **Intent**（goal / value / success_metrics）
- **User**（users / needs / pain_points / most_important_outcomes）
- **Agent Team**（角色 / 职责 / 是否 Agent / 决策边界 / 协作模式）
- **Workflow**（触发 / 步骤 / 完成条件 / 三类节点 / 关键规则）
- **Context**（knowledge / data_sources / tools_skills + 可获得性）
- **Validation**（can_execute / can_create_value / evolution）

## 必须形成的结论

逐字稿已被综合为一份可追溯的 MAAU 六板块源包，六板块字段完整，Workflow 三类节点齐备，Context 仅列已讨论确认项，Validation 三类证据充分，且未静默抹平分歧与推断。

## 常见 blocker

- 源包版本 / slug / project / group 与 state 不一致
- 未写 `generation_path=transcript-direct`，或试图直接读转写渲染而非源包
- 六板块固定字段缺失（未进入缺口表即视为缺失）
- Workflow 触发、步骤、完成条件或三类节点缺项
- Context 按常见做法自动补全而非仅列已讨论确认项
- Validation 三类证据或缺口表达不充分
- Intent / User / Workflow / Validation 跨板块不自洽
- 分歧、推断、未决项被静默抹平
- 确认人、确认时间、用户决策区不可追溯

## 评估要点

- 源包版本、slug、project/group 是否与 state 一致？
- 是否 `generation_path=transcript-direct`，且数据源为 Markdown 源包而非直接读转写渲染？
- 六板块固定字段是否完整？缺失是否都进入缺口表？
- Workflow 触发 / 步骤 / 完成条件 / 三类节点是否齐备？
- Context 是否仅列已讨论确认项并说明可获得性？
- Validation 三类（能否执行 / 能否创造价值 / 能否持续进化）证据或缺口表达是否充分？
- Intent / User / Workflow / Validation 跨板块是否自洽？
- 分歧、推断、未决项是否被静默抹平？
- 确认人、确认时间、用户决策区是否可追溯？

## 放行条件

每条放行条件拥有稳定 ID、分类和风险等级，供 Gate 报告与 `override_audit.items` 引用。

| ID | 条件 | 分类 | 风险等级 | 来源 |
|---|---|---|---|---|
| `MAAU-GATE-01` | 源包版本、slug、project/group 与 state 一致 | `information_integrity` | low | MAAU 源包 头部 + state.maau.{slug} |
| `MAAU-GATE-02` | `generation_path=transcript-direct` 且源包来自 Markdown，不直接读转写渲染 | `information_integrity` | low | MAAU 源包 头部 + maau-synth-spec |
| `MAAU-GATE-03` | 六板块固定字段完整，缺失均进入缺口表 | `information_integrity` | high | MAAU 源包 6.1-6.6 + 8 缺口表 |
| `MAAU-GATE-04` | Workflow 触发、步骤、完成条件与三类节点齐备 | `information_integrity` | high | MAAU 源包 6.4 Workflow |
| `MAAU-GATE-05` | Context 仅列已讨论确认项并说明可获得性 | `information_integrity` | medium | MAAU 源包 6.5 Context |
| `MAAU-GATE-06` | Validation 三类证据或缺口表达充分 | `business_risk` | medium | MAAU 源包 6.6 Validation |
| `MAAU-GATE-07` | Intent / User / Workflow / Validation 跨板块自洽 | `business_risk` | medium | MAAU 源包 6.1-6.6 跨板块 |
| `MAAU-GATE-08` | 分歧、推断、未决项没有被静默抹平 | `information_integrity` | high | MAAU 源包 7 结论表 + 9 推断表 |
| `MAAU-GATE-09` | 确认人、确认时间、用户决策区可追溯 | `information_integrity` | low | MAAU 源包 12 Gate 与用户决策 |

**详细说明**：

满足以下全部条件才可放行：

1. `MAAU-GATE-01`：源包版本、slug、project/group 与 state 一致。
2. `MAAU-GATE-02`：`generation_path=transcript-direct` 且源包来自 Markdown，不直接读转写渲染。
3. `MAAU-GATE-03`：六板块固定字段完整，缺失均进入缺口表（不静默缺省）。
4. `MAAU-GATE-04`：Workflow 触发、步骤、完成条件与三类节点（Agent 执行 / 人工操作确认 / 人审 + Agent 执行）齐备。
5. `MAAU-GATE-05`：Context 仅列已讨论确认项并说明可获得性；若因"自动补全"失败，按 `information_integrity` 不可 override；若仅为"可获得性说明不足"可视为 `business_risk`。
6. `MAAU-GATE-06`：Validation 三类证据或缺口表达充分（`business_risk`，可 override）。
7. `MAAU-GATE-07`：Intent / User / Workflow / Validation 跨板块自洽（`business_risk`，可 override）。
8. `MAAU-GATE-08`：分歧、推断、未决项没有被静默抹平。
9. `MAAU-GATE-09`：确认人、确认时间、用户决策区可追溯。

> **分类说明**：`information_integrity`（01-04、08、09 及 05 的自动补全情形）任一 FAIL 均不可 override，用户必须返回补问或修订；`business_risk`（06、07 及 05 的可获得性说明情形）可 override，但 override 审计项 ID 必须为 `MAAU-GATE-*` 且 `category=business_risk`。

## 来源 ID 约定

- `MAAU-{section}`：对应源包板块（如 `MAAU-6.4 Workflow`、`MAAU-6.5 Context`）。
- `MAAU-Gxx`：源包缺口 ID（Gate 报告引用）。
- `MAAU-Ixx`：源包推断 ID。
- `MAAU-Cxx`：源包结论 ID。
- `MAAU-GATE-xx`：本文件放行条件稳定 ID，仅用于 Gate 报告与 override 审计。
