# Pratyaya 变更日志

> 本文件记录 Pratyaya 专家的正式版本变更。
> 完整 SemVer 与架构说明见 [`README.md`](./README.md) / [`DESIGN.md`](./DESIGN.md)。

## [v3.8.2] - 2026-10-20

- **发布打包固化**：新增 `scripts/package_release.py`，把「源码仓库 → 可安装专家包」固化为可审计代码（zip 带版本名 `dist/<name>-<version>.zip`）。
- **共享画布引擎迁址**：`skills/_engine/` → `scripts/engine/`，`skills/` 现与 `plugin.json` `skills[]` 声明一一对应。
- `dist/` 加入 `.gitignore`。

## [v3.7.1] - 2026-09-20

- SWOT 画布底部间距修复与视觉简化（移除页头装饰横条与卡片强调竖条）。

## [v3.7.0] - 2026-09-13

- 新增 SWOT/TOWS 策略分析画布：四象限 + TOWS 策略推导 + 八项质量 Gate，独立确认包与渲染模板。

## [v3.6.3] - 2026-09-06

- 专家展示名由「Pratyaya Canvas Expert」缩短为「Pratyaya Coach」，满足平台名称长度限制。

## [v3.6.2] - 2026-09-06

- 渲染验收分级调整：浏览器级视觉检查与截图目检改为按需执行，默认只做静态结构审计。
- 渲染耗时留痕（`.render-trace.jsonl`）；Workflow 装配提速；FAQ 增强。

## [v3.6.1] - 2026-09-06

- Workflow 流程图回退为 LLM 直出（移除 python 确定性布局器 `workflow_layout`）。
- 恢复 AGENTS.md 规则 3 原文：禁止渲染脚本，渲染统一走 canvas-render Skill。

## [v3.6.0] - 2026-09-05

- MAAU 画布两阶段渲染（无图先交付、Workflow 图按需生成）。
- 输出文件版本化命名（`--v{N}` 后缀）与身份审计。
