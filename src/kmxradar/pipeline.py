from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import logging
import os

from .cluster import cluster_articles
from .config import DATA_DIR, editorial_config
from .discover import discover_all
from .editor import build_caption, compose_with_llm
from .extract import enrich_article
from .graphics import render_news_card
from .instagram import publish_image
from .models import Cluster
from .utils import read_json, utcnow_iso, write_json
from .verify import verify_cluster

LOG = logging.getLogger(__name__)
STATE_FILE = DATA_DIR / "state.json"
PUBLISHED_FILE = DATA_DIR / "published.json"


def _parse_iso(raw: str | None):
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def _rate_limit_allows_post() -> bool:
    cfg = editorial_config()["runtime"]
    published = read_json(PUBLISHED_FILE, {"posts": []}).get("posts", [])
    now = datetime.now(timezone.utc)
    today = [
        p for p in published
        if (_parse_iso(p.get("published_at")) or now - timedelta(days=2)) >= now - timedelta(days=1)
    ]
    if len(today) >= int(cfg["max_posts_per_day"]):
        return False
    state = read_json(STATE_FILE, {})
    last_post = _parse_iso(state.get("last_post_at"))
    if last_post and now - last_post < timedelta(minutes=int(cfg["min_minutes_between_posts"])):
        return False
    return True


def _already_seen(cluster: Cluster) -> bool:
    published = read_json(PUBLISHED_FILE, {"posts": []}).get("posts", [])
    return any(p.get("cluster_key") == cluster.key for p in published)


def _enrich_cluster(cluster: Cluster) -> Cluster:
    cfg = editorial_config()["runtime"]
    limit = int(cfg["fetch_sources_per_cluster"])
    chosen = []
    seen_domains = set()
    for article in cluster.articles:
        if article.domain in seen_domains:
            continue
        seen_domains.add(article.domain)
        chosen.append(article)
        if len(chosen) >= limit:
            break
    for article in chosen:
        enrich_article(article)
    return cluster


def select_candidate(clusters: list[Cluster]) -> Cluster | None:
    viable = [c for c in clusters if c.publishable and not _already_seen(c)]
    if not viable:
        return None
    viable.sort(
        key=lambda c: (c.verification_score, len(c.independent_domains), len(c.articles)),
        reverse=True,
    )
    return viable[0]


def run() -> int:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    state = read_json(STATE_FILE, {"seen_urls": []})
    seen_urls = set(state.get("seen_urls", []))

    articles = [a for a in discover_all() if a.url not in seen_urls]
    LOG.info("Discovered %d unseen articles", len(articles))
    clusters = [verify_cluster(c) for c in cluster_articles(articles)]
    clusters.sort(key=lambda c: (c.verification_score, len(c.articles)), reverse=True)

    for c in clusters[:10]:
        LOG.info(
            "candidate score=%s domains=%s articles=%s status=%s title=%s",
            c.verification_score,
            len(c.independent_domains),
            len(c.articles),
            c.status,
            c.canonical_title[:90],
        )

    pending_exists = (DATA_DIR / "pending_post.json").exists()
    candidate = None if pending_exists else (select_candidate(clusters) if _rate_limit_allows_post() else None)
    if pending_exists:
        LOG.info("A pending Instagram post already exists; skipping new candidate selection until it is published or cleared.")

    if candidate:
        _enrich_cluster(candidate)
        editorial = compose_with_llm(candidate)
        candidate.editorial = editorial
        image_path = render_news_card(candidate, editorial)
        caption = build_caption(candidate, editorial)

        publish_enabled = os.getenv("PUBLISH_ENABLED", "false").strip().lower() == "true"
        result = {"dry_run": not publish_enabled}
        if publish_enabled:
            pending = {
                "cluster_key": candidate.key,
                "image_path": str(image_path.relative_to(Path(__file__).resolve().parents[2])),
                "caption": caption,
                "editorial": editorial,
                "category": candidate.category,
                "status": candidate.status,
                "verification_score": candidate.verification_score,
                "source_domains": candidate.independent_domains[:8],
                "created_at": utcnow_iso(),
            }
            write_json(DATA_DIR / "pending_post.json", pending)
            result["pending"] = True
        else:
            result["preview"] = str(image_path)
            result["caption"] = caption

        record = {
            "cluster_key": candidate.key,
            "created_at": utcnow_iso(),
            "dry_run": not publish_enabled,
            "headline": editorial.get("headline"),
            "status": candidate.status,
            "verification_score": candidate.verification_score,
            "sources": candidate.independent_domains[:8],
            "image": str(image_path),
        }
        write_json(DATA_DIR / "last_candidate.json", record | result)

    state["last_run"] = utcnow_iso()
    merged_seen = list(dict.fromkeys([a.url for a in articles] + list(seen_urls)))[:4000]
    state["seen_urls"] = merged_seen
    write_json(STATE_FILE, state)
    return 0 if candidate else 3


def publish_pending() -> int:
    pending_path = DATA_DIR / "pending_post.json"
    if not pending_path.exists():
        LOG.info("No pending post")
        return 0
    pending = read_json(pending_path, None)
    if not pending:
        return 0

    root = Path(__file__).resolve().parents[2]
    image_path = root / pending["image_path"]
    result = publish_image(image_path, pending["caption"])

    published = read_json(PUBLISHED_FILE, {"posts": []})
    published.setdefault("posts", []).append(
        {
            "cluster_key": pending["cluster_key"],
            "published_at": utcnow_iso(),
            "media_id": result["media_id"],
            "image_url": result["image_url"],
            "headline": pending.get("editorial", {}).get("headline"),
            "category": pending.get("category"),
            "status": pending.get("status"),
            "verification_score": pending.get("verification_score"),
            "sources": pending.get("source_domains", []),
        }
    )
    write_json(PUBLISHED_FILE, published)
    state = read_json(STATE_FILE, {})
    state["last_post_at"] = utcnow_iso()
    write_json(STATE_FILE, state)
    pending_path.unlink(missing_ok=True)
    return 0
