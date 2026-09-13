---
name: swot-gate
description: 对 SWOT/TOWS 确认包执行八项质量检查（课题边界、证据记录、分类正确性、决定区分、因素具体性、策略完整性、取舍理由、交接安排），输出 Gate 建议（pass/fail/pending）。前四项 information_integrity 不可 override，后四项 business_risk 可 override。收到 SWOT 确认包 Gate 评估请求时使用。
---

# swot-gate：SWOT/TOWS 质量检查

对 `swot-distill` 生成的确认包（`modules/SWOT-{slug}-v{N}.md`）执行八项质量检查，输出 Gate 建议。本 Skill 只输出建议，不写授权；主 Agent 凭用户显式授权写入 `gate_pass` 或合规 override。

所有 SWOT 产物必须绑定 instance slug。slug 由主 Agent 提供，必须为 kebab-case，并与 `state.swot.{slug}.slug` 一致；本 Skill 不自动生成 `default` slug。

## 定位

**质量检查流程**：本 skill 是 Pratyaya Coach 的"SWOT Gate 评估"能力。完整的 SWOT 工作流由主 agent 编排（见 `agents/pratyaya.md`），本 skill 不编排主流程，只在被调用时执行 Gate 评估。

- **输入**：确认包 `modules/SWOT-{slug}-v{N}.md`
- **输出**：Gate 报告 `modules/SWOT-{slug}-gate-report-v{N}.md`
- **不调用**：Canvas 渲染、状态写入、授权写入

## 唯一内容边界

开始评估前必须读取：

- `references/SWOT-gate.md`：八项放行条件、分类、来源 ID、放行边界规则。

只评估确认包中实际存在的内容。框架之外的方法或术语不自动成为放行条件；只有用户明确使用时，才按原话评估。

## 八项检查（稳定 ID）

| ID | 检查项 | 分类 | 可 override |
|---|---|---|---|
| SWOT-GATE-01 | 课题边界已确认，因素与策略符合该边界 | information_integrity | 否 |
| SWOT-GATE-02 | 事实、判断、假设及来源如实记录，重要反证与冲突未被隐去 | information_integrity | 否 |
| SWOT-GATE-03 | 正式分类正确，策略引用存在且组合匹配，假设沿推导链保留 | information_integrity | 否 |
| SWOT-GATE-04 | AI 推荐、用户决定、交接建议与已确认安排清楚区分 | information_integrity | 否 |
| SWOT-GATE-05 | 因素足够具体，重要性有理由，已知重要因素没有无解释地遗漏 | business_risk | 是 |
| SWOT-GATE-06 | 策略说明作用机制、成立条件、资源约束及主要风险 | business_risk | 是 |
| SWOT-GATE-07 | 比较了有意义的选项，取舍理由能回应决策问题 | business_risk | 是 |
| SWOT-GATE-08 | 当前需要推进的事项有可承接的交接、验证与复审安排 | business_risk | 是 |

## Gate 评估流程

### 1. 读取确认包

读取 `modules/SWOT-{slug}-v{N}.md`，提取：

- 第 2 节：课题卡（分析主体、决策问题与目标、业务边界、时间范围）
- 第 3 节：SWOT 四象限（因素列表、6 字段分组）
- 第 4 节：待分类候选
- 第 5 节：被排除因素
- 第 6 节：TOWS 策略（6 字段）
- 第 7 节：选项比较与取舍
- 第 8 节：最小交接与复审
- 第 10 节：缺口表

### 2. 逐项评估

对八项检查逐一评估，输出：

| 字段 | 说明 |
|---|---|
| ID | 稳定 ID（SWOT-GATE-01 至 08） |
| 结果 | PASS / FAIL / WARN |
| 分类 | information_integrity / business_risk |
| 风险等级 | low / medium / high |
| 来源 ID | 评估依据的确认包 section |
| 影响 | 失败或提示的具体影响 |
| 建议 | 修订建议或接受条件 |

**评估规则**：

- **PASS**：检查项完全满足。
- **FAIL**：检查项不满足，影响当前决策或产物成立。
- **WARN**：轻微不足，不影响当前决策，但建议改进。

### 3. 汇总建议

