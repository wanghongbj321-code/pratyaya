# User Journey 确认包 v1

> 画布类型：User Journey 用户旅程画布
> 版本：v1
> 状态：confirmed
> 注：本版本为 2026-08-08 重构后的目标格式样本。新字段体系已在 audit / contract / example 三方统一应用；旧字段体系已全部退场（不再作为必填也不再作为历史镜像在确认包正文中出现）。

## 必展项（紧凑前置）

### 1. 一句话结论

当前旅程的主要痛点集中在跨系统等待与材料返工，并出现至少一项可转化的机会。

## 详情

### 6. 阶段地图

| 阶段序号 | 阶段名 | 行动 | 触点与系统 | 情绪 | 痛点 | 机会 | 来源引用 |
|---|---|---|---|---|---|---|---|
| 1 | 阶段名待填写 | 提交申请 | 表单 / 门店系统 | 中性 | 暂无明显等待 | 暂无明确机会 | Journey 关键主张 1 |
| 2 | 阶段名待填写 | 补充材料 | 客服 / 审批系统 | 负向 | 返工补交 | 统一材料口径 | Journey 关键主张 2 |
| 3 | 阶段名待填写 | 获取结果 | 短信 / 业务系统 | 正向 | 信息缺失 | 主动通知 | Journey 关键主张 3 |

> 此节为 `render-contract-journey.md` 中 `journey-stage-*` 动态锚点的事实源。
> 阶段数量由本表数据行决定，不使用固定 7 槽位。
> 自 v2.3.2 起：列 6 = `痛点`，列 7 = `机会`。

### 6a. 质量鉴别

| 维度 | 判定 | 依据 |
|---|---|---|
| user_perspective（用户视角） | 通过 | 阶段以用户动作表达 |
| business_outcome（到达业务结果） | 通过 | 终点到用户获取结果 |
| pain_opportunity_visible（痛点与机会可见） | 通过 | 痛点与机会已标出 |
| no_solution_bias（未预设方案） | 通过 | 未写入解决方案 |

### 6b. 痛点与机会

| ID | 阶段 | 类型 | 来源 | 描述 | 影响 | 机会判断 | 来源引用 |
|---|---|---|---|---|---|---|---|
| JOURNEY-F01 | 阶段 2 | pain_point | user_stated | 材料补交造成返工 | 延迟获取结果 | 统一材料口径可减少返工 | Journey 关键主张 2 |
| JOURNEY-F02 | 阶段 3 | pain_point | user_stated | 信息缺失导致门店无法预判到货 | 店长难以安排上架人力 | 加强主动通知可降低询问成本 | Journey 关键主张 3 |
| JOURNEY-F03 | 阶段 3 | opportunity | user_stated | 主动通知机制可作为新增能力 | 提升门店掌控感 | 与现有短信通道整合可低成本上线 | Journey 关键主张 3 |
| JOURNEY-F04 | 阶段 3 | opportunity | inferred_from_pain_point | 在 F02 痛点之上推断"补货状态看板"雏形 | 影响 F02 缓解速度 | 由 JOURNEY-Inf01 推断 | Journey 关键主张 3 |

> 类型固定为 `pain_point` / `opportunity`；来源 `user_stated` / `inferred_from_pain_point` / `inferred_from_quality`；ID 前缀 `JOURNEY-Fxx` 保留。

### 7. 结论登记表

| ID | 结论 | 类型 | 共识状态 |
|---|---|---|---|
| JOURNEY-C01 | 跨系统等待与返工是核心痛点 | fact | 共识 |

### 8. 缺口表

| ID | 等级 | 状态 | 描述 | 缺失影响 | 最少补问 |
|---|---|---|---|---|---|
| JOURNEY-G01 | minor | closed | 无 | 无 | 无 |

### 9. 推断表

| ID | 推断 | 影响 | 状态 |
|---|---|---|---|
| JOURNEY-Inf01 | 主动通知机制（F03）由用户 1 与 2 类断言共同支持 | 影响 F03 的优先级 | 待接受 |

### 10. 关键证据引用

- Journey Key Points 第 4 节显示阶段 2、3 均有痛点 / 机会信号。
- Journey Key Points 第 5 节显示四个质量维度均已判定。

## 12. Gate 与用户决策

Gate 建议：pass

