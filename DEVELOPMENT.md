# 维护者文档

> 面向维护专家包的人和运行时的 AI 助教。**不面向**工作坊用户（用户文档见 [docs/user-guide.md](./docs/user-guide.md)）。

## 1. 文档定位

本文件说明维护专家包所需的命令、流程约束和工具链。完整架构与不变量见 [DESIGN.md](./DESIGN.md)；工作坊用户使用流程见 [docs/user-guide.md](./docs/user-guide.md)；专家包元数据以 `.codebuddy-plugin/plugin.json` 为权威。

## 2. 质量闸门（LLM 自检）

画布结论闸门（Gate）由 LLM 评估；旧 Python 脚本 `check_gate.py` 已删除。执行流程（按画布类型对应 Skill）：

1. LLM 读取确认包 Markdown（MVL：`Mx-v{N}.md` / 黄金圈：`GC-{slug}-v{N}.md` / HMW：`HMW-{slug}-v{N}.md` / Persona：`PERSONA-{slug}-v{N}.md` / Journey：`JOURNEY-{slug}-v{N}.md` / MAAU：`MAAU-{slug}-v{N}.md` / V2C VAC：`V2C-VAC-{slug}-v{N}.md`）
2. 对照对应 Gate Skill 的判定规则（MVL 34 条放行条件；黄金圈 / HMW / Persona / Journey 各 6 条稳定放行条件 + 稳定 ID + 分类与风险等级；MAAU 用 `MAAU-GATE-01~09` 独立 ID 空间；V2C VAC 用 `V2C-GATE-01~12` 独立 ID 空间）
3. 输出 Markdown 判定报告（`references/Mx-gate.md` / `GC-gate.md` / `HMW-gate.md` / `PERSONA-gate.md` / `JOURNEY-gate.md` / `MAAU-{slug}-gate-report-v{N}.md` / `V2C-VAC-{slug}-gate-report-v{N}.md`），含 `gate_recommendation: pass/fail/pending` + `override_eligible: true/false`；**不**写最终授权

详细规则、缺口等级、推断术语、版本绑定的完整定义见 [skills/module-conclusion-gate/SKILL.md](./skills/module-conclusion-gate/SKILL.md)（MVL）、[skills/gc-gate/SKILL.md](./skills/gc-gate/SKILL.md)（黄金圈）、[skills/hmw-gate/SKILL.md](./skills/hmw-gate/SKILL.md)（HMW）、[skills/persona-gate/SKILL.md](./skills/persona-gate/SKILL.md)（Persona）、[skills/journey-gate/SKILL.md](./skills/journey-gate/SKILL.md)（Journey）、[skills/v2c-vac-gate/SKILL.md](./skills/v2c-vac-gate/SKILL.md)（V2C VAC）。

## 3. HTML 渲染（Python 静态审计 + 浏览器视觉验收）

正式交付分为两个阶段，首次渲染任一阶段失败保持画布 `confirmed`；已有成功产物的重渲染失败保持 `rendered`、原 `output_file` 和文件，全部验收成功才提交。

### 3.1 Python 静态审计

正式页面从专家包根目录运行（`{project_slug}/{group_id}/{topic_slug}` 占位），显式传入当前 topic 子目录下的 html/source/state（MVL 模块页示例）：

```bash
python3 skills/canvas-render/scripts/audit_canvas_html.py \
  workshop/{project_slug}/{group_id}/{topic_slug}/output/module-{n}-canvas--v{N}.html \
  --source workshop/{project_slug}/{group_id}/{topic_slug}/modules/Mx-v{N}.md \
  --state workshop/{project_slug}/{group_id}/{topic_slug}/state.json
```

黄金圈画布：`--type gc`；HMW、Persona、Journey、V2C VAC 与 5W 画布必须携带各自模板：

```bash
python3 skills/canvas-render/scripts/audit_canvas_html.py \
  workshop/{project_slug}/{group_id}/{topic_slug}/output/hmw-canvas-{slug}--v{N}.html \
  --source workshop/{project_slug}/{group_id}/{topic_slug}/modules/HMW-{slug}-v{N}.md \
  --state workshop/{project_slug}/{group_id}/{topic_slug}/state.json \
  --type hmw \
  --instance {slug} \
  --template skills/canvas-render/examples/hmw-canvas.html

python3 skills/canvas-render/scripts/audit_canvas_html.py \
  workshop/{project_slug}/{group_id}/{topic_slug}/output/persona-canvas-{slug}--v{N}.html \
  --source workshop/{project_slug}/{group_id}/{topic_slug}/modules/PERSONA-{slug}-v{N}.md \
  --state workshop/{project_slug}/{group_id}/{topic_slug}/state.json \
  --type persona \
  --instance {slug} \
  --template skills/canvas-render/examples/user-persona-canvas.html

python3 skills/canvas-render/scripts/audit_canvas_html.py \
  workshop/{project_slug}/{group_id}/{topic_slug}/output/v2c-vac-canvas-{slug}--v{N}.html \
  --source workshop/{project_slug}/{group_id}/{topic_slug}/modules/V2C-VAC-{slug}-v{N}.md \
  --state workshop/{project_slug}/{group_id}/{topic_slug}/state.json \
  --type v2c-vac \
  --instance {slug} \
  --template skills/canvas-render/examples/v2c-value-attribution-canvas.html

python3 skills/canvas-render/scripts/audit_canvas_html.py \
  workshop/{project_slug}/{group_id}/{topic_slug}/output/5w-canvas-{slug}--v{N}.html \
  --source workshop/{project_slug}/{group_id}/{topic_slug}/modules/5W-{slug}-v{N}.md \
  --state workshop/{project_slug}/{group_id}/{topic_slug}/state.json \
  --type 5w \
  --instance {slug} \
  --template skills/canvas-render/examples/5w-canvas.html
```

