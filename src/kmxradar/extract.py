from __future__ import annotations

import logging
import re

import requests
import trafilatura
from bs4 import BeautifulSoup

from .models import Article

LOG = logging.getLogger(__name__)
USER_AGENT = "Mozilla/5.0 (compatible; KMX-RADAR/0.1; +https://github.com/TheKillerMax/kmx-radar-bot)"


def enrich_article(article: Article, max_chars: int = 5500) -> Article:
    try:
        response = requests.get(
            article.url,
            timeout=22,
            headers={"User-Agent": USER_AGENT, "Accept-Language": "es,en;q=0.8"},
            allow_redirects=True,
        )
        response.raise_for_status()
        html = response.text
    except Exception as exc:
        LOG.debug("Fetch failed %s: %s", article.url, exc)
        return article

    try:
        extracted = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False,
            favor_precision=True,
            output_format="txt",
        ) or ""
        article.text = re.sub(r"\s+", " ", extracted).strip()[:max_chars]
    except Exception:
        pass

    try:
        soup = BeautifulSoup(html, "html.parser")
        if not article.description:
            meta = soup.find("meta", attrs={"name": "description"}) or soup.find(
                "meta", attrs={"property": "og:description"}
            )
            if meta and meta.get("content"):
                article.description = str(meta["content"]).strip()[:1000]
    except Exception:
        pass

    return article
