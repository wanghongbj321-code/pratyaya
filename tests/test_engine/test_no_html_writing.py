"""引擎不渲染 HTML 红线测试（§8.3 / §7.4 红线 1）。

锁定：`skills/_engine/` 下任何模块不得写 HTML（渲染只经 canvas-render Skill）。
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

ENGINE_DIR = REPO_ROOT / "skills" / "_engine"

_HTML_MARKERS = ("<!DOCTYPE html", "<html", "<canvas-data", "canvas.render")


def _engine_py_files() -> list[Path]:
    return sorted(ENGINE_DIR.glob("*.py"))


def test_engine_has_modules():
    assert _engine_py_files(), "skills/_engine 下应有 Python 模块"


def test_no_html_writing_in_engine():
    for f in _engine_py_files():
        src = f.read_text(encoding="utf-8")
        for marker in _HTML_MARKERS:
            assert marker not in src, f"{f.name} 出现 HTML 标记 {marker!r}（引擎不得渲染 HTML）"
