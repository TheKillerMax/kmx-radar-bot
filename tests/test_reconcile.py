import json

import kmxradar.reconcile as reconcile


def _write(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(payload, str):
        path.write_text(payload, encoding="utf-8")
    else:
        path.write_text(json.dumps(payload), encoding="utf-8")


def test_reconcile_creates_publish_marker_for_valid_approved_package(tmp_path, monkeypatch):
    approved = tmp_path / "approved"
    data = tmp_path / "data"
    package = approved / "kmx-test"
    package.mkdir(parents=True)
    for idx in range(1, 7):
        (package / f"{idx:02d}.png").write_bytes(b"fake")

    manifest = {
        "schema_version": 1,
        "publication_id": "kmx-test",
        "ready_to_publish": True,
        "status": "VERIFICADO",
        "headline": "Titular",
        "caption": "Texto #KMXRadar #Tema #Lugar",
        "images": [{"path": f"{i:02d}.png", "alt_text": "Alt"} for i in range(1, 7)],
        "sources": [{"url": "https://example.org", "label": "Fuente"}],
    }
    _write(package / "publication.json", manifest)
    _write(package / "visual-qc.json", {
        "result": "pass",
        "file_count": 6,
        "files": [{"path": f"{i:02d}.png", "width": 1080, "height": 1350, "exists": True} for i in range(1, 7)],
    })
    _write(package / "visual-sources.json", {
        "assets": [{
            "source_url": "https://example.org/a.jpg",
            "direct_url": "https://example.org/a.jpg",
            "original_creator": "Creator",
            "license_or_permission": "CC BY 4.0",
        }]
    })
    _write(package / "visuals.json", {
        "sources": {"a": {"direct_url": "https://example.org/a.jpg"}},
        "slides": [
            {"file": f"{i:02d}.png", "photo": "a", "alt_text": "Alt"}
            for i in range(1, 7)
        ],
    })
    _write(data / "chatgpt_state.json", {"last_publication_id": "kmx-test", "phase": "publishing"})

    monkeypatch.setattr(reconcile, "APPROVED_DIR", approved)
    monkeypatch.setattr(reconcile, "CHATGPT_STATE_FILE", data / "chatgpt_state.json")

    assert reconcile.reconcile_publish_markers() == 1
    assert (package / ".ready").exists()


def test_reconcile_does_not_create_ready_without_qc(tmp_path, monkeypatch):
    approved = tmp_path / "approved"
    package = approved / "kmx-test"
    package.mkdir(parents=True)
    _write(package / "publication.json", {
        "schema_version": 1,
        "publication_id": "kmx-test",
        "ready_to_publish": True,
        "status": "VERIFICADO",
        "headline": "Titular",
        "caption": "Texto #KMXRadar #Tema #Lugar",
        "images": [],
        "sources": [{"url": "https://example.org", "label": "Fuente"}],
    })
    monkeypatch.setattr(reconcile, "APPROVED_DIR", approved)

    assert reconcile.reconcile_publish_markers() == 0
    assert not (package / ".ready").exists()


def test_reconcile_ignores_noncurrent_ready_candidate(tmp_path, monkeypatch):
    approved = tmp_path / "approved"
    data = tmp_path / "data"
    stale = approved / "stale-package"
    stale.mkdir(parents=True)
    _write(stale / "publication.json", {
        "schema_version": 1,
        "publication_id": "stale-package",
        "ready_to_publish": True,
        "status": "VERIFICADO",
        "headline": "Viejo",
        "caption": "Texto #KMXRadar #Tema #Lugar",
        "images": [],
        "sources": [{"url": "https://example.org", "label": "Fuente"}],
    })
    _write(data / "chatgpt_state.json", {
        "last_publication_id": "current-package",
        "phase": "publishing",
    })
    monkeypatch.setattr(reconcile, "APPROVED_DIR", approved)
    monkeypatch.setattr(reconcile, "CHATGPT_STATE_FILE", data / "chatgpt_state.json")

    assert reconcile.reconcile_publish_markers() == 0
    assert not (stale / ".ready").exists()
