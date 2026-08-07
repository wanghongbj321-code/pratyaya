---
name: persona-gate
description: 用户画像闸门。对 PERSONA-v{N}.md 确认包执行 6 项放行条件检查，输出 gate_recommendation 与 override_eligible。
triggers:
  - "用户画像闸门"
  - "persona gate"
  - "画像质量检查"
---

# Persona Gate（用户画像闸门）

> 对 PERSONA-v{N}.md 确认包执行 6 项放行条件检查，输出 gate_recommendation 与 override_eligible。

## 触发词

- 用户画像闸门
- persona gate
- 画像质量检查

## 输入

| 参数 | 说明 | 示例 |
|---|---|---|
| `state_path` | 项目状态文件路径 | `./outputs/state.json` |
| `output_dir` | 输出目录（可选，默认 `./outputs`） | `./outputs` |

## 输出

| 文件 | 说明 |
|---|---|
| `PERSONA-gate-report-v1.md` | 闸门检查报告 |
| 更新 `state.json` | 写入 `persona.gate_recommendation` 与 `persona.override_eligible` |

## 执行流程

### 1. 读取确认包

读取 `PERSONA-v1.md`，提取：
- 9 基本信息
- 6 宫格
- 4 质量维度

### 2. 检查 6 项放行条件

读取 `references/PERSONA-gate.md`，逐项检查：

**P1: 关键基本信息完整性**
- name / job_title / industry 必须有值

**P2: 六宫格完整性**
- 6 个宫格必须有内容或标记为「待补问」

**P3: 质量维度证据充分**
- evidence_based 评分 ≥ 3
- 每个要点有证据支撑

**P4: 画像具体性**
- concrete 评分 ≥ 3
- 避免泛泛描述

**P5: 痛点原话记录**
- pain_in_voice 评分 ≥ 3
- 痛点使用用户原话

**P6: 代表性**
- representative 评分 ≥ 3
- 画像能代表一类用户

### 3. 输出闸门报告

```markdown
# 用户画像闸门报告 v1

## 闸门结果
- **结果**: PASS / FAIL
- **可覆写**: Yes / No

## 检查明细

| ID | 检查项 | 状态 | 说明 |
|---|---|---|---|
| P1 | 关键基本信息完整 | ✅ | ... |
| P2 | 六宫格完整 | ✅ | ... |
| P3 | 质量维度充分 | ⚠️ | ... |
| P4 | 画像具体 | ✅ | ... |
| P5 | 痛点原话 | ✅ | ... |
| P6 | 代表性 | ✅ | ... |

## 建议动作
- 全部 PASS → 可进入渲染
- 部分 FAIL → 进入补问环节
```

### 4. 更新 state.json

写入 `persona.gate_recommendation`（pass/fail）与 `persona.override_eligible`（true/false）。

## 覆写规则

仅当 **P3 / P4 / P5 / P6 中任一项 FAIL** 时，用户可选择覆写：
- 填写覆写理由
- 记录决策人
- 记录决策时间
- 记录补救措施

**P1 / P2 FAIL** 不可覆写，必须补问。

## 约束

- **不修改确认包内容**：只检查，不改写
- **不自动渲染**：输出建议，由用户决定是否渲染
- **可覆写项**：仅质量维度（P3-P6），基本信息完整性不可覆写

## 依赖

- `references/PERSONA-gate.md`（闸门条件定义）
- `skills/persona-distill/SKILL.md`（确认包结构）
