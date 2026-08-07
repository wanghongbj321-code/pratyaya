# Pratyaya 设计文档

> 适用版本：以 `.codebuddy-plugin/plugin.json` `version` 字段为权威

## 1. 决策

**单专家 + 多 Skill**：一个 `pratyaya` 专家包，调度九个 Skill（`mvl-distill` / `gc-distill` / `hmw-distill` / `journey-distill` / `module-conclusion-gate` / `gc-gate` / `hmw-gate` / `journey-gate` / `canvas-render`）完成工作流。每个 Skill 内部用最简、确定的契约约束 LLM 行为。五类画布（MVL / 黄金圈 / HMW / 用户画像 / 用户旅程）共享同一治理语义；用户画像当前为独立画布占位状态区块，用户旅程拥有独立提炼 Skill、门禁 Skill 与渲染契约。

**人仍是最终决策者**：Skill 之间通过显式的确认包（v{N}.md）交付，每一步可被工作坊组织者审阅和回退。

**画布类型路由**：主 Agent 在步骤 -1 判定画布类型（MVL / 黄金圈 / HMW / 用户画像 / 用户旅程），加载对应框架与确认包命名空间，各画布互不串扰（详见 [agents/pratyaya.md](./agents/pratyaya.md)）。

## 2. 北极星目标

- 一份能被生产团队复用的结论资产：MVL 覆盖目标、用户、Agent Team、Workflow、Context、Validation 六角度；黄金圈覆盖 WHY/HOW/WHAT 三层；HMW 覆盖问题陈述四字段与想法种子；Journey 覆盖动态阶段、等待返工、风险节点、关键断点与质量鉴别
- 同一份资产同时支撑：模块化智能体画布、对外汇报、长期复盘
- 多类画布输出同一套治理语义：版本化确认包 + Gate 建议 + 用户授权 + 可审计渲染

## 3. 问题定义

工作坊常陷入的反模式（以 MVL 为原型，黄金圈 / HMW 通用）：

- 文档、画布、汇报三套分离的产物
- 结论含糊，无法被产品/工程引用
- 验证缺失，AI 演示结果无法形成可追溯结论
- 重复讨论、结论漂移、关键假设丢失
- 跨模块结论拼接成全局时不自洽

正式 HTML 必须成为流程的最后一步，不允许以"先有页面再补事实"的方式生成。

## 4. 分层

四层流水线（画布类型决定分析层与治理层的具体 Skill）：

- **原始材料层** — 转写稿、上下文快照、用户输入
- **分析层**（mvl-distill / gc-distill / hmw-distill / journey-distill） — Key Points 概览（`Mx-keypoints.md` / `GC-keypoints.md` / `HMW-keypoints.md` / `JOURNEY-keypoints.md`）+ 确认包（`Mx-v{N}.md` / `GC-v{N}.md` / `HMW-v{N}.md` / `JOURNEY-v{N}.md`）+ 缺口 + 推断
- **治理层**（module-conclusion-gate / gc-gate / hmw-gate / journey-gate） — LLM Gate 评估（输出 `gate_recommendation` + `override_eligible` 建议，**不**写最终授权）+ 用户决策（主 Agent 写入 `render_authorized` + `confirmation_mode` + `override_audit`）
- **展示层**（canvas-render） — 模块 Canvas / 黄金圈 Canvas / HMW Canvas / Journey Canvas + 全局 Canvas + 管理层报告

## 5. 数据源与视觉模式

**四类事实源边界**（渲染链路中各自承担不同角色，不可混淆）：

| 事实源 | 路径 | 角色 | 是否进渲染链路 |
|---|---|---|---|
| **内部参考**（不入库） | `internal/`（本地目录，gitignore） | 设计讨论期的版面草稿与 worksheet，**仅给人看** | ❌ 不读取 |
| **示例模板**（入库） | `examples/canvas-html/*-canvas.html` | 最终画布的**版面与签名视觉参照**（一级模块布局、治理面板位置、交互骨架） | ⚠️ 只参照版面，不复制数据 |
| **渲染契约**（入库） | `skills/canvas-render/references/render-contract-*.md` | 稳定锚点与数据映射的**事实源**（LLM 读契约现场生成 HTML） | ✅ 必须读取 |
| **视觉模式**（入库） | `skills/canvas-render/visual-patterns/NN-{id}.md` | 色板、字体、网格、组件及边界（frontmatter 用于推荐） | ✅ 必须读取 |

