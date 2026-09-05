"""audit_canvas_html.py 的全局页 Workflow BPMN 流程图（#workflow-flow）审计测试。

覆盖 MVL/MAAU 全局页共享契约：
- PASS：MAAU transcript-direct 三轨图、Phase 2 单轨 main 图；
- FAIL：缺 #workflow-flow、Start/End、三类任务、编号、合法 type、tracks、actor、
  dashed reflow、SVG/data 节点数、edges 引用、正交连接。
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT = REPO_ROOT / "skills" / "canvas-render" / "scripts" / "audit_canvas_html.py"
MAAU_FIXTURES = REPO_ROOT / "tests" / "fixtures" / "maau"
MVL_FIXTURES = REPO_ROOT / "tests" / "fixtures" / "e2e" / "mvl" / "output"
MVL_EXAMPLE = REPO_ROOT / "skills" / "canvas-render" / "examples" / "mvl-canvas" / "maau-global-canvas.html"
PYTHON = sys.executable

MAAU_HTML = MAAU_FIXTURES / "maau-global-canvas-retail-demo.html"
PHASE2_HTML = MVL_FIXTURES / "maau-global-canvas-phase2-demo.html"


def run_audit(html: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            PYTHON, str(AUDIT), str(html),
            "--type", "mvl",
            "--page-type", "global",
        ],
        capture_output=True,
        text=True,
    )


def copy_and_mutate(tmp_path: Path, old: str, new: str, *, source: Path = MAAU_HTML) -> Path:
    out = tmp_path / "canvas.html"
    text = source.read_text(encoding="utf-8")
    assert old in text, f"mutate target not found: {old}"
    out.write_text(text.replace(old, new), encoding="utf-8")
    return out


def read_canvas_data(html: Path) -> dict:
    text = html.read_text(encoding="utf-8")
    match = re.search(
        r'<script\s+type="application/json"\s+id="canvas-data">\s*(.*?)\s*</script>',
        text,
        re.DOTALL,
    )
    assert match, "missing canvas-data"
    return json.loads(match.group(1))


class TestWorkflowFlowPass:
    def test_maau_three_track_workflow_flow_passes(self) -> None:
        result = run_audit(MAAU_HTML)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "PASS" in result.stdout

    def test_phase2_single_main_track_workflow_flow_passes(self) -> None:
        result = run_audit(PHASE2_HTML)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "PASS" in result.stdout


class TestWorkflowReferenceTopology:
    def test_mvl_example_follows_suozhang_reference_workflow_topology(self) -> None:
        text = MVL_EXAMPLE.read_text(encoding="utf-8")
        data = read_canvas_data(MVL_EXAMPLE)
        workflow = data["workflow"]
        node_ids = {node["id"] for node in workflow["nodes"]}
        node_types = {node["type"] for node in workflow["nodes"]}
        labels = "\n".join(node["label"] for node in workflow["nodes"])

        assert {track["id"] for track in workflow["tracks"]} == {"A", "B", "C"}
        assert {
            "S1_TIMER_START", "A1", "A2", "A3", "A4", "A5", "G_GATEWAY",
            "TIMER_740", "A6", "MSG_KPI", "B1", "B2", "B3", "END_EVENT",
            "C1", "C2", "EXPERIENCE_STORE",
        } <= node_ids
        for semantic_label in (
            "A1", "A2", "A3", "A4", "A5", "A6", "B1", "B2", "B3", "C1", "C2", "经验库",
        ):
            assert semantic_label in labels
        assert {"timer", "message", "data_store"} <= node_types
        assert text.count('class="bpmn-sequence bpmn-reflow"') >= 2
        assert "7:40" in text
        assert "考核项下发" in text
        assert "次日循环" in text
        assert "经验反哺" in text


class TestWorkflowFlowFail:
    def test_missing_workflow_flow_id_fails(self, tmp_path: Path) -> None:
        out = copy_and_mutate(tmp_path, 'id="workflow-flow"', 'id="workflow-flow-removed"')
        result = run_audit(out)
        assert result.returncode != 0
        assert "MISSING_ID" in result.stdout

    def test_missing_start_event_fails(self, tmp_path: Path) -> None:
        out = copy_and_mutate(tmp_path, 'data-node-type="start"', 'data-node-type="gateway"')
        result = run_audit(out)
        assert result.returncode != 0
        assert "WORKFLOW_FLOW" in result.stdout
        assert "Start Event" in result.stdout

    def test_missing_end_event_fails(self, tmp_path: Path) -> None:
        out = copy_and_mutate(tmp_path, 'data-node-type="end"', 'data-node-type="gateway"')
        result = run_audit(out)
        assert result.returncode != 0
        assert "WORKFLOW_FLOW" in result.stdout
        assert "End Event" in result.stdout

    def test_missing_three_type_node_fails(self, tmp_path: Path) -> None:
        out = copy_and_mutate(tmp_path, '"type": "human_operation"', '"type": "agent_execution"')
        result = run_audit(out)
        assert result.returncode != 0
        assert "WORKFLOW_FLOW" in result.stdout
        assert "human_operation" in result.stdout

    def test_illegal_node_type_fails(self, tmp_path: Path) -> None:
        out = copy_and_mutate(tmp_path, '"type": "timer"', '"type": "schedule"')
        result = run_audit(out)
        assert result.returncode != 0
        assert "WORKFLOW_FLOW" in result.stdout
        assert "schedule" in result.stdout

    def test_svg_node_count_mismatch_fails(self, tmp_path: Path) -> None:
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
        out = copy_and_mutate(tmp_path, '"from": "w2", "to": "w3"', '"from": "w2", "to": "w-missing"')
        result = run_audit(out)
        assert result.returncode != 0
        assert "WORKFLOW_FLOW" in result.stdout
        assert "w-missing" in result.stdout

    def test_curve_sequence_flow_fails(self, tmp_path: Path) -> None:
        out = copy_and_mutate(tmp_path, 'd="M104 80 H144"', 'd="M104 80 C 120 60, 130 100, 144 80"')
        result = run_audit(out)
        assert result.returncode != 0
        assert "WORKFLOW_FLOW" in result.stdout
        assert "曲线命令" in result.stdout

    def test_missing_node_number_fails(self, tmp_path: Path) -> None:
        out = copy_and_mutate(
            tmp_path,
            '{ "id": "w0", "number": "01", "type": "start", "track": "A", "label": "业务员下店报数" }',
            '{ "id": "w0", "type": "start", "track": "A", "label": "业务员下店报数" }',
        )
        result = run_audit(out)
        assert result.returncode != 0
        assert "WORKFLOW_FLOW" in result.stdout
        assert "number 字段" in result.stdout

    def test_duplicate_node_number_fails(self, tmp_path: Path) -> None:
        out = copy_and_mutate(
            tmp_path,
            '{ "id": "w2", "number": "03", "type": "agent_execution", "track": "A", "actor": "ai", "label": "库存预测" }',
            '{ "id": "w2", "number": "01", "type": "agent_execution", "track": "A", "actor": "ai", "label": "库存预测" }',
        )
        result = run_audit(out)
        assert result.returncode != 0
        assert "WORKFLOW_FLOW" in result.stdout
        assert "number 必须唯一" in result.stdout

    def test_missing_tracks_fails(self, tmp_path: Path) -> None:
        out = copy_and_mutate(tmp_path, '"tracks": [', '"tracks_removed": [')
        result = run_audit(out)
        assert result.returncode != 0
        assert "WORKFLOW_FLOW" in result.stdout
        assert "tracks must be a non-empty array" in result.stdout

    def test_svg_track_mismatch_fails(self, tmp_path: Path) -> None:
        out = copy_and_mutate(tmp_path, 'class="bpmn-track" data-track="C"', 'class="bpmn-track" data-track="Z"')
        result = run_audit(out)
        assert result.returncode != 0
        assert "WORKFLOW_FLOW" in result.stdout
        assert "bpmn-track ids" in result.stdout

    def test_node_track_not_in_tracks_fails(self, tmp_path: Path) -> None:
        out = copy_and_mutate(
            tmp_path,
            '{ "id": "w8", "number": "09", "type": "end", "track": "C", "label": "补货完成且复盘" }',
            '{ "id": "w8", "number": "09", "type": "end", "track": "Z", "label": "补货完成且复盘" }',
        )
        result = run_audit(out)
        assert result.returncode != 0
        assert "WORKFLOW_FLOW" in result.stdout
        assert "track='Z'" in result.stdout

    def test_illegal_actor_fails(self, tmp_path: Path) -> None:
        out = copy_and_mutate(tmp_path, '"actor": "ai"', '"actor": "robot"')
        result = run_audit(out)
        assert result.returncode != 0
        assert "WORKFLOW_FLOW" in result.stdout
        assert "robot" in result.stdout

    def test_missing_actor_badge_fails(self, tmp_path: Path) -> None:
        out = copy_and_mutate(tmp_path, 'class="bpmn-actor" data-actor="ai"', 'class="bpmn-actor" data-actor="system"')
        result = run_audit(out)
        assert result.returncode != 0
        assert "WORKFLOW_FLOW" in result.stdout
        assert "actor 徽标" in result.stdout

    def test_dashed_edge_without_reflow_path_fails(self, tmp_path: Path) -> None:
        out = copy_and_mutate(tmp_path, 'class="bpmn-sequence bpmn-reflow"', 'class="bpmn-sequence"')
        result = run_audit(out)
        assert result.returncode != 0
        assert "WORKFLOW_FLOW" in result.stdout
        assert "bpmn-reflow" in result.stdout
