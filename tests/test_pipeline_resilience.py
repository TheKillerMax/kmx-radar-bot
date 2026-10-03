from datetime import datetime, timezone

import pytest

import kmxradar.publication as publication
from kmxradar.visual_phase import _validate_visual_spec


def test_daily_quota_counts_corrections_as_one_story(monkeypatch):
    now = datetime.now(timezone.utc).isoformat()
    posts = [
        {"publication_id": "story-v1", "source_event_id": "event-a", "published_at": now},
        {"publication_id": "story-v2", "source_event_id": "event-a", "published_at": now},
    ]

    monkeypatch.setattr(
        publication,
        "editorial_config",
        lambda: {"runtime": {"max_posts_per_day": 2, "min_minutes_between_posts": 0}},
    )

    def fake_read_json(path, default):
        if path == publication.PUBLISHED_FILE:
            return {"posts": posts}
        if path == publication.STATE_FILE:
            return {}
        return default

    monkeypatch.setattr(publication, "read_json", fake_read_json)
    assert publication._rate_limit_allows_post() is True

    posts.append(
        {"publication_id": "other-story", "source_event_id": "event-b", "published_at": now}
    )
    assert publication._rate_limit_allows_post() is False


def test_visual_spec_rejects_partial_slide_set(tmp_path):
    visuals = {
        "sources": {
            "photo": {
                "direct_url": "https://example.org/photo.jpg",
                "credit": "Example",
            }
        },
        "slides": [
            {
                "n": i,
                "file": f"{i:02d}.png",
                "photo": "photo",
                "alt_text": "Texto alternativo",
            }
            for i in range(1, 4)
        ],
    }
    rights = [
        {
            "source_url": "https://example.org/page",
            "direct_url": "https://example.org/photo.jpg",
            "original_creator": "Example",
            "license_or_permission": "CC BY 4.0",
        }
    ]
    with pytest.raises(RuntimeError, match="6 to 10"):
        _validate_visual_spec(tmp_path, visuals, rights)


def test_visual_spec_accepts_complete_licensed_set(tmp_path):
    visuals = {
        "sources": {
            "photo": {
                "direct_url": "https://example.org/photo.jpg",
                "credit": "Example",
            }
        },
        "slides": [
            {
                "n": i,
                "file": f"{i:02d}.png",
                "photo": "photo",
                "alt_text": "Texto alternativo",
            }
            for i in range(1, 7)
        ],
    }
    rights = [
        {
            "source_url": "https://example.org/page",
            "direct_url": "https://example.org/photo.jpg",
            "original_creator": "Example",
            "license_or_permission": "CC BY 4.0",
        }
    ]
    slides = _validate_visual_spec(tmp_path, visuals, rights)
    assert len(slides) == 6
