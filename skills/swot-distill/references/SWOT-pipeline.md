# SWOT/TOWS 工作流管线

> 本文件是 `swot-distill` 的调用契约，描述 SWOT/TOWS 从课题澄清到画布渲染的完整管线。
> 主 Agent 编排整体流程，`swot-distill` 只负责 Stage 1（Key Points 抽取）和 Stage 2（确认包生成）。

## 管线总览

```
课题澄清 → 关键材料整理 → SWOT 因素提炼 → 因素质量检查 → SWOT 聚焦 → TOWS 策略推导 → 策略比较与取舍 → 最小交接 → Gate → 用户确认 → 画布渲染
```

## 阶段与产物

| 阶段 | 产物 | 产物路径 | 说明 |
|---|---|---|---|
| 课题澄清 | 课题卡（初步） | 主 Agent 内存 | 先提取再补问，每轮只追问最影响分析的 1–2 项 |
| 关键材料整理 | Key Points | `modules/SWOT-{slug}-keypoints.md` | Stage 1 产物，30 秒浏览 |
| SWOT 因素提炼 | 确认包 | `modules/SWOT-{slug}-v{N}.md` | Stage 2 产物，唯一事实源 |
| Gate | Gate 报告 | `modules/SWOT-{slug}-gate-report-v{N}.md` | 由 `swot-gate` 生成 |
| 画布渲染 | HTML 画布 | `output/swot-canvas-{slug}--v{N}.html` | 由 `canvas-render` 生成 |

## Stage 1：Key Points 抽取

**目标**：在 30 秒内让用户了解"这次讨论了什么、课题边界是否明确、因素覆盖度如何、缺什么"。

**触发**：主 Agent 在课题卡核心边界确认后调用。

**输入**：

- 逐字稿或用户提供的材料（已由主 Agent 存档）
- 课题卡（初步）

**输出**：`modules/SWOT-{slug}-keypoints.md`，结构如下：

```markdown
# SWOT Key Points（第 X 轮）

> 生成时间：{YYYY-MM-DD HH:MM}
> 画布类型：SWOT/TOWS 分析与策略画布
> 轮次：第 X 轮
> 数据源：{来源说明}
> 实例：{slug}

## 1. 课题卡概览

| 字段 | 内容 | 状态 |
|---|---|---|
| 分析主体 | ... | 已确认 / 待确认 |
| 决策问题与目标 | ... | 已确认 / 待确认 |
| 业务边界 | ... | 已确认 / 待确认 |
| 时间范围 | ... | 已确认 / 待确认 |
| 比较基准 | ... | 已确认 / 待补 |
| 可控边界 | ... | 已记录 |
| 已知约束 | ... | 已记录 |
| 关键假设与分歧 | ... | 持续记录 |

## 2. 材料整理摘要

本次讨论/材料中的关键信息：

- 关键信息 1：...
- 关键信息 2：...

## 3. SWOT 因素候选

### 优势（Strengths）

- SWOT-F-S01：...（来源：...；判断性质：...）
- S-02：...

### 劣势（Weaknesses）

- SWOT-F-W01：...
- W-02：...

### 机会（Opportunities）

- SWOT-F-O01：...
- O-02：...

### 威胁（Threats）

- SWOT-F-T01：...
- T-02：...

### 待分类候选

- CAND-01：...（归属未明，原因：...）

## 4. 因素质量初判

| 因素 | 证据强度 | 分类确定性 | 重要性 | 处理建议 |
|---|---|---|---|---|
| SWOT-F-S01 | 强/中/弱 | 高/中/低 | 高/中/低 | 保留/待验证/排除 |
| ... | ... | ... | ... | ... |

## 5. TOWS 策略线索

### SO 策略（利用优势抓住机会）

- SWOT-STR-SO01 候选：...（关联因素：SWOT-F-S01, SWOT-F-O01）

### ST 策略（利用优势应对威胁）

- SWOT-STR-ST01 候选：...

### WO 策略（克服劣势抓住机会）

- SWOT-STR-WO01 候选：...

### WT 策略（克服劣势应对威胁）

- SWOT-STR-WT01 候选：...

## 6. 覆盖度初判

| 区块 | 状态 | 简评 |
|---|---|---|
| 课题卡核心边界 | 已覆盖 / 部分覆盖 / 未涉及 | ... |
| 优势象限 | ... | ... |
| 劣势象限 | ... | ... |
| 机会象限 | ... | ... |
| 威胁象限 | ... | ... |
| SO 策略 | ... | ... |
| ST 策略 | ... | ... |
| WO 策略 | ... | ... |
| WT 策略 | ... | ... |

## 7. 用户决策提示

> 基于以上概览，请选择：**提炼** / **补问** / **先看个样子**
```

