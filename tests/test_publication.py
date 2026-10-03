import json

from kmxradar.publication import _validate_manifest


def test_valid_publication_package(tmp_path):
    (tmp_path / "01.jpg").write_bytes(b"fake")
    manifest = {
        "schema_version": 1,
        "publication_id": "kmx-test",
        "ready_to_publish": True,
        "headline": "Titular de prueba",
        "caption": "Texto de prueba",
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