**MAAU transcript-direct 实例页**（`--type mvl --page-type global --instance {slug} --generation-path transcript-direct`）：

```bash
python3 skills/canvas-render/scripts/audit_canvas_html.py \
  workshop/{project_slug}/{group_id}/{topic_slug}/output/maau-global-canvas-{slug}--noflow-v{N}.html \
  --source workshop/{project_slug}/{group_id}/{topic_slug}/modules/MAAU-{slug}-v{N}.md \
  --state workshop/{project_slug}/{group_id}/{topic_slug}/state.json \
  --type mvl \
  --page-type global \
  --instance {slug} \
  --generation-path transcript-direct
```

MAAU 实例页 audit 校验：`generation_path=transcript-direct`、`data-instance`/`canvas-data.instance` 与 slug 一致、`canvas-data.source_file` 与源包一致、`[来源: transcript-direct]` 标头必填、override 时 `override_audit.items[].assessment_id` 为 `MAAU-GATE-*` 且 `category=business_risk`；缺 `--state` 时**不作为正式验收**（`MAAU_STATE` FAIL）。

脚本使用 Python 标准库，负责（MVL / GC / HMW / Persona / Journey / MAAU / V2C VAC / 5W 通用）：

1. 页面类型、画布和版本元数据；
2. 契约大模块、共享结构、稳定锚点存在且唯一；
3. 模块锚点顺序与对应 `render-contract-*.md` 映射表行顺序一致；
4. `canvas-data` JSON、确认包版本和 `state.json` 授权元数据一致；
5. 离线安全、必要打印规则、草稿标记和 override caveat 必需结构。

**HMW / Persona / Journey / V2C VAC / 5W 双 Gate 模型**：`--type hmw`、`--type persona`、`--type journey`、`--type v2c-vac` 或 `--type 5w` 时输出分为两个检查面——`[CONTENT/AUTH GATE]`（业务一致性：版本 / 事实源 / 授权 / 锚点 / canvas-data，语义与 MVL 一致）与 `[TEMPLATE GATE]`（结构完整性：`HMW-TPL-GATE-01~06` / `PERSONA-TPL-GATE-01~06` / `JOURNEY-TPL-GATE-01~06` / `V2C-VAC-TPL-GATE-01~08` / `5W-TPL-GATE-01~06`，**不可 override**，见 [DESIGN.md](./DESIGN.md) §12.2 / §13.4 / §14.4 及 [skills/canvas-render/references/render-contract-5w.md](./skills/canvas-render/references/render-contract-5w.md)）。`--template` 缺失时正式交付 FAIL（`HMW-TPL-GATE-00` / `PERSONA-TPL-GATE-00` / `JOURNEY-TPL-GATE-00` / `V2C-VAC-TPL-GATE-00` / `5W-TPL-GATE-00`）；模板自身先通过结构自审计才放行成品。

锚点顺序直接解析自对应 `render-contract-*.md`，不得在脚本中维护第二份清单。脚本 PASS 返回 0；FAIL 返回非零状态并列出失败项、期望值和实际值。

### 3.2 精简浏览器视觉验收

Python PASS 后再检查：

1. 桌面 `1440 × 900`：阅读顺序、溢出、遮挡、重叠和异常空白；
2. 窄屏 `390 × 844`：堆叠顺序、文字裁切和高密度内容滚动；
3. 打印预览：分页顺序、必要内容保留和编辑控件隐藏；
4. 选定视觉模式的色板、字体、网格、组件及 caveat 视觉结果。

浏览器阶段不重复检查锚点、JSON、授权字段或离线字符串。详细依据见 [skills/canvas-render/SKILL.md](./skills/canvas-render/SKILL.md) 与 [skills/canvas-render/references/render-contract.md](./skills/canvas-render/references/render-contract.md)。

### 3.3 MAAU 综合路径调试（常见阻断场景）

MAAU 一次性综合（`generation_path=transcript-direct`）从逐字稿直接生成 MVL 全局画布六板块源包 `modules/MAAU-{slug}-v{N}.md`，再经 Gate + 授权渲染为 `output/maau-global-canvas-{slug}--noflow-v{N}.html`。常见阻断与处置：

