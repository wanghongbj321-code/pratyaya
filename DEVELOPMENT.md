# 维护者文档

> 面向维护专家包的人和运行时的 AI 助教。**不面向**工作坊用户（用户文档见 [docs/user-guide.md](./docs/user-guide.md)）。

## 1. 文档定位

本文件说明维护专家包所需的命令、流程约束和工具链。完整架构与不变量见 [DESIGN.md](./DESIGN.md)；工作坊用户使用流程见 [docs/user-guide.md](./docs/user-guide.md)；专家包元数据以 `.codebuddy-plugin/plugin.json` 为权威。

## 2. 质量闸门（LLM 自检）

模块结论闸门（Gate）由 LLM 评估；旧 Python 脚本 `check_gate.py` 已删除。执行流程：

1. LLM 读取 `modules/Mx-v{N}.md`（确认包 Markdown）
2. 对照 `skills/module-conclusion-gate/SKILL.md` 的判定规则（34 条放行条件 + 稳定 ID + 分类与风险等级）
3. 输出 Markdown 判定报告 `skills/module-conclusion-gate/references/Mx-gate.md`，含 `gate_recommendation: pass/fail/pending` + `override_eligible: true/false`；**不**写最终授权

详细规则、缺口等级、推断术语、版本绑定的完整定义见 [skills/module-conclusion-gate/SKILL.md](./skills/module-conclusion-gate/SKILL.md)。

## 3. HTML 渲染（Python 静态审计 + 浏览器视觉验收）

正式交付分为两个阶段，任一阶段失败都保持模块 `confirmed`，不得提前标记为 `rendered`。

### 3.1 Python 静态审计

正式模块页从专家包根目录运行：

```bash
python3 scripts/audit_canvas_html.py <项目目录>/output/module-N-canvas.html \
  --source <项目目录>/modules/Mx-v{N}.md \
  --state <项目目录>/state.json
```

脚本使用 Python 标准库，负责：

1. 页面类型、模块和版本元数据；
2. 契约大模块、共享结构、稳定锚点存在且唯一；
3. `#module-outputs` 内模块锚点顺序与 `render-contract.md` 对应映射表行顺序一致；
4. `canvas-data` JSON、确认包版本和 `state.json` 授权元数据一致；
5. 离线安全、必要打印规则、草稿标记和 override caveat 必需结构。

模块锚点顺序直接解析自 `render-contract.md`，不得在脚本中维护第二份 M1–M6 清单。脚本 PASS 返回 0；FAIL 返回非零状态并列出失败项、期望值和实际值。

### 3.2 精简浏览器视觉验收

Python PASS 后再检查：

1. 桌面 `1440 × 900`：阅读顺序、溢出、遮挡、重叠和异常空白；
2. 窄屏 `390 × 844`：堆叠顺序、文字裁切和高密度内容滚动；
3. 打印预览：分页顺序、必要内容保留和编辑控件隐藏；
4. 选定视觉模式的色板、字体、网格、组件及 caveat 视觉结果。

浏览器阶段不重复检查锚点、JSON、授权字段或离线字符串。详细依据见 [skills/canvas-render/SKILL.md](./skills/canvas-render/SKILL.md) 与 [skills/canvas-render/references/render-contract.md](./skills/canvas-render/references/render-contract.md)。

## 4. Canvas 视觉模式维护

Canvas 视觉系统由 `skills/canvas-render/visual-patterns/` 下的 Markdown 规格定义，不使用预制 HTML 外壳或集中登记册。

- 候选文件固定匹配 `[0-9][0-9]-*.md`，当前基线恰好 9 个。
- 文件名必须为 `NN-{id}.md`，并与 frontmatter `id` 一致；序号和 ID 均唯一。
- frontmatter 恰好包含 `id / visual_system / layout / formality / density / best_for`。
- 正文固定包含“色板 token / 字体 / 网格 / 组件库 / 适用场景 / 反例”六节。
- 新增或修改公司命名模式时，必须记录当前官方色值证据；一个模式只有一个结构主色。
- 主 Agent 扫描并推荐 1–2 个候选，用户选择后传递完整仓库相对路径；不得用 ID 猜路径或静默回退。

维护入口见 [视觉模式 README](./skills/canvas-render/visual-patterns/README.md)。

## 5. 模块工作流

四阶段管线（数据源与闸门）：

```text
Key Points (Mx-keypoints.md) → 提炼 (Mx-v{N}.md) → Gate (Mx-gate.md) → 渲染 (HTML)
```

每个阶段的输入/输出/状态变化由对应 Skill 定义，详见 [skills/mvl-distill/SKILL.md](./skills/mvl-distill/SKILL.md) / [skills/module-conclusion-gate/SKILL.md](./skills/module-conclusion-gate/SKILL.md) / [skills/canvas-render/SKILL.md](./skills/canvas-render/SKILL.md)。