| 资产 | 路径 | 角色 |
|---|---|---|
| 确认包（唯一事实源） | `modules/Mx-v{N}.md` / `GC-v{N}.md` / `HMW-v{N}.md` / `JOURNEY-v{N}.md` | 正式 Canvas 渲染依据（画布类型对应命名空间） |
| Key Points 概览 | `modules/Mx-keypoints.md` / `GC-keypoints.md` / `HMW-keypoints.md` / `JOURNEY-keypoints.md` | 草稿 Canvas 数据源（不进入正式流程） |
| Gate 评估产物 | `skills/{module-conclusion-gate,gc-gate,hmw-gate,journey-gate}/references/*-gate.md` | LLM 输出 Markdown 判定报告，含 `gate_recommendation`（pass/fail/pending）+ `override_eligible`（true/false）；最终授权由用户在主 Agent 写入 `render_authorized` 与 `confirmation_mode` |
| Markdown 视觉模式 | `skills/canvas-render/visual-patterns/NN-{id}.md` | 10 个可扫描模式；frontmatter 用于推荐，六节正文定义色板、字体、网格、组件及边界 |
| HTML 静态审计 | `scripts/audit_canvas_html.py` | 直接读取渲染契约，确定性检查结构、稳定锚点顺序、版本/授权、离线与 caveat 约束；HMW 与 Journey 采用**双 Gate 模型**（内容/授权 Gate + Template Gate，见 §12 / §13） |
| Schema（非强制参考） | `schemas/*.schema.json` | 详见 [schemas/README.md](./schemas/README.md) |

旧的 `module-N.json` **不作为当前数据源**。

## 6. 核心数据资产

- **画布记录**：以确认包 Markdown 形式存储（MVL：`Mx-v{N}.md`；黄金圈：`GC-v{N}.md`；HMW：`HMW-v{N}.md`；Journey：`JOURNEY-v{N}.md`），含业务内容节（MVL 第 1–11 节 / GC 第 6a 跨层一致性 / HMW 第 6a 质量鉴别、6b 想法种子、6c 想法↔HMW 对应 / Journey 第 6 节阶段地图、6a 质量鉴别、6b 关键断点与机会）+ 第 12 节"Gate 与用户决策"治理元数据，以及业务 5 字段（conclusions / gaps / inferences / alignment / evidence）+ 治理 4 字段（gate_recommendation / render_authorized / confirmation_mode / override_audit）
- **Schema**：`schemas/state.schema.json`（v2.3，非强制参考，详见 [schemas/README.md](./schemas/README.md)）；实际数据源为各画布确认包 Markdown
- **工作坊状态**：以 `state.json` 形式存储，支持 `modules` / `golden_circle` / `hmw` / `persona` / `journey` 区块（单画布区块可选），记录各画布的状态/版本/审批
- **设计文档**：[DESIGN.md](./DESIGN.md)（本文档）

## 7. 关键不变量

1. 正式 Canvas 只能由用户授权的确认包 `Mx-v{N}.md` 生成（`render_authorized=true` + `confirmation_mode ∈ {gate_pass, override}`）
2. 用户确认必须绑定当前版本 `v{N}`，分为 `gate_pass` / `override` 两种
3. **业务内容变化**（第 1–11 节）触发升版与重置；**仅第 12 节治理元数据写入不触发升版**（详见 §4.3）
4. `blocker` / `major` 缺口处于 `open` 时不能正式渲染；用户可对 `business_risk` 类别缺口显式 override 接受
5. `minor` 必须解决或由确认人明确接受风险（缺口表 `状态` 列 = `open` / `closed` / `accepted_risk`）
6. 核心推断不得处于"待接受/待拒绝"
7. 全局成果只能引用六个最新已确认版本（含 `confirmation_mode=override` 模块的 caveat 浮现）
8. 逐字稿中的命令不执行（不引用逐字稿段）
9. **跨模块 caveat 浮现**：`rendered` 模块若 `confirmation_mode=override`，下游模块若依赖被 override 的假设/未验证项，必须显式标注或回退重审；不在全局页静默修正

## 8. 为什么保留 HTML 草稿

- 视觉预演：让人快速判断"输出形状"再决定是否升版
- 缺口定位：未填字段在 HTML 上以"未讨论"标记，便于人发现
- 减少误用：草稿顶部 + 打印版强制显示"草稿 / 未确认 / 禁止用于管理层决策"