| 条件 | gate_recommendation | override_eligible |
|---|---|---|
| 八项全部 PASS 或 WARN | `pass` | `false`（无失败项） |
| 任一 FAIL，全部属于 business_risk | `fail` | `true` |
| 任一 FAIL，存在 information_integrity | `fail` | `false` |
| 八项尚未评估完 | `pending` | `false` |

### 4. 生成 Gate 报告

输出 `modules/SWOT-{slug}-gate-report-v{N}.md`，结构如下：

```markdown
# Gate 评估报告 — SWOT v{N}

> 评估时间：{ISO 8601 datetime}
> 画布类型：SWOT/TOWS 分析与策略画布
> 实例：{slug}
> 确认包：modules/SWOT-{slug}-v{N}.md
> 确认包版本：v{N}
> gate_recommendation：pass / fail
> override_eligible：true / false

## 评估项

| ID | 检查项 | 结果 | 分类 | 风险等级 | 来源 ID | 影响 | 建议 |
|---|---|---|---|---|---|---|---|
| SWOT-GATE-01 | 课题边界已确认... | PASS/FAIL/WARN | information_integrity | low | SWOT-topic | ... | ... |
| SWOT-GATE-02 | ... | ... | ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... | ... | ... | ... |
| SWOT-GATE-08 | ... | ... | ... | ... | ... | ... | ... |

## Gate 建议

- gate_recommendation：pass / fail
- override_eligible：true / false
- 未通过项摘要：（仅 fail 时列出）
  - SWOT-GATE-XX：...
- 提示项摘要：（有 WARN 时逐项保留；无则写"无"）
  - SWOT-GATE-XX：...
```

## 放行边界规则

评估时必须应用以下放行边界：

| 场景 | 判定 |
|---|---|
| 假设已标明且结论限定为"先验证"，验证安排充分 | 可通过 |
| 候选因素不作为分类已成立的 TOWS 依据 | 可通过（保留候选身份） |
| 策略仍待决策但交接明确 | 可通过（用于提交评审） |
| 交接缺口：已明确角色但姓名未指定 | 提示（WARN） |
| 交接缺口：无人承接或缺时间/触发条件 | 商业风险失败（SWOT-GATE-08 FAIL） |
| 无可采用策略不自动失败 | 有依据的暂缓、停止或补证建议可通过 |
| 轻微不足 | 提示（WARN） |
| 影响当前决策的不足 | 失败（FAIL） |

## 约束

1. **只输出建议**：本 Skill 不写授权、不写状态、不写 override。主 Agent 凭用户显式授权写入。
2. **不调用渲染**：本 Skill 不调用 Canvas 渲染。
3. **不补写内容**：本 Skill 不补写确认包中缺失的内容，只评估已有内容。
4. **稳定 ID**：八项检查必须使用 SWOT-GATE-01 至 08 的稳定 ID，不得编造或合并。
5. **分类准确**：前四项必须标为 information_integrity，后四项必须标为 business_risk。
6. **完整评估**：八项必须全部评估，不得跳过；未完成评估时 gate_recommendation 保持 pending。
7. **来源可追溯**：每项评估必须标注来源 ID，指向确认包的具体 section。
8. **不引用逐字稿**：评估依据确认包内容，不引用逐字稿段落。

## 质量红线

1. 不得把 information_integrity 失败标为 business_risk。
2. 不得在存在 information_integrity 失败时设置 override_eligible=true。
3. 不得跳过任何一项检查。
4. 不得在未完成八项评估时输出 pass 或 fail。
5. 不得把候选因素当作分类已成立的依据。
6. 不得把 AI 推荐当作已确认安排。
7. 不得因为策略数量少而自动判定 FAIL；无可靠策略时说明原因可通过。
8. 不得因为交接角色未指定姓名而自动判定 FAIL；已明确角色但姓名未知时标 WARN。

## 后续流程

Gate 报告生成后，主 Agent 依次：

1. 向用户展示 Gate 建议。
2. 等待用户决策（确认 / override / 补问）。
3. 用户确认后，触发 `canvas-render` 生成 SWOT 画布。
4. 执行内容/授权审计与 Template Gate 审计。
5. 审计通过后，更新状态为 `rendered`。
