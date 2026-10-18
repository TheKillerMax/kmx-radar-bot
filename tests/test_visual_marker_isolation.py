import json

import kmxradar.visual_phase as visual_phase


def test_stale_visual_marker_does_not_render_or_regress_current_state(tmp_path, monkeypatch):
    approved = tmp_path / "approved"
    obsolete = approved / "kmx-old"
    obsolete.mkdir(parents=True)
    (obsolete / ".visualize").write_text("stale", encoding="utf-8")
    state_file = tmp_path / "data" / "chatgpt_state.json"
    state_file.parent.mkdir(parents=True)
    original = {"last_publication_id": "kmx-current", "phase": "published"}
    state_file.write_text(json.dumps(original), encoding="utf-8")

    monkeypatch.setattr(visual_phase, "APPROVED_DIR", approved)
    monkeypatch.setattr(visual_phase, "STATE_FILE", state_file)
    monkeypatch.setattr(
        visual_phase, "build_space_visuals",
        lambda *args: (_ for _ in ()).throw(AssertionError("MUST NOT RENDER")),
    )
    assert visual_phase.prepare_visual_packages() == 0
    assert (obsolete / ".visualize").exists()
    assert json.loads(state_file.read_text(encoding="utf-8")) == original


def test_current_published_marker_is_skipped_without_regression(tmp_path, monkeypatch):
    approved = tmp_path / "approved"
    package = approved / "kmx-current"
    package.mkdir(parents=True)
    (package / ".visualize").write_text("stale", encoding="utf-8")
    state_file = tmp_path / "data" / "chatgpt_state.json"
    state_file.parent.mkdir(parents=True)
    original = {"last_publication_id": "kmx-current", "phase": "published"}
    state_file.write_text(json.dumps(original), encoding="utf-8")

    monkeypatch.setattr(visual_phase, "APPROVED_DIR", approved)
    monkeypatch.setattr(visual_phase, "STATE_FILE", state_file)
    assert visual_phase.prepare_visual_packages() == 0
    assert (package / ".visualize").exists()
    assert json.loads(state_file.read_text(encoding="utf-8")) == original
