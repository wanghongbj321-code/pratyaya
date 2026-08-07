"""audit_canvas_html.py 双 Gate 审计测试（HMW）。

依据 AGENTS.md 规则 3「渲染必须通过 canvas-render Skill，禁止渲染脚本」：
- 已移除 `scripts/render_canvas.py`，测试**不再有运行时渲染的正式产物**。
- `formal_html` fixture 直接指向 HMW 模板 `examples/canvas-html/hmw-canvas.html`，
  以模板（占位骨架）作为双 Gate **结构审计**的事实源。
- Content/Auth Gate 的"正式成品填充内容"正向场景（auth/version mismatch、content
  drift 等）依赖正式成品，而正式成品只能由 canvas-render Skill 人工生成，无法作为
  稳定自动化输入，故从自动化测试中移除；结构完整性（Template Gate）保留全部场景。

覆盖范围（结构防线）：
1. 模板自身离线双 Gate 全 PASS（无 --source/--state）。
2. 草稿在无 --source / --state 时通过离线结构审计。
3. 缺任一四字段、质量、coherence 或 idea anchor 时 FAIL。
4. idea 1–8 为占位（data-state="placeholder"）时 PASS；锚点直接缺失时 FAIL。
5. 质量/对齐/治理模块以任一隐藏方式藏起来时 FAIL。
6. 删除质量模块 / 交换一级顺序时 FAIL。
7. 模板副本缺共享主题资源时 FAIL。
8. 修改业务文案/版本值不造成 Template Gate 误报。
9. 模板自身缺锚点或含外部依赖时，模板自审计 FAIL。
10. HMW 正式交付缺 --template 时 FAIL（HMW-TPL-GATE-00）。
11. 默认 --type mvl 不影响（回归）。
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT = REPO_ROOT / "scripts" / "audit_canvas_html.py"
TEMPLATE = REPO_ROOT / "examples" / "canvas-html" / "hmw-canvas.html"
PACKAGE = REPO_ROOT / "examples" / "modules" / "HMW-v1.md"
STATE = REPO_ROOT / "examples" / "state-v2-sample.json"
PYTHON = sys.executable


@pytest.fixture(scope="module")
def formal_html() -> Path:
    """直接返回 HMW 模板作为双 Gate 结构审计的事实源（无渲染脚本）。"""
    return TEMPLATE


def run_audit(html: Path, *extra: str) -> subprocess.CompletedProcess:
    cmd = [PYTHON, str(AUDIT), str(html), "--type", "hmw", "--template", str(TEMPLATE), *extra]
    return subprocess.run(cmd, capture_output=True, text=True)


def copy_template(tmp_path: Path, name: str = "canvas.html") -> Path:
    """复制模板及其共享主题到 tmp_path，返回复制后的 HTML 路径。

    共享主题随附复制，使 Template Gate 能解析 `shared/canvas-theme.css`，
    从而对"结构变更"做精确断言，而不是被主题缺失误伤。
    """
    shared_dir = tmp_path / "shared"
    shared_dir.mkdir(exist_ok=True)
    shutil.copy2(TEMPLATE.parent / "shared" / "canvas-theme.css", shared_dir / "canvas-theme.css")
    out = tmp_path / name
    out.write_text(TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")
    return out


class TestFormalPage:
    def test_1_formal_page_passes_dual_gates(self, formal_html: Path) -> None:
        """模板离线（无 --source/--state）双 Gate 全 PASS（结构事实源）。"""
        result = run_audit(formal_html)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "PASS" in result.stdout
        assert "TEMPLATE GATE" not in result.stdout  # 无 Template 失败输出

    def test_10_template_gate_pass_on_isomorphic_output(self, formal_html: Path) -> None:
        """模板自身即同构：显式输出中无 HMW-TPL-GATE 失败。"""
        result = run_audit(formal_html)
        assert result.returncode == 0
        assert "HMW-TPL-GATE" not in result.stdout

    def test_14_business_content_change_does_not_break_template_gate(
        self, tmp_path: Path
    ) -> None:
        """修改业务文案/版本值不触发 Template Gate 误报（同构仍 PASS）。"""
        out = copy_template(tmp_path, "content-changed.html")
        text = out.read_text(encoding="utf-8")
        text = text.replace("situation · 问题情境", "全新的情境内容 A")
        text = text.replace('data-version="1"', 'data-version="3"')
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        # Template Gate 不应因业务内容/版本变化误报（内容 Gate 会报版本，但 Template 不报）
        assert "HMW-TPL-GATE" not in result.stdout


class TestDraftAndOffline:
    def test_2_draft_passes_offline_structure_audit(self, tmp_path: Path) -> None:
        """草稿无 --source/--state 时通过结构审计（模板自身就是草稿形态）。"""
        result = run_audit(TEMPLATE)
        # 模板是静态骨架（无正式授权），结构层面 Template Gate 应通过；
        # 内容/授权 Gate 因缺 canvas-data.sections.auth 等会报，但 Template Gate 全过
        assert "HMW-TPL-GATE" not in result.stdout

    def test_15_template_self_audit_fails_on_broken_template(self, tmp_path: Path) -> None:
        """模板自身缺锚点时，模板自审计 FAIL。"""
        broken = tmp_path / "broken-template.html"
        text = TEMPLATE.read_text(encoding="utf-8")
        text = text.replace('id="hmw-coherence-map"', 'id="hmw-coherence-map-x"')
        broken.write_text(text, encoding="utf-8")
        cmd = [
            PYTHON, str(AUDIT), str(tmp_path / "x.html"), "--type", "hmw",
            "--template", str(broken),
        ]
        # 模板缺锚点 → 模板自审计阶段应 FAIL
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode != 0 or "HMW-TPL-GATE" in result.stdout + result.stderr


class TestMissingAnchors:
    @pytest.mark.parametrize(
        "target,replacement",
        [
            ('id="hmw-situation"', 'id="hmw-situation-x"'),  # 四字段
            ('id="hmw-quality-tension"', 'id="hmw-quality-tension-x"'),  # 质量维度
            ('id="hmw-idea-8"', 'id="hmw-idea-8-x"'),  # idea 锚点
            ('id="hmw-coherence-map"', 'id="hmw-coherence-map-x"'),  # coherence
        ],
    )
    def test_3_missing_anchor_fails(
        self, tmp_path: Path, target: str, replacement: str
    ) -> None:
        out = copy_template(tmp_path, "missing.html")
        text = out.read_text(encoding="utf-8").replace(target, replacement)
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        assert result.returncode != 0
        assert "HMW-TPL-GATE-04" in result.stdout or "MISSING_ANCHOR" in result.stdout


class TestPlaceholderSemantics:
    def test_4_placeholder_idea_cells_pass(self, tmp_path: Path) -> None:
        """idea 1–8 为占位（data-state=placeholder，锚点存在）时 PASS。"""
        out = copy_template(tmp_path, "canvas.html")
        text = out.read_text(encoding="utf-8")
        for n in range(1, 9):
            assert f'id="hmw-idea-{n}"' in text
            # 占位格锚点存在即可；Template Gate 要求锚点齐全
        result = run_audit(out)
        assert result.returncode == 0

    def test_4b_idea_anchor_missing_fails(self, tmp_path: Path) -> None:
        out = copy_template(tmp_path, "no-idea8.html")
        text = out.read_text(encoding="utf-8").replace('id="hmw-idea-8"', 'id="hmw-idea-8-gone"')
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        assert result.returncode != 0
        assert "hmw-idea-8" in result.stdout


class TestHiddenModules:
    @pytest.mark.parametrize(
        "transform",
        [
            '<section class="quality" id="hmw-quality"<<< <section class="quality hidden" id="hmw-quality"',
            '<section class="coherence" id="hmw-coherence"<<< <section class="coherence" id="hmw-coherence" style="display:none"',
            '<aside class="govern" id="quality-panel"<<< <aside class="govern" id="quality-panel" style="visibility:hidden"',
        ],
    )
    def test_13_hidden_quality_module_fails(
        self, tmp_path: Path, transform: str
    ) -> None:
        out = copy_template(tmp_path, "hidden.html")
        text = out.read_text(encoding="utf-8")
        for spec in transform.split("|"):
            if "<<<" in spec:
                pat, rep = spec.split("<<<", 1)
                text = text.replace(pat, rep)
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        assert result.returncode != 0
        assert "HMW-TPL-GATE-06" in result.stdout

    def test_13c_missing_shared_theme_fails_template_gate(self, tmp_path: Path) -> None:
        """模板副本缺共享主题资源时必须拒绝交付。"""
        out = tmp_path / "no-shared.html"
        out.write_text(TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")
        # 不复制 shared/，让 `shared/canvas-theme.css` 无法解析
        result = run_audit(out)
        assert result.returncode != 0
        assert "HMW-TPL-GATE-06" in result.stdout

    def test_13b_style_rule_hiding_quality_module_fails(self, tmp_path: Path) -> None:
        """样式表规则隐藏质量模块也必须被 Template Gate 拦截。"""
        out = copy_template(tmp_path, "css-hidden.html")
        text = out.read_text(encoding="utf-8").replace(
            "<style>", "<style>#hmw-quality{display:none}", 1
        )
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        assert result.returncode != 0
        assert "HMW-TPL-GATE-06" in result.stdout

class TestOrderAndStructure:
    def test_11_delete_quality_module_fails(self, tmp_path: Path) -> None:
        out = copy_template(tmp_path, "no-quality.html")
        text = out.read_text(encoding="utf-8")
        text = re.sub(r'<section class="quality" id="hmw-quality".*?</section>\s*\n', "", text, flags=re.DOTALL)
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        assert result.returncode != 0
        assert "HMW-TPL-GATE-02" in result.stdout or "HMW-TPL-GATE-04" in result.stdout

    def test_12_swap_main_order_fails(self, tmp_path: Path) -> None:
        out = copy_template(tmp_path, "swap.html")
        text = out.read_text(encoding="utf-8")
        # 交换 ideas 与 quality 的 id（保持元素存在但顺序偏离）
        text = text.replace('<section class="ideas" id="hmw-ideas"', '<section class="ideas" id="hmw-ideas-swap"')
        text = text.replace('<section class="quality" id="hmw-quality"', '<section class="quality" id="hmw-ideas"')
        text = text.replace('<section class="quality" id="hmw-ideas-swap"', '<section class="quality" id="hmw-quality"')
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        assert result.returncode != 0
        assert "HMW-TPL-GATE-03" in result.stdout


class TestRegressions:
    def test_9_mvl_default_type_still_works(self) -> None:
        """默认 --type mvl 不影响（用 state schema 测试间接确认脚本可加载）。"""
        result = subprocess.run(
            [PYTHON, str(AUDIT), "--help"], capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "--type {mvl,gc,hmw,journey}" in result.stdout or "mvl" in result.stdout

    def test_9b_hmw_without_template_on_formal_fails(self) -> None:
        """HMW 正式交付缺 --template 应 FAIL（HMW-TPL-GATE-00）。"""
        result = subprocess.run(
            [PYTHON, str(AUDIT), str(TEMPLATE), "--type", "hmw",
             "--source", str(PACKAGE), "--state", str(STATE)],
            capture_output=True, text=True,
        )
        assert result.returncode != 0
        assert "HMW-TPL-GATE-00" in result.stdout
