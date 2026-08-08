# User Persona 确认包 v1

> 画布类型：User Persona（用户画像）画布
> 版本：v1
> 状态：confirmed

## 必展项

### 1. 一句话结论

周晨是需要在高压协作中快速获得可信证据的教育产品经理。

### 2. 对齐摘要

- 共识：3 项
- 分歧：0 项
- 决策：1 项

### 3. 阻塞项

无。

### 4. 缺口速览

- blocker：0
- major：0
- minor：1（accepted_risk）

### 5. 待确认版本

v1

## 详情

### 6. 9 基本信息 + 6 宫格

#### 6.1 9 基本信息

| 字段 | 内容 | 来源引用 |
|---|---|---|
| name（姓名） | 周晨 | Persona 关键主张 1 |
| gender（性别） | 女 | Persona 关键主张 1 |
| age（年龄） | 30–35 岁 | Persona 关键主张 1 |
| location（所在地） | 上海 | Persona 关键主张 1 |
| education（学历） | 硕士 | Persona 关键主张 1 |
| job_title（职位） | 教育产品经理 | Persona 关键主张 1 |
| industry（行业） | 教育科技 | Persona 关键主张 1 |
| family_status（家庭状况） | 待补充 | PERSONA-G01 |
| income（收入） | 待补充 | PERSONA-G01 |

#### 6.2 6 宫格

| 宫格 | 内容 | 来源引用 |
|---|---|---|
| description（人物描述） | 在跨部门协作中负责教育产品的方案取舍。 | Persona 关键主张 2 |
| goals_needs（目标与需求） | 在有限时间内做出可解释的产品决策。 | Persona 关键主张 2 |
| behaviors（行为） | 会访谈用户、整理反馈并对比竞品。 | Persona 关键主张 2 |
| pain_points（痛点） | “我不想再凭感觉拍板。” | Persona 关键主张 2 |
| motivation（动机） | 项目上线节点临近时，希望降低返工风险。 | Persona 关键主张 2 |
| decision_factors（决策因素） | 证据可信度、协作成本和交付时间。 | Persona 关键主张 2 |

### 6a. 质量鉴别

| 维度 | 判定 | 依据 |
|---|---|---|
| evidence_based（真实依据） | 通过 | 行为与痛点均有讨论线索 |
| concrete（具体非刻板） | 通过 | 有明确岗位、场景与行为 |
| pain_in_voice（痛点用原话） | 通过 | 保留了用户原话 |
| representative（代表性） | 通过 | 当前目标群体的典型岗位 |

### 7. 结论登记表

| ID | 结论 | 类型 | 共识状态 |
|---|---|---|---|
| PERSONA-C01 | 可信证据是其高压决策的核心需求。 | fact | 共识 |

### 8. 缺口表

| ID | 等级 | 状态 | 描述 | 缺失影响 | 最少补问 |
|---|---|---|---|---|---|
| PERSONA-G01 | minor | accepted_risk | 家庭与收入信息待补充 | 暂不影响核心工作场景判断 | 下轮补充生活约束与购买力 |

### 9. 推断表

| ID | 推断 | 影响 | 状态 |
|---|---|---|---|
| PERSONA-Inf01 | 可优先提供证据汇总能力。 | 需要后续验证 | 待接受 |

### 10. 关键证据引用

- Persona Key Points 第 2 节关键主张。

### 11. 待用户决策

请确认 v1、override 或补问 / 修订。

### 12. Gate 与用户决策

- `gate_recommendation`：pass
- `confirmation_mode`：gate_pass
- `render_authorized`：true
