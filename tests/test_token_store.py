import requests
import pytest

import kmxradar.token_store as token_store
import kmxradar.instagram as instagram


class FakeRefreshResponse:
    def __init__(self, candidate):
        self.candidate = candidate

    def raise_for_status(self):
        if self.candidate == "encrypted-invalid":
            raise requests.HTTPError("simulated expired credential")

    def json(self):
        return {"access_token": "refreshed-valid", "expires_in": 5184000}


def test_refresh_accepts_validated_new_secret_when_encrypted_token_fails(monkeypatch):
    monkeypatch.setattr(token_store, "load_token", lambda: "encrypted-invalid")
    monkeypatch.setenv("INSTAGRAM_ACCESS_TOKEN", "verified-secret")
    monkeypatch.setattr(token_store, "editorial_config", lambda: {
        "brand": {"handle": "@kmxradar"},
        "instagram": {"graph_host": "https://graph.example"},
    })
    monkeypatch.setattr(
        token_store.requests, "get",
        lambda url, params, timeout: FakeRefreshResponse(params["access_token"]),
    )
    monkeypatch.setattr(
        instagram, "get_account",
        lambda token: {"username": "kmxradar", "user_id": "123"},
    )
    saved = []
    monkeypatch.setattr(token_store, "save_token", lambda value, metadata: saved.append((value, metadata)))
    assert token_store.refresh_token() == "refreshed-valid"
    assert saved[0][0] == "refreshed-valid"
    assert saved[0][1]["source"] == "refresh-from-verified-github-secret"


def test_refresh_rejects_secret_belonging_to_another_instagram_account(monkeypatch):
    monkeypatch.setattr(token_store, "load_token", lambda: "encrypted-invalid")
    monkeypatch.setenv("INSTAGRAM_ACCESS_TOKEN", "other-secret")
    monkeypatch.setattr(token_store, "editorial_config", lambda: {
        "brand": {"handle": "@kmxradar"},
        "instagram": {"graph_host": "https://graph.example"},
    })
    monkeypatch.setattr(
        token_store.requests, "get",
        lambda url, params, timeout: FakeRefreshResponse(params["access_token"]),
    )
    monkeypatch.setattr(
        instagram, "get_account",
        lambda token: {"username": "other-account", "user_id": "999"},
    )
    saved = []
    monkeypatch.setattr(token_store, "save_token", lambda *args: saved.append(args))
    with pytest.raises(RuntimeError, match="another account"):
        token_store.refresh_token()
    assert saved == []
