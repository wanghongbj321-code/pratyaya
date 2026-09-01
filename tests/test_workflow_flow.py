"""audit_canvas_html.py 的全局页 Workflow BPMN 流程图（#workflow-flow）审计测试。

覆盖设计方案（全局画布Workflow-BPMN流程图设计方案-2026-0901-2316.md）§7.1：
- PASS：完整拓扑（start / end / 三类节点 / SVG 节点数一致 / edges 引用有效）；
- FAIL：缺 #workflow-flow 锚点（GLOBAL_MAIN_IDS MISSING_ID）；
- FAIL：SVG 缺 Start / End Event；
- FAIL：canvas-data.workflow.nodes 缺三类节点之一；
- FAIL：SVG bpmn-node 数量与 nodes 数量不一致；
- FAIL：edges 引用不存在的 node id。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT = REPO_ROOT / "skills" / "canvas-render" / "scripts" / "audit_canvas_html.py"
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "maau"
PYTHON = sys.executable

MAAU_HTML = FIXTURES / "maau-global-canvas-retail-demo.html"
SLUG = "retail-demo"


def run_audit(html: Path) -> subprocess.CompletedProcess:
    # workflow-flow 是全局页契约（Phase 2 全局页与 MAAU 实例页通用）；
    # 不带 --instance，以纯 global 页模式运行，避免触发 MAAU 实例页的 --state 要求。
    return subprocess.run(
        [
            PYTHON, str(AUDIT), str(html),
            "--type", "mvl",
            "--page-type", "global",
        ],
        capture_output=True,
        text=True,
    )


def copy_and_mutate(tmp_path: Path, old: str, new: str) -> Path:
    out = tmp_path / "canvas.html"
    text = MAAU_HTML.read_text(encoding="utf-8")
    assert old in text, f"mutate target not found: {old}"
    out.write_text(text.replace(old, new), encoding="utf-8")
    return out


class TestWorkflowFlowPass:
    def test_full_workflow_flow_passes(self) -> None:
        """完整 #workflow-flow + 拓扑 → 全 PASS。"""
        result = run_audit(MAAU_HTML)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "PASS" in result.stdout


class TestWorkflowFlowFail:
    def test_missing_workflow_flow_id_fails(self, tmp_path: Path) -> None:
        """缺 #workflow-flow 锚点 → MISSING_ID。"""
        out = copy_and_mutate(tmp_path, 'id="workflow-flow"', 'id="workflow-flow-removed"')
        result = run_audit(out)
        assert result.returncode != 0
        assert "MISSING_ID" in result.stdout

    def test_missing_start_event_fails(self, tmp_path: Path) -> None:
        """SVG 缺 Start Event → WORKFLOW_FLOW。"""
        out = copy_and_mutate(tmp_path, 'data-node-type="start"', 'data-node-type="gateway"')
        result = run_audit(out)
        assert result.returncode != 0
        assert "WORKFLOW_FLOW" in result.stdout
        assert "Start Event" in result.stdout

    def test_missing_end_event_fails(self, tmp_path: Path) -> None:
        """SVG 缺 End Event → WORKFLOW_FLOW。"""
        out = copy_and_mutate(tmp_path, 'data-node-type="end"', 'data-node-type="gateway"')
        result = run_audit(out)
        assert result.returncode != 0
        assert "WORKFLOW_FLOW" in result.stdout
        assert "End Event" in result.stdout

    def test_missing_three_type_node_fails(self, tmp_path: Path) -> None:
        """canvas-data.workflow.nodes 缺 human_operation → WORKFLOW_FLOW。"""
        out = copy_and_mutate(tmp_path, '"type": "human_operation"', '"type": "agent_execution"')
        result = run_audit(out)
        assert result.returncode != 0
        assert "WORKFLOW_FLOW" in result.stdout
        assert "human_operation" in result.stdout

    def test_svg_node_count_mismatch_fails(self, tmp_path: Path) -> None:
        """SVG bpmn-node 数量与 nodes 数量不一致 → WORKFLOW_FLOW。"""
        out = copy_and_mutate(
            tmp_path,
            'class="bpmn-node" data-node-type="agent_execution" data-node-id="w2"',
            'class="removed-node" data-node-type="agent_execution" data-node-id="w2"',
        )
        result = run_audit(out)
        assert result.returncode != 0
        assert "WORKFLOW_FLOW" in result.stdout
        assert "bpmn-node 数量" in result.stdout

    def test_edge_references_missing_node_fails(self, tmp_path: Path) -> None:
        """edges 引用不存在的 node id → WORKFLOW_FLOW。"""
        out = copy_and_mutate(tmp_path, '"from": "w2", "to": "w3"', '"from": "w2", "to": "w-missing"')
        result = run_audit(out)
        assert result.returncode != 0
        assert "WORKFLOW_FLOW" in result.stdout
        assert "w-missing" in result.stdout

    def test_curve_sequence_flow_fails(self, tmp_path: Path) -> None:
        """Sequence Flow 含曲线命令（C）→ WORKFLOW_FLOW（连接线必须正交）。"""
        out = copy_and_mutate(tmp_path, 'd="M84 80 H120"', 'd="M84 80 C 100 60, 110 100, 120 80"')
        result = run_audit(out)
        assert result.returncode != 0
        assert "WORKFLOW_FLOW" in result.stdout
        assert "曲线命令" in result.stdout

    def test_missing_node_number_fails(self, tmp_path: Path) -> None:
        """canvas-data.workflow.nodes 缺 number 字段 → WORKFLOW_FLOW。"""
        out = copy_and_mutate(
            tmp_path,
            '{ "id": "w0", "number": "01", "type": "start", "label": "触发预测" }',
            '{ "id": "w0", "type": "start", "label": "触发预测" }',
        )
        result = run_audit(out)
        assert result.returncode != 0
        assert "WORKFLOW_FLOW" in result.stdout
        assert "number 字段" in result.stdout

    def test_duplicate_node_number_fails(self, tmp_path: Path) -> None:
        """canvas-data.workflow.nodes number 重复 → WORKFLOW_FLOW。"""
        out = copy_and_mutate(
            tmp_path,
            '{ "id": "w1", "number": "02", "type": "agent_execution", "label": "预测" }',
            '{ "id": "w1", "number": "01", "type": "agent_execution", "label": "预测" }',
        )
        result = run_audit(out)
        assert result.returncode != 0
        assert "WORKFLOW_FLOW" in result.stdout
        assert "number 必须唯一" in result.stdout
