# V2C VAC Gate 放行条件

本文件是 `v2c-vac-gate` 的评估依据，定义 V2C Value Attribution Canvas（VAC）确认包的稳定放行条件、分类、风险等级与来源 ID。

V2C VAC 的思路来源于王鸿的 V2C FDE 工作方法论。Gate 只审查当前确认包是否足以作为“价值归因观察画布”的正式事实源，不证明业务价值已经发生。

## 放行条件（12 条，稳定 ID）

| ID | 条件 | 分类 | 风险等级 | 来源 |
|---|---|---|---|---|
| `V2C-GATE-01` | 确认包版本、slug、project/group/topic 与 `state.v2c_vac.{slug}` 一致 | `information_integrity` | low | 确认包头部 + state.v2c_vac.{slug} |
| `V2C-GATE-02` | `canvas_type=v2c-vac`，且 `generation_path` 明确为 `pipeline` 或 `transcript-direct` | `information_integrity` | low | 确认包头部 + v2c-vac-spec |
| `V2C-GATE-03` | 确认包第 1-12 节结构完整；缺失 section 已登记缺口，不静默补齐 | `information_integrity` | high | 确认包 1-12 + `V2C-AGxx` |
| `V2C-GATE-04` | Scenario、Capability、Change、Business Impact、Value 严格分层，未把 KPI / Measure / 技术组件写成因果节点 | `information_integrity` | high | 确认包 5-9 + `V2C-Qxx` |
| `V2C-GATE-05` | Primary Capability 描述为业务能力，含作用对象、判断 / 决策 / 执行动作与可用标准 | `information_integrity` | high | 确认包 6 + `V2C-Cxx` + `V2C-AG01` |
| `V2C-GATE-06` | 仅一个 Primary Change 进入 Business Impact Chain；Other Observed Changes 未静默连入主链 | `information_integrity` | high | 确认包 7-8 + `V2C-CHxx` + `V2C-AG02` |
| `V2C-GATE-07` | Primary Change 到 Business Impact Chain 的关系有来源线索、证据状态和断点说明 | `business_risk` | high | 确认包 8 + `V2C-AG03` + `V2C-AG04` |
| `V2C-GATE-08` | Value 是经营价值锚点，未把 Capability、Change、Driver 或中间 KPI 当最终 Value | `business_risk` | medium | 确认包 9 + `V2C-Vxx` + `V2C-AG05` |
| `V2C-GATE-09` | Baseline、Actual / Improvement、Confounders / Attribution 表达诚实；无 Baseline 时未输出量化收益 | `business_risk` | high | 确认包 9 + `V2C-AG06` |
| `V2C-GATE-10` | `F / H / ? / E` 证据状态使用正确，`E` 仅用于 Pilot / 数据 / 观察 / 对照验证支持 | `information_integrity` | high | 确认包 5-12 + 证据状态表 |
| `V2C-GATE-11` | Attribution Gaps 与推断表完整：未知、冲突、假设和未验证关系均有 `V2C-AGxx` 或 `V2C-Infxx` 登记 | `information_integrity` | high | 确认包 10-12 |
| `V2C-GATE-12` | Attribution Quality Check 四维度均有判定，下一步建议为 Proceed / Explore / Defer / Stop 且理由与证据状态一致 | `business_risk` | medium | 确认包 11 |

## 分类与可 override 关系

| 分类 | 含义 | 用户 override |
|---|---|---|
| `information_integrity` | 正式产物能否真实成立，包括身份一致、字段覆盖、语义分层、证据状态、缺口登记与推断登记 | **否** |
| `business_risk` | 归因链已有事实基础，但价值判断、Baseline、验证计划或下一步投入建议仍有业务不确定性 | **是**（填写理由后） |

**分类汇总**：7 条 `information_integrity` + 5 条 `business_risk`。

只要存在任一 `information_integrity` FAIL，`override_eligible=false`；当前版本只能回到补问或修订，不得进入正式 override。

仅存在 `business_risk` FAIL 时，`override_eligible=true`。用户必须看见风险影响，并填写理由、确认人、确认时间和补救措施后，主 Agent 才能进入 override 授权流程。

## V2C-GATE 与 V2C-AG 的边界

| ID 空间 | 用途 | 示例 | 是否可作为 override_audit.assessment_id |
|---|---|---|---|
| `V2C-GATE-*` | Gate 放行条件稳定 ID | `V2C-GATE-09`：Baseline 与量化收益检查 | 是 |
| `V2C-AGxx` | 归因断点 / 补问 / 验证计划 ID | `V2C-AG06`：是否已经建立可比较 Baseline | 否 |

