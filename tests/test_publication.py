import json

from kmxradar.publication import _validate_manifest


def test_valid_publication_package(tmp_path):
    (tmp_path / "01.jpg").write_bytes(b"fake")
    manifest = {
        "schema_version": 1,
        "publication_id": "kmx-test",
        "ready_to_publish": True,
        "headline": "Titular de prueba",
        "caption": "Texto de prueba #KMXRadar #Prueba #Noticias",
        "sources": [{"url": "https://example.org/source", "label": "Fuente"}],
        "images": [{"path": "01.jpg", "alt_text": "Imagen de prueba"}],
    }
    assert _validate_manifest(tmp_path, manifest) == []


def test_rejects_missing_source_and_image(tmp_path):
    manifest = {
        "schema_version": 1,
        "publication_id": "kmx-test",
        "ready_to_publish": True,
        "headline": "Titular de prueba",
        "caption": "Texto de prueba",
        "sources": [],
        "images": [{"path": "missing.jpg"}],
    }
    errors = _validate_manifest(tmp_path, manifest)
    assert any("missing image" in x for x in errors)
    assert any("source" in x for x in errors)


def test_rejects_too_many_hashtags(tmp_path):
    (tmp_path / "01.jpg").write_bytes(b"fake")
    manifest = {
        "schema_version": 1,
        "publication_id": "kmx-test",
        "ready_to_publish": True,
        "headline": "Titular de prueba",
        "caption": "Texto #KMXRadar #Uno #Dos #Tres #Cuatro #Cinco",
        "sources": [{"url": "https://example.org/source", "label": "Fuente"}],
        "images": [{"path": "01.jpg", "alt_text": "Imagen de prueba"}],
    }
    errors = _validate_manifest(tmp_path, manifest)
    assert any("at most 5 hashtags" in x for x in errors)



def test_publish_auth_190_preserves_ready_and_sets_retry(tmp_path, monkeypatch):
    import kmxradar.publication as publication
    from kmxradar.instagram import InstagramAPIError

    approved = tmp_path / "approved"
    package = approved / "kmx-current"
    package.mkdir(parents=True)
    (package / ".ready").write_text("ok", encoding="utf-8")
    (package / "01.jpg").write_bytes(b"fake")
    manifest = {
        "schema_version": 1, "publication_id": "kmx-current",
        "ready_to_publish": True, "status": "VERIFICADO",
        "headline": "Titular", "caption": "Texto #KMXRadar #Tema #Lugar",
        "sources": [{"url": "https://example.org", "label": "Fuente"}],
        "images": [{"path": "01.jpg", "alt_text": "Texto alternativo"}],
    }
    (package / "publication.json").write_text(json.dumps(manifest), encoding="utf-8")
    data = tmp_path / "data"
    data.mkdir()
    (data / "chatgpt_state.json").write_text(
        json.dumps({
            "phase": "publishing",
            "last_publication_id": "kmx-current",
            "last_media_id": "historical-media",
            "published_at": "2026-10-08T00:00:00Z",
        }),
        encoding="utf-8",
    )
    monkeypatch.setattr(publication, "APPROVED_DIR", approved)
    monkeypatch.setattr(publication, "PUBLISHED_FILE", data / "published.json")
    monkeypatch.setattr(publication, "STATE_FILE", data / "state.json")
    monkeypatch.setattr(publication, "CHATGPT_STATE_FILE", data / "chatgpt_state.json")
    monkeypatch.setattr(publication, "load_yaml", lambda _: {"enabled": True})
    monkeypatch.setattr(publication, "editorial_config", lambda: {
        "runtime": {"max_posts_per_day": 8, "min_minutes_between_posts": 75}
    })
    monkeypatch.setattr(publication, "_validate_before_publishing", lambda *args: None)
    monkeypatch.setattr(publication, "publish_package", lambda *args: (_ for _ in ()).throw(
        InstagramAPIError("security checkpoint", code=190)
    ))
    assert publication.publish_ready_packages() == 0
    state = json.loads((data / "chatgpt_state.json").read_text(encoding="utf-8"))
    assert state["phase"] == "publish_error"
    assert state["external_error_code"] == "instagram_auth_190"
    assert state["last_media_id"] is None
    assert state["published_at"] is None
    assert state["next_publish_retry_at"]
    assert (package / ".ready").exists()
    assert not (package / ".published.json").exists()


