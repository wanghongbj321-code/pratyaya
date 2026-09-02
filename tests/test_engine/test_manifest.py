"""group / project manifest 自重建测试（§8）。"""

from skills._engine import manifest


def test_summarize_topic_state():
    state = {
        "project_slug": "p", "group_id": "g", "topic_slug": "t", "topic_name": "T",
        "modules": {
            "M1": {"version": 1, "status": "rendered", "gate_recommendation": "pass",
                   "confirmation_mode": "gate_pass"},
        },
        "golden_circle": {
            "s": {"version": 2, "status": "confirmed", "gate_recommendation": "pending",
                  "confirmation_mode": None},
        },
    }
    s = manifest.summarize_topic_state(state)
    assert s["topic_slug"] == "t"
    assert s["modules"]["M1"]["status"] == "rendered"
    assert s["golden_circle"]["s"]["version"] == 2


def test_derive_group_manifest():
    m = manifest.derive_group_manifest("g", {"t1": {"topic_slug": "t1"}})
    assert m["group_id"] == "g"
    assert "t1" in m["topics"]


def test_derive_project_manifest():
    m = manifest.derive_project_manifest("p", {"g": {"t": {"topic_slug": "t"}}})
    assert m["project_slug"] == "p"
    assert "t" in m["groups"]["g"]["topics"]


def test_rebuild_group_manifest(tmp_path):
    group = tmp_path / "g"
    (group / "t1").mkdir(parents=True)
    (group / "t1" / "state.json").write_text('{"topic_slug":"t1"}')
    m = manifest.rebuild_group_manifest(group)
    assert m["group_id"] == "g"
    assert "t1" in m["topics"]
    assert (group / "manifest.json").exists()


def test_rebuild_project_manifest(tmp_path):
    proj = tmp_path / "p"
    (proj / "g" / "t").mkdir(parents=True)
    (proj / "g" / "t" / "state.json").write_text('{"topic_slug":"t"}')
    m = manifest.rebuild_project_manifest(proj)
    assert m["project_slug"] == "p"
    assert "t" in m["groups"]["g"]["topics"]
    assert (proj / "manifest.json").exists()
