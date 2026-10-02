from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

from .config import editorial_config
from .models import Cluster
from .utils import numeric_tokens

LOG = logging.getLogger(__name__)


def _evidence(cluster: Cluster) -> str:
    cfg = editorial_config()["runtime"]
    max_chars = int(cfg["max_source_chars_for_llm"])
    blocks: list[str] = []
    for idx, article in enumerate(cluster.articles[: int(cfg["fetch_sources_per_cluster"])], start=1):
        text = article.text or article.description or article.title
        text = re.sub(r"\s+", " ", text).strip()[:max_chars]
        blocks.append(
            f"FUENTE {idx}\nDOMINIO: {article.domain}\nTÍTULO: {article.title}\nTEXTO: {text}"
        )
    return "\n\n".join(blocks)


def _fallback(cluster: Cluster) -> dict[str, Any]:
    domains = cluster.independent_domains[:4]
    return {
        "headline": cluster.canonical_title[:105],
        "summary": (
            f"Diversos medios informan sobre este acontecimiento. KMX RADAR lo clasifica como "
            f"{cluster.status.lower()} tras contrastar {len(cluster.independent_domains)} fuentes independientes."
        ),
        "known": [
            f"La información aparece en {len(cluster.independent_domains)} dominios independientes.",
            ("Existe una fuente primaria u oficial entre las referencias." if cluster.primary_source_present
             else "No se ha identificado una fuente primaria directa entre las referencias disponibles."),
        ],
        "unknown": ["Los detalles pueden cambiar a medida que aparezcan nuevas fuentes."],
        "source_domains": domains,
    }


def _load_model():
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    model_id = os.getenv("KMX_MODEL_ID") or editorial_config()["llm"]["model_id"]
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
    )
    model.eval()
    return tokenizer, model


def _extract_json(raw: str) -> dict[str, Any] | None:
    match = re.search(r"\{.*\}", raw, flags=re.S)
    if not match:
        return None
    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def compose_with_llm(cluster: Cluster) -> dict[str, Any]:
    if not editorial_config()["llm"].get("enabled", True):
        return _fallback(cluster)

    evidence = _evidence(cluster)
    if not evidence.strip():
        return _fallback(cluster)

    system = (
        "Eres editor de KMX RADAR, una cuenta informativa neutral. Redacta solo con los hechos contenidos "
        "en las fuentes suministradas. No inventes nombres, cifras, causas, citas ni consecuencias. Distingue "
        "hechos confirmados de incertidumbre. En política y elecciones, describe hechos y posiciones sin "
        "recomendar, apoyar, oponerte, puntuar ni predecir ganadores. No copies más de 8 palabras consecutivas "
        "de ninguna fuente. Devuelve solo JSON válido en español."
    )
    user = f"""
CATEGORÍA: {cluster.category}
ESTADO EDITORIAL: {cluster.status}
FUENTES INDEPENDIENTES: {len(cluster.independent_domains)}
FUENTE PRIMARIA: {cluster.primary_source_present}

EVIDENCIA:
{evidence}

Devuelve exactamente esta estructura:
{{
  "headline": "titular factual de máximo 95 caracteres",
  "summary": "2 frases, máximo 320 caracteres en total",
  "known": ["2 o 3 hechos muy breves"],
  "unknown": ["0 a 2 aspectos todavía inciertos"],
  "source_domains": {json.dumps(cluster.independent_domains[:5], ensure_ascii=False)}
}}
""".strip()

    try:
        tokenizer, model = _load_model()
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt")
        cfg = editorial_config()["llm"]
        output = model.generate(
            **inputs,
            max_new_tokens=int(cfg["max_new_tokens"]),
            do_sample=False,
            temperature=None,
            top_p=None,
            pad_token_id=tokenizer.eos_token_id,
        )
        decoded = tokenizer.decode(output[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True)
        payload = _extract_json(decoded)
        if payload and validate_editorial(payload, evidence):
            payload["source_domains"] = cluster.independent_domains[:5]
            return payload
        LOG.warning("LLM output rejected by validator")
    except Exception as exc:
        LOG.warning("LLM composition failed: %s", exc)

    return _fallback(cluster)


def validate_editorial(payload: dict[str, Any], evidence: str) -> bool:
    required = {"headline", "summary", "known", "unknown", "source_domains"}
    if not required.issubset(payload):
        return False
    if not isinstance(payload["headline"], str) or not 8 <= len(payload["headline"]) <= 120:
        return False
    if not isinstance(payload["summary"], str) or len(payload["summary"]) > 420:
        return False
    if not isinstance(payload["known"], list) or not isinstance(payload["unknown"], list):
        return False

    composed = " ".join(
        [payload["headline"], payload["summary"]]
        + [str(x) for x in payload["known"]]
        + [str(x) for x in payload["unknown"]]
    )
    allowed_numbers = numeric_tokens(evidence)
    output_numbers = numeric_tokens(composed)
    if output_numbers - allowed_numbers:
        return False
    return True


def build_caption(cluster: Cluster, editorial: dict[str, Any]) -> str:
    known = "\n".join(f"• {x}" for x in editorial.get("known", [])[:3])
    unknowns = editorial.get("unknown", [])[:2]
    unknown_block = ""
    if unknowns:
        unknown_block = "\n\n🔎 POR CONFIRMAR\n" + "\n".join(f"• {x}" for x in unknowns)
    sources = " · ".join(editorial.get("source_domains") or cluster.independent_domains[:5])
    caption = (
        f"📡 KMX RADAR | {cluster.category}\n\n"
        f"{editorial['headline']}\n\n"
        f"{editorial['summary']}\n\n"
        f"✅ QUÉ SABEMOS\n{known}"
        f"{unknown_block}\n\n"
        f"Estado: {cluster.status}\n"
        f"Fuentes contrastadas: {sources}\n\n"
        f"@kmxradar · Detectamos lo que importa"
    )
    return caption[: editorial_config()["instagram"]["caption_max_chars"]]
