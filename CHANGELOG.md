# MVL 变更日志

> 本文件记录 MVL 项目的所有重要版本变更。
> 完整 SemVer 与架构说明见 [`README.md`](./README.md) / [`DESIGN.md`](./DESIGN.md) / [`docs/MVL-整体架构设计.md`](./docs/MVL-整体架构设计.md)。

## [v4.0.0] - 2026-07-31

### 重大变更（MAJOR，破坏性）

**Gate 用户权威化重构**：基于 `tmp/docs/dev-plan/gate-user-authority-plan-20260730-191044.md` 计划，4 阶段实施：

| 阶段 | Commit | 范围 |
|---|---|---|
| A（P0） | `ec99983` | 核心工作流与状态契约 |
| B（P1） | `fb5b71a` | 确认包与审计承接 |
| C（P2） | `64768cf` | 架构与用户文档同步 |
| D（P3） | （本 commit）| SemVer 与发布验证 |

### 破坏性变更（4 项）

1. **state.json 字段契约**：
   - 删除 `render_allowed` 字段
   - 新增 `gate_recommendation`（pass / fail / pending）—— LLM Gate 原始建议
   - 新增 `render_authorized`（boolean）—— 主 Agent 在用户决策后写入
   - 新增 `confirmation_mode`（gate_pass / override / null）—— caveat 属性
   - 新增 `override_audit`（条件必填，override 时）—— 含 items / reason / confirmed_by / confirmed_at
   - 3 条 if/then 条件约束：override ↔ fail+audit；gate_pass ↔ pass；前 3 态 ↔ 未授权

2. **Gate 角色从最终闸门改为建议者**：
   - Gate 只输出 `gate_recommendation`（pass/fail/pending）+ `override_eligible`（true/false）
   - 最终授权由用户在主 Agent 步骤 6 决策后写入 `render_authorized` + `confirmation_mode` + `override_audit`
   - Gate FAIL 时**不**自动回退状态；状态机由用户决策驱动

3. **Canvas 正式渲染前置条件**：
   - 旧：`render_allowed=true`
   - 新：`render_authorized=true` + `confirmation_mode ∈ {gate_pass, override}` + override 时审计完整

4. **用户确认时序**：
   - 旧：用户先说"确认 vN"才触发 Gate
   - 新：步骤 5 确认包展示后**自动**进入 Gate；"确认 vN"仅当用户已看到 Gate 报告时表示最终确认

### 5 态状态机保持不变

`draft → gaps_open ↔ review_ready → confirmed → rendered`

`confirmation_mode` 是**属性**（`gate_pass` / `override` / `null`），不是状态。

### 34 条放行条件分类（Gate Skill 重构）

| 分类 | 条数 | override 行为 |
|---|---|---|
| `information_integrity` | 28 | **不可 override**（核心事实源 / 版本 / 共识 / 必填 section 完整） |
| `business_risk` | 6 | 可 override（用户显式接受风险） |

`business_risk` 6 条具体定位：
- `M4-GATE-06`：delivery_preparation Owner / 时间
- `M5-GATE-04`（high）：can_create_value 与 M1 success_metrics 对应
- `M5-GATE-05`（high）：trust_risk_controls ≥ 3 项
- `M5-GATE-06`：issues_corrections 全 closed / accepted_risk
- `M6-GATE-05`：evolution_assets ≥ 3 项
- `M6-GATE-06`：next_step_plan 每项含动作 / Owner / 时间 / 验收

风险等级分布：28 low + 4 medium + 2 high。

### 升版边界（核心规则）

| 写入范围 | 是否触发升版 | 是否重跑 Gate | 是否重置授权 |
|---|---|---|---|
| 第 1–11 节业务内容变化 | **是**（vN → vN+1） | **是** | **是** |
| 仅第 12 节治理元数据写入 | **否**（保留 vN） | 否 | 否 |

### 主 Agent 步骤 5–7 重写

