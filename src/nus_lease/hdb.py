from __future__ import annotations

import csv
import json
import urllib.request
from datetime import date
from pathlib import Path

from .time_utils import shift_month

DATASET_ID = "d_c9f57187485a850908655db0e8cfe651"
CATALOG_URL = f"https://api-open.data.gov.sg/v1/public/api/datasets/{DATASET_ID}/poll-download"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json,text/plain,*/*",
}


def parse_month(value: str) -> date:
    year, month = value.split("-")
    return date(int(year), int(month), 1)


def fetch_download_url() -> str:
    request = urllib.request.Request(CATALOG_URL, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.load(response)
    if payload.get("code") != 0:
        raise RuntimeError(f"Failed to fetch HDB dataset: {payload}")
    return payload["data"]["url"]


def fetch_recent_approvals(out_path: Path, months: int = 3) -> dict:
    download_url = fetch_download_url()
    request = urllib.request.Request(download_url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=120) as response:
        lines = response.read().decode("utf-8").splitlines()

    reader = csv.DictReader(lines)
    all_rows = list(reader)
    latest_available = max(parse_month(row["rent_approval_date"]) for row in all_rows)
    window_start = shift_month(latest_available, -(months - 1))

    filtered = []
    for row in all_rows:
        approval_month = parse_month(row["rent_approval_date"])
        if approval_month < window_start or approval_month > latest_available:
            continue
        flat_type = row["flat_type"].strip().upper()
        if flat_type == "EXECUTIVE":
            flat_type = "EXEC"
        else:
            flat_type = flat_type.replace("-ROOM", "-RM")
        filtered.append(
            {
                "source": "hdb",
                "approval_month": approval_month.isoformat(),
                "town": row["town"].strip(),
                "flat_type": flat_type,
                "block": row["block"].strip(),
                "street_name": row["street_name"].strip(),
                "rent": float(row["monthly_rent"]),
            }
        )

    output = {
        "meta": {
            "source": "HDB Renting Out of Flats from Jan 2021",
            "window_months": months,
            "latest_available_month": latest_available.isoformat(),
            "window_start": window_start.isoformat(),
            "filtered_record_count": len(filtered),
        },
        "records": filtered,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    return output