| 场景 | 现象 | 处置 |
|---|---|---|
| 源包缺 slug / generation_path | `maau_source_identity` 解析失败，audit 报 `SOURCE` | 检查 `MAAU-{slug}-v{N}.md` 头部是否含 `> slug：{slug}` 与 `> 生成路径：transcript-direct` |
| 缺 `--state` | audit 报 `MAAU_STATE` FAIL | MAAU 正式验收必须传 `--state` 读取 `state.maau.{slug}` 授权；无授权不得 `rendered` |
| state 未授权 | `AUTH_MISMATCH`（render_authorized=false 或 confirmation_mode 非法） | 让用户确认 vN 或 override 后写入 `render_authorized=true` |
| `generation_path` 错 | `MAAU_GENERATION`（HTML 或 state 非 transcript-direct） | 统一为 `transcript-direct`，不混用 M1-M6 Phase 2 |
| 缺 `[来源: transcript-direct]` 标头 | `MAAU_HEADER` FAIL | 实例页必须含该标头 |
| override 项 ID/分类错误 | `MAAU_OVERRIDE` FAIL | `override_audit.items[].assessment_id` 为 `MAAU-GATE-*` 且 `category=business_risk`；`information_integrity` 不接受 override |
| `data-instance` 与 source slug 不一致 | `INSTANCE` / `MAAU_SOURCE_SLUG` | HTML `data-instance` 与 `canvas-data.instance`、源包 slug、`--instance` 四者一致 |
| 误把 transcript-direct 混入 M1-M6 Phase 2 全局页 | — | 同一 group 的 MAAU 输出只能二选一；实例页不伪造 `module-{1-6}-canvas.html` 下钻 |

### 3.4 V2C VAC 调试（常见阻断场景）

V2C VAC 使用 `canvas_type=v2c-vac`、状态路径 `state.v2c_vac.{slug}`，支持 `generation_path=pipeline` 与 `generation_path=transcript-direct`。常见阻断与处置：

| 场景 | 现象 | 处置 |
|---|---|---|
| 误用 `canvas_type=v2c` | `CANVAS_TYPE` / 契约一致性 `V2C_VAC_CANVAS_TYPE` FAIL | `v2c` 是系列名，Value Attribution Canvas 的机器标识必须是 `v2c-vac` |
| 缺 `--template` | `V2C-VAC-TPL-GATE-00` FAIL | 正式交付必须传 `--template skills/canvas-render/examples/v2c-value-attribution-canvas.html` |
| 缺归因链锚点 | `MISSING_ANCHOR` / `V2C-VAC-TPL-GATE-*` FAIL | 保留 `v2c-vac-attribution-chain`、五层主链、六类 `V2C-AGxx`、质量面板与 `canvas-data` |
| override 项 ID 错 | `V2C_OVERRIDE` FAIL | `override_audit.items[].assessment_id` 必须为 `V2C-GATE-*`，`V2C-AGxx` 只能作来源或断点 |
| `generation_path` 与状态不一致 | `AUTH_MISMATCH` 或 schema 测试失败 | `pipeline` / `transcript-direct` 必须在 HTML `canvas-data` 与 `state.v2c_vac.{slug}` 中一致 |
| 无 Baseline 却声称量化收益 | `V2C-GATE-09` 业务风险 | 不得输出量化收益承诺；补 Baseline 或由用户显式接受业务风险 |

### 3.5 5W 调试（常见阻断场景）

5W 使用 `canvas_type=5w`、状态路径 `state.five_whys.{slug}`，默认采用丰田三层面追问框架（制造层 Why 1-2 / 检验层 Why 3-4 / 体系层 Why 5）。常见阻断与处置：

| 场景 | 现象 | 处置 |
|---|---|---|
| 缺 `--template` | `5W-TPL-GATE-00` FAIL | 正式交付必须传 `--template skills/canvas-render/examples/5w-canvas.html` |
| 五层锚点缺失 | `MISSING_ANCHOR` / `5W-TPL-GATE-*` FAIL | `5w-why-1` ~ `5w-why-5` 必须全部存在；层数弹性暂不支持 |
| 误用 `canvas_type=5W`（大写） | `CANVAS_TYPE` FAIL | 机器标识固定为小写 `5w`；`5W-` 只用于文件前缀与 Gate ID |
| source slug 与 instance 不一致 | `5W_SOURCE_SLUG` FAIL | 源包文件 `5W-{slug}-v{N}.md` 的 slug 必须等于 `--instance` |
| override 项 ID 错 | `5W_OVERRIDE` FAIL | `override_audit.items[].assessment_id` 必须为 `5W-GATE-*`（pattern `^5W-GATE-[0-9]+$`）且 `category=business_risk` |
| 个人归因 / 非事实陈述 | `5W-GATE-01/04` `information_integrity` FAIL | 不可 override；返回补问或修订确认包 |
| 根因无对策四要素 | `5W-GATE-06` 业务风险 | 补对策 / 负责人 / 截止日期 / 验证方式，或由用户显式接受业务风险 |

