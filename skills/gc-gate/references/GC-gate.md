# 黄金圈闸门策略

> 黄金圈（Golden Circle）画布的最低可用结论与常见 blocker。本文件由 `gc-gate` 在 Gate 评估时读取。

> 每条放行条件包含稳定 ID、分类（`information_integrity` / `business_risk`）和风险等级，供 Gate 报告与 override 审计引用。

## 必填 section

参见 `../../gc-distill/references/gc-spec.md` 中黄金圈确认包必填 section：

- WHY 三子字段：belief（领导信念） / purpose（存在目的） / mission（使命/愿景）
- HOW 三子字段：principles（做事原则） / differentiation（差异化） / methods（方法/流程）
- WHAT 三子字段：products（产品） / services（服务） / evidence（市场证据）
- 跨层一致性：WHY→HOW 推导链 / HOW→WHAT 推导链

## 必须形成的结论

三层 9 子字段有实质性内容（非占位）、跨层推导链已建立或显式标为缺口、WHY 有讨论证据支撑。

## 常见 blocker

- WHY 层全军覆没——讨论中从未出现任何信念、目的或使命的实质性讨论
- HOW 层的差异化与 WHY 信念之间无任何可辨识的逻辑关系（完全脱节）
- WHAT 层没有具体产品或服务（只写"产品 A""服务 B"等占位符）
- 跨层一致性第 6a 节未填写或全部标为"未建立"且缺口表未登记

## 评估要点

- WHY 三子字段是否全部有内容或显式标为缺口？
- HOW 三子字段是否全部有内容或显式标为缺口？
- WHAT 三子字段是否全部有内容或显式标为缺口？
- WHY→HOW 推导链是否自洽？讨论中有没有"HOW 的差异化源自 WHY 的信念"的证据？
- HOW→WHAT 推导链是否自洽？讨论中有没有"WHAT 体现了 HOW 的方法"的证据？
- WHY 核心理念是否来自实际讨论，还是占位话术？

## 放行条件

每条放行条件拥有稳定 ID、分类和风险等级，供 Gate 报告与 `override_audit.items` 引用。

| ID | 条件 | 分类 | 风险等级 | 来源 |
|---|---|---|---|---|
| `GC-GATE-01` | WHY 三子字段（belief / purpose / mission）全部有内容或显式标为缺口 | `information_integrity` | low | GC-why |
| `GC-GATE-02` | HOW 三子字段（principles / differentiation / methods）全部有内容或显式标为缺口 | `information_integrity` | low | GC-how |
| `GC-GATE-03` | WHAT 三子字段（products / services / evidence）全部有内容或显式标为缺口 | `information_integrity` | low | GC-what |
| `GC-GATE-04` | WHY→HOW 推导链自洽：HOW 的差异化与 WHY 的信念之间存在可辨识的逻辑关系 | `business_risk` | medium | GC-why, GC-how |
| `GC-GATE-05` | HOW→WHAT 推导链自洽：WHAT 的产品/服务与 HOW 的方法/原则之间存在可辨识的逻辑关系 | `business_risk` | medium | GC-how, GC-what |
| `GC-GATE-06` | WHY 的核心理念有讨论证据支撑（非占位话术如"让世界更美好"——除非讨论中真实阐述了具体内涵） | `information_integrity` | low | GC-why |

### 分类汇总

- **`information_integrity`**（4 条）：GC-GATE-01, GC-GATE-02, GC-GATE-03, GC-GATE-06。任一 FAIL 均不可 override；用户必须返回补问或修订。
- **`business_risk`**（2 条）：GC-GATE-04, GC-GATE-05。FAIL 时用户可显式 override，必须填写理由、影响确认、确认人与时间。

### 与 MVL 门禁的差异

GC 的跨层推导一致性（GC-GATE-04, GC-GATE-05）属于**可 override 的业务风险**——品牌定位的 WHY→HOW→WHAT 推导链在现实中有主观性，团队可以接受"当前推导不完美但方向对"的风险。M1 Gate 的 5 条全为 `information_integrity`，不具备这种灵活性。

### 详细说明

满足以下全部条件才可放行：

1. `GC-GATE-01`：WHY 三子字段全部有内容或显式标为缺口。
2. `GC-GATE-02`：HOW 三子字段全部有内容或显式标为缺口。
3. `GC-GATE-03`：WHAT 三子字段全部有内容或显式标为缺口。
4. `GC-GATE-04`：第 6a 节 WHY→HOW 推导链有结论且一致性判断不为空。
5. `GC-GATE-05`：第 6a 节 HOW→WHAT 推导链有结论且一致性判断不为空。
6. `GC-GATE-06`：WHY 信念/目的/使命中有至少一项来自讨论证据（非占位话术）。

## 来源 ID 约定

- `GC-why`、`GC-how`、`GC-what`：对应三层必填 section
- `GC-Gxx`：本画布缺口 ID（Gate 报告引用）
- `GC-Ixx`：本画布推断 ID
- `GC-Cxx`：本画布结论 ID
