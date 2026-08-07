# 安装指南

> 适用版本：以 `.codebuddy-plugin/plugin.json` `version` 字段为权威
> 适用工具：WorkBuddy

> **TL;DR**：把 [第三节](#3-给-workbuddy-的一键安装提示词) 的提示词**完整复制**到 WorkBuddy 的"专家导入"入口。安装后**必须重启** WorkBuddy。

## 1. 概述

**Pratyaya Canvas Expert**（专家标识 `pratyaya`）是多画布工作坊专家包，专为 WorkBuddy 平台设计，支持三种画布类型：

| 画布 | 定位 | 结构 |
|---|---|---|
| **MVL** | 最小可验证自治闭环工作坊 | M1-M6 六模块 |
| **黄金圈** | Golden Circle 战略澄清 | WHY/HOW/WHAT 三层 |
| **HMW** | How Might We 问题重构 | 陈述四字段 + 想法种子 |

核心能力：

- 四类画布（MVL / 黄金圈 / HMW / 用户画像）的引导、转写提炼与确认包沉淀
- 质量门禁（Gate）建议 + 用户授权
- 模块化智能体画布（Canvas）的生成（HMW 走双 Gate 审计）
- 5 态画布生命周期管理（四类画布共用）

专家包的元数据（`displayName` / `profession` / `displayDescription` / `quickPrompts` / `tags`）定义在 `.codebuddy-plugin/plugin.json`。**本指南不重复 plugin.json 字段，统一以一句话指向 plugin.json 作为权威来源**。详细字段值请查阅 `plugin.json`。

## 2. 安装前准备

在运行 WorkBuddy 的机器上准备：

- WorkBuddy（最新版）
- 仓库目录：`my-codes/pratyaya`
- Git 命令行（用于 clone/拉取）

> **注**：专家包是项目仓库的子目录（`.codebuddy-plugin/`），不是独立安装包。请先把仓库 clone 到本地。

## 3. 给 WorkBuddy 的一键安装提示词

将以下代码块**完整复制**到 WorkBuddy 的"专家导入"入口（一键粘贴即可完成注册与安装）：

```text
请帮我安装本地的多画布工作坊专家（Pratyaya Canvas Expert），仓库路径为 ./pratyaya/。
该专家包由本仓库的 .codebuddy-plugin/plugin.json 描述。
请按 plugin.json 的字段读取专业名称、描述、快速指令集和标签。
专家包内的 agents/pratyaya.md 是主 Agent 入口。
安装完成后请重启 WorkBuddy 并验证。
```

> **关键信息**：
> - 提示词内已含"专家仓库路径""plugin.json 路径""主 Agent 路径"三个核心路径
> - 版本号以 plugin.json `version` 字段为权威
> - 专家导入必须成功完成注册写入；重启只负责重新加载，不能替代注册
> - 安装失败时请把 WorkBuddy 错误信息回传

## 4. 安装后必须重启

WorkBuddy 完成专家注册后必须重启，才能完整加载 agent、skill、avatar 和视觉模式资源：

1. 关闭 WorkBuddy
2. 重新打开 WorkBuddy
3. 进入"我的专家"页面，验证 “Pratyaya Canvas Expert” 已出现

不重启可能导致：专家已安装但 Agent 加载失败、Skill 路径不识别、avatar 缺失等异常。

## 5. 如何找到并验证专家

### 5.1 在 WorkBuddy 中找到专家

打开 WorkBuddy 后，在"我的专家"页面查找：

- **专业名称、标签**：以 plugin.json 的 `displayName` 与 `tags` 字段为准（详见 `.codebuddy-plugin/plugin.json`）
- 3 个快速指令：在 plugin.json 的 `quickPrompts` 字段中定义

### 5.2 验证对话

向专家发送以下任一问题验证：

- "请显示你的 3 个快速指令"
- "请告诉我你的专业名称和描述"
- "请展示你的标签列表"

如果专家能准确回传 plugin.json 的 `quickPrompts` / `displayName` / `tags` 字段，则安装成功。

### 5.3 验证画布生命周期

向专家发送：

> "请告诉我 HMW 画布的当前状态机"

预期回答（5 态 + `confirmation_mode` 属性）：

```text
状态：draft → gaps_open ↔ review_ready → confirmed → rendered
confirmation_mode：gate_pass / override / null（属性，不是状态）
```

也可验证画布类型路由："请介绍一下你支持哪几种画布"（预期：MVL / 黄金圈 / HMW / 用户画像四类）。

> `confirmation_mode` 是属性（不是状态）；用户可对 `business_risk` 显式 override 后进入 `confirmed`，并触发 caveat 显式呈现。HMW 正式渲染额外要求结构 Template Gate 通过（详见 [DEVELOPMENT.md §3.1](../DEVELOPMENT.md#31-python-静态审计)）。

## 6. 常见问题排查

### 6.1 "我的专家"页面没有出现专家

- 确认 `.codebuddy-plugin/plugin.json` 文件存在
- 确认 WorkBuddy 已重启
- 确认 plugin.json 的 `name` 字段是 `pratyaya`

### 6.2 专家出现但 Agent 加载失败

- 检查 `agents/pratyaya.md` 文件存在且未被修改
- 文件名严格为 `pratyaya.md`，并与 plugin.json 的 `agentName` 一致

### 6.3 标签或快速指令显示异常

- 确认 plugin.json 是合法 JSON
- 确认 `tags` / `quickPrompts` 字段是字符串数组

### 6.4 工作流异常

- 检查 `skills/` 目录完整（应含 9 个 Skill：mvl-distill / gc-distill / hmw-distill / persona-distill / module-conclusion-gate / gc-gate / hmw-gate / persona-gate / canvas-render）
- 检查 `skills/canvas-render/visual-patterns/` 包含 `README.md` 和 10 个编号模式文件
- 检查 `examples/modules/` 与 `examples/canvas-html/` 目录完整

### 6.5 草稿 Canvas 与正式 Canvas 混淆

- 草稿 Canvas 顶部应有"草稿 / 未确认 / 禁止用于管理层决策"字样
- 正式 Canvas 顶部应有画布名（MVL Canvas / Golden Circle / HMW Canvas）+ 版本号
- 如无区分标志，请重新安装
- HMW 正式 Canvas 无法生成时，检查是否已通过双 Gate（`--template` 缺失会 FAIL）

---

**版本**：以 `.codebuddy-plugin/plugin.json` 为权威
**适用平台**：WorkBuddy
**配套文档**：[用户指南](./user-guide.md) / [DEVELOPMENT.md](../DEVELOPMENT.md) / [DESIGN.md](../DESIGN.md)
