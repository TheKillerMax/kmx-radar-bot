from __future__ import annotations

import argparse
import json
import logging

from .instagram import get_account
from .pipeline import publish_pending, run
from .token_store import load_token, refresh_token


def main() -> int:
    parser = argparse.ArgumentParser(prog="kmx-radar")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("run")
    sub.add_parser("publish-pending")
    sub.add_parser("check-instagram")
    sub.add_parser("refresh-token")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    if args.command == "run":
        return run()
    if args.command == "publish-pending":
        return publish_pending()
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
