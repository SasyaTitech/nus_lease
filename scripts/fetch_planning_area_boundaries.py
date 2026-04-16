#!/usr/bin/env python3
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

DATASET_ID = "d_2cc750190544007400b2cfd5d7f53209"
CATALOG_URL = f"https://api-open.data.gov.sg/v1/public/api/datasets/{DATASET_ID}/poll-download"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json,text/plain,*/*",
}


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def fetch_text(url: str) -> str:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read().decode("utf-8")


def main() -> None:
    out = Path("data/raw/planning_area_boundaries.geojson")
    out.parent.mkdir(parents=True, exist_ok=True)

    payload = fetch_json(CATALOG_URL)
    if payload.get("code") != 0:
        raise SystemExit(f"Failed to fetch dataset download URL: {payload}")

    download_url = payload["data"]["url"]
    content = fetch_text(download_url)

    out.write_text(content, encoding="utf-8")
    print(f"Wrote planning area GeoJSON to {out}")


if __name__ == "__main__":
    main()
