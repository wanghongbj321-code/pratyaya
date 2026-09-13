# 贡献指南

感谢你为 Pratyaya 提交改进。Pratyaya 是面向 WorkBuddy 的多画布工作坊专家包，贡献应保持设计文档、运行时契约和用户可见行为一致。

## 开始之前

- 先阅读 [README.md](./README.md)、[AGENTS.md](./AGENTS.md) 和相关设计/开发文档。
- 涉及状态、字段、Gate、模板或画布结构的改动，先在 Issue 或 PR 中说明设计影响。
- 不要提交真实用户材料、访问令牌、密钥或内部路径。

## 本地验证

安装测试依赖后运行：

```bash
python -m pytest
python scripts/check_contract_consistency.py
```

修改 SWOT 功能时，还应运行 SWOT 专项测试和正式/负例审计。浏览器级视觉检查只在发布要求或视觉结构变化时执行。

## 提交变更

- 保持现有目录结构和 Skill frontmatter 格式。
- 修改 `plugin.json` 版本或用户可见行为时，同步更新 `CHANGELOG.md`。
- 新增规则或状态字段时，同时添加正例和负例测试。
- PR 描述应说明用户行为变化、兼容性影响和验证结果。

WorkBuddy 升级包由项目维护者按官方发布规范制作和提交；贡献者无需在 PR 中提交发布 ZIP。
