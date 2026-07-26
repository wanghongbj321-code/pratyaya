# MVL 工作坊助教（闭环助教）

3 天 AI 原生 MVL（最小可验证自治闭环）工作坊的全程 AI 助教：引导小组讨论、提炼录音转写、逐模块生成竖版 MAAU 画布，最终汇总全局画布与演示报告。

## 类型

Agent 型（单个 AI 专家）+ 内嵌技能包 `mvl-distill`

## 功能

- **工作坊引导**：6 个模块的引导问题清单与讨论支架（M1 战略对齐 → M6 总结演示）
- **转写提炼**：把 2-5 万字讨论转写提炼为结构化 module-N.md，映射 MAAU 六板块（增长式填充）
- **缺口追问**：识别缺失/矛盾信息，输出补问清单
- **推断标注**：〔推断〕前缀严格区分讨论原话与 AI 推断，严禁编造
- **画布生成**：模块竖版 HTML ×6 → 全局 MAAU 画布 HTML + 演示报告
- **状态管理**：按组隔离目录（`mvl-workshop/group-XX/`），跨会话断点续传，支持多组并行

## 使用示例（助教三句话上手）

- 「我们是第1组，项目名是【XXX】，开始MVL工作坊第一天上午模块」
- 「这是本模块的讨论转写，请提炼并生成模块画布」
- 「六个模块已全部完成，请生成全局MAAU画布和演示报告」

## 目录结构

```
mvl-workshop-facilitator/
├── agents/mvl-workshop-facilitator.md    # 主专家定义（状态机+指令卡）
└── skills/mvl-distill/
    ├── SKILL.md                          # 转写提炼技能（五趟处理流程）
    ├── frameworks/                       # M1~M6 六个模块提炼框架
    └── references/
        ├── maau-canvas-spec.md           # MAAU 画布字段与视觉规范
        ├── workshop-schedule.md          # 3 天日程与模块定义
        └── methods/                      # 14 个脱敏方法论文件（按主题分拆）
```

## 安装

1. 从 Gitee 仓库下载：https://gitee.com/botson/mvl-workshop-facilitator
2. 在 WorkBuddy 中打开「专家」→「安装专家」→ 选择下载的目录

安装完成后，在专家中心即可看到「闭环助教」，直接开始对话使用。
