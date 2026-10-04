from __future__ import annotations

from pathlib import Path
import json
import logging

from .config import DATA_DIR
from .publication import APPROVED_DIR, _validate_manifest
from .utils import read_json, utcnow_iso, write_json
from .visual_phase import _validate_rights, _validate_visual_spec

LOG = logging.getLogger(__name__)
CHATGPT_STATE_FILE = DATA_DIR / "chatgpt_state.json"
FINAL_STATUSES = {"VERIFICADO", "CORROBORADO", "EN DESARROLLO", "CONTEXTO", "CORRECCIÓN"}


def _update_state_for(publication_id: str, **updates) -> bool:
    state = read_json(CHATGPT_STATE_FILE, {})
    if str(state.get("last_publication_id") or "") != publication_id:
        return False
    changed = False
    for key, value in updates.items():
        if state.get(key) != value:
            state[key] = value
            changed = True
    if changed:
        write_json(CHATGPT_STATE_FILE, state)
    return changed


def _validate_visual_qc(package_dir: Path, manifest: dict) -> None:
    qc_path = package_dir / "visual-qc.json"
    if not qc_path.exists():
        raise RuntimeError(f"{package_dir.name}: visual-qc.json missing")
    qc = json.loads(qc_path.read_text(encoding="utf-8"))
    if qc.get("result") != "pass":
        raise RuntimeError(f"{package_dir.name}: visual QC did not pass")

    images = manifest.get("images")
    if not isinstance(images, list) or not (6 <= len(images) <= 10):
        raise RuntimeError(f"{package_dir.name}: expected 6 to 10 final images")
    if qc.get("file_count") != len(images):
        raise RuntimeError(f"{package_dir.name}: visual QC count does not match publication images")

    qc_files = {
        str(item.get("path") or ""): item
        for item in (qc.get("files") or [])
        if isinstance(item, dict)
    }
    for item in images:
        path_name = str(item.get("path") or "")
        file_path = package_dir / path_name
        if not path_name or not file_path.exists():
            raise RuntimeError(f"{package_dir.name}: missing final image {path_name!r}")
        row = qc_files.get(path_name)
        if not row or row.get("width") != 1080 or row.get("height") != 1350 or row.get("exists") is not True:
            raise RuntimeError(f"{package_dir.name}: QC mismatch for {path_name}")


def _validate_publishable_package(package_dir: Path, manifest: dict) -> None:
    errors = _validate_manifest(package_dir, manifest)
    if errors:
        raise RuntimeError(f"{package_dir.name}: {'; '.join(errors)}")
    if str(manifest.get("status") or "") not in FINAL_STATUSES:
        raise RuntimeError(f"{package_dir.name}: publication status is not final")
    _validate_visual_qc(package_dir, manifest)
    assets = _validate_rights(package_dir)
    visuals_path = package_dir / "visuals.json"
    if not visuals_path.exists():
        raise RuntimeError(f"{package_dir.name}: visuals.json missing")
    visuals = json.loads(visuals_path.read_text(encoding="utf-8"))
    _validate_visual_spec(package_dir, visuals, assets)


def reconcile_receipts() -> int:
    changed = 0
    if not APPROVED_DIR.exists():
        return 0
    for receipt_path in APPROVED_DIR.glob("*/.published.json"):
        package_dir = receipt_path.parent
        receipt = read_json(receipt_path, {})
        publication_id = str(receipt.get("publication_id") or package_dir.name)
        instagram = receipt.get("instagram") or {}
        if (package_dir / ".ready").exists():
            (package_dir / ".ready").unlink(missing_ok=True)
            changed += 1
        if _update_state_for(
            publication_id,
            phase="published",
            last_result="published",
            last_media_id=instagram.get("media_id"),
            published_at=receipt.get("published_at"),
            note="Pipeline reconciler confirmed the Instagram receipt and publication history.",
        ):
            changed += 1
    return changed


def reconcile_visual_markers() -> int:
    created = 0
    if not APPROVED_DIR.exists():
        return 0

    for package_dir in sorted(p for p in APPROVED_DIR.iterdir() if p.is_dir()):
        if (package_dir / ".published.json").exists() or (package_dir / ".visualize").exists():
            continue
        manifest_path = package_dir / "publication.json"
        visuals_path = package_dir / "visuals.json"
        rights_path = package_dir / "visual-sources.json"
        if not (manifest_path.exists() and visuals_path.exists() and rights_path.exists()):
            continue

        manifest = read_json(manifest_path, {})
        if manifest.get("ready_to_publish") is not False:
            continue
        if str(manifest.get("status") or "") != "editorial_ready_for_visuals":
            continue
        handoff = read_json(package_dir / "handoff.json", {})
        if str(handoff.get("phase") or "") == "superseded":
            continue

        publication_id = str(manifest.get("publication_id") or package_dir.name)
        try:
            assets = _validate_rights(package_dir)
            visuals = json.loads(visuals_path.read_text(encoding="utf-8"))
            _validate_visual_spec(package_dir, visuals, assets)
        except Exception as exc:
            LOG.warning("Visual marker not created for %s: %s", package_dir.name, exc)
            _update_state_for(
                publication_id,
                phase="visual_incomplete",
                last_result="visual_incomplete",
                note=f"Visual package validation failed before rendering: {exc}",
            )
            continue

        (package_dir / ".visualize").write_text(
            f"auto-reconciled: {utcnow_iso()}\n",
            encoding="utf-8",
        )
        created += 1
        LOG.info("Created missing .visualize marker for %s", package_dir.name)
    return created


def reconcile_publish_markers() -> int:
    created = 0
    if not APPROVED_DIR.exists():
        return 0

    for package_dir in sorted(p for p in APPROVED_DIR.iterdir() if p.is_dir()):
        if (package_dir / ".published.json").exists() or (package_dir / ".ready").exists():
            continue
        manifest_path = package_dir / "publication.json"
        if not manifest_path.exists():
            continue
        manifest = read_json(manifest_path, {})
        if manifest.get("ready_to_publish") is not True:
            continue

        publication_id = str(manifest.get("publication_id") or package_dir.name)
        try:
            _validate_publishable_package(package_dir, manifest)
        except Exception as exc:
            LOG.warning("Publish marker not created for %s: %s", package_dir.name, exc)
            _update_state_for(
                publication_id,
                phase="publish_blocked",
                last_result="publish_blocked",
                note=f"Automated publish preflight failed: {exc}",
            )
            continue

        (package_dir / ".ready").write_text(
            f"auto-reconciled: {utcnow_iso()}\n",
            encoding="utf-8",
        )
        _update_state_for(
            publication_id,
            phase="publishing",
            last_result="publishing",
            note="Pipeline reconciler created the missing publish marker after all preflight checks passed.",
        )
        created += 1
        LOG.info("Created missing .ready marker for %s", package_dir.name)
    return created


def reconcile_pipeline() -> int:
    receipts = reconcile_receipts()
    visual_markers = reconcile_visual_markers()
    publish_markers = reconcile_publish_markers()
    LOG.info(
        "Pipeline reconciliation complete: receipts=%d visual_markers=%d publish_markers=%d",
        receipts,
        visual_markers,
        publish_markers,
    )
    return 0
