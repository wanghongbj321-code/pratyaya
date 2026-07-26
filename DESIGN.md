# MVL 工作坊专家团 · 设计文档

> **仓库布局（2026-07-26 定稿）**：本目录 `D:\AI\AI原生MVL工作坊` 是 git 主仓库（推 Gitee）。
> 专家包**实体文件**在专家目录 `C:\Users\bson9\.workbuddy\plugins\marketplaces\my-experts\plugins\mvl-workshop-facilitator`（WorkBuddy 强制要求），本目录下的 `mvl-workshop-facilitator/` 是指向实体的 **Junction**——两边是同一批文件，改哪边都实时生效，git 可正常穿透提交。
> ⚠️ 维护注意：删除 Junction 只能用 `[System.IO.Directory]::Delete(路径)`，严禁 `Remove-Item -Recurse`（会穿透删除实体）；慎用 `git clean -fdx`。

## 一、需求

3 天 AI 原生 MVL（最小可验证自治闭环）工作坊，3~6 个小组并行。每组助教把每模块的讨论录音转写交给 WorkBuddy，由专家团完成：

1. **模块输出**：每模块一张竖版 HTML 画布（共 6 张）
2. **全局汇总**：6 模块内容重组为全局 MAAU 画布 HTML
3. **报告输出**：报告型演示稿（HTML，浏览器全屏放映）

最终打成专家包发布到版本库，各组助教下载即用。

## 二、已锁定决策（2026-07-26）

| 决策点 | 结论 |
|--------|------|
| 专家形态 | 1 个主专家（agent 型）+ 技能包，助教零切换 |
| 模块↔MAAU 映射 | 增长式填充：M1→Intent，M2→User，M3→Workflow草案+Intent回填，M4→AgentTeam+Context+Workflow冻结，M5→Validation，M6→Validation补全+一句话总结 |
| PPT 形式 | HTML 演示稿（浏览器全屏放映，不做可编辑 pptx） |
| 场景适配 | 专家包场景无关，一切内容从转写提取 |

## 三、架构

```
录音 → 外部转写工具 → 助教粘贴
        ↓
MVL 工作坊助教（主专家：引导师 / 提炼师 / 追问官）
        ↓
技能包：mvl-distill（6 模块提炼框架 + 五趟处理流程）
        ↓
状态目录 mvl-workshop/group-XX/（state.json 断点续传、按组隔离）
        ↓
输出：模块竖版HTML ×6 → 全局MAAU画布HTML + 演示报告HTML
```

## 四、关键机制

1. **断点续传**：进度落盘 `state.json`，每次对话先读状态
2. **多组隔离**：`group-XX/` 目录按组隔离，初始化时确认组号
3. **推断标注**：`〔推断〕` 前缀区分原话与 AI 推断，推断项进待确认清单
4. **先确认再出图**：结构化文字版 → 小组确认 → 才生成 HTML
5. **长文本五趟处理**：存档 → 分段 → 逐段提取 → 框架归并 → 推断标注 → 确认版

## 五、构建阶段

- [x] 阶段一：骨架 —— 专家定义 + 指令卡 + 状态机 + M1~M6 提炼框架 + MAAU 规范 + 样例归档（2026-07-26 完成，已注册）
- [ ] 阶段二：输出引擎 —— maau-render（模块竖版 + 全局画布模板）、maau-report（HTML 演示稿）
- [ ] 阶段三：联调 —— 用真实转写文本（用户提供）从 M1 跑到全局汇总
- [ ] 阶段四：打包发布 —— 头像生成（ImageGen，约 5-10 积分）→ package_expert.py 打包 → 版本库发布

## 六、现场运营 SOP（助教侧）

1. 每模块讨论时录音，预留最后 30 分钟做转写与确认
2. 模块转写交给助教专家 → 确认文字版 → 出画布
3. 补问清单在下一模块开场前 10 分钟处理
4. D3 下午预留 60 分钟做全局汇总

## 七、版本管理与 Gitee 发布

- 仓库：`D:\AI\AI原生MVL工作坊`（main 分支，首次提交 cde7345 已完成）
- 忽略规则：`.workbuddy/`（本机记忆）、`mvl-workshop/`（助教运行时组目录）、`test-transcripts/`（真实转写，业务敏感不入库）
- 日常开发：直接在本目录编辑（经 Junction 即改专家实体），改完 `git add . && git commit`；涉及包结构变更后需重跑 validate + register
- 推 Gitee：`git remote add origin <gitee-repo-url>` 后 `git push -u origin main`
- 助教侧安装：从 Gitee 克隆后，把 `mvl-workshop-facilitator/` 复制到自己的专家目录，跑 register_expert.py 即可用