## 6. 版本与发布

专家包版本号遵循 SemVer（语义化版本），定义在 `.codebuddy-plugin/plugin.json` 的 `version` 字段：

- **MAJOR**：破坏性变更（数据源切换、状态机调整、Skill 重写等）
- **MINOR**：新增功能（新增 Skill 子任务、新增文档章节等）
- **PATCH**：Bug 修复、措辞调整

当前版本：v1.0.0（`plugin.json` 1.0.0 同步）。

发布流程（按 workbuddy 指导执行）：

1. **定位** — 确认改动范围（在哪个文件、影响哪些 Skill、Agent 或视觉模式）
2. **确认范围** — 评估是否需要同步 docs/、DEVELOPMENT.md、DESIGN.md
3. **执行修改** — 改完代码与文档
4. **校验** — `python3 -c "import json; json.load(open('.codebuddy-plugin/plugin.json'))"` 验证 plugin.json 是合法 JSON；再从 WorkBuddy 工具目录运行 `python3 scripts/validate_expert.py <expert-dir>`
5. **注册** — 从 WorkBuddy 工具目录运行 `python3 scripts/register_expert.py <expert-dir> --session-id <sid>`；通过 WorkBuddy“专家导入”入口安装时，须确认导入流程已完成等价的注册写入
6. **重新加载** — 注册成功后重启 WorkBuddy（详见 [docs/installation.md §4](./docs/installation.md#4-安装后必须重启)）

已发布专家严禁原地修改（按 workbuddy 指导）：`name` 字段（kebab-case 唯一标识）、`agentName` 字段、`plugin` 字段、专家目录名、agents/ 下的 .md 文件名。如需新名称，应创建并注册新的专家身份。

**派生关系**：`name` / `agentName` / `plugin` 三个字段值同源（当前均为 `pratyaya`）。创建专家身份时三个必须一致；否则专家市场注册信息会与本地配置脱节。

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
| `python3 scripts/audit_canvas_html.py <html> --source <Mx-vN.md> --state <state.json>` | 审计正式模块 Canvas HTML |
| `python3 scripts/check_contract_consistency.py` | 跑契约一致性检查器（开发辅助，**非 CI 强制**），输出规则化问题清单 |
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
> 远低于被它保护的资产。当前 22 error 中有 5 个是 `v1.0.0` 改造进行中的中间状态（schema 4
> 字段、路径漂移、DEPRECATED），过早接入会卡死正在做的 PR。

### 8.1 当前覆盖的规则族（31 条）

| 阶段 | 类别 | code |
|---|---|---|
| A 最小强门禁 | manifest / 入口 / 版本 | `MANIFEST_JSON` `IDENTITY_MATCH` `ENTRY_EXISTS` `AGENT_ENTRY` `SKILL_ENTRY` `VERSION_FORMAT` `CHANGELOG_VERSION` |
| A 最小强门禁 | GATE 文件 | `GATE_FILE_SET` `GATE_TABLE_PARSE` `GATE_TABLE_WIDTH` `GATE_ID_FORMAT` `GATE_ID_MODULE` `GATE_ID_UNIQUE` `GATE_CATEGORY` `GATE_RISK` `GATE_SOURCE` |
| A 最小强门禁 | 视觉模式 | `PATTERN_COUNT` `PATTERN_FILENAME` `PATTERN_SEQUENCE` `PATTERN_ID` `PATTERN_METADATA` `PATTERN_ENUM` |
| A 最小强门禁 | 文档/链接 | `LOCAL_LINK` `DEPRECATED_TERM` |
| B 跨契约结构 | section / schema / 状态机 | `GATE_SECTION_SYNC` `RENDER_SECTION_SYNC` `SKILL_TEMPLATE_SYNC` `STATE_ENUM_SYNC` `AUTH_FIELDS` `OVERRIDE_CATEGORY` |

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

1. **专家包 v2.0+ 正式发布**——v1.0 改造还在进行中（22 error 含 5 个"设计进行中"中间状态）
2. **多人协作有真实 PR 流程**——当前单人维护，没有 PR 边界
3. **当前 error 清单已清零**（或被白名单显式接受）——22 个 error 中至少 `LOCAL_LINK` / `AUTH_FIELDS` / `OVERRIDE_CATEGORY` / `DEPRECATED_TERM` 这 4 类需修复

任一条件不满足时，本检查器应保持在"开发辅助"形态，作为改写前/后的差异分析工具使用，而非拦截 PR。

---

**版本**：v1.0.0
**配套文档**：[DESIGN.md](./DESIGN.md) / [docs/installation.md](./docs/installation.md) / [docs/user-guide.md](./docs/user-guide.md)
