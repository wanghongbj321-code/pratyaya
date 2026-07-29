# M2 闸门策略

> M2 模块（需求发现、用户与真实流程拆解）的最低可用结论与常见 blocker。本文件由 `module-conclusion-gate` 在 Gate 评估时读取。

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

满足以下全部条件才可放行：

1. 6 个必填 section 全部有内容或显式标为缺口；
2. users 至少包含一个具体用户角色 + 场景 + 行为链路；
3. pain_points 每项痛点可追溯到 current_workflow 中的具体环节；
4. requirements 明确区分 AI 刚需与增值需求，并标注优先级；
5. most_important_outcomes 由业务方明确认可（共识状态非"待确认"）。
