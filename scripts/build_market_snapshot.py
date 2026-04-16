#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from nus_lease.aggregation import aggregate_market_snapshot


def load_records(path: Path) -> tuple[dict, list[dict]]:
    if not path.exists():
        return {}, []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("meta", {}), payload.get("records", [])


def main() -> None:
    parser = argparse.ArgumentParser(description="Combine transaction and listing data into a dashboard snapshot.")
    parser.add_argument(
        "--transactions",
        type=Path,
        default=Path("data/raw/ura_private_rentals.json"),
        help="Normalized URA transaction file.",
    )
    parser.add_argument(
        "--listings",
        type=Path,
        default=Path("data/raw/propertyguru_listings.json"),
        help="Normalized PropertyGuru listing file.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/processed/market_snapshot.json"),
        help="Output snapshot path.",
    )
    parser.add_argument(
        "--hdb",
        type=Path,
        default=Path("data/raw/hdb_rentals.json"),
        help="Normalized HDB approvals file.",
    )
    args = parser.parse_args()

    tx_meta, tx_records = load_records(args.transactions)
    listing_meta, listing_records = load_records(args.listings)
    hdb_meta, hdb_records = load_records(args.hdb)
    snapshot = aggregate_market_snapshot(tx_records, listing_records, hdb_records)
    snapshot["meta"] = {
        "generated_at": datetime.now(UTC).isoformat(),
        "transactions_meta": tx_meta,
        "listings_meta": listing_meta,
        "hdb_meta": hdb_meta,
        "notes": [
            "URA transaction data is official and reflects private residential rental contracts submitted to IRAS for Stamp Duty assessment.",
            "PropertyGuru data reflects current asking rents, not closed deals.",
            "HDB data reflects approved rental applications aggregated from the latest available months of the official HDB open dataset.",
            "Bathrooms are only reliable on the listing side. URA transactions do not expose bathroom counts.",
            "The condo map merges official URA planning-area boundaries into a D01-D28 district proxy layer.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote market snapshot to {args.out}")


if __name__ == "__main__":
    main()
