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



def test_get_verified_account_uses_only_validated_alternative(monkeypatch):
    monkeypatch.setattr(instagram, "load_token", lambda: "stale")
    monkeypatch.setenv("INSTAGRAM_ACCESS_TOKEN", "fresh")
    monkeypatch.setattr(instagram, "editorial_config", lambda: {"brand": {"handle": "@kmxradar"}})
    saved = []
    monkeypatch.setattr(instagram, "save_token", lambda token, metadata: saved.append((token, metadata)))

    def fake_get_account(token):
        if token == "stale":
            raise instagram.InstagramAPIError("Instagram challenge", code=190)
        return {"username": "kmxradar", "user_id": "1"}

    monkeypatch.setattr(instagram, "get_account", fake_get_account)
    token, account = instagram.get_verified_account()
    assert token == "fresh"
    assert account["username"] == "kmxradar"
    assert saved[0][0] == "fresh"


def test_get_verified_account_rejects_secret_for_wrong_account(monkeypatch):
    monkeypatch.setattr(instagram, "load_token", lambda: "stale")
    monkeypatch.setenv("INSTAGRAM_ACCESS_TOKEN", "wrong")
    monkeypatch.setattr(instagram, "editorial_config", lambda: {"brand": {"handle": "@kmxradar"}})
    saved = []
    monkeypatch.setattr(instagram, "save_token", lambda *args: saved.append(args))

    def fake_get_account(token):
        if token == "stale":
            raise instagram.InstagramAPIError("Instagram challenge", code=190)
        return {"username": "otheraccount", "user_id": "2"}

    monkeypatch.setattr(instagram, "get_account", fake_get_account)
    import pytest
    with pytest.raises(RuntimeError, match="unexpected account"):
        instagram.get_verified_account()
    assert saved == []


def test_get_verified_account_no_alternate_does_not_hide_checkpoint(monkeypatch):
    monkeypatch.setattr(instagram, "load_token", lambda: "stale")
    monkeypatch.delenv("INSTAGRAM_ACCESS_TOKEN", raising=False)
    monkeypatch.setattr(instagram, "get_account", lambda token: (_ for _ in ()).throw(
        instagram.InstagramAPIError("Challenge", code=190)))
    import pytest
    with pytest.raises(instagram.InstagramAPIError):
        instagram.get_verified_account()