## 4. Canvas 视觉模式维护

Canvas 视觉系统由 `skills/canvas-render/visual-patterns/` 下的 Markdown 规格定义，不使用预制 HTML 外壳或集中登记册。

- 候选文件固定匹配 `[0-9][0-9]-*.md`，当前基线恰好 10 个。
- 文件名必须为 `NN-{id}.md`，并与 frontmatter `id` 一致；序号和 ID 均唯一。
- frontmatter 恰好包含 `id / zh_name / visual_system / layout / formality / density / best_for`。
- 正文固定包含“色板 token / 字体 / 网格 / 组件库 / 适用场景 / 反例”六节。
- 新增或修改公司命名模式时，必须记录当前官方色值证据；一个模式只有一个结构主色。
- 主 Agent 扫描并推荐 1–2 个候选，用户选择后传递完整仓库相对路径；不得用 ID 猜路径或静默回退。

维护入口见 [视觉模式 README](./skills/canvas-render/visual-patterns/README.md)。

## 5. 模块工作流

四阶段管线（数据源与闸门），多类画布共用，差异在命名空间：

| 画布 | 路径 | Key Points | 提炼 | Gate | 渲染 |
|---|---|---|---|---|---|
| MAAU（transcript-direct） | **默认** | 逐字稿存档 `maau-{slug}-raw.md` | `MAAU-{slug}-v{N}.md`（六板块源包） | `MAAU-{slug}-gate-report-v{N}.md` | `maau-global-canvas-{slug}--noflow-v{N}.html` / 可选索引 |
| MVL（M1-M6） | **备选**（显式声明启用） | `Mx-keypoints.md` | `Mx-v{N}.md` | `Mx-gate.md` | `module-N-canvas.html` / 全局 |
| 黄金圈 | — | `GC-{slug}-keypoints.md` | `GC-{slug}-v{N}.md` | `GC-{slug}-gate-report-v{N}.md` | `gc-canvas-{slug}--v{N}.html` / `gc-canvas.html` 索引 |
| HMW | — | `HMW-{slug}-keypoints.md` | `HMW-{slug}-v{N}.md` | `HMW-{slug}-gate-report-v{N}.md` | `hmw-canvas-{slug}--v{N}.html` / `hmw-canvas.html` 索引 |
| Persona | — | `PERSONA-{slug}-keypoints.md` | `PERSONA-{slug}-v{N}.md` | `PERSONA-{slug}-gate-report-v{N}.md` | `persona-canvas-{slug}--v{N}.html` / `persona-canvas.html` 索引 |
| Journey | — | `JOURNEY-{slug}-keypoints.md` | `JOURNEY-{slug}-v{N}.md` | `JOURNEY-{slug}-gate-report-v{N}.md` | `journey-canvas-{slug}--v{N}.html` / `journey-canvas.html` 索引 |
| V2C VAC | `pipeline` / `transcript-direct` | `V2C-VAC-{slug}-keypoints.md` + 可选 `V2C-VAC-{slug}-stage-{stage}.md` | `V2C-VAC-{slug}-v{N}.md` | `V2C-VAC-{slug}-gate-report-v{N}.md` | `v2c-vac-canvas-{slug}--v{N}.html` / `v2c-vac-canvas.html` 索引 |
| 5W | — | `5W-{slug}-keypoints.md` | `5W-{slug}-v{N}.md` | `5W-{slug}-gate-report-v{N}.md` | `5w-canvas-{slug}--v{N}.html` / `5w-canvas.html` 索引 |

```text
Key Points → 提炼（确认包 v{N}.md）→ Gate（判定报告）→ 渲染（HTML）
```

每个阶段的输入/输出/状态变化由对应 Skill 定义，详见 [skills/mvl-distill/SKILL.md](./skills/mvl-distill/SKILL.md) / [skills/gc-distill/SKILL.md](./skills/gc-distill/SKILL.md) / [skills/hmw-distill/SKILL.md](./skills/hmw-distill/SKILL.md) / [skills/persona-distill/SKILL.md](./skills/persona-distill/SKILL.md) / [skills/journey-distill/SKILL.md](./skills/journey-distill/SKILL.md) / [skills/v2c-vac-distill/SKILL.md](./skills/v2c-vac-distill/SKILL.md) / [skills/5w-distill/SKILL.md](./skills/5w-distill/SKILL.md) / [skills/module-conclusion-gate/SKILL.md](./skills/module-conclusion-gate/SKILL.md) / [skills/gc-gate/SKILL.md](./skills/gc-gate/SKILL.md) / [skills/hmw-gate/SKILL.md](./skills/hmw-gate/SKILL.md) / [skills/persona-gate/SKILL.md](./skills/persona-gate/SKILL.md) / [skills/journey-gate/SKILL.md](./skills/journey-gate/SKILL.md) / [skills/v2c-vac-gate/SKILL.md](./skills/v2c-vac-gate/SKILL.md) / [skills/5w-gate/SKILL.md](./skills/5w-gate/SKILL.md) / [skills/canvas-render/SKILL.md](./skills/canvas-render/SKILL.md)。