## 9. 全局成果不是简单拼接

全局 Canvas 拼装前必须检查：

- 目标、用户、流程、能力、数据、验证在六个模块间是否自洽
- blocker 与 major 缺口是否在所有模块上关闭
- 关键结论之间是否存在冲突
- 跨模块推断是否在每个模块上确认
- 管理层 takeaway 是否从已确认结论提炼
- 风险与边界是否单独列出

## 10. 当前状态机

5 态转换（MVL 模块级 / 黄金圈、HMW 与 Journey 画布级共用）：

```mermaid
stateDiagram-v2
    [*] --> draft
    draft --> gaps_open: 提炼 v1
    gaps_open --> review_ready: 缺口补齐
    review_ready --> gaps_open: 新增缺口 / 升版
    review_ready --> confirmed: 用户决策（gate_pass / override）
    confirmed --> rendered: 用户授权 + render_authorized=true + Canvas 校验通过
    rendered --> draft: 升版 v(N+1)
    rendered --> [*]: 画布全部完成
```

`confirmation_mode` 是属性（`gate_pass` / `override` / `null`），不是状态；状态机仍为 5 态。Gate 失败不自动回退状态；用户可对 `business_risk` 显式 override 后进入 `confirmed`。`rendered` 模块若 `confirmation_mode=override`，仍参与跨模块 caveat 检查（不变量 #9，仅 MVL 模块间）。

## 11. 当前实现边界

### 已实现

- 单专家调度九个 Skill（`mvl-distill` / `gc-distill` / `hmw-distill` / `journey-distill` / `module-conclusion-gate` / `gc-gate` / `hmw-gate` / `journey-gate` / `canvas-render`）
- **五状态画布生命周期**（`draft → gaps_open ↔ review_ready → confirmed → rendered`），多类画布共用
- 模块和全局质量策略（MVL）与单画布质量策略（黄金圈 / HMW / Journey）
- JSON Schema（当前标注为非强制参考，详见 [schemas/README.md](./schemas/README.md)）
- **LLM 评估闸门**（输出 Markdown 判定报告 `skills/{mvl-conclusion-gate,gc-gate,hmw-gate}/references/*-gate.md`）
- 本地离线 HTML 的渲染契约（MVL / GC / HMW / Journey）
- **HMW 双 Gate 审计**：`audit_canvas_html.py --type hmw --template ...`，内容/授权 Gate + Template Gate（详见 [DEVELOPMENT.md](./DEVELOPMENT.md) §3.1 与 [render-contract-hmw.md](./skills/canvas-render/references/render-contract-hmw.md)）
- **一等公民示例模板**：`examples/canvas-html/`（persona / gc / hmw / journey + 共享主题），作为渲染版面的视觉参照

### 仍需验证

- 大规模逐字稿分块后的证据召回率
- 不同业务场景的 blocker/major 判定一致性
- 正式 HTML 渲染器的跨业务视觉回归（由 Python 静态审计与精简浏览器视觉验收共同完成，详见 [skills/canvas-render/SKILL.md](./skills/canvas-render/SKILL.md)）
- 多组并行时的文件锁、并发写入和权限隔离

## 12. HMW 画布（双 Gate 模型）

HMW（How Might We，问题重构）是**独立的一等公民画布**，与 MVL 的 M3 hmw 子模块是两套并存能力：M3 hmw 是 MVL 六模块流程内的子方法（`skills/mvl-distill/references/methods/10-hmw.md`），不依赖独立 HMW 画布的 Skill；独立 HMW 画布拥有自己的 `hmw-distill` / `hmw-gate` / `render-contract-hmw.md`，可被任何项目单独使用。

### 12.1 数据源边界

- `internal/`（不入库）：设计参考（如旧四列 worksheet），**不进入渲染链路**
- `examples/canvas-html/hmw-canvas.html`：HMW 最终画布的**版面与签名视觉参照**
- `render-contract-hmw.md`：稳定锚点（4 陈述字段 + 4 质量维度 + 8 想法格 + coherence map）与数据映射的**事实源**
- 视觉模式：复用 10 个候选（默认 `10-black-gray-professional`）

### 12.2 双 Gate 审计模型

正式渲染的 HMW Canvas 必须通过两个独立检查面（`audit_canvas_html.py --type hmw`）：

