"""legacy 迁移（v2.6 instance map / v2.9 default topic）测试（§8）。"""

from skills._engine import migration


def _legacy_state():
    return {
        "golden_circle": {
            "version": 2, "status": "rendered", "gate_recommendation": "pass",
            "render_authorized": True, "confirmation_mode": "gate_pass",
        },
        "hmw": {
            "version": 1, "status": "confirmed", "gate_recommendation": "pass",
            "render_authorized": True, "confirmation_mode": "gate_pass",
        },
    }


def test_is_legacy_single_canvas():
    full = {"version": 1, "status": "draft", "gate_recommendation": "pending",
            "render_authorized": False, "confirmation_mode": None}
    assert migration.is_legacy_single_canvas(full) is True
    assert migration.is_legacy_single_canvas({"status": "draft"}) is False
    assert migration.is_legacy_single_canvas("x") is False


def test_migrate_to_instance_map():
    migrated, report = migration.migrate_state_to_instance_map(_legacy_state())
    assert report["applied"] is True
    assert report["force_consent"] is True

    gc_default = migrated["golden_circle"]["default"]
    assert gc_default["slug"] == "default"
    assert gc_default["source_file"] == "modules/GC-default-v2.md"
    assert migrated["hmw"]["default"]["output_file"] == "output/hmw-canvas-default.html"


def test_migrate_noop():
    state = {"golden_circle": {"default": {"status": "rendered"}}}
    _, report = migration.migrate_state_to_instance_map(state)
    assert report["applied"] is False


def test_append_group_meta_migration():
    meta = migration.append_group_meta_migration(
        {}, {"applied": True, "force_consent": True, "details": {}},
        applied_at="t", actor="a",
    )
    assert meta["legacy_migrations"]["v2_6_0_instance_map"]["by"] == "a"


def test_append_group_meta_noop():
    meta = migration.append_group_meta_migration({}, {"applied": False, "details": {}})
    assert meta == {}


def test_migrate_v2_9_topic_state():
    state = {"project_slug": "p", "group_id": "g", "topic_slug": "old", "topic_name": "Old"}
    m = migration.migrate_v2_9_topic_state(state)
    assert m["topic_slug"] == "default"
    assert m["topic_name"] == "default"
    assert state["topic_slug"] == "old"  # 不改入参


def test_stage_default_topic(tmp_path):
    group = tmp_path / "g"
    group.mkdir()
    (group / "state.json").write_text('{"project_slug":"p","group_id":"g"}')
    result = migration.stage_default_topic(group)
    assert result["migrated_state"]["topic_slug"] == "default"
    assert (result["staging_dir"] / "topic_meta.json").exists()
    assert result["topic_meta"]["topic_slug"] == "default"