def test_auth_retry_pending_skips_until_deadline(monkeypatch):
    import os
    from datetime import datetime, timedelta, timezone
    import kmxradar.publication as publication

    monkeypatch.setenv("GITHUB_EVENT_NAME", "schedule")
    future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    state = {
        "phase": "publish_error",
        "external_error_code": "instagram_auth_190",
        "next_publish_retry_at": future,
    }
    assert publication._auth_retry_pending(state)
    monkeypatch.setenv("GITHUB_EVENT_NAME", "workflow_dispatch")
    assert not publication._auth_retry_pending(state)


def test_ready_without_active_id_remains_unpublished(tmp_path, monkeypatch):
    import kmxradar.publication as publication
    approved = tmp_path / "approved"
    package = approved / "kmx-old"
    package.mkdir(parents=True)
    (package / ".ready").write_text("old", encoding="utf-8")
    state_file = tmp_path / "chatgpt_state.json"
    state_file.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(publication, "APPROVED_DIR", approved)
    monkeypatch.setattr(publication, "CHATGPT_STATE_FILE", state_file)
    monkeypatch.setattr(publication, "load_yaml", lambda _: {"enabled": True})
    monkeypatch.setattr(publication, "publish_package",
                        lambda *args: (_ for _ in ()).throw(AssertionError("MUST NOT PUBLISH")))
    assert publication.publish_ready_packages() == 0
    assert (package / ".ready").exists()


def test_published_phase_cannot_republish_lingering_ready(tmp_path, monkeypatch):
    import kmxradar.publication as publication
    approved = tmp_path / "approved"
    package = approved / "kmx-done"
    package.mkdir(parents=True)
    (package / ".ready").write_text("old", encoding="utf-8")
    state_file = tmp_path / "chatgpt_state.json"
    state_file.write_text(json.dumps({
        "last_publication_id": "kmx-done", "phase": "published",
    }), encoding="utf-8")
    monkeypatch.setattr(publication, "APPROVED_DIR", approved)
    monkeypatch.setattr(publication, "CHATGPT_STATE_FILE", state_file)
    monkeypatch.setattr(publication, "load_yaml", lambda _: {"enabled": True})
    monkeypatch.setattr(publication, "publish_package",
                        lambda *args: (_ for _ in ()).throw(AssertionError("MUST NOT PUBLISH")))
    assert publication.publish_ready_packages() == 0
    assert (package / ".ready").exists()


def test_publisher_rejects_ready_without_visual_qc(tmp_path, monkeypatch):
    import pytest
    import kmxradar.publication as publication
    approved = tmp_path / "approved"
    package = approved / "kmx-current"
    package.mkdir(parents=True)
    (package / ".ready").write_text("ok", encoding="utf-8")
    (package / "01.jpg").write_bytes(b"fake")
    manifest = {
        "schema_version": 1, "publication_id": "kmx-current",
        "ready_to_publish": True, "status": "VERIFICADO",
        "headline": "Titular", "caption": "Texto #KMXRadar #Tema #Lugar",
        "sources": [{"url": "https://example.org", "label": "Fuente"}],
        "images": [{"path": "01.jpg", "alt_text": "Texto alternativo"}],
    }
    (package / "publication.json").write_text(json.dumps(manifest), encoding="utf-8")
    data = tmp_path / "data"
    data.mkdir()
    (data / "chatgpt_state.json").write_text(
        json.dumps({"phase": "publishing", "last_publication_id": "kmx-current"}),
        encoding="utf-8",
    )
    monkeypatch.setattr(publication, "APPROVED_DIR", approved)
    monkeypatch.setattr(publication, "PUBLISHED_FILE", data / "published.json")
    monkeypatch.setattr(publication, "STATE_FILE", data / "state.json")
    monkeypatch.setattr(publication, "CHATGPT_STATE_FILE", data / "chatgpt_state.json")
    monkeypatch.setattr(publication, "load_yaml", lambda _: {"enabled": True})
    monkeypatch.setattr(publication, "editorial_config", lambda: {
        "runtime": {"max_posts_per_day": 8, "min_minutes_between_posts": 75}
    })
    monkeypatch.setattr(publication, "publish_package",
                        lambda *args: (_ for _ in ()).throw(AssertionError("MUST NOT PUBLISH")))
    with pytest.raises(RuntimeError, match="visual-qc.json missing"):
        publication.publish_ready_packages()
    state = json.loads((data / "chatgpt_state.json").read_text(encoding="utf-8"))
    assert state["phase"] == "publish_blocked"
    assert (package / ".ready").exists()
