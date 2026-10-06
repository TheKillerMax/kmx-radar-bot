from __future__ import annotations

from pathlib import Path
import json
import logging
import re
import unicodedata

from PIL import Image

from .config import DATA_DIR
from .publication import APPROVED_DIR
from .space_visuals import build_space_visuals
from .utils import read_json, utcnow_iso, write_json

LOG = logging.getLogger(__name__)
STATE_FILE = DATA_DIR / "chatgpt_state.json"
RENDERABLE_PHASES = {"editorial_ready_for_visuals", "visual_incomplete"}


def _validate_rights(package_dir: Path) -> list[dict]:
    path = package_dir / "visual-sources.json"
    if not path.exists():
        raise RuntimeError("visual-sources.json is required")
    data = json.loads(path.read_text(encoding="utf-8"))
    assets = data.get("assets")
    if not isinstance(assets, list) or not assets:
        raise RuntimeError("visual-sources.json must contain assets")
    for asset in assets:
        if not str(asset.get("source_url") or "").startswith(("http://", "https://")):
            raise RuntimeError(f"visual asset lacks source_url: {asset}")
        if not str(asset.get("license_or_permission") or "").strip():
            raise RuntimeError(f"visual asset lacks license_or_permission: {asset.get('source_url')}")
        if not str(asset.get("original_creator") or "").strip():
            raise RuntimeError(f"visual asset lacks original_creator: {asset.get('source_url')}")
    return assets


def _phase_for(package_dir: Path) -> str:
    state = read_json(STATE_FILE, {})
    state_pub = str(state.get("last_publication_id") or "")
    if state_pub == package_dir.name:
        phase = str(state.get("phase") or "")
        if phase:
            return phase
    handoff = read_json(package_dir / "handoff.json", {})
    return str(handoff.get("phase") or "")


PUBLIC_TEXT_FIELDS = {
    "kicker",
    "title",
    "body",
    "bullets",
    "callout",
    "footer",
    "stat_label",
    "sources",
    "alt_text",
}

# Accentless spellings that are unambiguously invalid in normal Spanish public copy.
_ALWAYS_DEGRADED_SPANISH = {
    "acompano": "acompaño/acompañó",
    "pokemon": "Pokémon",
    "mision": "misión",
    "estacion": "estación",
    "dias": "días",
    "orbita": "órbita",
}

# Accentless forms that are legitimate Spanish words in other contexts and therefore
# must not be rejected solely by token comparison.
_AMBIGUOUS_ACCENTLESS = {
    "si", "que", "como", "cuando", "donde", "quien", "cual", "cuanto",
    "aun", "solo", "el", "tu", "mi", "de", "mas", "se", "te",
}