Gate 报告的来源 ID 可以引用 `V2C-AGxx`、确认包 section、`V2C-Qxx`、`V2C-Infxx` 或 `state.v2c_vac.{slug}`。但 override 审计项必须引用 `V2C-GATE-*`：

```json
{
  "assessment_id": "V2C-GATE-09",
  "source_id": "V2C-AG06",
  "category": "business_risk",
  "risk_level": "high"
}
```

不得把 `V2C-AGxx` 写入 `assessment_id`。用户接受的是某条 Gate 风险，不是把某个归因断点改写为事实。

## 缺口等级定义

| 等级 | 影响 | 处置 |
|---|---|---|
| `blocker` | 使主归因链或 Gate 评估无法成立 | 必须关闭，不允许接受风险 |
| `major` | 会显著改变归因链、价值判断或下一步建议 | 必须关闭或明确接受风险 |
| `minor` | 不改变核心归因判断 | 可后续补齐或明确接受风险 |

严重度（blocker / major / minor）与分类（information_integrity / business_risk）是两个维度：

- `information_integrity`：无论严重度，均不可正式 override；
- `business_risk`：用户可在看见影响并填写理由后 override；
- minor 仍不得静默忽略，必须关闭或显式接受。

## 默认 Attribution Gap 映射

| Gap ID | 断点 | 默认分类 | 默认等级 | 主要关联 Gate |
|---|---|---|---|---|
| `V2C-AG01` | Capability 组合是否达到业务可用水平 | information_integrity | blocker | `V2C-GATE-05` |
| `V2C-AG02` | Primary Change 是否真实发生 | information_integrity | blocker | `V2C-GATE-06` |
| `V2C-AG03` | Primary Change 如何转化为实际业务执行 | business_risk | major | `V2C-GATE-07` |
| `V2C-AG04` | 执行变化是否改善 Business Impact | business_risk | major | `V2C-GATE-07` |
| `V2C-AG05` | Business Impact 如何贡献最终 Value | business_risk | major | `V2C-GATE-08` |
| `V2C-AG06` | 是否已经建立可比较 Baseline | business_risk | major | `V2C-GATE-09` |

默认 Gap 未关闭时，Gate 必须在对应 `V2C-GATE-*` 项中说明影响。`information_integrity` 默认 Gap open 时，不得建议 override。

## 证据状态

| 状态 | 含义 | Gate 判定规则 |
|---|---|---|
| `F` | Fact（事实） | 必须有当前项目材料、访谈、业务记录或明确来源线索 |
| `H` | Hypothesis（假设） | 可保留，但必须有验证计划或进入业务风险说明 |
| `?` | Question / Gap（未知或断点） | 必须登记 `V2C-AGxx` 或 `V2C-Infxx`，不得静默放行 |
| `E` | Evidence-supported（验证支持） | 必须有 Pilot、业务数据、现场观察或对照验证说明 |

`E` 不是 Estimate / External。估算、行业基准或外部材料若未在当前项目验证，不得标为 `E`。

## 来源 ID 约定

- `state.v2c_vac.{slug}`：当前 V2C VAC instance 状态指针。
- `V2C-Sxx`：Scenario 事实。
- `V2C-Cxx`：Capability 结论。
- `V2C-CHxx`：Change 结论。
- `V2C-BIxx`：Business Impact 结论。
- `V2C-Vxx`：Value 结论。
- `V2C-AGxx`：Attribution Gap。
- `V2C-Qxx`：Quality Check。
- `V2C-Infxx`：Inference。
- `V2C-GATE-*`：Gate 放行条件稳定 ID，仅用于 Gate 报告与 override 审计。

## 评估表输出格式

Gate 评估报告必须为每条放行条件输出：稳定 ID、PASS/FAIL、分类、风险等级、来源 ID、影响和建议。评估报告格式见 `v2c-vac-gate/SKILL.md` 的“Gate 评估流程”。

## 质量红线

1. `information_integrity` FAIL 不可 override。
2. `business_risk` FAIL 可以 override，但必须完整审计。
3. `override_audit.assessment_id` 必须使用 `V2C-GATE-*`。
4. `V2C-AGxx` 只能作为来源或归因断点，不能作为 Gate 条件 ID。
5. 无 Baseline 时不得放行含量化收益的确认包。
6. 未经 Pilot / 数据 / 观察 / 对照验证的内容不得标为 `E`。
7. 不得为了输出完整画布而补齐未讨论的因果关系。
8. Gate 文件只定义建议规则，不写授权、不写状态、不触发渲染。
