from __future__ import annotations

from pathlib import Path
import json
import logging

import cairosvg

from .publication import APPROVED_DIR
from .utils import write_json
from .real_visuals import build_real_visuals

LOG = logging.getLogger(__name__)


def prepare_ready_packages() -> int:
    if not APPROVED_DIR.exists():
        return 0

    ready_dirs = sorted({p.parent for p in APPROVED_DIR.glob("*/.ready")})
    for package_dir in ready_dirs:
        manifest_path = package_dir / "publication.json"
        if not manifest_path.exists():
            continue

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        changed = False

        real_config_path = package_dir / "real-visuals.json"
        if real_config_path.exists():
            real_config = json.loads(real_config_path.read_text(encoding="utf-8"))
            build_real_visuals(package_dir, real_config)
            changed = True

        for item in manifest.get("images", []):
            path = package_dir / str(item.get("path") or "")
            if path.suffix.lower() != ".svg":
                continue
            if not path.exists():
                raise FileNotFoundError(path)

            png_path = path.with_suffix(".png")
            cairosvg.svg2png(
                url=str(path),
                write_to=str(png_path),
                output_width=1080,
                output_height=1350,
            )
            item["path"] = png_path.name
            changed = True
            LOG.info("Rendered %s -> %s", path.name, png_path.name)

        if changed:
            write_json(manifest_path, manifest)

    return 0
