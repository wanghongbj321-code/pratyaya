# M1 闸门策略

> M1 模块（战略对齐、项目分组与闭环证据准备）的最低可用结论与常见 blocker。本文件由 `module-conclusion-gate` 在 Gate 评估时读取。

> **v4.0.0 更新**：每条放行条件增加稳定 ID、分类（`information_integrity` / `business_risk`）和风险等级，供 Gate 报告与 override 审计引用。

## 必填 section

参见 `../../mvl-distill/references/workshop-canvas-map.md` 中"M1 必填 section"：

- `goal`（业务目标）
- `value`（价值）
- `success_metrics`（成功指标：指标、基线、目标、衡量方式）
- `evidence`（核心证据：业务数据、用户案例、现有流程痛点等）
- `boundary`（边界）
- `acceptance`（校验标准）
- `grouping`（项目分组）

## 必须形成的结论

业务目标、价值、成功指标、核心证据、校验标准、边界和项目分组已明确。

## 常见 blocker

- 没有证据（讨论中未提供任何业务数据/用户案例/流程痛点）
- 成功指标缺基线、目标或衡量方式（仅写"提升效率"等不可验证描述）
- 边界或校验标准不清（讨论中未明确"哪些不在范围内"或"如何判定通过"）
- 业务方对"业务目标"和"价值"未达成共识
- 项目分组未明确（每组的 MVL 候选不清）

## 评估要点

- 业务方对"业务目标"和"价值"是否有共识？
- 成功指标是否包含基线、目标、衡量方式三项？
- 核心证据是否来源于实际讨论（非补全）？
- 项目分组是否明确（每组的 MVL 候选、组号、组员）？
- 边界与校验标准是否清晰、可执行？

## 放行条件

每条放行条件拥有稳定 ID、分类和风险等级，供 Gate 报告与 `override_audit.items` 引用。

| ID | 条件 | 分类 | 风险等级 | 来源 |
|---|---|---|---|---|
| `M1-GATE-01` | 7 个必填 section 全部有内容或显式标为缺口 | `information_integrity` | low | M1 必填 section 表 |
| `M1-GATE-02` | 业务方对 goal / value / success_metrics 三个核心 section 有明确共识 | `information_integrity` | low | M1-goal, M1-value, M1-success_metrics |
| `M1-GATE-03` | success_metrics 至少有一项包含"基线 + 目标 + 衡量方式"完整三要素 | `information_integrity` | low | M1-success_metrics |
| `M1-GATE-04` | 边界 section 明确写出"不在范围内"的具体内容 | `information_integrity` | low | M1-boundary |
| `M1-GATE-05` | 项目分组明确（每个 MVL 候选有组号、组员、目标场景） | `information_integrity` | low | M1-grouping |

**详细说明**：

满足以下全部条件才可放行：

1. `M1-GATE-01`：7 个必填 section 全部有内容或显式标为缺口。
2. `M1-GATE-02`：业务方对 goal / value / success_metrics 三个核心 section 有明确共识。
3. `M1-GATE-03`：success_metrics 至少有一项包含"基线 + 目标 + 衡量方式"完整三要素。
4. `M1-GATE-04`：边界 section 明确写出"不在范围内"的具体内容。
5. `M1-GATE-05`：项目分组明确（每个 MVL 候选有组号、组员、目标场景）。

> **分类说明**：M1 五条放行条件均为 `information_integrity`，任一 FAIL 均不可 override；用户必须返回补问或修订。

## 来源 ID 约定

- `M1-{section}`：对应必填 section（如 `M1-goal`、`M1-grouping`）。
- `M1-Gxx`：本模块缺口 ID（Gate 报告引用）。
- `M1-Ixx`：本模块推断 ID。
- `M1-Cxx`：本模块结论 ID。
