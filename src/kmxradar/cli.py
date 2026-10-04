from __future__ import annotations

import argparse
import json
import logging

from .collector import collect_package
from .instagram import get_account
from .media_prepare import prepare_ready_packages
from .publication import publish_ready_packages
from .reconcile import reconcile_pipeline
from .token_store import load_token, refresh_token
from .visual_phase import prepare_visual_packages


def main() -> int:
    parser = argparse.ArgumentParser(prog="kmx-radar")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("collect")
    sub.add_parser("prepare-approved")
    sub.add_parser("prepare-visuals")
    sub.add_parser("publish-approved")
    sub.add_parser("reconcile-pipeline")
    sub.add_parser("check-instagram")
    sub.add_parser("refresh-token")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if args.command == "collect":
        path = collect_package()
        print(path)
        return 0
    if args.command == "prepare-approved":
        return prepare_ready_packages()
    if args.command == "prepare-visuals":
        return prepare_visual_packages()
    if args.command == "publish-approved":
        return publish_ready_packages()
    if args.command == "reconcile-pipeline":
        return reconcile_pipeline()
    if args.command == "check-instagram":
        payload = get_account(load_token())
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    if args.command == "refresh-token":
        refresh_token()
        print("Token refreshed successfully")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
