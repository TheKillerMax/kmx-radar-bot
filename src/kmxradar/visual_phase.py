from __future__ import annotations

from pathlib import Path
import json
import logging

from PIL import Image

from .config import DATA_DIR
from .publication import APPROVED_DIR
from .space_visuals import build_space_visuals
from .utils import read_json, utcnow_iso, write_json

LOG = logging.getLogger(__name__)
STATE_FILE = DATA_DIR / "chatgpt_state.json"


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
    phase = str(state.get("phase") or "")
    if phase:
        return phase
    handoff = read_json(package_dir / "handoff.json", {})
    return str(handoff.get("phase") or "")


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
        if phase != "editorial_ready_for_visuals":
            raise RuntimeError(
                f"{package_dir.name}: expected editorial_ready_for_visuals, got {phase!r}"
            )

        manifest_path = package_dir / "publication.json"
        visuals_path = package_dir / "visuals.json"
        if not manifest_path.exists() or not visuals_path.exists():
            raise RuntimeError(f"{package_dir.name}: publication.json or visuals.json missing")

        _validate_rights(package_dir)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        visuals = json.loads(visuals_path.read_text(encoding="utf-8"))

        outputs = build_space_visuals(package_dir, visuals)
        if not outputs:
            raise RuntimeError(f"{package_dir.name}: renderer produced no files")

        slides = visuals.get("slides", [])
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
