#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from nus_lease.hdb import fetch_recent_approvals


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch recent HDB rental approvals and normalize them.")
    parser.add_argument(
        "--months",
        type=int,
        default=3,
        help="Number of latest available months to keep. Default: 3",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/raw/hdb_rentals.json"),
        help="Output JSON path.",
    )
    args = parser.parse_args()
    payload = fetch_recent_approvals(args.out, months=args.months)
    print(f"Wrote {payload['meta']['filtered_record_count']} HDB approval rows to {args.out}")


if __name__ == "__main__":
    main()
