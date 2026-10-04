from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import logging
import re

from .config import DATA_DIR, editorial_config, load_yaml
from .instagram import publish_package
from .utils import read_json, utcnow_iso, write_json

LOG = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[2]
APPROVED_DIR = ROOT / "approved"
PUBLISHED_FILE = DATA_DIR / "published.json"
STATE_FILE = DATA_DIR / "state.json"
CHATGPT_STATE_FILE = DATA_DIR / "chatgpt_state.json"


def _parse_iso(raw: str | None):
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def _rate_limit_status() -> tuple[bool, str | None, str | None]:
    cfg = editorial_config()["runtime"]
    now = datetime.now(timezone.utc)
    published = read_json(PUBLISHED_FILE, {"posts": []}).get("posts", [])
    recent = [
        p for p in published
        if (_parse_iso(p.get("published_at")) or now - timedelta(days=2)) >= now - timedelta(days=1)
    ]
    recent_story_keys = {
        str(p.get("source_event_id") or p.get("publication_id") or "").strip()
        for p in recent
        if str(p.get("source_event_id") or p.get("publication_id") or "").strip()
    }
    if len(recent_story_keys) >= int(cfg["max_posts_per_day"]):
        return False, "daily_story_limit", None

    state = read_json(STATE_FILE, {})
    last_post = _parse_iso(state.get("last_post_at"))
    if last_post:
        retry_at = last_post + timedelta(minutes=int(cfg["min_minutes_between_posts"]))
        if now < retry_at:
            return False, "minimum_interval", retry_at.isoformat().replace("+00:00", "Z")
    return True, None, None


def _rate_limit_allows_post() -> bool:
    return _rate_limit_status()[0]


def _set_chatgpt_state(publication_id: str, **updates) -> None:
    state = read_json(CHATGPT_STATE_FILE, {})
    current_id = str(state.get("last_publication_id") or "")
    if current_id and current_id != publication_id:
        return
    state["last_publication_id"] = publication_id
    for key, value in updates.items():
        state[key] = value
    write_json(CHATGPT_STATE_FILE, state)


def _validate_manifest(package_dir: Path, manifest: dict) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "publication_id",
        "ready_to_publish",
        "headline",
        "caption",
        "images",
        "sources",
    }
    missing = required - set(manifest)
    if missing:
        errors.append(f"Missing fields: {sorted(missing)}")
    if manifest.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if manifest.get("ready_to_publish") is not True:
        errors.append("ready_to_publish must be true")
    caption = manifest.get("caption")
    if not isinstance(caption, str) or len(caption) > 2200:
        errors.append("caption must be a string <= 2200 chars")
    elif isinstance(caption, str):
        hashtags = re.findall(r"(?<!\w)#([\wÁÉÍÓÚÜÑáéíóúüñ]+)", caption, flags=re.UNICODE)
        normalized = [h.casefold() for h in hashtags]
        if len(hashtags) > 5:
            errors.append("Instagram caption must use at most 5 hashtags")
        if len(hashtags) < 3:
            errors.append("Instagram caption should use 3 to 5 relevant hashtags")
        if len(set(normalized)) != len(normalized):
            errors.append("Instagram caption contains duplicate hashtags")
        if hashtags and "kmxradar" not in normalized:
            errors.append("Instagram caption must include #KMXRadar")

    images = manifest.get("images")
    if not isinstance(images, list) or not (1 <= len(images) <= 10):
        errors.append("images must contain 1 to 10 items")
    else:
        for item in images:
            if not isinstance(item, dict) or not item.get("path"):
                errors.append("each image item needs path")
                continue
            path = package_dir / str(item["path"])
            if not path.exists():
                errors.append(f"missing image: {item['path']}")
            elif path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                errors.append(f"unsupported image type: {item['path']}")

    sources = manifest.get("sources")
    if not isinstance(sources, list) or len(sources) < 1:
        errors.append("at least one source is required")
    else:
        for item in sources:
            if not isinstance(item, dict) or not str(item.get("url", "")).startswith(("http://", "https://")):
                errors.append("every source needs a valid http(s) URL")
    return errors


