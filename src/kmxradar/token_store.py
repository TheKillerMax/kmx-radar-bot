from __future__ import annotations

from base64 import urlsafe_b64encode
from hashlib import sha256
import os

from cryptography.fernet import Fernet, InvalidToken
import requests

from .config import DATA_DIR, editorial_config
from .utils import utcnow_iso, write_json

TOKEN_FILE = DATA_DIR / "instagram_token.enc"
TOKEN_META = DATA_DIR / "instagram_token_meta.json"


def _fernet() -> Fernet:
    secret = os.environ.get("TOKEN_ENCRYPTION_PASSWORD", "").encode("utf-8")
    if len(secret) < 24:
        raise RuntimeError("TOKEN_ENCRYPTION_PASSWORD must be at least 24 characters")
    key = urlsafe_b64encode(sha256(secret).digest())
    return Fernet(key)


def save_token(token: str, metadata: dict | None = None) -> None:
    TOKEN_FILE.write_bytes(_fernet().encrypt(token.encode("utf-8")))
    meta = {"updated_at": utcnow_iso(), **(metadata or {})}
    write_json(TOKEN_META, meta)


def load_token() -> str:
    if TOKEN_FILE.exists():
        try:
            return _fernet().decrypt(TOKEN_FILE.read_bytes()).decode("utf-8")
        except InvalidToken as exc:
            raise RuntimeError("Encrypted Instagram token cannot be decrypted with current password") from exc
    env_token = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "").strip()
    if not env_token:
        raise RuntimeError("No Instagram token available")
    save_token(env_token, {"source": "github-secret"})
    return env_token


def refresh_token() -> str:
    """Refresh without silently preferring a stale encrypted token forever.

    A GitHub secret is accepted as a recovery candidate only after its
    Instagram account is verified and a refresh succeeds. Never print tokens.
    """
    token = load_token()
    cfg = editorial_config()
    host = cfg["instagram"]["graph_host"]

    def request_refresh(candidate: str) -> dict:
        response = requests.get(
            f"{host}/refresh_access_token",
            params={"grant_type": "ig_refresh_token", "access_token": candidate},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    source = "refresh"
    try:
        payload = request_refresh(token)
    except requests.HTTPError:
        alternative = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "").strip()
        if not alternative or alternative == token:
            raise
        # A refreshed access token must still belong to the correct account.
        from .instagram import get_account

        account = get_account(alternative)
        expected = str(cfg.get("brand", {}).get("handle") or "").lstrip("@").casefold()
        actual = str(account.get("username") or "").casefold()
        if not actual or (expected and actual != expected):
            raise RuntimeError("Refusing Instagram refresh with a secret for another account")
        payload = request_refresh(alternative)
        source = "refresh-from-verified-github-secret"

    new_token = payload.get("access_token")
    if not new_token:
        raise RuntimeError("Instagram refresh response did not contain access_token")
    save_token(new_token, {"expires_in": payload.get("expires_in"), "source": source})
    return new_token
