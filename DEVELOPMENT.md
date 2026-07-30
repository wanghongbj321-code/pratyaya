# 维护者文档

> 面向维护专家包的人和运行时的 AI 助教。**不面向**工作坊用户（用户文档见 [docs/user-guide.md](./docs/user-guide.md)）。

## 1. 文档定位

本文件说明维护专家包所需的命令、流程约束和工具链。完整架构与不变量见 [DESIGN.md](./DESIGN.md)；工作坊用户使用流程见 [docs/user-guide.md](./docs/user-guide.md)；专家包元数据以 `.codebuddy-plugin/plugin.json` 为权威。

## 2. 质量闸门（LLM 自检）

v2.0 起，模块结论闸门（Gate）由 LLM 评估替代 v1.x 的 Python 脚本（`check_gate.py` 已删除）。执行流程：

1. LLM 读取 `modules/Mx-v{N}.md`（确认包 Markdown）
2. 对照 `skills/module-conclusion-gate/SKILL.md` 的判定规则（34 条放行条件 + 稳定 ID + 分类与风险等级）
3. 输出 Markdown 判定报告 `skills/module-conclusion-gate/references/Mx-gate.md`，含 `gate_recommendation: pass/fail/pending` + `override_eligible: true/false`；**不**写最终授权

详细规则、缺口等级、推断术语、版本绑定的完整定义见 [skills/module-conclusion-gate/SKILL.md](./skills/module-conclusion-gate/SKILL.md)。

## 3. HTML 渲染（LLM 自检）

v2.0 起，HTML 渲染审计由 LLM 自检替代 v1.x 的 Python 脚本（`audit_canvas_html.py` 已删除）。v3.2.0 正式交付前执行 10 项 render-contract 检查（v3.0 8 项 + v3.2.0 新增 2 项）：

1. 数据源一致（HTML 内嵌 `canvas-data` 与 `Mx-v{N}.md` 同版本）
2. DOM 结构（对照 `render-contract.md` 章节 A/B）
3. 共享结构（`quality-panel` / `alignment-section` / `local-notes`）
4. 离线安全（无 `fetch("file...")`、无 iframe、无外部网络资源）
5. 打印规则（`@media print` 隐藏编辑控件，保留版本/确认/风险/质量状态/结论/override caveat）
6. 草稿标记（草稿模式顶部与打印版含"草稿/未确认"字样）
7. 视觉系统单一（仅一种 `visual_system`，不混搭）
8. 模式一致（色板、字体、网格、组件及专属组件符合选定 Markdown 模式）
9. **授权元数据**（v3.2.0 新增）：`canvas-data.auth` 含 `render_authorized` / `confirmation_mode` / `override_audit`（override 时），与 `state.json` 完全一致
10. **Caveat 显示**（v3.2.0 新增，仅 `confirmation_mode=override` 模块）：页面顶部"已确认 · 带保留意见"状态标识 + `quality-caveat` 锚点 + 风险详情 + 打印版保留 + `canvas-data` 内嵌 override_audit

详细自检依据、DOM 映射表、共享结构、离线约束、数据完整性见 [skills/canvas-render/SKILL.md](./skills/canvas-render/SKILL.md) 与 [skills/canvas-render/references/render-contract.md](./skills/canvas-render/references/render-contract.md)。

## 4. Canvas 视觉模式维护

v3.0 起，Canvas 视觉系统由 `skills/canvas-render/visual-patterns/` 下的 Markdown 规格定义，不再使用预制 HTML 外壳或集中登记册。

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

当前版本：v3.2.0-p1 试用（`plugin.json` 仍 `3.1.0`，P3 阶段 D 升 `3.2.0`）。

发布流程（按 workbuddy 指导第十节"修改已有专家"5 步）：

1. **定位** — 确认改动范围（在哪个文件、影响哪些 Skill、Agent 或视觉模式）
2. **确认范围** — 评估是否需要同步 docs/、DEVELOPMENT.md、DESIGN.md
3. **执行修改** — 改完代码与文档
4. **校验** — `python3 -c "import json; json.load(open('.codebuddy-plugin/plugin.json'))"` 验证 plugin.json 是合法 JSON；运行 `scripts/validate_expert.py`（如存在）
5. **重新注册** — WorkBuddy 重启加载（详见 [docs/installation.md §4](./docs/installation.md#4-安装后必须重启)）

严禁修改（按 workbuddy 指导）：`name` 字段（kebab-case 唯一标识）、`agentName` 字段、专家目录名、agents/ 下的 .md 文件名。这些字段的修改会导致专家丢失。

## 7. 命令速查

| 命令 | 用途 |
|---|---|
| `git log --oneline` | 查看 commit 历史 |
| `git diff` | 查看当前未提交变更 |
| `python3 -c "import json; json.load(open('.codebuddy-plugin/plugin.json'))"` | 验证 plugin.json 合法 |
| `find skills/canvas-render/visual-patterns -maxdepth 1 -type f -name '[0-9][0-9]-*.md' \| sort` | 列出视觉模式候选 |
| `rg -n '^id:|^visual_system:|^layout:|^formality:|^density:|^best_for:' skills/canvas-render/visual-patterns/*.md` | 复核选择元数据 |
| `grep -rn "check_gate.py\|audit_canvas_html.py" .` | 检查旧脚本引用残留 |
| `grep -rn "module-N\.json" .` | 检查旧 JSON 引用残留 |
| `wc -l README.md DEVELOPMENT.md DESIGN.md docs/*.md` | 检查现行文档规模 |

---

**版本**：v3.2.0-p1 试用
**配套文档**：[DESIGN.md](./DESIGN.md) / [docs/installation.md](./docs/installation.md) / [docs/user-guide.md](./docs/user-guide.md)