def _already_published(publication_id: str) -> bool:
    posts = read_json(PUBLISHED_FILE, {"posts": []}).get("posts", [])
    return any(p.get("publication_id") == publication_id for p in posts)


def publish_ready_packages() -> int:
    auto = load_yaml("autopublish.yml")
    if not bool(auto.get("enabled", False)):
        LOG.info("Automatic publishing is disabled in config/autopublish.yml.")
        return 0

    if not APPROVED_DIR.exists():
        LOG.info("No approved directory.")
        return 0

    ready_dirs = sorted({p.parent for p in APPROVED_DIR.glob("*/.ready")})
    if not ready_dirs:
        LOG.info("No .ready publication packages.")
        return 0

    allowed, limit_reason, retry_at = _rate_limit_status()
    if not allowed:
        publication_id = ready_dirs[0].name
        note = f"Publishing is waiting for rate limit: {limit_reason}"
        if retry_at:
            note += f"; retry after {retry_at}"
        _set_chatgpt_state(
            publication_id,
            phase="publishing_waiting_rate_limit",
            last_result="publishing_waiting_rate_limit",
            note=note,
            next_publish_retry_at=retry_at,
        )
        LOG.info("Publishing rate limit blocked this run: %s", note)
        return 0

    for package_dir in ready_dirs:
        manifest_path = package_dir / "publication.json"
        if not manifest_path.exists():
            LOG.warning("Skipping %s: publication.json missing", package_dir)
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:
            LOG.warning("Skipping %s: invalid JSON: %s", package_dir, exc)
            continue

        publication_id = str(manifest.get("publication_id") or package_dir.name)
        if _already_published(publication_id):
            LOG.info("Already published: %s", publication_id)
            (package_dir / ".ready").unlink(missing_ok=True)
            published = read_json(PUBLISHED_FILE, {"posts": []}).get("posts", [])
            row = next((p for p in published if p.get("publication_id") == publication_id), {})
            _set_chatgpt_state(
                publication_id,
                phase="published",
                last_result="published",
                last_media_id=row.get("media_id"),
                published_at=row.get("published_at"),
                note="Publisher reconciled an already-recorded publication.",
            )
            continue

        errors = _validate_manifest(package_dir, manifest)
        if errors:
            message = f"Invalid publication package {publication_id}: {'; '.join(errors)}"
            _set_chatgpt_state(
                publication_id,
                phase="publish_blocked",
                last_result="publish_blocked",
                note=message,
            )
            raise RuntimeError(message)

        try:
            result = publish_package(package_dir, manifest)
        except Exception as exc:
            _set_chatgpt_state(
                publication_id,
                phase="publish_error",
                last_result="publish_error",
                note=f"Instagram publication failed; .ready retained for retry: {exc}",
            )
            LOG.exception("Instagram publication failed for %s", publication_id)
            raise

        published_at = utcnow_iso()
        published = read_json(PUBLISHED_FILE, {"posts": []})
        published.setdefault("posts", []).append(
            {
                "publication_id": publication_id,
                "source_event_id": manifest.get("source_event_id"),
                "headline": manifest.get("headline"),
                "status": manifest.get("status"),
                "published_at": published_at,
                "media_id": result["media_id"],
                "image_urls": result.get("image_urls", []),
                "sources": manifest.get("sources", []),
            }
        )
        write_json(PUBLISHED_FILE, published)

        state = read_json(STATE_FILE, {})
        state["last_post_at"] = published_at
        write_json(STATE_FILE, state)

        receipt = {
            "publication_id": publication_id,
            "published_at": published_at,
            "instagram": result,
        }
        write_json(package_dir / ".published.json", receipt)
        (package_dir / ".ready").unlink(missing_ok=True)
        _set_chatgpt_state(
            publication_id,
            phase="published",
            last_result="published",
            last_media_id=result.get("media_id"),
            published_at=published_at,
            next_publish_retry_at=None,
            note="Publisher completed Instagram publication and recorded the receipt.",
        )
        LOG.info("Published %s", publication_id)
        return 0

    return 0
