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


def _media_url(relative_path: str) -> str:
    repo = os.getenv("GITHUB_REPOSITORY", "TheKillerMax/kmx-radar-bot")
    branch = os.getenv("KMX_MEDIA_BRANCH", "main")
    return f"https://raw.githubusercontent.com/{repo}/{branch}/{relative_path.lstrip('/')}"


def _post_media(ig_id: str, data: dict, token: str) -> str:
    cfg = editorial_config()["instagram"]
    endpoint = f"{cfg['graph_host']}/{cfg['api_version']}/{ig_id}/media"
    payload = {**data, "access_token": token}
    response = requests.post(endpoint, data=payload, timeout=45)
    response.raise_for_status()
    result = response.json()
    container_id = result.get("id")
    if not container_id:
        raise RuntimeError(f"Instagram did not return a media container id: {result}")
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
    raise RuntimeError(f"Instagram container {container_id} did not become ready in time")


def _publish_container(ig_id: str, container_id: str, token: str) -> str:
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


def _wait_public_url(url: str, attempts: int = 10, seconds: int = 5) -> None:
    last_error: Exception | None = None
    for _ in range(attempts):
        try:
            response = requests.get(url, timeout=20, stream=True)
            if response.status_code == 200 and response.headers.get("content-type", "").startswith("image/"):
                return
            last_error = RuntimeError(
                f"HTTP {response.status_code} content-type={response.headers.get('content-type')}"
            )
        except Exception as exc:
            last_error = exc
        time.sleep(seconds)
    raise RuntimeError(f"Media is not publicly reachable at {url}: {last_error}")


def publish_package(package_dir: Path, manifest: dict) -> dict:
    token = load_token()
    account = get_account(token)
    ig_id = str(account.get("user_id") or account.get("id") or "")
    if not ig_id:
        raise RuntimeError(f"Unable to obtain Instagram professional account id: {account}")

    root = Path(__file__).resolve().parents[2]
    images = manifest["images"]
    urls: list[str] = []
    for item in images:
        absolute = (package_dir / item["path"]).resolve()
        try:
            rel = absolute.relative_to(root.resolve()).as_posix()
        except ValueError as exc:
            raise RuntimeError(f"Publication image must stay inside the repository: {absolute}") from exc
        url = _media_url(rel)
        _wait_public_url(url)
        urls.append(url)

    caption = str(manifest["caption"])
    ai_generated = bool(manifest.get("ai_generated", True))

    if len(images) == 1:
        data = {
            "image_url": urls[0],
            "caption": caption,
        }
        if images[0].get("alt_text"):
            data["alt_text"] = images[0]["alt_text"]
        if ai_generated:
            data["is_ai_generated"] = "true"
        container = _post_media(ig_id, data, token)
        wait_until_ready(container, token)
        media_id = _publish_container(ig_id, container, token)
        return {
            "media_id": media_id,
            "container_id": container,
            "image_urls": urls,
            "username": account.get("username"),
            "ig_id": ig_id,
        }

    child_ids: list[str] = []
    for item, url in zip(images, urls):
        data = {"image_url": url, "is_carousel_item": "true"}
        if item.get("alt_text"):
            data["alt_text"] = item["alt_text"]
        child = _post_media(ig_id, data, token)
        wait_until_ready(child, token)
        child_ids.append(child)

    parent_data = {
        "media_type": "CAROUSEL",
        "children": ",".join(child_ids),
        "caption": caption,
    }
    if ai_generated:
        parent_data["is_ai_generated"] = "true"
    parent = _post_media(ig_id, parent_data, token)
    wait_until_ready(parent, token)
    media_id = _publish_container(ig_id, parent, token)
    return {
        "media_id": media_id,
        "container_id": parent,
        "children": child_ids,
        "image_urls": urls,
        "username": account.get("username"),
        "ig_id": ig_id,
    }
