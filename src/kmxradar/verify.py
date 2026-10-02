from __future__ import annotations

from .config import editorial_config, source_config
from .models import Cluster


def _matches(domain: str, configured: str) -> bool:
    domain = domain.lower().strip(".")
    configured = configured.lower().strip(".")
    return domain == configured or domain.endswith("." + configured)


def _is_government_like(domain: str) -> bool:
    return (
        domain.endswith(".gov")
        or ".gov." in domain
        or ".gob." in domain
        or domain.endswith(".gob.cl")
        or domain.endswith(".gob.es")
        or domain.endswith(".gc.ca")
        or domain.endswith(".gov.uk")
    )


def verify_cluster(cluster: Cluster) -> Cluster:
    cfg = source_config()
    runtime = editorial_config()["runtime"]
    primary_cfg = cfg.get("primary_domains", [])
    high_cfg = cfg.get("high_trust_domains", [])
    factcheck_cfg = cfg.get("factcheck_domains", [])

    domains = sorted({a.domain.lower() for a in cluster.articles if a.domain})
    primary_domains = [
        d for d in domains
        if _is_government_like(d)
        or any(_matches(d, p) for p in primary_cfg)
        or any(a.domain == d and a.primary_hint for a in cluster.articles)
    ]
    high_domains = [d for d in domains if any(_matches(d, p) for p in high_cfg)]
    factcheck_domains = [d for d in domains if any(_matches(d, p) for p in factcheck_cfg)]

    cluster.independent_domains = domains
    cluster.primary_source_present = bool(primary_domains)
    cluster.high_trust_domains = high_domains

    n_domains = len(domains)
    n_high = len(high_domains)
    article_count = len(cluster.articles)

    score = 0.15
    score += min(0.36, n_domains * 0.09)
    score += min(0.18, article_count * 0.025)
    score += min(0.18, n_high * 0.06)
    if primary_domains:
        score += 0.22
    if n_domains == 1:
        score -= 0.18
    if article_count >= 8 and n_domains >= 4:
        score += 0.05
    score = max(0.0, min(1.0, score))
    cluster.verification_score = round(score, 3)

    min_domains = int(runtime["minimum_independent_domains"])
    if cluster.risk == "high":
        threshold = float(runtime["publish_threshold_high_risk"])
        domain_rule = n_domains >= min_domains and (
            cluster.primary_source_present
            or (n_domains >= int(runtime["high_risk_minimum_domains_without_primary"]) and n_high >= 2)
        )
    else:
        threshold = float(runtime["publish_threshold_low_risk"])
        domain_rule = n_domains >= min_domains or (cluster.primary_source_present and n_domains >= 2)

    # Fact-checking labels are higher-risk than ordinary summaries. Requiring
    # multiple specialist fact-check outlets helps avoid auto-publishing a
    # "FALSO" style conclusion from generic coverage alone.
    if cluster.category == "VERIFICACIÓN":
        domain_rule = domain_rule and len(factcheck_domains) >= 2 and n_domains >= 3
        threshold = max(threshold, 0.86)

    cluster.publishable = bool(score >= threshold and domain_rule)
    if cluster.publishable:
        cluster.status = "VERIFICADO" if cluster.primary_source_present else "CORROBORADO"
    elif score >= 0.58 and n_domains >= 2:
        cluster.status = "EN DESARROLLO"
    else:
        cluster.status = "SIN CONFIRMAR"
    return cluster