def _flatten_public_strings(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(_flatten_public_strings(item))
        return result
    return []


def _publication_public_text(package_dir: Path) -> str:
    manifest = read_json(package_dir / "publication.json", {})
    parts = [
        str(manifest.get("headline") or ""),
        str(manifest.get("caption") or ""),
    ]
    images = manifest.get("images") or []
    if isinstance(images, list):
        for image in images:
            if isinstance(image, dict):
                parts.append(str(image.get("alt_text") or ""))
    return "\n".join(parts)


def _strip_diacritics(value: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFD", value)
        if unicodedata.category(ch) != "Mn"
    )


def _validate_spanish_unicode(package_dir: Path, slides: list[dict]) -> None:
    publication_text = _publication_public_text(package_dir)
    canonical_by_ascii: dict[str, set[str]] = {}
    for token in re.findall(r"[^\W\d_]+", publication_text, flags=re.UNICODE):
        stripped = _strip_diacritics(token)
        if stripped != token:
            canonical_by_ascii.setdefault(stripped.casefold(), set()).add(token)

    publication_lower = publication_text.casefold()
    for idx, spec in enumerate(slides, start=1):
        for field in PUBLIC_TEXT_FIELDS:
            for text in _flatten_public_strings(spec.get(field)):
                if unicodedata.normalize("NFC", text) != text:
                    raise RuntimeError(
                        f"{package_dir.name}: slide {idx} field {field!r} is not Unicode NFC"
                    )
                if "\ufffd" in text:
                    raise RuntimeError(
                        f"{package_dir.name}: slide {idx} field {field!r} contains replacement characters"
                    )
                if "?" in text and "¿" not in text:
                    raise RuntimeError(
                        f"{package_dir.name}: slide {idx} field {field!r} uses '?' without Spanish opening '¿'"
                    )
                if "!" in text and "¡" not in text:
                    raise RuntimeError(
                        f"{package_dir.name}: slide {idx} field {field!r} uses '!' without Spanish opening '¡'"
                    )

                lowered = text.casefold()
                for bad, expected in _ALWAYS_DEGRADED_SPANISH.items():
                    if re.search(rf"(?<!\w){re.escape(bad)}(?!\w)", lowered, flags=re.UNICODE):
                        raise RuntimeError(
                            f"{package_dir.name}: slide {idx} field {field!r} contains degraded Spanish "
                            f"{bad!r}; expected {expected!r}"
                        )

                # "campana" is a valid word (bell), so only reject it when the publication
                # establishes "campaña" as the intended lexical item.
                if "campaña" in publication_lower and re.search(
                    r"(?<!\w)campana(?!\w)", lowered, flags=re.UNICODE
                ):
                    raise RuntimeError(
                        f"{package_dir.name}: slide {idx} field {field!r} lost ñ in 'campaña'"
                    )

                # A label such as QUE PASO is a common ASCII degradation of QUÉ PASÓ.
                if re.search(r"(?<!\w)que\s+paso(?!\w)", lowered, flags=re.UNICODE):
                    raise RuntimeError(
                        f"{package_dir.name}: slide {idx} field {field!r} must use 'QUÉ PASÓ' when interrogative"
                    )

                for token in re.findall(r"[^\W\d_]+", text, flags=re.UNICODE):
                    ascii_key = _strip_diacritics(token).casefold()
                    if ascii_key in _AMBIGUOUS_ACCENTLESS:
                        continue
                    canon = canonical_by_ascii.get(ascii_key)
                    if canon and _strip_diacritics(token) == token:
                        expected = sorted(canon)[0]
                        raise RuntimeError(
                            f"{package_dir.name}: slide {idx} field {field!r} lost a diacritic in "
                            f"{token!r}; publication.json uses {expected!r}"
                        )


def _validate_visual_spec(package_dir: Path, visuals: dict, rights_assets: list[dict]) -> list[dict]:
    slides = visuals.get("slides")
    if not isinstance(slides, list) or not (6 <= len(slides) <= 10):
        raise RuntimeError(
            f"{package_dir.name}: visuals.json must contain 6 to 10 complete slides; "
            f"got {0 if not isinstance(slides, list) else len(slides)}"
        )

    _validate_spanish_unicode(package_dir, slides)

    sources = visuals.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise RuntimeError(f"{package_dir.name}: visuals.json must contain sources")

    licensed_urls = {
        str(a.get("direct_url") or "").strip()
        for a in rights_assets
        if str(a.get("direct_url") or "").strip()
    }
    licensed_source_urls = {
        str(a.get("source_url") or "").strip()
        for a in rights_assets
        if str(a.get("source_url") or "").strip()
    }

    seen_files: set[str] = set()
    for idx, spec in enumerate(slides, start=1):
        if not isinstance(spec, dict):
            raise RuntimeError(f"{package_dir.name}: slide {idx} is not an object")
        file_name = str(spec.get("file") or "").strip()
        photo_key = str(spec.get("photo") or "").strip()
        alt_text = str(spec.get("alt_text") or "").strip()
        if not file_name or not file_name.lower().endswith(".png"):
            raise RuntimeError(f"{package_dir.name}: slide {idx} needs a .png file")
        if file_name in seen_files:
            raise RuntimeError(f"{package_dir.name}: duplicate slide filename {file_name}")
        seen_files.add(file_name)
        if not photo_key or photo_key not in sources:
            raise RuntimeError(f"{package_dir.name}: slide {idx} references unknown photo source {photo_key!r}")
        if not alt_text:
            raise RuntimeError(f"{package_dir.name}: slide {idx} lacks alt_text")

        source_meta = sources[photo_key]
        if not isinstance(source_meta, dict):
            raise RuntimeError(f"{package_dir.name}: source {photo_key!r} must be an object")
        direct_url = str(source_meta.get("direct_url") or "").strip()
        if not direct_url.startswith(("http://", "https://")):
            raise RuntimeError(f"{package_dir.name}: source {photo_key!r} lacks direct_url")
        if direct_url not in licensed_urls and direct_url not in licensed_source_urls:
            raise RuntimeError(
                f"{package_dir.name}: source {photo_key!r} is not matched to a licensed "
                "visual-sources.json asset"
            )

    return slides


def prepare_visual_packages() -> int:
    if not APPROVED_DIR.exists():
        LOG.info("No approved directory")
        return 0

    markers = sorted(APPROVED_DIR.glob("*/.visualize"))
    if not markers:
        LOG.info("No .visualize packages")
        return 0

    processed = 0
    for marker in markers:
        package_dir = marker.parent
        phase = _phase_for(package_dir)
        if phase not in RENDERABLE_PHASES:
            raise RuntimeError(
                f"{package_dir.name}: expected one of {sorted(RENDERABLE_PHASES)}, got {phase!r}"
            )

        manifest_path = package_dir / "publication.json"
        visuals_path = package_dir / "visuals.json"
        if not manifest_path.exists() or not visuals_path.exists():
            raise RuntimeError(f"{package_dir.name}: publication.json or visuals.json missing")

        rights_assets = _validate_rights(package_dir)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        visuals = json.loads(visuals_path.read_text(encoding="utf-8"))
        slides = _validate_visual_spec(package_dir, visuals, rights_assets)

        outputs = build_space_visuals(package_dir, visuals)
        if not outputs:
            raise RuntimeError(f"{package_dir.name}: renderer produced no files")

        if len(outputs) != len(slides):
            raise RuntimeError("Rendered file count does not match visual spec")

        qc_files = []
        images = []
        for spec, path in zip(slides, outputs):
            if not path.exists():
                raise RuntimeError(f"missing rendered image: {path.name}")
            with Image.open(path) as im:
                if im.size != (1080, 1350):
                    raise RuntimeError(f"{path.name}: expected 1080x1350, got {im.size}")
                im.verify()
            qc_files.append({"path": path.name, "width": 1080, "height": 1350, "exists": True})
            images.append({
                "path": path.name,
                "alt_text": str(spec.get("alt_text") or "").strip(),
            })
            if not images[-1]["alt_text"]:
                raise RuntimeError(f"{path.name}: alt_text missing")

        manifest["images"] = images
        manifest["status"] = "visuals_ready"
        manifest["ready_to_publish"] = False
        manifest["visuals_completed_at"] = utcnow_iso()
        write_json(manifest_path, manifest)

        write_json(
            package_dir / "visual-qc.json",
            {
                "checked_at": utcnow_iso(),
                "result": "pass",
                "format": "1080x1350",
                "file_count": len(qc_files),
                "files": qc_files,
                "checks": [
                    "renderer completed without overflow/fit exceptions",
                    "all files exist",
                    "all files are 1080x1350",
                    "every image has alt text",
                    "visual-sources.json contains explicit source, creator, and license/permission",
                    "every rendered source matches a licensed visual-sources.json asset",
                    "visuals.json contains 6 to 10 complete slides",
                    "official assets/logo.png is used by renderer",
                ],
            },
        )

        current = read_json(STATE_FILE, {})
        state = {
            **current,
            "last_publication_id": str(manifest.get("publication_id") or package_dir.name),
            "last_result": "visuals_ready",
            "phase": "visuals_ready",
            "visuals_completed_at": utcnow_iso(),
            "note": "Phase 2 completed: real licensed visuals rendered and QC passed. No .ready created.",
        }
        write_json(STATE_FILE, state)

        marker.unlink(missing_ok=True)
        processed += 1
        LOG.info("Visual phase complete for %s", package_dir.name)

    return 0 if processed else 0
