"""Pratyaya 运行期脚本包。

此 __init__.py 将 scripts/ 钉为常规 Python 包（区别于命名空间包），
使 `from scripts.engine import ...` 等包内导入可稳定解析，避免命名空间包
跨 sys.path 合并同名目录的歧义。

engine/ 为共享画布引擎（规则判定层）；check_contract_consistency.py 与
contract_consistency/ 为开发期契约对账工具，不随专家包分发。
"""
