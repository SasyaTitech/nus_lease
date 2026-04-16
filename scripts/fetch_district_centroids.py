#!/usr/bin/env python3
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path

from nus_lease.constants import DISTRICT_MAP_QUERIES, DISTRICT_NAMES

ONEMAP_SEARCH_URL = "https://www.onemap.gov.sg/api/common/elastic/search"


def fetch_onemap_result(query: str) -> dict:
    params = urllib.parse.urlencode(
        {
            "searchVal": query,
            "returnGeom": "Y",
            "getAddrDetails": "Y",
            "pageNum": 1,
        }
    )
    with urllib.request.urlopen(f"{ONEMAP_SEARCH_URL}?{params}", timeout=60) as response:
        payload = json.load(response)
    results = payload.get("results") or []
    if not results:
        raise RuntimeError(f"No OneMap results for {query!r}")
    return results[0]


def main() -> None:
    out = Path("data/raw/district_centroids.json")
    out.parent.mkdir(parents=True, exist_ok=True)

    records = []
    for district, query in DISTRICT_MAP_QUERIES.items():
        result = fetch_onemap_result(query)
        records.append(
            {
                "district": district,
                "district_name": DISTRICT_NAMES[district],
                "query": query,
                "searchval": result.get("SEARCHVAL"),
                "latitude": float(result["LATITUDE"]),
                "longitude": float(result["LONGITUDE"]),
                "postal": result.get("POSTAL"),
            }
        )

    out.write_text(
        json.dumps(
            {
                "meta": {
                    "source": "OneMap Search API",
                    "count": len(records),
                },
                "records": records,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Wrote district centroids to {out}")


if __name__ == "__main__":
    main()
