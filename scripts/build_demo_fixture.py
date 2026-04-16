#!/usr/bin/env python3
from __future__ import annotations

import json
import random
import argparse
from datetime import UTC, datetime
from pathlib import Path

from nus_lease.constants import BEDROOM_BUCKETS, DISTRICT_NAMES, HDB_FLAT_TYPES, HDB_TOWNS

random.seed(5)

DISTRICT_BASE_RENTS = {
    "01": 3600,
    "02": 3300,
    "03": 2900,
    "04": 3000,
    "05": 2800,
    "06": 3400,
    "07": 3300,
    "08": 2800,
    "09": 4200,
    "10": 4500,
    "11": 3900,
    "12": 2600,
    "13": 2550,
    "14": 2750,
    "15": 3200,
    "16": 2850,
    "17": 2500,
    "18": 2450,
    "19": 2400,
    "20": 2650,
    "21": 3050,
    "22": 2250,
    "23": 2150,
    "24": 1900,
    "25": 2050,
    "26": 2600,
    "27": 2250,
    "28": 2350,
}

BUCKET_OFFSETS = {
    "Studio / 1BR": 0,
    "2BR": 950,
    "3BR": 1600,
    "4BR+": 2350,
    "Unknown": 1200,
}


def build_condo_rows() -> list[dict]:
    rows = []
    for district, district_name in DISTRICT_NAMES.items():
        district_base = DISTRICT_BASE_RENTS[district]
        for bucket in BEDROOM_BUCKETS:
            base = district_base + BUCKET_OFFSETS[bucket]
            transaction_median = round(base + random.randint(-140, 160), 2)
            listing_median = round(transaction_median * (1.02 + random.random() * 0.14), 2)
            listing_count = max(3, 30 - BEDROOM_BUCKETS.index(bucket) * 5 + (int(district) % 5))
            transaction_count = max(2, 20 - BEDROOM_BUCKETS.index(bucket) * 4 + (int(district) % 4))
            delta = round(listing_median - transaction_median, 2)
            premium_pct = round(delta / transaction_median, 4)
            rows.append(
                {
                    "district": district,
                    "district_name": district_name,
                    "segment": "non-landed",
                    "bedroom_bucket": bucket,
                    "listing_median": listing_median,
                    "transaction_median": transaction_median,
                    "delta": delta,
                    "premium_pct": premium_pct,
                    "listing_count": listing_count,
                    "transaction_count": transaction_count,
                    "transaction_project_count": max(0, transaction_count - 1),
                    "listing_layout_medians": (
                        {"2BR": listing_median, "2BR2BA": round(listing_median * 1.04, 2)}
                        if bucket == "2BR"
                        else {}
                    ),
                }
            )
    return rows


def build_hdb_rows() -> list[dict]:
    rows = []
    for town_index, town in enumerate(HDB_TOWNS, start=1):
        for flat_index, flat_type in enumerate(HDB_FLAT_TYPES, start=1):
            base = 1050 + town_index * 36 + flat_index * 210
            median_rent = round(base + random.randint(-80, 120), 2)
            approval_count = max(4, 58 - flat_index * 6 + (town_index % 8))
            if flat_type == "1-RM" and town not in {"ANG MO KIO", "BEDOK", "BUKIT MERAH", "CENTRAL AREA", "GEYLANG", "KALLANG/WHAMPOA", "TOA PAYOH"}:
                median_rent = None
                approval_count = 0
            rows.append(
                {
                    "town": town,
                    "flat_type": flat_type,
                    "median_rent": median_rent,
                    "approval_count": approval_count,
                }
            )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a synthetic dashboard fixture.")
    parser.add_argument(
        "--sync-processed",
        action="store_true",
        help="Also write the demo payload to data/processed/market_snapshot.json.",
    )
    args = parser.parse_args()

    payload = {
        "meta": {
            "generated_at": datetime.now(UTC).isoformat(),
            "mode": "demo",
            "hdb_meta": {
                "source": "HDB Renting Out of Flats from Jan 2021",
                "window_months": 3,
                "latest_available_month": "2026-03-01",
                "window_start": "2026-01-01",
            },
            "notes": [
                "This file is synthetic and exists only so the dashboard can render before live data is wired in.",
                "Run the ingestion scripts to replace it with real URA, PropertyGuru, and HDB-derived data.",
                "2BR2BA is only available on the listing side. URA transactions do not expose bathroom counts.",
                "The condo map merges official URA planning-area boundaries into a D01-D28 district proxy layer.",
                "The HDB mode uses one official source only: recent HDB rental approvals aggregated by town and flat type.",
            ],
        },
        "condo": {
            "districts": build_condo_rows(),
            "district_names": DISTRICT_NAMES,
            "bedroom_buckets": BEDROOM_BUCKETS,
            "segments": ["non-landed"],
        },
        "hdb": {
            "towns": build_hdb_rows(),
            "town_names": HDB_TOWNS,
            "flat_types": HDB_FLAT_TYPES,
        },
    }
    outputs = [Path("data/fixtures/demo_market_snapshot.json")]
    if args.sync_processed:
        outputs.append(Path("data/processed/market_snapshot.json"))
    for out in outputs:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote demo fixture to {out}")


if __name__ == "__main__":
    main()
