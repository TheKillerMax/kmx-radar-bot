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
