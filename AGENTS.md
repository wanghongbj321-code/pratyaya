# AGENTS.md

> 面向在本项目内工作的 AI Agent。先读 [README.md](./README.md) 再开始。

## 规则

### 1. 动手前先读 README

先读 [README.md](./README.md) 了解项目全貌，再按任务类型读对应文档（`SKILL.md` / `DEVELOPMENT.md` / `DESIGN.md` / `docs/user-guide.md` 等）。术语不确定先查证，不要凭模型先验推断。

### 2. 遇到设计问题必须先问用户

涉及状态机、数据源、Skill/Agent 边界、字段定义、Gate 规则、模板、SemVer、文档边界或任何"按惯例/默认"的选择时，**先停下来**列方案与影响，等用户拍板再实现。不确定是不是设计问题，按"是"处理，先问再做。

### 3. 渲染必须通过 canvas-render Skill，禁止渲染脚本

- **禁止新增或使用渲染脚本**（如 `scripts/render_canvas.py` 等任何把数据写成 HTML 的脚本）；渲染统一通过调用 `canvas-render` Skill 完成，参照 `skills/canvas-render/examples/` 对应画布示例模板生成画布。
- `skills/canvas-render/scripts/audit_canvas_html.py` 是**审计**工具（校验产物结构与授权元数据），不是渲染工具；渲染后必须用它做静态审计。
- 画布类型判定（`canvas_type`）、渲染契约（`render-contract-*.md`）、视觉模式（`visual-patterns/`）以 `skills/canvas-render/` 为准，不另起渲染实现。
- 若未来确需自动化渲染入口，先按规则 2 提出设计变更，经用户确认后再实现。

### 4. Release 正文与 CHANGELOG 条目编写规则

- Release 正文**面向专家包终端用户**（下载、安装并使用本专家的人），不是给维护者/审查者的变更说明；**禁止**把 PR body 或文件级改动清单粘贴为 Release 正文。
- CHANGELOG 条目与 Release 正文**同一颗粒度**：CHANGELOG 从写入时就按本规则精简，Release 直接引用对应条目，不另做细化。
- 只写：用户可感的**行为变化**（新功能、修复效果）；升级后**须知**（新用法、产物命名、获取方式变化）；**兼容性与迁移边界**（历史产物、schema 是否变、是否需要重新获取）；必须让用户知晓的**取舍**。
- 不写：文件路径与删除清单、内部工具名/断言名、验证过程与数字（pytest、audit、grep 等）、内部决策与审查编号（如 Q1-A、审查报告）、PR/commit 内部细节。
- 篇幅：PATCH 不超过 5 条；MINOR/MAJOR 一条概要段 + 若干要点；不设"验证"小节。
- 模板：

```markdown
## vX.Y.Z — <一句话主题>

### 修复（PATCH）/ 新增功能（MINOR/MAJOR）
- <用户可感变化，一条一句>

### 兼容性与升级注意
- <历史产物、schema、重新获取事项>
```

- 本规则适用于其后新写入的版本条目；已发布条目（含 v3.6.1）为历史档案，不追溯改写。

### 5. 发布打包必须使用 scripts/package_release.py

- 出包唯一入口：`python3 scripts/package_release.py`。必须先 `--dry-run` 核对清单与条数，再真出包；禁止手工 zip 源码目录，禁止绕过本打包器直接使用官方 `package_expert.py`（其不排开发脚本与运行态目录，且 zip 名不带版本）。
- 版本唯一真值是 `.codebuddy-plugin/plugin.json` 的 `version`；每次出包前必须递增（平台按版本号决定是否迁移缓存，不升版等于没改）。zip 名 `<name>-<version>.zip` 由打包器从 plugin.json 派生，不手工命名。
- 产物输出至 `dist/`（已 git 忽略）；旧包由打包器自动移入 `dist/archive/`，`dist/` 只留当前版本一个包。
- 出包后必须完成包体核验：六条核验（条目数 / 顶层唯一 / 一级项 / 违禁零命中 / 逐文件 diff / 关键文案抽检）+ L1 平台校验（解压件临时放入 plugins/ 下校验）。凡写「已发布」，必须附当场可复跑命令与原始输出（`ls -l` / `unzip -Z1 | wc -l`），不接受自我声明。
- Release 正文与 CHANGELOG 条目按规则 4 编写；本规则管「怎么出、怎么验」，规则 4 管「发布文案写什么」，互补不重叠。
