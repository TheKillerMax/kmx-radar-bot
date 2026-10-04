import kmxradar.instagram as instagram


class DummyResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def test_find_recent_media_by_caption_exact_match(monkeypatch):
    monkeypatch.setattr(
        instagram,
        "editorial_config",
        lambda: {"instagram": {"graph_host": "https://graph.example", "api_version": "v1"}},
    )
    monkeypatch.setattr(
        instagram.requests,
        "get",
        lambda *args, **kwargs: DummyResponse({
            "data": [
                {"id": "111", "caption": "Otro texto"},
                {"id": "222", "caption": "Caption exacto", "permalink": "https://instagram.example/p/222"},
            ]
        }),
    )
    item = instagram.find_recent_media_by_caption("ig", "Caption exacto", "token")
    assert item["id"] == "222"


def test_find_recent_media_by_caption_requires_exact_match(monkeypatch):
    monkeypatch.setattr(
        instagram,
        "editorial_config",
        lambda: {"instagram": {"graph_host": "https://graph.example", "api_version": "v1"}},
    )
    monkeypatch.setattr(
        instagram.requests,
        "get",
        lambda *args, **kwargs: DummyResponse({
            "data": [{"id": "111", "caption": "Caption parecido"}]
        }),
    )
    assert instagram.find_recent_media_by_caption("ig", "Caption", "token") is None


def test_publish_or_recover_finds_post_after_publish_error(monkeypatch):
    monkeypatch.setattr(
        instagram,
        "_publish_container",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("ambiguous publish error")),
    )
    monkeypatch.setattr(
        instagram,
        "find_recent_media_by_caption",
        lambda *args, **kwargs: {
            "id": "333",
            "caption": "Caption exacto",
            "permalink": "https://instagram.example/p/333",
        },
    )
    monkeypatch.setattr(instagram.time, "sleep", lambda *_: None)

    media_id, recovered = instagram._publish_or_recover(
        "ig", "container", "Caption exacto", "token", attempts=1, seconds=0
    )
    assert media_id == "333"
    assert recovered["id"] == "333"


def test_publish_or_recover_raises_when_post_never_appears(monkeypatch):
    monkeypatch.setattr(
        instagram,
        "_publish_container",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("real publish failure")),
    )
    monkeypatch.setattr(instagram, "find_recent_media_by_caption", lambda *args, **kwargs: None)
    monkeypatch.setattr(instagram.time, "sleep", lambda *_: None)

    try:
        instagram._publish_or_recover(
            "ig", "container", "Caption", "token", attempts=1, seconds=0
        )
    except RuntimeError as exc:
        assert "real publish failure" in str(exc)
    else:
        raise AssertionError("Expected publish failure to propagate")
