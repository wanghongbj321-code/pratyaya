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
| `grep -rn "check_gate.py" .` | 检查已删除 Gate 脚本引用残留 |
| `grep -rn "module-N\.json" .` | 检查旧 JSON 引用残留 |
| `wc -l README.md DEVELOPMENT.md DESIGN.md docs/*.md` | 检查现行文档规模 |

---

**版本**：v1.0.0
**配套文档**：[DESIGN.md](./DESIGN.md) / [docs/installation.md](./docs/installation.md) / [docs/user-guide.md](./docs/user-guide.md)
