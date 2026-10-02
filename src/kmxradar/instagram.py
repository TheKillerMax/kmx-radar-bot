from __future__ import annotations

import logging
import os
import time
from pathlib import Path

import requests

from .config import editorial_config
from .token_store import load_token

LOG = logging.getLogger(__name__)


def get_account(token: str | None = None) -> dict:
    token = token or load_token()
    cfg = editorial_config()["instagram"]
    response = requests.get(
        f"{cfg['graph_host']}/{cfg['api_version']}/me",
        params={"fields": "user_id,username,account_type", "access_token": token},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def _public_media_url(path: Path) -> str:
    override = os.getenv("KMX_MEDIA_BASE_URL", "").rstrip("/")
    if override:
        return f"{override}/{path.name}"
    repo = os.getenv("GITHUB_REPOSITORY", "TheKillerMax/kmx-radar-bot")
    branch = os.getenv("KMX_MEDIA_BRANCH", "main")
    return f"https://raw.githubusercontent.com/{repo}/{branch}/docs/media/{path.name}"


def create_image_container(ig_id: str, image_url: str, caption: str, token: str) -> str:
    cfg = editorial_config()["instagram"]
    endpoint = f"{cfg['graph_host']}/{cfg['api_version']}/{ig_id}/media"
    response = requests.post(
        endpoint,
        data={"image_url": image_url, "caption": caption, "access_token": token},
        timeout=45,
    )
    response.raise_for_status()
    payload = response.json()
    container_id = payload.get("id")
    if not container_id:
        raise RuntimeError(f"Instagram did not return a media container id: {payload}")
    return str(container_id)


def wait_until_ready(container_id: str, token: str) -> None:
    cfg = editorial_config()["instagram"]
    endpoint = f"{cfg['graph_host']}/{cfg['api_version']}/{container_id}"
    for _ in range(int(cfg["poll_attempts"])):
        response = requests.get(
            endpoint,
            params={"fields": "status_code", "access_token": token},
            timeout=30,
        )
        response.raise_for_status()
        status = str(response.json().get("status_code") or "").upper()
        if status in {"FINISHED", "PUBLISHED"}:
            return
        if status in {"ERROR", "EXPIRED"}:
            raise RuntimeError(f"Instagram container status is {status}")
        time.sleep(int(cfg["poll_seconds"]))


def publish_container(ig_id: str, container_id: str, token: str) -> str:
    cfg = editorial_config()["instagram"]
    endpoint = f"{cfg['graph_host']}/{cfg['api_version']}/{ig_id}/media_publish"
    response = requests.post(
        endpoint,
        data={"creation_id": container_id, "access_token": token},
        timeout=45,
    )
    response.raise_for_status()
    payload = response.json()
    media_id = payload.get("id")
    if not media_id:
        raise RuntimeError(f"Instagram did not return published media id: {payload}")
    return str(media_id)


def _wait_public_url(url: str, attempts: int = 8, seconds: int = 5) -> None:
    last_error: Exception | None = None
    for _ in range(attempts):
        try:
            response = requests.get(url, timeout=20, stream=True)
            if response.status_code == 200 and response.headers.get("content-type", "").startswith("image/"):
                return
            last_error = RuntimeError(f"HTTP {response.status_code} content-type={response.headers.get('content-type')}")
        except Exception as exc:
            last_error = exc
        time.sleep(seconds)
    raise RuntimeError(f"Generated media is not publicly reachable at {url}: {last_error}")


def publish_image(path: Path, caption: str) -> dict:
    token = load_token()
    account = get_account(token)
    ig_id = str(account.get("user_id") or account.get("id") or "")
    if not ig_id:
        raise RuntimeError(f"Unable to obtain Instagram professional account id: {account}")
    image_url = _public_media_url(path)
    _wait_public_url(image_url)
    container_id = create_image_container(ig_id, image_url, caption, token)
    wait_until_ready(container_id, token)
    media_id = publish_container(ig_id, container_id, token)
    return {
        "media_id": media_id,
        "container_id": container_id,
        "image_url": image_url,
        "username": account.get("username"),
        "ig_id": ig_id,
    }