`faq-answer` 是支持型 Skill，负责使用、状态和异常解释，不进入 `Key Points → 提炼 → Gate → 渲染` 四阶段管线，不写 `state.json`、确认包或 HTML。维护入口见 [skills/faq-answer/SKILL.md](./skills/faq-answer/SKILL.md)。

以上文件路径均相对当前 topic 工作目录 `workshop/{project_slug}/{group_id}/{topic_slug}/`；group 级 `manifest.json` 仅用于本组 topic 汇总，可从当前 group 各 topic 的 `state.json` 重建；project 级 `manifest.json` 仅用于跨组 / 跨 topic 汇总，可从各 `{group_id}/{topic_slug}/state.json` 重建。两者均为派生缓存，不作为业务真相源。

## 6. 版本与发布

专家包版本号遵循 SemVer（语义化版本），定义在 `.codebuddy-plugin/plugin.json` 的 `version` 字段：

- **MAJOR**：破坏性变更（数据源切换、状态机调整、Skill 重写等）
- **MINOR**：新增功能（新增 Skill 子任务、新增文档章节等）
- **PATCH**：Bug 修复、措辞调整

当前版本：以 `.codebuddy-plugin/plugin.json` `version` 字段为权威。

发布流程（按 workbuddy 指导执行）：

1. **定位** — 确认改动范围（在哪个文件、影响哪些 Skill、Agent 或视觉模式）
2. **确认范围** — 评估是否需要同步 docs/、DEVELOPMENT.md、DESIGN.md
3. **执行修改** — 改完代码与文档
4. **校验** — `python3 -c "import json; json.load(open('.codebuddy-plugin/plugin.json'))"` 验证 plugin.json 是合法 JSON；再从 WorkBuddy 工具目录运行 `python3 scripts/validate_expert.py <expert-dir>`
5. **注册** — 从 WorkBuddy 工具目录运行 `python3 scripts/register_expert.py <expert-dir> --session-id <sid>`；通过 WorkBuddy“专家导入”入口安装时，须确认导入流程已完成等价的注册写入
6. **重新加载** — 注册成功后重启 WorkBuddy（详见 [docs/installation.md §4](./docs/installation.md#4-安装后必须重启)）

已发布专家严禁原地修改（按 workbuddy 指导）：`name` 字段（kebab-case 唯一标识）、`agentName` 字段、`plugin` 字段、专家目录名、agents/ 下的 .md 文件名。如需新名称，应创建并注册新的专家身份。

**派生关系**：`name` / `agentName` / `plugin` 三个字段值同源（当前均为 `pratyaya`）。创建专家身份时三个必须一致；否则专家市场注册信息会与本地配置脱节。

## 6. Journey 画布迁移边界（v2.3.2 PATCH 起）

> 本节固化 `render-contract-journey.md` 的迁移边界条目，供开发者或 agent 在跨版本渲染时强一致识别。

### 6.1 不兼容的旧产物

| 产物类型 | 范围 | 处置 |
|---|---|---|
| v2.3.1 及更早 `output/journey-canvas.html` | HTML | 不能直接复用为 v2.3.2 渲染产物；仅作阅读用 |
| v2.3.1 及更早 `JOURNEY-v{N}.md` 确认包 | Markdown | 不得直接按新契约渲染；需迁移为新版本或重新提炼 |
| v2.3.1 及更早 `JOURNEY-keypoints.md` | Markdown | 可作为 Stage 2 的背景输入，但 Stage 2 必须按新列头生成确认包 |
| v2.3.1 及更早 `canvas-data.stages[]` 中 `wait_rework` / `risk` | canvas data | 不再是新契约字段；audit 报 `JOURNEY-TPL-GATE-04` FAIL |

### 6.2 迁移映射规范

| 旧字段 | 新字段 | 开发者必须做的 |
|---|---|---|
| `wait_rework` | `pain_point` | 改写为期望与现实落差导致的痛点 |
| `risk` | `opportunity` | 只有从痛点导出改进方向时才写入；推断型机会登记 `JOURNEY-Infxx` |
| `friction_visible` | `pain_opportunity_visible` | 6a 维度键切换；判定方法不变 |

### 6.3 验收硬要求

迁移后的确认包必须重新跑 `journey-gate`，**不能沿用旧 Gate 结论**。具体验收命令：

```bash
# 1. 契约一致性检查
python scripts/check_contract_consistency.py

# 2. 跑 Journey 6 条放行条件（Stage 2 的 journey-gate 评估）
# 在 agent 中按 skills/journey-gate/SKILL.md 流程执行

# 3. 渲染前 audit 必填检查
python skills/canvas-render/scripts/audit_canvas_html.py \
  workshop/{project_slug}/{group_id}/{topic_slug}/output/journey-canvas-{slug}--v{N}.html \
  --source workshop/{project_slug}/{group_id}/{topic_slug}/modules/JOURNEY-{slug}-v{N}.md \
  --state workshop/{project_slug}/{group_id}/{topic_slug}/state.json \
  --type journey \
  --instance {slug} \
  --template skills/canvas-render/examples/user-journey-canvas.html
```

3 条命令全部 PASS 后方可视为 v2.3.2 新契约产物。audit 中的任何 `JOURNEY-TPL-GATE-*` FAIL 都属于**不可 override** 的 Template Gate 错误。

### 6.4 不在迁移范围内

- **`JOURNEY-Fxx` ID 前缀**：含义已切换为「痛点 / 机会条目」，但前缀本身保留；迁移期不强制替换。
- **`state.schema.json` `schema_version`**：当前 `2.4`（v3.2.0 新增 5W 时由 2.3 升版）；v2.6.0 通过 `_meta.instance_map_schema_version` 标记一等公民画布 instance map 子版本。旧 GC / HMW / Persona / Journey 单字段 state 需先迁移为 `state.{canvas}.{slug}`。
- **离线工作表** `internal/.../02-用户旅程画布.html`：文案已切到新字段，但属设计参考；不参与 audit。

## 7. 命令速查

| 命令 | 用途 |
|---|---|
| `git log --oneline` | 查看 commit 历史 |
| `git diff` | 查看当前未提交变更 |
| `python3 -c "import json; json.load(open('.codebuddy-plugin/plugin.json'))"` | 验证 plugin.json 合法 |
| `python3 scripts/validate_expert.py <expert-dir>` | 在 WorkBuddy 工具目录运行官方专家校验 |
| `python3 scripts/register_expert.py <expert-dir> --session-id <sid>` | 在 WorkBuddy 工具目录注册或重新注册专家 |
| `find skills/canvas-render/visual-patterns -maxdepth 1 -type f -name '[0-9][0-9]-*.md' \| sort` | 列出视觉模式候选 |
| `rg -n '^id:|^visual_system:|^layout:|^formality:|^density:|^best_for:' skills/canvas-render/visual-patterns/*.md` | 复核选择元数据 |
| `python3 skills/canvas-render/scripts/audit_canvas_html.py workshop/{project_slug}/{group_id}/{topic_slug}/output/module-{n}-canvas--v{N}.html --source workshop/{project_slug}/{group_id}/{topic_slug}/modules/Mx-vN.md --state workshop/{project_slug}/{group_id}/{topic_slug}/state.json` | 审计正式模块 Canvas HTML |
| `python3 skills/canvas-render/scripts/audit_canvas_html.py workshop/{project_slug}/{group_id}/{topic_slug}/output/gc-canvas-{slug}--v{N}.html --source workshop/{project_slug}/{group_id}/{topic_slug}/modules/GC-{slug}-vN.md --state workshop/{project_slug}/{group_id}/{topic_slug}/state.json --type gc --instance {slug}` | 审计黄金圈 Canvas HTML |
| `python3 skills/canvas-render/scripts/audit_canvas_html.py workshop/{project_slug}/{group_id}/{topic_slug}/output/hmw-canvas-{slug}--v{N}.html --source workshop/{project_slug}/{group_id}/{topic_slug}/modules/HMW-{slug}-vN.md --state workshop/{project_slug}/{group_id}/{topic_slug}/state.json --type hmw --instance {slug} --template skills/canvas-render/examples/hmw-canvas.html` | 审计 HMW Canvas HTML（双 Gate：内容/授权 + Template） |
| `python3 skills/canvas-render/scripts/audit_canvas_html.py workshop/{project_slug}/{group_id}/{topic_slug}/output/persona-canvas-{slug}--v{N}.html --source workshop/{project_slug}/{group_id}/{topic_slug}/modules/PERSONA-{slug}-vN.md --state workshop/{project_slug}/{group_id}/{topic_slug}/state.json --type persona --instance {slug} --template skills/canvas-render/examples/user-persona-canvas.html` | 审计 Persona Canvas HTML（双 Gate：内容/授权 + Template） |
| `python3 skills/canvas-render/scripts/audit_canvas_html.py workshop/{project_slug}/{group_id}/{topic_slug}/output/journey-canvas-{slug}--v{N}.html --source workshop/{project_slug}/{group_id}/{topic_slug}/modules/JOURNEY-{slug}-vN.md --state workshop/{project_slug}/{group_id}/{topic_slug}/state.json --type journey --instance {slug} --template skills/canvas-render/examples/user-journey-canvas.html` | 审计 Journey Canvas HTML（动态阶段 + 双 Gate） |
| `python3 skills/canvas-render/scripts/audit_canvas_html.py workshop/{project_slug}/{group_id}/{topic_slug}/output/v2c-vac-canvas-{slug}--v{N}.html --source workshop/{project_slug}/{group_id}/{topic_slug}/modules/V2C-VAC-{slug}-vN.md --state workshop/{project_slug}/{group_id}/{topic_slug}/state.json --type v2c-vac --instance {slug} --template skills/canvas-render/examples/v2c-value-attribution-canvas.html` | 审计 V2C VAC HTML（归因链 + V2C-VAC Template Gate） |
| `python3 skills/canvas-render/scripts/audit_canvas_html.py workshop/{project_slug}/{group_id}/{topic_slug}/output/5w-canvas-{slug}--v{N}.html --source workshop/{project_slug}/{group_id}/{topic_slug}/modules/5W-{slug}-vN.md --state workshop/{project_slug}/{group_id}/{topic_slug}/state.json --type 5w --instance {slug} --template skills/canvas-render/examples/5w-canvas.html` | 审计 5W Canvas HTML（五层因果链 + 5W Template Gate） |
| `python3 skills/canvas-render/scripts/audit_canvas_html.py workshop/{project_slug}/{group_id}/{topic_slug}/output/maau-global-canvas-{slug}--noflow-v{N}.html --source workshop/{project_slug}/{group_id}/{topic_slug}/modules/MAAU-{slug}-vN.md --state workshop/{project_slug}/{group_id}/{topic_slug}/state.json --type mvl --page-type global --instance {slug} --generation-path transcript-direct` | 审计 MAAU transcript-direct 实例页 HTML（`MAAU_GENERATION` / `[来源: transcript-direct]` / `MAAU-GATE-*` override） |
| `python3 skills/canvas-render/scripts/audit_canvas_html.py workshop/{project_slug}/{group_id}/{topic_slug}/output/persona-canvas.html --state workshop/{project_slug}/{group_id}/{topic_slug}/state.json --type persona --index` | 审计 Persona instance 索引页 |
| `python3 skills/canvas-render/scripts/audit_canvas_html.py workshop/{project_slug}/{group_id}/{topic_slug}/output/v2c-vac-canvas.html --state workshop/{project_slug}/{group_id}/{topic_slug}/state.json --type v2c-vac --index --page-type v2c-vac-index` | 审计 V2C VAC instance 索引页 |
| `python3 skills/canvas-render/scripts/audit_canvas_html.py workshop/{project_slug}/{group_id}/{topic_slug}/output/5w-canvas.html --state workshop/{project_slug}/{group_id}/{topic_slug}/state.json --type 5w --index --page-type 5w-index` | 审计 5W instance 索引页 |
| `python3 -m pytest tests/ -q` | 跑全部单元测试（schema / 契约 / 双 Gate 审计） |
| `python3 scripts/check_contract_consistency.py` | 跑契约一致性检查器（开发辅助，**非 CI 强制**），输出规则化问题清单 |
| `python3 scripts/check_contract_consistency.py --rules V2C_VAC_SKILL_PATH,V2C_VAC_GATE_FILE,V2C_VAC_RENDER_CONTRACT,V2C_VAC_STATE_SCHEMA` | 只跑 V2C VAC 契约一致性检查 |
| `python3 scripts/check_contract_consistency.py --rules MANIFEST_JSON,GATE_TABLE_PARSE` | 只跑指定规则（逗号分隔 code） |
| `python3 scripts/check_contract_consistency.py --list` | 列出所有规则 code / category / description |
| `python3 -m pytest tests/test_contract_consistency.py` | 跑契约一致性检查器的单元测试 |
| `grep -rn "check_gate.py" .` | 检查已删除 Gate 脚本引用残留 |
| `grep -rn "module-N\.json" .` | 检查旧 JSON 引用残留 |
| `wc -l README.md DEVELOPMENT.md DESIGN.md docs/*.md` | 检查现行文档规模 |

## 8. 契约一致性检查器（开发辅助）

`scripts/check_contract_consistency.py` 是本仓库的**契约一致性检查器**。设计依据见
`tmp/pratyaya-internal/docs/design/契约一致性检查器-206-0801-1003.md`，对应单元测试在
`tests/test_contract_consistency.py` 与 `tests/fixtures/contract-consistency/`。

> **定位**：开发辅助工具，用于变更前后对比 / 改写前的差异分析 / 一次性 drift 排查。
> **不是** CI 门禁——本仓库没有 `.github/workflows/`，单人维护 + 未发布阶段的工具复杂度应
> 远低于被它保护的资产。当前基线为 error=0, warning=0。M1-M6 Gate 表已正式接受
> 5 列精简版（`ID / 条件 / 分类 / 风险等级 / 来源`），检查器仍兼容历史 8 列详版。

### 8.1 当前覆盖的规则族

| 阶段 | 类别 | code |
|---|---|---|
| A 最小强门禁 | manifest / 入口 / 版本 | `MANIFEST_JSON` `IDENTITY_MATCH` `ENTRY_EXISTS` `AGENT_ENTRY` `SKILL_ENTRY` `VERSION_FORMAT` `CHANGELOG_VERSION` |
| A 最小强门禁 | GATE 文件（MVL） | `GATE_FILE_SET` `GATE_TABLE_PARSE` `GATE_TABLE_WIDTH`（5 列精简版 / 8 列详版） `GATE_ID_FORMAT` `GATE_ID_MODULE` `GATE_ID_UNIQUE` `GATE_CATEGORY` `GATE_RISK` `GATE_SOURCE` |
| A 最小强门禁 | GATE 文件（黄金圈） | `GC_GATE_FILE_SET` `GC_GATE_TABLE` |
| A 最小强门禁 | GATE 文件（HMW） | `HMW_GATE_FILE_SET` |
| A 最小强门禁 | GATE 文件（Journey） | `JOURNEY_GATE_FILE_SET` |
| A 最小强门禁 | GATE 文件（V2C VAC） | `V2C_VAC_GATE_FILE` |
| A 最小强门禁 | 视觉模式 | `PATTERN_COUNT` `PATTERN_FILENAME` `PATTERN_SEQUENCE` `PATTERN_ID` `PATTERN_METADATA` `PATTERN_ENUM` |
| A 最小强门禁 | HMW 结构 | `HMW_SKILL_PATH` `HMW_TEMPLATE_MISSING` `HMW_INF_ID` |
| A 最小强门禁 | Journey 结构 | `JOURNEY_SKILL_PATH` `JOURNEY_EXAMPLE_MISSING` |
| A 最小强门禁 | V2C VAC 结构 | `V2C_VAC_SKILL_PATH` |
| A 最小强门禁 | 文档/链接 | `LOCAL_LINK` `DEPRECATED_TERM` |
| B 跨契约结构 | section / schema / 状态机 | `GATE_SECTION_SYNC` `RENDER_SECTION_SYNC` `SKILL_TEMPLATE_SYNC` `STATE_ENUM_SYNC` `AUTH_FIELDS` `OVERRIDE_CATEGORY` |
| B 跨契约结构 | HMW Template Gate | `HMW_TPL_GATE_UNIQUE` |
| B 跨契约结构 | Journey Template Gate / 动态阶段 | `JOURNEY_ANCHOR_SYNC` `JOURNEY_SEVEN_ELEMENTS` |
| B 跨契约结构 | V2C VAC contract / schema / route | `V2C_VAC_RENDER_CONTRACT` `V2C_VAC_STATE_SCHEMA` |

每条规则有唯一的 `<CATEGORY>-<NAME>` 标识。`--list` 查看完整列表；输出含 `code / level / where / message / hint` 五字段。

> **未包含的规则**（设计有但本仓库**暂不**启用，避免误报与越界）：
> - `GATE_ID_SEQUENCE` / `GATE_COUNT_SYNC`：设计本身允许 GATE 序号跳号（M1-GATE-02 → 03 是设计），规则会与合法跳号冲突
> - `PATTERN_HEADINGS` / `PATTERN_OFFLINE`：6 个固定标题 / 外部字体检测属于"内容质量"而非"契约一致性"
> - `AGENT_DISPLAY_SYNC` / `VERSION_SYNC`：检查"agent MD 是否引用了 displayName / 版本号"——属于内容质量检查，**不**是一致性
> - `CONFIRMATION_MODE`：与 `OVERRIDE_CATEGORY` 重叠
>
> 何时重新引入：等到有真实问题驱动时再加（"为造而造"的规则会拉低维护者对门禁的信任）。

### 8.2 运行与退出码

* 默认 `--root` 指向仓库根目录；通过 `--root <dir>` 跑合成仓库（便于单元测试）。
* 退出码：`0` = 无 error；`1` = 至少 1 条 error；`2` = 参数错误。`--strict` 把 warning 也算 1。
* 失败项按 code 分组输出：每个 code 下列出所有问题位置和修复建议。
* `--json` 输出 JSON（无消费者前可省略，但已实现，未来需要时直接可用）。
* `--rules <code1>,<code2>` 只跑指定规则；`--list` 列出全部 code。

### 8.3 何时考虑接入 CI

**当前不接**。CI 强制化必须满足以下所有条件，缺一不可：

1. **专家包 v3.0+ 正式发布**——V2C VAC 与显式画布路由完成发布后再评估
2. **多人协作有真实 PR 流程**——当前单人维护，没有 PR 边界
3. **当前 warning 清单已处理或被白名单显式接受**——当前基线应保持 warning=0

任一条件不满足时，本检查器应保持在"开发辅助"形态，作为改写前/后的差异分析工具使用，而非拦截 PR。

---

**版本**：以 `.codebuddy-plugin/plugin.json` 为权威
**配套文档**：[DESIGN.md](./DESIGN.md) / [docs/installation.md](./docs/installation.md) / [docs/user-guide.md](./docs/user-guide.md)
