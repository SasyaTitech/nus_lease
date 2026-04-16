#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from nus_lease.ura import fetch_recent_rentals


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch recent URA private residential rental contracts.")
    parser.add_argument(
        "--months",
        type=int,
        default=3,
        help="Rolling calendar window size, counted by month. Default: 3",
    )
    parser.add_argument(
        "--as-of",
        type=str,
        default=date.today().isoformat(),
        help="As-of date in YYYY-MM-DD. Default: today.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/raw/ura_private_rentals.json"),
        help="Output JSON path.",
    )
    args = parser.parse_args()
    payload = fetch_recent_rentals(args.out, months=args.months, as_of=date.fromisoformat(args.as_of))
    print(f"Wrote {payload['meta']['filtered_record_count']} URA records to {args.out}")


if __name__ == "__main__":
    main()
