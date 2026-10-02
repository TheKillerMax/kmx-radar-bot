from __future__ import annotations

from typing import Iterable
import logging
import time

import feedparser
import requests

from .config import editorial_config, query_config, rss_config
from .models import Article
from .utils import domain_of

LOG = logging.getLogger(__name__)
GDELT_ENDPOINT = "https://api.gdeltproject.org/api/v2/doc/doc"
USER_AGENT = "KMX-RADAR/0.1 (+https://github.com/TheKillerMax/kmx-radar-bot)"


def _gdelt_articles(payload: dict, *, category: str, risk: str) -> list[Article]:
    rows = payload.get("articles") or payload.get("items") or payload.get("data") or []
    if isinstance(rows, dict):
        rows = rows.get("articles") or rows.get("items") or []
    output: list[Article] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        url = str(row.get("url") or row.get("external_url") or "").strip()
        title = str(row.get("title") or "").strip()
        if not url or not title:
            continue
        output.append(
            Article(
                title=title,
                url=url,
                domain=str(row.get("domain") or domain_of(url)),
                language=str(row.get("language") or row.get("lang") or ""),
                source_country=str(row.get("sourcecountry") or row.get("source_country") or ""),
                seen_at=str(row.get("seendate") or row.get("date_published") or row.get("date") or ""),
                social_image=str(row.get("socialimage") or row.get("image") or ""),
                category=category,
                risk=risk,
            )
        )
    return output


def discover_gdelt(session: requests.Session | None = None) -> list[Article]:
    cfg = editorial_config()["runtime"]
    session = session or requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    all_articles: list[Article] = []

    for item in query_config().get("queries", []):
        params = {
            "query": item["query"],
            "mode": "artlist",
            "format": "json",
            "sort": "datedesc",
            "maxrecords": cfg["gdelt_max_records_per_query"],
            "timespan": cfg["gdelt_timespan"],
        }
        try:
            response = session.get(GDELT_ENDPOINT, params=params, timeout=35)
            response.raise_for_status()
            payload = response.json()
            rows = _gdelt_articles(payload, category=item["category"], risk=item["risk"])
            LOG.info("GDELT %s: %s articles", item["id"], len(rows))
            all_articles.extend(rows)
        except Exception as exc:
            LOG.warning("GDELT query %s failed: %s", item.get("id"), exc)
        time.sleep(1.1)

    return dedupe_urls(all_articles)


def discover_rss() -> list[Article]:
    output: list[Article] = []
    for feed in rss_config().get("feeds", []):
        try:
            parsed = feedparser.parse(feed["url"])
            for entry in parsed.entries[:25]:
                url = str(entry.get("link") or "").strip()
                title = str(entry.get("title") or "").strip()
                if not url or not title:
                    continue
                output.append(
                    Article(
                        title=title,
                        url=url,
                        domain=domain_of(url),
                        language="en",
                        seen_at=str(entry.get("published") or entry.get("updated") or ""),
                        category=feed.get("category", "MUNDO"),
                        risk=feed.get("risk", "medium"),
                        primary_hint=bool(feed.get("primary", False)),
                        description=str(entry.get("summary") or ""),
                    )
                )
        except Exception as exc:
            LOG.warning("RSS %s failed: %s", feed.get("name"), exc)
    return output


def dedupe_urls(articles: Iterable[Article]) -> list[Article]:
    by_url: dict[str, Article] = {}
    for article in articles:
        by_url.setdefault(article.url, article)
    return list(by_url.values())


def discover_all() -> list[Article]:
    cfg = editorial_config()["runtime"]
    rows = dedupe_urls([*discover_gdelt(), *discover_rss()])
    return rows[: int(cfg["max_candidates_per_run"]) * 8]
