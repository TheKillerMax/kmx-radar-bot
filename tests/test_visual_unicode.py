import json
import unicodedata

import pytest

from kmxradar.visual_phase import _validate_visual_spec


def _package(tmp_path, title="Misión en órbita"):
    publication = {
        "headline": title,
        "caption": "La misión continúa en órbita.",
        "images": [{"alt_text": "La misión continúa."}],
    }
    (tmp_path / "publication.json").write_text(
        json.dumps(publication, ensure_ascii=False),
        encoding="utf-8",
    )
    rights = [{
        "key": "photo",
        "source_url": "https://example.org/photo",
        "direct_url": "https://example.org/photo.jpg",
        "original_creator": "Autor",
        "license_or_permission": "CC BY 4.0",
    }]
    visuals = {
        "sources": {"photo": {"direct_url": "https://example.org/photo.jpg"}},
        "slides": [
            {
                "file": f"{i:02d}.png",
                "photo": "photo",
                "kicker": "QUÉ PASÓ",
                "title": "MISIÓN EN ÓRBITA",
                "body": "La misión continúa.",
                "alt_text": "La misión continúa en órbita.",
            }
            for i in range(1, 7)
        ],
    }
    return visuals, rights


def test_visual_unicode_accepts_nfc_spanish(tmp_path):
    visuals, rights = _package(tmp_path)
    assert len(_validate_visual_spec(tmp_path, visuals, rights)) == 6


def test_visual_unicode_rejects_ascii_degradation(tmp_path):
    visuals, rights = _package(tmp_path)
    visuals["slides"][0]["title"] = "MISION EN ORBITA"
    with pytest.raises(RuntimeError, match="degraded Spanish|lost a diacritic"):
        _validate_visual_spec(tmp_path, visuals, rights)


def test_visual_unicode_rejects_non_nfc(tmp_path):
    visuals, rights = _package(tmp_path)
    visuals["slides"][0]["title"] = unicodedata.normalize("NFD", "MISIÓN EN ÓRBITA")
    with pytest.raises(RuntimeError, match="Unicode NFC"):
        _validate_visual_spec(tmp_path, visuals, rights)
