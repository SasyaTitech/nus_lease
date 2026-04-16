#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from nus_lease.propertyguru import parse_propertyguru_html


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse PropertyGuru search-result HTML files that were exported from a real browser session."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/raw/propertyguru_html"),
        help="Directory containing saved PropertyGuru HTML pages.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/raw/propertyguru_listings.json"),
        help="Output JSON path.",
    )
    args = parser.parse_args()

    records = []
    pages = []
    for html_path in sorted(args.input_dir.glob("*.html")):
        parsed = parse_propertyguru_html(html_path)
        pages.append(parsed["meta"])
        records.extend(parsed["records"])

    output = {
        "meta": {
            "source": "PropertyGuru browser-export HTML",
            "page_count": len(pages),
            "record_count": len(records),
        },
        "pages": pages,
        "records": records,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} parsed listing records to {args.out}")


if __name__ == "__main__":
    main()
