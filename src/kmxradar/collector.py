from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import logging
import os
import shutil
import tempfile
import zipfile

from .cluster import cluster_articles
from .config import ASSETS_DIR, DATA_DIR, editorial_config
from .discover import discover_all
from .extract import enrich_article
from .models import Cluster
from .utils import utcnow_iso
from .verify import verify_cluster

LOG = logging.getLogger(__name__)


def _rank(cluster: Cluster) -> float:
    # Deterministic intake ranking. This is NOT a probability of truth.
    return (
        cluster.verification_score
        + min(0.20, len(cluster.independent_domains) * 0.025)
        + min(0.12, len(cluster.articles) * 0.01)
        + (0.10 if cluster.primary_source_present else 0.0)
        + (0.05 if cluster.high_trust_domains else 0.0)
    )


def _eligible(cluster: Cluster) -> bool:
    # ChatGPT will independently research again. Reject obvious one-source noise.
    return len(cluster.independent_domains) >= 2 or cluster.primary_source_present


def _enrich(cluster: Cluster, limit: int) -> None:
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


def _source_record(article, excerpt_chars: int) -> dict:
    text = (article.text or article.description or "").strip()
    return {
        "title": article.title,
        "url": article.url,
        "domain": article.domain,
        "language": article.language,
        "source_country": article.source_country,
        "seen_at": article.seen_at,
        "primary_hint": article.primary_hint,
        "excerpt": text[:excerpt_chars],
    }


def _chatgpt_instructions() -> str:
    return """# KMX RADAR — instrucciones para ChatGPT

Este ZIP es un expediente de entrada generado automáticamente. No publiques ni redactes basándote solo en el ZIP.

Tu trabajo:
1. revisa los candidatos;
2. investiga nuevamente en la web;
3. prioriza fuentes primarias/oficiales y documentos originales;
4. comprueba fechas, lugares, cifras y contexto;
5. identifica si varias noticias dependen de una misma fuente original;
6. distingue hechos confirmados, declaraciones, inferencias e información todavía incierta;
7. selecciona solo acontecimientos realmente relevantes;
8. redacta en español claro y factual;
9. genera las imágenes/carrusel de KMX RADAR con el logo incluido;
10. prepara el paquete final siguiendo publication-package-schema.json.

Reglas editoriales:
- no inventes cifras, citas, causas, consecuencias ni nombres;
- no presentes rumores como hechos;
- no uses una fotografía sintética como si documentara un acontecimiento real;
- para política/elecciones: informa de hechos y posiciones documentadas sin apoyar, oponerte, puntuar, clasificar ni predecir ganadores;
- en salud, seguridad, conflictos, fallecimientos, acusaciones criminales o elecciones, exige verificación reforzada;
- para declarar algo FALSO/ENGAÑOSO/FUERA DE CONTEXTO, busca evidencia específica y preferentemente verificadores profesionales o fuentes primarias;
- cita las fuentes utilizadas en el caption o en la última diapositiva;
- si la información no alcanza el estándar, no prepares publicación.

Flujo recomendado con este repositorio conectado:
- genera approved/<publication_id>/publication.json;
- añade de 1 a 10 imágenes .jpg o .png;
- añade approved/<publication_id>/.ready solo al final, cuando todo esté completo y el usuario haya indicado que quiere publicarlo.
"""


def _publication_schema() -> dict:
    return {
        "schema_version": 1,
        "publication_id": "kmx-YYYYMMDD-slug",
        "source_event_id": "event-id-from-this-zip",
        "ready_to_publish": True,
        "status": "VERIFICADO|CORROBORADO|EN DESARROLLO|CONTEXTO|CORRECCIÓN",
        "headline": "Titular factual",
        "caption": "Texto final para Instagram",
        "ai_generated": True,
        "created_at": "ISO-8601 UTC",
        "sources": [{"url": "https://...", "label": "Fuente"}],
        "images": [{"path": "01-cover.jpg", "alt_text": "Descripción accesible de la imagen"}],
    }


