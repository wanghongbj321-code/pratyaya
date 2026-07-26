---
name: module-conclusion-gate
description: 审核 MVL 工作坊单模块的结论、证据、信息缺口、推断和人工确认，决定是否允许生成正式 Canvas。收到模块提炼结果、用户要求确认结论或生成画布，以及全局汇总前校验时使用。
---

# 模块结论闸门

把“内容已经讨论过”与“内容足以成为项目结论”分开。这个 Skill 只做质量闸门和确认登记，不生成 HTML，也不替用户补结论。

## 输入

- `modules/module-N.json`：符合 `../../schemas/module-record.schema.json` 的唯一事实源
- 对应模块框架：`../mvl-distill/frameworks/mN-*.md`
- 日程与 Canvas 唯一映射：`../mvl-distill/references/workshop-canvas-map.md`
- 原始证据：`transcripts/` 中带段落 ID 的转写
- 当前状态：`state.json`

## 工作流

1. 检查模块记录的版本、字段和引用 ID 是否完整。
2. 按 `references/gate-policy.md` 和 `workshop-canvas-map.md` 验证本次日程固定产出与对应 Canvas 字段，而不是按“页面能否填满”验收。
3. 检查每条核心结论是否有 `evidence_refs`，并区分事实、决策、假设和建议。
4. 将缺口分为 `blocker`、`major`、`minor`，逐条写明缺失影响、补问问题与状态。
5. 汇总所有推断，核心推断必须由人接受或拒绝，不能静默混入结论。
6. 向用户展示结论登记表、证据摘要、缺口与影响、推断清单，并明确询问：
   - 结论是否准确？
   - 是否还有未讨论但会影响结论的主题？
   - 是否确认当前版本可作为本模块正式成果？
7. 用户确认的是具体版本。记录确认人、角色、时间与接受风险；任何内容变更都使旧确认失效。
8. 运行 `scripts/check_gate.py modules/module-N.json`。只有退出码为 `0` 且 `render_allowed=true` 才可进入正式渲染。

未出现在 `workshop-canvas-map.md` 的方法或字段不得成为 blocker。用户没有讨论的额外方法，不得为了“完整”而要求补做。

## 正式成果放行规则

以下条件必须同时满足：

- 不存在状态为 `open` 的 `blocker` 或 `major` 缺口。
- 所有结论都有证据引用，且 `review_status` 为 `confirmed` 或 `validated`。
- 不存在状态为 `pending` 且影响为 `core` 的推断。
- `approval.version` 与模块当前 `version` 一致，且至少有一名业务责任人确认。
- 结论闸门脚本返回 `render_allowed=true`。

`minor` 缺口可以在人工明确接受风险后保留，但必须在成果中显示。`blocker` 不能以“先出图再补”的方式绕过。

## 草稿与正式版

- 草稿 Canvas 仅用于继续讨论，必须带“草稿 / 未确认 / 禁止用于管理层决策”水印。
- 草稿不得进入全局 Canvas 或领导汇报。
- 正式 Canvas 必须来自已确认的同一版本模块 JSON。
- 闸门未通过时，不得调用 Canvas 渲染；只输出阻断原因和下一轮最少补问。

## 输出

闸门结果至少包含：

```json
{
  "module_id": "M1",
  "version": 1,
  "render_allowed": false,
  "reasons": ["open blocker M1-G01: 缺少现状基线"]
}
```

将结果写回模块记录的 `gate`，同时更新 `state.json`：

- 有未关闭关键缺口：`gaps_open`
- 内容完整、等待人确认：`review_ready`
- 人确认且闸门通过：`confirmed`
- HTML 已按同版本生成：`rendered`

详细判定见 `references/gate-policy.md`。
