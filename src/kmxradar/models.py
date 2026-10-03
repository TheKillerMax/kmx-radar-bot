from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class Article:
    title: str
    url: str
    domain: str
    publisher: str = ""
    language: str = ""
    source_country: str = ""
    seen_at: str = ""
    social_image: str = ""
    category: str = "MUNDO"
    risk: str = "medium"
    primary_hint: bool = False
    text: str = ""
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Cluster:
    key: str
    category: str
    risk: str
    articles: list[Article] = field(default_factory=list)
    verification_score: float = 0.0
    status: str = "SIN CONFIRMAR"
    primary_source_present: bool = False
    independent_domains: list[str] = field(default_factory=list)
    high_trust_domains: list[str] = field(default_factory=list)
    publishable: bool = False
    canonical_title: str = ""
    editorial: dict[str, Any] = field(default_factory=dict)

    @property
    def newest_seen_at(self) -> datetime:
        parsed: list[datetime] = []
        for article in self.articles:
            raw = article.seen_at.strip()
            if not raw:
                continue
            for fmt in ("%Y%m%dT%H%M%SZ", "%Y%m%d%H%M%S", "%Y-%m-%dT%H:%M:%SZ"):
                try:
                    parsed.append(datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc))
                    break
                except ValueError:
                    pass
        return max(parsed) if parsed else datetime.now(timezone.utc)
