"""导入边界与零副作用测试（§8.3）。

锁定：`skills/_engine/canvas_registry.py` 在干净环境（无 PYTHONPATH）下可独立导入、
零 IO 副作用、只依赖标准库，不引入 audit/render 等重模块。
"""

import ast
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

_STDLIB = set(getattr(sys, "stdlib_module_names", set())) | {"__future__"}


def _top_level_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    top: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                top.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                top.add(node.module.split(".")[0])
    return top


def _assert_stdlib_only(path: Path) -> None:
    top = _top_level_imports(path)
    non_stdlib = top - _STDLIB
    assert not non_stdlib, f"{path.name} 引入了非标准库: {sorted(non_stdlib)}"


def _clean_env() -> dict:
    return {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}


def test_clean_import_prints_canvas_count():
    code = "import skills._engine.canvas_registry as r; print(len(r.CANVASES))"
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(REPO_ROOT),
        env=_clean_env(),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "8"


def test_registry_only_stdlib():
    _assert_stdlib_only(REPO_ROOT / "skills" / "_engine" / "canvas_registry.py")


def test_state_only_stdlib():
    _assert_stdlib_only(REPO_ROOT / "skills" / "_engine" / "state.py")


def test_paths_only_stdlib():
    _assert_stdlib_only(REPO_ROOT / "skills" / "_engine" / "paths.py")
