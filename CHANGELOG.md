# Pratyaya 变更日志

> 本文件记录 Pratyaya 专家的正式版本变更。
> 完整 SemVer 与架构说明见 [`README.md`](./README.md) / [`DESIGN.md`](./DESIGN.md) / [docs/MVL-整体架构设计.md](./docs/MVL-整体架构设计.md)。

## [v1.0.2] - 2026-08-01

### 字段对齐

- `profession` 的中英文值改为与 `displayName` 一致（统一为 `Pratyaya MVL Expert`），影响 `.codebuddy-plugin/plugin.json` 与 `agents/pratyaya.md` frontmatter。

### 文档去重

- 6 个文档（README / DEVELOPMENT / DESIGN / docs/installation / docs/MVL-整体架构设计 / docs/user-guide）删除重复的"版本：v1.0.X"行，改为指向 `.codebuddy-plugin/plugin.json` `version` 字段为权威。后续升版仅需改 `plugin.json` 与本文件。

## [v1.0.1] - 2026-08-01

### 措辞调整

- 精简 `displayDescription.zh` 至开发指导要求的 40-50 字区间。原 49 字符的"AI 原生的 MVL（Minimum Verifiable Loop，最小可验证自治闭环）工作坊引导专家包"过长，按 `workbuddy-expert-开发指导.md` §10.1 硬约束改为 30 字符的"AI 原生的 MVL 工作坊引导专家，蒸馏转写、卡模块结论、生成画布"。仅一处文件一处字段的措辞变更，不影响功能与契约。

## [v1.0.0] - 2026-08-01

### 初始版本

- 初始化 `pratyaya` 专家身份，展示名称统一为 `Pratyaya MVL Expert`。
- 提供 MVL 工作坊引导、转写提炼、模块 Gate 建议与 Canvas 渲染能力。
- 建立 Key Points → 提炼 → Gate → 渲染四阶段管线。
- 建立 `draft → gaps_open ↔ review_ready → confirmed → rendered` 五态生命周期。
- Gate 仅提供建议，用户是最终决策者。
- 正式渲染要求 `render_authorized=true` 且 `confirmation_mode ∈ {gate_pass, override}`。
- 提供 9 个 Markdown Canvas 视觉模式及离线 HTML 渲染契约。