**约束**：

- 长度控制：每节最多 5 条因素，供 30 秒快速浏览。
- 不做确认包生成、不评估 Gate、不写策略取舍结论。
- 末尾必须输出用户决策提示。
- 跨轮次覆盖：第 N 轮 Key Points 覆盖第 N-1 轮（同文件覆盖式更新，保留最后一轮）。
- 覆盖度初判必须包含课题卡核心边界 + 四象限 + TOWS 四组。

## Stage 2：确认包生成

**目标**：将 Key Points 转化为经过对齐的、唯一事实源的确认包 `SWOT-{slug}-v{N}.md`。

**触发**：主 Agent 在用户回复"提炼"后调用。

**输入**：

- 逐字稿或用户材料（已存档）
- `modules/SWOT-{slug}-keypoints.md`（Stage 1 产物）
- `frameworks/swot-frame.md`（SWOT 框架）

**输出**：`modules/SWOT-{slug}-v{N}.md`，全 Markdown，结构见 SKILL.md 的确认包模板。

**约束**：

- 引用格式：仅引用 Key Points 与确认包自身的 section，不引用逐字稿段落。
- 推断必须独立登记，不写入结论登记表。
- 缺口必须说明"缺失影响"，不能只说"信息不足"。
- 不调用 Canvas 渲染、不执行 Gate 判定。
- 状态写入由主 Agent 在用户确认后执行，不在本 skill 内部。
- 版本号管理：升版时 vN → vN+1，旧版本归档为 `modules/SWOT-{slug}-v{N}.md.previous`，不清空。
- 缺口表必须含 `状态` 列（`open` / `closed` / `accepted_risk`），其中 `accepted_risk` 由确认人在确认环节写入，不由本 skill 写入。
- 元数据必须包含：`画布类型` / `版本` / `状态` / `生成时间`（ISO 8601 datetime，skill 生成时自动写入） / `确认人` / `确认人角色（可选）` / `确认时间`（用户填写）。
- 第 12 节"Gate 与用户决策"由 Gate 流程与主 Agent 在用户决策后写入；本 skill 不写治理结果，只负责预留该节结构。

## 后续流程（主 Agent 编排）

Stage 2 完成后，主 Agent 依次：

1. 触发 `swot-gate` 执行八项检查，生成 Gate 报告。
2. 向用户展示 Gate 建议，等待用户决策（确认 / override / 补问）。
3. 用户确认后，触发 `canvas-render` 生成 SWOT 画布。
4. 执行内容/授权审计与 Template Gate 审计。
5. 审计通过后，更新状态为 `rendered`。

## 升版边界

确认包版本受两类写入影响：

| 写入范围 | 是否触发升版 | 是否重跑 Gate | 是否重置授权 |
|---|---|---|---|
| 第 1–11 节业务内容（含课题卡、因素、策略、交接、结论、缺口、推断、证据登记）变化 | **是**（vN → vN+1） | **是** | **是**（清空 `gate_recommendation` / `render_authorized` / `confirmation_mode` / `override_audit`） |
| 仅第 12 节"Gate 与用户决策"治理元数据写入（Gate 报告、用户决策、Override 审计） | **否**（保留 vN） | 否（已是当前评估结果） | 否（这是当前版本的授权写入） |

**规则**：

- **业务内容变化**：必须 `version + 1` + `gate_recommendation=pending` + `render_authorized=false` + `confirmation_mode=null` + 清空当前版本 `override_audit`；旧版本确认包归档为 `SWOT-{slug}-v{N}.md.previous`，旧版第 12 节审计随旧版保留。
- **治理元数据写入**（仅第 12 节）：不触发升版；Gate 报告摘要与用户授权属于当前版本的元数据补充。
- **历史版本审计**不得清空：旧版 `SWOT-{slug}-v{N}.md.previous` 的第 12 节（包括历史 override 审计）必须完整保留，用于追溯。

## 元数据生成时间字段

- `生成时间`（`SWOT-{slug}-v{N}.md` 顶部）由本 skill 在 Stage 2 生成确认包时按系统真实时间写入（ISO 8601 datetime）。
- `确认时间`由主 Agent 在用户决策后写入；不得使用 skill 生成时间。
- 禁止在文件名、文档标题、报告标识中编造时间戳。
