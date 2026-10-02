from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"
ASSETS_DIR = ROOT / "assets"


def load_yaml(name: str) -> dict[str, Any]:
    path = CONFIG_DIR / name
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected object in {path}")
    return data


def editorial_config() -> dict[str, Any]:
    return load_yaml("editorial.yml")


def query_config() -> dict[str, Any]:
    return load_yaml("queries.yml")


def source_config() -> dict[str, Any]:
    return load_yaml("sources.yml")


def rss_config() -> dict[str, Any]:
    return load_yaml("rss.yml")
