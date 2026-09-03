# 使用示例（端到端对话流程）

> 本文件由主 Agent（`agents/pratyaya.md`）下沉而来。主 Agent 保留 1 个端到端示例作为行为锚点，
> 其余示例在此维护。

## 使用示例

### 示例 1：M1 Gate 全 PASS 流程

```
用户：开始 M1
Agent：M1 引导问题已加载（步骤 0 模式 A）...

用户：M1 引导
Agent：（加载 frameworks/m1-intent.md，输出本模块核心价值和引导问题）

用户：这是我们的逐字稿：<粘贴文本>
Agent：（存档为 transcripts/module-1-T01-raw.md，生成 M1-keypoints.md）
      （输出 Key Points 概览，末尾提示「请选择：提炼 / 补问 / 先看个样子」）

用户：提炼
Agent：（步骤 2，调用 mvl-distill 生成 M1-v1.md 确认包）
      （步骤 5，展示必展项 5 条 + 详情折叠）
      （步骤 6，自动调用 module-conclusion-gate，输出 Gate 报告：gate_recommendation=pass）

用户：确认 v1
Agent：（Gate 全 PASS + 用户确认 → confirmation_mode=gate_pass / render_authorized=true / status=confirmed）
      （步骤 7，扫描视觉模式 frontmatter，列出全部候选、默认预选 10 黑灰，等用户确认/改选）

用户：选择 blue-professional-balanced
Agent：（从本轮扫描结果保存 `skills/canvas-render/visual-patterns/01-blue-professional-balanced.md`，不根据 ID 拼接路径）
      （把完整路径 + state.json 授权元数据传给 canvas-render）
      （生成 output/module-1-canvas.html，状态 → rendered）
```

### 示例 2：M5 business_risk override 流程

```
用户：开始 M5
Agent：M5 引导问题已加载...

用户：<提交 M5 转写> → 提炼
Agent：（生成 M5-v2.md，状态 review_ready）
      （步骤 6，自动调用 Gate，输出 gate_recommendation=fail）
      （Gate 报告：M5-GATE-04 业务风险 FAIL——can_create_value 实测值未达目标值；M5-GATE-05 业务风险 FAIL——trust_risk_controls 仅 2 项具体控制；override_eligible=true）

用户：我接受这两个风险，先形成带保留意见的正式成果。
     M5-GATE-04 原因：模拟环境无法复现真实生产数据分布；补救：生产试点前完成专项验证。
     M5-GATE-05 原因：第三轮验证受时间限制未跑完所有控制项；补救：上线前补全权限边界、人工兜底两项控制。
     确认人：业务负责人张三
     确认时间：2026-07-30T20:00:00+08:00
Agent：（写入 override_audit，confirmation_mode=override / render_authorized=true / status=confirmed）
      （步骤 7，扫描视觉模式 frontmatter，列出全部候选、默认预选 10 黑灰，等用户确认/改选）

用户：选择 03-signal-balanced
Agent：（生成 output/module-5-canvas.html，顶部显示"已确认 · 带保留意见"，quality-caveat 列出两项 override 详情；状态 → rendered）
      （Phase 2 全局汇总时，M5 出现在"带保留意见的结论"分组中，并检查下游 M6 是否依赖被 override 的假设）
```

### 示例 3：M3 information_integrity 失败不接受 override

```
用户：开始 M3
Agent：M3 引导问题已加载...

用户：<提交转写> → 提炼
Agent：（生成 M3-v1.md，状态 review_ready）
      （步骤 6，Gate 报告：M3-GATE-04 information_integrity FAIL——loop_goal 未由业务方与技术方共同确认）

用户：我接受这个风险，先确认 v1。
Agent：（阻断）M3-GATE-04 属于 information_integrity 类别，不可 override。请返回步骤 2 修订 loop_goal 后重新生成确认包。
```

### 示例 4：分支决策（补问 vs 提炼）

```
用户：提交转写
Agent：（生成 M2-keypoints.md，末尾提示决策）

用户：补问
Agent：（步骤 3，输出 M2-gaps.md 补问清单，状态 → gaps_open）

用户：<提交新一轮转写>
Agent：（存档为 transcripts/module-2-T02-raw.md）
      （生成 M2-keypoints.md 第 2 轮，覆盖第 1 轮 Key Points 摘要）
      （末尾提示决策）

用户：提炼
Agent：（生成 M2-v2.md 确认包，v1 的 `render_authorized` 已重置为 `false`；v1 旧 HTML 标记为过期）
```

### 示例 5：先看个样子（草稿 Canvas）

```
用户：先看个样子
Agent：（步骤 4，调用 canvas-render 生成草稿 Canvas）
      （数据源：当前最新 M3-keypoints.md，非确认包）
      （带永久水印，状态不变，仍为 draft）
      （提示：草稿不能进入全局汇总或管理层报告）
```

