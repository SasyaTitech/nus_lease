#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from nus_lease.propertyguru import PropertyGuruBlocked, fetch_search_pages


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Attempt to fetch PropertyGuru search pages with Playwright. This may be blocked by Cloudflare."
    )
    parser.add_argument(
        "--url",
        action="append",
        dest="urls",
        help="Search result URL. Repeat for multiple pages or districts.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/raw/propertyguru_html"),
        help="Where to save the HTML snapshots.",
    )
    parser.add_argument(
        "--storage-state",
        type=str,
        default=None,
        help="Optional Playwright storage-state JSON captured from a warmed real-browser session.",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Launch Chromium in headed mode.",
    )
    args = parser.parse_args()
    if not args.urls:
        raise SystemExit("Pass at least one --url.")
    try:
        snapshots = fetch_search_pages(
            urls=args.urls,
            output_dir=args.output_dir,
            headless=not args.headed,
            storage_state=args.storage_state,
        )
    except PropertyGuruBlocked as exc:
        raise SystemExit(str(exc)) from exc
    print(f"Saved {len(snapshots)} PropertyGuru HTML pages into {args.output_dir}")


if __name__ == "__main__":
    main()
