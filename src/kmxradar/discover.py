from __future__ import annotations

from typing import Iterable
import logging

import feedparser
import requests
from bs4 import BeautifulSoup

from .config import editorial_config, query_config, rss_config
from .models import Article
from .utils import domain_of

LOG = logging.getLogger(__name__)
GDELT_ENDPOINT = "https://api.gdeltproject.org/api/v2/doc/doc"
USER_AGENT = "KMX-RADAR/0.2 (+https://github.com/TheKillerMax/kmx-radar-bot)"


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
                publisher=str(row.get("source") or row.get("domain") or ""),
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
    runtime = editorial_config()["runtime"]
    if not runtime.get("gdelt_enabled", False):
        LOG.info("GDELT disabled for this run; RSS discovery is primary.")
        return []

    session = session or requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    all_articles: list[Article] = []

    # Deliberately limit the number of GDELT calls. Shared GitHub runner IPs can
    # hit GDELT rate limits, so GDELT is supplementary rather than required.
    for item in query_config().get("queries", [])[: int(runtime.get("gdelt_max_queries_per_run", 1))]:
        params = {
            "query": item["query"],
            "mode": "artlist",
            "format": "json",
            "sort": "datedesc",
            "maxrecords": runtime["gdelt_max_records_per_query"],
            "timespan": runtime["gdelt_timespan"],
        }
        try:
            response = session.get(GDELT_ENDPOINT, params=params, timeout=25)
            if response.status_code == 429:
                LOG.warning("GDELT rate-limited this runner; skipping GDELT for the current run.")
                break
            response.raise_for_status()
            payload = response.json()
            rows = _gdelt_articles(payload, category=item["category"], risk=item["risk"])
            LOG.info("GDELT %s: %s articles", item["id"], len(rows))
            all_articles.extend(rows)
        except Exception as exc:
            LOG.warning("GDELT query %s failed: %s", item.get("id"), exc)
            break

    return dedupe_urls(all_articles)


def _clean_summary(raw: str) -> str:
    if not raw:
        return ""
    try:
        return BeautifulSoup(raw, "html.parser").get_text(" ", strip=True)
    except Exception:
        return raw


def _entry_source(entry) -> tuple[str, str]:
    source = entry.get("source") or {}
    if hasattr(source, "get"):
        href = str(source.get("href") or source.get("url") or "").strip()
        title = str(source.get("title") or "").strip()
    else:
        href, title = "", ""
    return href, title


def discover_rss() -> list[Article]:
    runtime = editorial_config()["runtime"]
    limit = int(runtime.get("rss_max_entries_per_feed", 40))
    output: list[Article] = []

    for feed in rss_config().get("feeds", []):
        try:
            parsed = feedparser.parse(feed["url"], agent=USER_AGENT)
            if getattr(parsed, "bozo", False) and not parsed.entries:
                LOG.warning("RSS %s parse error: %s", feed.get("name"), getattr(parsed, "bozo_exception", "unknown"))
                continue

            count = 0
            for entry in parsed.entries[:limit]:
                url = str(entry.get("link") or "").strip()
                title = str(entry.get("title") or "").strip()
                if not url or not title:
                    continue

                source_url, source_title = _entry_source(entry)
                source_domain = domain_of(source_url) if source_url else domain_of(url)
                # Google News links resolve through news.google.com, but the RSS
                # source element identifies the underlying publisher and URL.
                domain = source_domain or domain_of(url)

                output.append(
                    Article(
                        title=title,
                        url=url,
                        domain=domain,
                        publisher=source_title or feed.get("name", ""),
                        language=feed.get("language", ""),
                        seen_at=str(entry.get("published") or entry.get("updated") or ""),
                        category=feed.get("category", "MUNDO"),
                        risk=feed.get("risk", "medium"),
                        primary_hint=bool(feed.get("primary", False)),
                        description=_clean_summary(str(entry.get("summary") or entry.get("description") or ""))[:1600],
                    )
                )
                count += 1
            LOG.info("RSS %s: %s articles", feed.get("name"), count)
        except Exception as exc:
            LOG.warning("RSS %s failed: %s", feed.get("name"), exc)
    return dedupe_urls(output)


def dedupe_urls(articles: Iterable[Article]) -> list[Article]:
    by_url: dict[str, Article] = {}
    for article in articles:
        by_url.setdefault(article.url, article)
    return list(by_url.values())


def discover_all() -> list[Article]:
    runtime = editorial_config()["runtime"]
    rows = dedupe_urls([*discover_rss(), *discover_gdelt()])
    LOG.info("Discovery total after URL deduplication: %s", len(rows))
    return rows[: int(runtime["max_candidates_per_run"]) * 8]