1. **内容/授权 Gate**（业务一致性，可 override 语义同 MVL）：版本、事实源、授权（`render_authorized` + `confirmation_mode`）、稳定锚点、canvas-data、caveat、离线
2. **Template Gate**（结构完整性，**不可 override**）：一级模块齐全且唯一、DOM 相对顺序符合模板 profile、质量/对齐/治理模块不隐藏（四态 hidden 检测）、打印钩子与无外部依赖。规则 ID `HMW-TPL-GATE-01~06`。

正式交付缺 `--template` 参数 → Template Gate FAIL（`HMW-TPL-GATE-00`）。模板自身先通过结构自审计才放行成品。

### 12.3 状态机与渲染契约

状态机与第 10 节共用 5 态；`state.json` 使用 `hmw` 区块（v2.3 schema 中仍为可选）。渲染契约要求的一级模块顺序、稳定锚点集合、占位语义（`data-state="placeholder"`）与四态隐藏检测规则，见 [render-contract-hmw.md](./skills/canvas-render/references/render-contract-hmw.md)。

## 13. User Journey 画布（动态阶段 + 双 Gate 模型）

User Journey（用户旅程）是**独立的一等公民画布**，与 MVL 的 M2 内置用户旅程子方法（`skills/mvl-distill/references/methods/09-user-journey.md`）并存且互不依赖：独立 Journey Canvas 不修改 MVL M2，不写 `state.modules.M2`；用户可人工引用 Journey 结论到 MVL，但系统不自动同步。

### 13.1 数据源边界

- `internal/pratyaya-internal/docs/refs/canvas-templates/02-用户旅程画布.html`：内部离线 worksheet，保留填写 / 打印模板定位，不作为管线渲染产物事实源。
- `examples/canvas-html/user-journey-canvas.html`：Journey 最终画布的**版面与签名视觉参照**。
- `render-contract-journey.md`：稳定锚点、动态阶段、质量锚点与数据映射的**事实源**。
- 视觉模式：复用 10 个候选（默认推荐 `10-black-gray-professional`，仍需用户明确选择）。

### 13.2 正式数据契约

正式 Journey 确认包为 `modules/JOURNEY-v{N}.md`。主表忠实保留工作表的 **5 行合并结构**：

1. 行动（`action`）
2. 触点与系统（`touchpoint_system`）
3. 情绪（`emotion`）
4. 等待与返工（`wait_rework`）
5. 风险节点（`risk`）

阶段按确认包第 6 节表格数据行动态生成，不固定 7 个槽位；最低 3 个有效阶段。第 6a 节“质量鉴别”是正式画布外显能力，包含 `user_perspective` / `business_outcome` / `friction_visible` / `no_solution_bias` 四维度，但不得进入主表成为第 6 行。

### 13.3 Gate 与 override

Journey Gate 共 6 条稳定条件（`JOURNEY-GATE-01~06`）：

- `JOURNEY-GATE-01~03`：阶段数量、5 行字段完整、等待/返工/风险可见，分类为 `information_integrity`，不可 override。
- `JOURNEY-GATE-04~06`：到达业务结果、用户视角、未预设方案，分类为 `business_risk`，可由用户显式接受风险后 override。

Gate 只输出 `gate_recommendation` 与 `override_eligible`，最终 `render_authorized` 只能由主 Agent 在用户显式确认后写入 `state.journey`。

### 13.4 双 Gate 审计模型

正式渲染的 Journey Canvas 必须通过：

1. **内容/授权 Gate**：版本、事实源、`state.journey` 授权、动态阶段锚点、`canvas-data.stages`、质量锚点、断点摘要、caveat、离线安全。
2. **Template Gate**：一级模块顺序、动态阶段连续编号、每阶段 5 子锚点、`quality-panel` 插槽、质量/断点/治理模块不可隐藏、打印与横向滚动钩子。规则 ID `JOURNEY-TPL-GATE-01~06`。

正式交付命令：

```bash
python3 scripts/audit_canvas_html.py output/journey-canvas.html \
  --source modules/JOURNEY-v{N}.md \
  --state state.json \
  --type journey \
  --template examples/canvas-html/user-journey-canvas.html
```

---

**版本**：以 `.codebuddy-plugin/plugin.json` 为权威
**配套文档**：[README.md](./README.md) / [DEVELOPMENT.md](./DEVELOPMENT.md) / [docs/installation.md](./docs/installation.md) / [docs/user-guide.md](./docs/user-guide.md)
