# Pratyaya FAQ 索引

> `faq.md` 的检索目录。`faq-answer` 回答静态 FAQ 前**先读本索引**：按用户问题匹配「命中问法 / 关键词」，确定命中的 faq.md 小节标题，再在 `faq.md` 中按该标题定位、**只读对应小节正文**；不得在未读索引前通读 `faq.md` 全文。
> 维护纪律：`faq.md` 新增 / 修订 / 删除问答条目时**必须同步本索引**（同步该行的分类与命中问法）。索引锚 = faq.md 小节标题（唯一且稳定）；**不维护行号**，标题即锚。

## 开场前缀（常驻小区域：官方自介 / 能力 / 起步 / 边界）

用户问「你是谁 / 你能做什么 / 怎么开始 / 能做什么不能做什么 / 能力边界」时，只读 faq.md 下方小节（位于文件最前部，`## 启动与项目` 之前），不需要读问答索引：

| faq.md 小节标题（锚） | 何时读取 |
|---|---|
| 官方自我介绍 | 开场一句话定位；「介绍一下你能做什么」 |
| 能做什么（口径与 plugin.json displayDescription 一致） | 画布清单与能力一览 |
| 怎么开始 | 如何启动新项目 / 工作坊起步 |
| 边界与平台底线 | 能力边界、不可写项、平台限制 |

## 问答索引

| 分类 | faq.md 小节标题（锚） | 命中问法 / 关键词 |
|---|---|---|
| 启动与项目 | pratyaya 能做什么？ | 你能做什么、能帮我做什么、这个专家有什么用、FAQ |
| 启动与项目 | 如何开始新工作坊？ | 怎么开始、开始新工作坊、第一个步骤 |
| 启动与项目 | project_slug、group_id 和 topic_slug 是什么？ | project_slug、group_id、topic_slug、组号、议题、短名 |
| 画布选择 | 各类画布分别适合什么？ | 画布选择、哪个画布、适合什么、MVL、MAAU、黄金圈、HMW、画像、旅程、V2C、5W 选哪个 |
| 画布选择 | V2C VAC 是什么？ | V2C、VAC、价值归因、Value Attribution、capability、change |
| MVL M1–M6 流程 | M1 战略对齐、项目分组与闭环证据准备，做什么？ | M1、战略对齐、项目分组、闭环证据 |
| MVL M1–M6 流程 | M2 需求发现、用户与真实流程拆解，做什么？ | M2、需求发现、用户、真实流程 |
| MVL M1–M6 流程 | M3 闭环目标定义、HMW 拆解与方案方向锁定，做什么？ | M3、闭环目标、HMW 拆解、方案方向 |
| MVL M1–M6 流程 | M4 闭环冻结、原型两轮迭代与开发筹备，做什么？ | M4、闭环冻结、原型迭代、开发筹备 |
| MVL M1–M6 流程 | M5 三轮验证、交互优化与信任控制校验，做什么？ | M5、三轮验证、交互优化、信任控制 |
| MVL M1–M6 流程 | M6 终极打磨、方案择优、成果演示与闭环总结，做什么？ | M6、终极打磨、方案择优、成果演示 |
| MVL M1–M6 流程 | M1–M6 总览：六模块怎么衔接，与全局 Canvas 怎么对应？ | M1-M6 总览、六模块衔接、全局汇总、Final Canvas、maau-global-canvas |
| MVL M1–M6 流程 | M3 的 `workflow_draft` 与 M4 的 `workflow_final` 有什么区别？ | workflow_draft、workflow_final、M3 M4 的 workflow 区别 |
| 模式与流程 | A / B / C 模式是什么？ | A 模式、B 模式、C 模式、模式选择 |
| 模式与流程 | 为什么不能直接从逐字稿渲染？ | 逐字稿直接渲染、为什么需要确认包、跳过提炼 |
| Gate 与确认 | Gate pass / fail / pending 是什么？ | Gate、gate_pass、gate fail、gate pending、门禁、闸门 |
| override | override 什么时候可以用？ | override、绕过门禁、强制授权、覆盖建议 |
| 渲染与产物 | HTML 产物在哪里？ | HTML 产物、产物位置、output 目录、输出文件在哪 |
| 渲染与产物 | 为什么不能正式渲染？ | 不能渲染、不能生成 HTML、为什么没有 rendered、渲染被阻断 |
| 状态与下一步 | 当前 topic 到哪一步怎么看？ | 当前状态、下一步做什么、进行到哪一步、state.json 怎么看 |
| 异常处理 | Template Gate fail 怎么办？ | Template Gate、TPL-GATE、结构门禁失败 |
| 异常处理 | 找不到视觉模式怎么办？ | 视觉模式、visual-patterns、模式找不到 |
| 画布来源与版权 | MAAU / V2C VAC 画布的来源与版权是什么？ | 版权、来源、著作权、归属、致谢、檀林、王鸿、FDE |

## 使用约定（faq-answer 执行）

1. 收到**静态 FAQ 问题** → 先读本索引，按「命中问法 / 关键词」或分类匹配 1–2 个小节。
2. 命中 → 在 `faq.md` 中按小节标题定位，**只读该小节正文**（小节结束于下一个同层或上层标题）。
3. **开场 / 自介 / 起步**问题 → 只读 faq.md「开场前缀」列出的小节，无需读问答索引。
4. **未命中或问题需全貌比对** → 才允许通读 `faq.md` 全文（兜底），并在回答依据中自报「全文检索」。
5. **当前项目状态 / 异常定位**（非纯静态，如"当前 topic 到哪一步"）→ 静态口径走 1–2，项目实际状态按 `faq-answer` SKILL.md Source Priority 读 `workshop/...` 下 `state.json` / `manifest.json` 等事实文件。
6. 依据优先级（口径冲突时）：`.codebuddy-plugin/plugin.json` > `README.md` > `docs/user-guide.md` > faq.md 小节 > `DESIGN.md` / `DEVELOPMENT.md`。