- **步骤 5**：确认包展示后自动进入 Gate（不再等"确认 vN"）
- **步骤 6**：Gate 写入 `gate_recommendation` 但不写 `render_authorized`；等待用户决策（gate_pass / override / 补问-修订）；`information_integrity` 失败不接受 override
- **步骤 7**：使用 `render_authorized` + `confirmation_mode`；override 审计缺失时阻断；`confirmation_mode=override` 时显示 caveat 标识（页面顶部"已确认 · 带保留意见" + `quality-caveat` 锚点 + 风险详情 + 打印版保留 + `canvas-data` 内嵌 override_audit）
- 渲染校验失败：状态保持 `confirmed`，`confirmation_mode` 与 `gate_recommendation` 保持原值

### 跨模块 caveat 浮现（不变量 #9）

`rendered` 模块若 `confirmation_mode=override`，下游模块若依赖被 override 的假设 / 未验证项，必须显式标注或回退重审；不在全局页静默修正。

### 确认包第 12 节（治理元数据承载层）

`Mx-v{N}.md` 新增第 12 节"Gate 与用户决策"：
- **12.1 Gate 建议**：`gate_recommendation` / Gate 评估时间 / 报告摘要
- **12.2 用户决策**：`confirmation_mode` / `render_authorized` / 确认人 / 确认人角色（可选）/ 确认时间
- **12.3 Override 审计**（仅 override 时）：表格（Gate 项 ID / 来源 ID / 分类 / 风险等级 / 影响）+ 理由 + 补救措施

缺口表加 `状态` 列：`open` / `closed` / `accepted_risk`（`accepted_risk` 由确认人在确认环节写入，不由 `mvl-distill` skill 写入）。

### 文档与维护变更

- 10 项 render-contract 自检（v3.0 8 项 + v3.2.0 新增 2 项：授权元数据 + Caveat 显示）
- 8 个核心文档同步（README / DESIGN / DEVELOPMENT / installation / user-guide / 架构文档 / mvl-canvas-spec / openai.yaml）
- 19 个文件修改（含 plugin.json）；56 处版本号 / 同步说明同步

### 端到端场景验证清单（待人工执行）

> P3 阶段 D T10 第 7 项要求；自动化无法覆盖，需 WorkBuddy 实际启动后验证。

- [ ] WorkBuddy 实际启动 + 加载 v4.0.0 plugin
- [ ] 状态机循环：draft → gaps_open ↔ review_ready → confirmed → rendered 全路径
- [ ] 真实 override 路径：用户在主 Agent 决策"override" → `confirmation_mode=override` + `override_audit` 完整 → Canvas 顶部 caveat 标识显示
- [ ] 跨模块 caveat 浮现：6 模块中 1 个 override → 全局页显式标注 + 下游模块回退检查
- [ ] 渲染校验失败：HTML 自检失败 → 状态保持 `confirmed`，`confirmation_mode` 不变
- [ ] 升版边界：仅第 12 节治理元数据写入 → 不触发升版；第 1–11 节业务内容变化 → 升版 + 重跑 Gate
- [ ] 历史版本审计：旧版 `Mx-v{N}.md.previous` 第 12 节完整保留

## [v3.1.0] - 2026-07-30

### MINOR 变更

- 文档失修修复（19 处路径引用）
- 方案 C 数据源统一（gate-policy/ 从项目目录移除，frameworks/ 与 visual-patterns/ 同步统一为纯 skill 资源读）
- 同步 plugin.json 3.0.0 → 3.1.0

## [v3.0.0] - 2026-07-30（更早）

### MAJOR 变更

- v3 整体重构：4 阶段管线（Key Points → 提炼 → Gate → 渲染）
- 视觉模式 9 文件基线
- 引入 `output/*.html` 离线可编辑交付
- 引入 `mvl-distill` / `module-conclusion-gate` / `canvas-render` 三 skill
