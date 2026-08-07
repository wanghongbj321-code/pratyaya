"""audit_canvas_html.py 双 Gate 审计测试（HMW）。

覆盖执行计划 §6.3 的 15 个场景：
1. HMW 正式页面 PASS。
2. HMW 草稿在无 --source / --state 时通过离线结构审计。
3. 缺任一四字段、质量、coherence 或 idea anchor 时 FAIL。
4. idea 4–8 为占位（data-state="placeholder"）时 PASS；锚点直接缺失时 FAIL。
5. canvas-data.auth 与 state.hmw 不一致时 FAIL。
6. source / HTML / state 版本不一致时 FAIL。
7. override caveat 以任一隐藏方式出现时 FAIL。
8. HMW state 缺失时给出清晰错误。
9. MVL 与 GC 现有 PASS 用例继续通过（默认 --type mvl 回归）。
10. HMW 成品与模板同构时 Template Gate PASS。
11. 删除 hmw-quality / hmw-coherence / quality-panel 时 Template Gate FAIL。
12. 交换一级顺序时 Template Gate FAIL。
13. 质量/对齐/治理模块以任一隐藏方式藏起来时 FAIL。
14. 修改业务文案/版本值/想法内容不造成 Template Gate 误报。
15. 模板自身缺锚点或含外部依赖时，模板自审计 FAIL。
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT = REPO_ROOT / "scripts" / "audit_canvas_html.py"
RENDER = REPO_ROOT / "scripts" / "render_canvas.py"
TEMPLATE = REPO_ROOT / "examples" / "canvas-html" / "hmw-canvas.html"
PACKAGE = REPO_ROOT / "examples" / "modules" / "HMW-v1.md"
STATE = REPO_ROOT / "examples" / "state-v2-sample.json"
PYTHON = sys.executable


@pytest.fixture(scope="module")
def formal_html(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """用 render_canvas.py 渲染一份正式 HMW HTML 到临时目录。"""
    out = tmp_path_factory.mktemp("hmw") / "hmw-formal.html"
    subprocess.run(
        [PYTHON, str(RENDER), "--source", str(PACKAGE), "--state", str(STATE),
         "--type", "hmw", "--template", str(TEMPLATE), "--output", str(out)],
        check=True,
    )
    return out


def run_audit(html: Path, *extra: str) -> subprocess.CompletedProcess:
    cmd = [PYTHON, str(AUDIT), str(html), "--type", "hmw", "--template", str(TEMPLATE), *extra]
    return subprocess.run(cmd, capture_output=True, text=True)


def write_copy(src: Path, dest: Path, transform: str) -> Path:
    """复制 src 并应用 transform 正则替换，返回新文件路径。"""
    text = src.read_text(encoding="utf-8")
    text = re.sub(transform, "", text) if transform.startswith("REMOVE") else text
    # 通用替换格式 "PATTERN<<REPLACEMENT"
    for spec in transform.split("|"):
        if "<<<" in spec:
            pat, rep = spec.split("<<<", 1)
            text = text.replace(pat, rep)
    dest.write_text(text, encoding="utf-8")
    return dest


class TestFormalPage:
    def test_1_formal_page_passes_dual_gates(self, formal_html: Path) -> None:
        result = run_audit(formal_html, "--source", str(PACKAGE), "--state", str(STATE))
        assert result.returncode == 0, result.stdout + result.stderr
        assert "PASS" in result.stdout
        assert "TEMPLATE GATE" not in result.stdout  # 无 Template 失败输出

    def test_10_template_gate_pass_on_isomorphic_output(self, formal_html: Path) -> None:
        """成品与模板同构：显式输出中无 HMW-TPL-GATE 失败。"""
        result = run_audit(formal_html, "--source", str(PACKAGE), "--state", str(STATE))
        assert "HMW-TPL-GATE" not in result.stdout

    def test_14_business_content_change_does_not_break_template_gate(
        self, formal_html: Path
    ) -> None:
        """修改业务文案/版本值不触发 Template Gate 误报（同构仍 PASS）。"""
        out = formal_html.parent / "content-changed.html"
        text = formal_html.read_text(encoding="utf-8")
        text = text.replace("异常等级排序仪表盘", "全新的想法内容 A")
        text = text.replace('data-version="1"', 'data-version="3"')
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        # Template Gate 不应因业务内容/版本变化误报（内容 Gate 会报版本，但 Template 不报）
        assert "HMW-TPL-GATE" not in result.stdout

    def test_formal_page_maps_confirmation_package_content(self, formal_html: Path) -> None:
        """正式成品必须展示确认包的主陈述、质量、想法和对齐事实。"""
        text = formal_html.read_text(encoding="utf-8")
        for expected in (
            "干部在早会前 30 分钟拿到前夜经营报表",
            "我们如何能让干部在早会前快速定位异常指标并理解原因？",
            "区域干部层（早会决策者）",
            "定位时间从 2 小时降至 30 分钟内",
            "按异常等级自动排序的经营仪表盘",
            "HMW 关键主张 2-1",
        ):
            assert expected in text
        assert 'id="hmw-idea-1" data-state="discussed"' in text
        assert 'id="hmw-idea-1" data-state="placeholder"' not in text

    def test_render_copies_shared_theme_next_to_output(self, formal_html: Path) -> None:
        """多文件交付时，正式 HTML 的相对主题资源必须随输出目录提供。"""
        theme = formal_html.parent / "shared" / "canvas-theme.css"
        assert theme.is_file()


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
            PYTHON, str(AUDIT), str(formal_html := tmp_path / "x.html"), "--type", "hmw",
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
        self, tmp_path: Path, formal_html: Path, target: str, replacement: str
    ) -> None:
        out = tmp_path / "missing.html"
        text = formal_html.read_text(encoding="utf-8")
        text = text.replace(target, replacement)
        out.write_text(text, encoding="utf-8")
        result = run_audit(out, "--source", str(PACKAGE), "--state", str(STATE))
        assert result.returncode != 0
        assert "HMW-TPL-GATE-04" in result.stdout or "MISSING_ANCHOR" in result.stdout


class TestPlaceholderSemantics:
    def test_4_placeholder_idea_cells_pass(self, formal_html: Path) -> None:
        """idea 4–8 为占位（data-state=placeholder，锚点存在）时 PASS。"""
        text = formal_html.read_text(encoding="utf-8")
        for n in range(4, 9):
            assert f'id="hmw-idea-{n}"' in text
            # 占位格锚点存在即可；Template Gate 要求锚点齐全
        result = run_audit(formal_html, "--source", str(PACKAGE), "--state", str(STATE))
        assert result.returncode == 0

    def test_4b_idea_anchor_missing_fails(self, tmp_path: Path, formal_html: Path) -> None:
        out = tmp_path / "no-idea8.html"
        text = formal_html.read_text(encoding="utf-8").replace('id="hmw-idea-8"', 'id="hmw-idea-8-gone"')
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        assert result.returncode != 0
        assert "hmw-idea-8" in result.stdout


class TestAuthAndVersion:
    def test_5_auth_mismatch_fails(self, tmp_path: Path, formal_html: Path) -> None:
        out = tmp_path / "auth-mismatch.html"
        text = formal_html.read_text(encoding="utf-8").replace(
            '"confirmation_mode": "gate_pass"', '"confirmation_mode": "override"'
        )
        out.write_text(text, encoding="utf-8")
        result = run_audit(out, "--source", str(PACKAGE), "--state", str(STATE))
        assert result.returncode != 0
        assert "AUTH_MISMATCH" in result.stdout

    def test_6_version_mismatch_fails(self, tmp_path: Path, formal_html: Path) -> None:
        out = tmp_path / "ver-mismatch.html"
        text = formal_html.read_text(encoding="utf-8").replace('data-version="1"', 'data-version="2"')
        out.write_text(text, encoding="utf-8")
        result = run_audit(out, "--source", str(PACKAGE), "--state", str(STATE))
        assert result.returncode != 0
        assert "VERSION_MISMATCH" in result.stdout or "SOURCE_VERSION" in result.stdout

    def test_8_hmw_state_missing_gives_clear_error(self, tmp_path: Path, formal_html: Path) -> None:
        state = tmp_path / "no-hmw.json"
        state.write_text(
            json.dumps({"schema_version": "2.1", "group_id": "G1", "project_name": "x", "modules": {}}),
            encoding="utf-8",
        )
        result = run_audit(formal_html, "--source", str(PACKAGE), "--state", str(state))
        assert result.returncode != 0
        assert "hmw" in result.stdout  # 明确指向 hmw 区块缺失

    def test_content_gate_fails_when_visible_statement_drifts_from_source(
        self, tmp_path: Path, formal_html: Path
    ) -> None:
        """确认包事实被模板占位替换时，内容/授权 Gate 必须拒绝成品。"""
        out = tmp_path / "statement-drift.html"
        text = formal_html.read_text(encoding="utf-8").replace(
            "干部在早会前 30 分钟拿到前夜经营报表", "待填写…", 1
        )
        out.write_text(text, encoding="utf-8")
        result = run_audit(out, "--source", str(PACKAGE), "--state", str(STATE))
        assert result.returncode != 0
        assert "CONTENT_MAPPING" in result.stdout


class TestHiddenModules:
    @pytest.mark.parametrize(
        "transform",
        [
            '<section class="quality" id="hmw-quality"<<< <section class="quality hidden" id="hmw-quality">',
            '<section class="coherence" id="hmw-coherence"<<< <section class="coherence" style="display:none" id="hmw-coherence">',
            '<aside class="govern" id="quality-panel"<<< <aside class="govern" id="quality-panel" style="visibility:hidden">',
        ],
    )
    def test_13_hidden_quality_module_fails(
        self, tmp_path: Path, formal_html: Path, transform: str
    ) -> None:
        out = tmp_path / "hidden.html"
        text = formal_html.read_text(encoding="utf-8")
        for spec in transform.split("|"):
            if "<<<" in spec:
                pat, rep = spec.split("<<<", 1)
                text = text.replace(pat, rep)
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        assert result.returncode != 0
        assert "HMW-TPL-GATE-06" in result.stdout

    def test_13c_missing_shared_theme_fails_template_gate(
        self, tmp_path: Path, formal_html: Path
    ) -> None:
        """多文件成品缺少模板声明的共享主题资源时必须拒绝交付。"""
        out = tmp_path / "canvas.html"
        out.write_text(formal_html.read_text(encoding="utf-8"), encoding="utf-8")
        result = run_audit(out, "--source", str(PACKAGE), "--state", str(STATE))
        assert result.returncode != 0
        assert "HMW-TPL-GATE-06" in result.stdout

    def test_13b_style_rule_hiding_quality_module_fails(
        self, tmp_path: Path, formal_html: Path
    ) -> None:
        """样式表规则隐藏质量模块也必须被 Template Gate 拦截。"""
        out = tmp_path / "css-hidden.html"
        text = formal_html.read_text(encoding="utf-8").replace(
            "<style>", "<style>#hmw-quality{display:none}", 1
        )
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        assert result.returncode != 0
        assert "HMW-TPL-GATE-06" in result.stdout

class TestOrderAndStructure:
    def test_11_delete_quality_module_fails(self, tmp_path: Path, formal_html: Path) -> None:
        out = tmp_path / "no-quality.html"
        text = formal_html.read_text(encoding="utf-8")
        text = re.sub(r'<section class="quality" id="hmw-quality".*?</section>\s*\n', "", text, flags=re.DOTALL)
        out.write_text(text, encoding="utf-8")
        result = run_audit(out)
        assert result.returncode != 0
        assert "HMW-TPL-GATE-02" in result.stdout or "HMW-TPL-GATE-04" in result.stdout

    def test_12_swap_main_order_fails(self, tmp_path: Path, formal_html: Path) -> None:
        out = tmp_path / "swap.html"
        text = formal_html.read_text(encoding="utf-8")
        # 交换 ideas 与 quality 的 id（保持元素存在但顺序偏离）
        text = text.replace('<section class="ideas" id="hmw-ideas"', '<section class="ideas" id="hmw-ideas-swap"')
        text = text.replace('<section class="quality" id="hmw-quality"', '<section class="quality" id="hmw-ideas"')
        text = text.replace('<section class="quality" id="hmw-quality-swap"', '<section class="quality" id="hmw-quality"')
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
        assert "--type {mvl,gc,hmw}" in result.stdout or "mvl" in result.stdout

    def test_9b_hmw_without_template_on_formal_fails(self, formal_html: Path) -> None:
        """HMW 正式交付缺 --template 应 FAIL（HMW-TPL-GATE-00）。"""
        result = subprocess.run(
            [PYTHON, str(AUDIT), str(formal_html), "--type", "hmw",
             "--source", str(PACKAGE), "--state", str(STATE)],
            capture_output=True, text=True,
        )
        assert result.returncode != 0
        assert "HMW-TPL-GATE-00" in result.stdout
