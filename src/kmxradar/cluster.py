from __future__ import annotations

from collections import Counter
from rapidfuzz.fuzz import token_set_ratio

from .models import Article, Cluster
from .utils import normalize_text, stable_hash

STOPWORDS = {
    "de", "la", "el", "los", "las", "un", "una", "unos", "unas", "y", "o", "en", "por",
    "para", "con", "del", "al", "que", "se", "es", "son", "su", "sus", "a", "the", "of",
    "and", "in", "to", "for", "on", "with", "from", "as", "at", "is", "are", "new", "última",
    "hora", "noticia", "noticias",
}


def _keywords(title: str) -> set[str]:
    return {w for w in normalize_text(title).split() if len(w) >= 4 and w not in STOPWORDS}


def _similar(a: Article, b: Article) -> bool:
    score = token_set_ratio(normalize_text(a.title), normalize_text(b.title))
    if score >= 72:
        return True
    ka, kb = _keywords(a.title), _keywords(b.title)
    if not ka or not kb:
        return False
    jaccard = len(ka & kb) / len(ka | kb)
    return jaccard >= 0.42


def cluster_articles(articles: list[Article]) -> list[Cluster]:
    clusters: list[Cluster] = []
    for article in articles:
        placed = False
        for cluster in clusters:
            if cluster.category != article.category:
                continue
            if any(_similar(article, existing) for existing in cluster.articles[:8]):
                cluster.articles.append(article)
                if article.risk == "high":
                    cluster.risk = "high"
                placed = True
                break
        if not placed:
            key = stable_hash(article.category, normalize_text(article.title))
            clusters.append(Cluster(key=key, category=article.category, risk=article.risk, articles=[article]))

    for cluster in clusters:
        cluster.canonical_title = canonical_title(cluster.articles)
    return clusters


def canonical_title(articles: list[Article]) -> str:
    if not articles:
        return ""
    keywords = Counter()
    for article in articles:
        keywords.update(_keywords(article.title))
    top = set(k for k, _ in keywords.most_common(12))
    scored = []
    for article in articles:
        overlap = len(_keywords(article.title) & top)
        length_penalty = max(0, len(article.title) - 120) / 40
        scored.append((overlap - length_penalty, article.title))
    return max(scored, key=lambda x: x[0])[1]