def collect_package() -> Path:
    cfg = editorial_config()["runtime"]
    articles = discover_all()
    clusters = [verify_cluster(c) for c in cluster_articles(articles)]
    clusters = [c for c in clusters if _eligible(c)]
    clusters.sort(key=_rank, reverse=True)
    selected = clusters[: int(cfg["max_intake_events"])]

    for cluster in selected:
        _enrich(cluster, int(cfg["fetch_sources_per_cluster"]))

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = Path(os.getenv("KMX_OUTBOX_DIR", "outbox"))
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / f"kmx-radar-intake-{stamp}.zip"

    with tempfile.TemporaryDirectory(prefix="kmx-radar-intake-") as tmp:
        root = Path(tmp)
        (root / "events").mkdir(parents=True, exist_ok=True)
        (root / "brand").mkdir(parents=True, exist_ok=True)

        manifest = {
            "schema_version": 1,
            "generated_at": utcnow_iso(),
            "brand": editorial_config()["brand"],
            "event_count": len(selected),
            "note": "Verification scores are deterministic intake signals, not probabilities of truth.",
        }
        (root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        (root / "instructions.md").write_text(_chatgpt_instructions(), encoding="utf-8")
        (root / "publication-package-schema.json").write_text(
            json.dumps(_publication_schema(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        published_path = DATA_DIR / "published.json"
        if published_path.exists():
            shutil.copy2(published_path, root / "previous_posts.json")
        else:
            (root / "previous_posts.json").write_text('{"posts": []}\n', encoding="utf-8")

        for logo_name in ("logo.svg", "logo.png"):
            logo = ASSETS_DIR / logo_name
            if logo.exists():
                shutil.copy2(logo, root / "brand" / logo.name)

        excerpt_chars = int(cfg["excerpt_chars_per_source"])
        for idx, cluster in enumerate(selected, start=1):
            event_id = f"{idx:02d}-{cluster.key}"
            event_dir = root / "events" / event_id
            event_dir.mkdir(parents=True, exist_ok=True)

            sources = [_source_record(a, excerpt_chars) for a in cluster.articles[:12]]
            event = {
                "event_id": event_id,
                "category": cluster.category,
                "risk": cluster.risk,
                "canonical_title": cluster.canonical_title,
                "intake_status": cluster.status,
                "verification_signal": cluster.verification_score,
                "primary_source_present": cluster.primary_source_present,
                "independent_domains": cluster.independent_domains,
                "high_trust_domains": cluster.high_trust_domains,
                "article_count": len(cluster.articles),
                "rank_signal": round(_rank(cluster), 3),
                "sources": sources,
            }
            (event_dir / "event.json").write_text(
                json.dumps(event, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            lines = [
                f"# {cluster.canonical_title}",
                "",
                f"- Categoría: {cluster.category}",
                f"- Riesgo: {cluster.risk}",
                f"- Estado de entrada: {cluster.status}",
                f"- Dominios independientes detectados: {len(cluster.independent_domains)}",
                f"- Fuente primaria detectada: {'sí' if cluster.primary_source_present else 'no'}",
                "",
                "## Evidencia recopilada",
                "",
            ]
            for n, src in enumerate(sources, start=1):
                lines += [
                    f"### Fuente {n}: {src['domain']}",
                    f"- URL: {src['url']}",
                    f"- Título: {src['title']}",
                    f"- Fecha detectada: {src['seen_at'] or 'sin dato'}",
                    "",
                    src["excerpt"] or "[No fue posible extraer texto; revisar la URL manualmente.]",
                    "",
                ]
            (event_dir / "evidence.md").write_text("\n".join(lines), encoding="utf-8")

        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in root.rglob("*"):
                if path.is_file():
                    zf.write(path, path.relative_to(root))

    LOG.info("Created intake package with %d events: %s", len(selected), zip_path)
    return zip_path
