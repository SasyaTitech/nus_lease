from __future__ import annotations

from collections import defaultdict
from statistics import median
from typing import Iterable

from .constants import (
    BEDROOM_BUCKETS,
    DISTRICT_NAMES,
    HDB_FLAT_TYPES,
    HDB_TOWNS,
    PRIVATE_SEGMENTS,
)


def normalize_district(value: str | int | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    digits = "".join(ch for ch in text if ch.isdigit())
    if not digits:
        return None
    return digits.zfill(2)


def bedroom_bucket(bedrooms: str | int | None) -> str:
    if bedrooms in (None, "", "-", "NA"):
        return "Unknown"
    text = str(bedrooms).strip().lower()
    if "studio" in text:
        return "Studio / 1BR"
    digits = "".join(ch for ch in text if ch.isdigit())
    if not digits:
        return "Unknown"
    value = int(digits)
    if value <= 1:
        return "Studio / 1BR"
    if value == 2:
        return "2BR"
    if value == 3:
        return "3BR"
    return "4BR+"


def listing_layout_bucket(bedrooms: str | int | None, bathrooms: str | int | None) -> str:
    bucket = bedroom_bucket(bedrooms)
    if bucket == "2BR":
        bath_digits = "".join(ch for ch in str(bathrooms or "") if ch.isdigit())
        if bath_digits and int(bath_digits) >= 2:
            return "2BR2BA"
    return bucket


def segment_from_property_type(property_type: str | None) -> str:
    text = (property_type or "").strip().lower()
    if text in {"non-landed properties", "apartment", "condominium"}:
        return "non-landed"
    if text in {"executive condominium", "exec condo"}:
        return "executive-condo"
    if any(token in text for token in ["terrace", "semi", "detached", "landed"]):
        return "landed"
    return "non-landed"


def median_or_none(values: Iterable[float]) -> float | None:
    data = sorted(float(value) for value in values)
    return round(median(data), 2) if data else None


def aggregate_condo_snapshot(
    transaction_records: list[dict],
    listing_records: list[dict],
) -> dict:
    keyed: dict[tuple[str, str, str], dict] = {}

    for district in DISTRICT_NAMES:
        for segment in PRIVATE_SEGMENTS:
            for bucket in BEDROOM_BUCKETS:
                keyed[(district, segment, bucket)] = {
                    "district": district,
                    "district_name": DISTRICT_NAMES[district],
                    "segment": segment,
                    "bedroom_bucket": bucket,
                    "transaction_rents": [],
                    "listing_rents": [],
                    "listing_layout_rents": defaultdict(list),
                    "transaction_projects": set(),
                    "listing_count": 0,
                    "transaction_count": 0,
                }

    for row in transaction_records:
        district = normalize_district(row.get("district"))
        if not district or district not in DISTRICT_NAMES:
            continue
        segment = row.get("segment") or segment_from_property_type(row.get("property_type"))
        if segment not in PRIVATE_SEGMENTS:
            continue
        bucket = bedroom_bucket(row.get("bedrooms"))
        slot = keyed[(district, segment, bucket)]
        slot["transaction_rents"].append(float(row["rent"]))
        slot["transaction_projects"].add(row.get("project") or "")
        slot["transaction_count"] += 1

    for row in listing_records:
        district = normalize_district(row.get("district"))
        if not district or district not in DISTRICT_NAMES:
            continue
        segment = row.get("segment") or segment_from_property_type(row.get("property_type"))
        if segment not in PRIVATE_SEGMENTS:
            continue
        bucket = bedroom_bucket(row.get("bedrooms"))
        slot = keyed[(district, segment, bucket)]
        price = float(row["rent"])
        slot["listing_rents"].append(price)
        slot["listing_layout_rents"][listing_layout_bucket(row.get("bedrooms"), row.get("bathrooms"))].append(price)
        slot["listing_count"] += 1

    districts = []
    for district in DISTRICT_NAMES:
        for segment in PRIVATE_SEGMENTS:
            for bucket in BEDROOM_BUCKETS:
                slot = keyed[(district, segment, bucket)]
                transaction_median = median_or_none(slot["transaction_rents"])
                listing_median = median_or_none(slot["listing_rents"])
                delta = None
                premium_pct = None
                if transaction_median and listing_median:
                    delta = round(listing_median - transaction_median, 2)
                    premium_pct = round(delta / transaction_median, 4)
                layout_medians = {
                    name: median_or_none(values)
                    for name, values in slot["listing_layout_rents"].items()
                    if values
                }
                districts.append(
                    {
                        "district": district,
                        "district_name": DISTRICT_NAMES[district],
                        "segment": segment,
                        "bedroom_bucket": bucket,
                        "listing_median": listing_median,
                        "transaction_median": transaction_median,
                        "delta": delta,
                        "premium_pct": premium_pct,
                        "listing_count": slot["listing_count"],
                        "transaction_count": slot["transaction_count"],
                        "transaction_project_count": len(slot["transaction_projects"] - {""}),
                        "listing_layout_medians": layout_medians,
                    }
                )

    return {
        "districts": districts,
        "district_names": DISTRICT_NAMES,
        "bedroom_buckets": BEDROOM_BUCKETS,
        "segments": PRIVATE_SEGMENTS,
    }


def aggregate_hdb_snapshot(hdb_records: list[dict]) -> dict:
    keyed: dict[tuple[str, str], list[float]] = {}
    counts: dict[tuple[str, str], int] = {}

    all_towns = sorted({record["town"] for record in hdb_records} or set(HDB_TOWNS))
    all_flat_types = [flat_type for flat_type in HDB_FLAT_TYPES if any(record["flat_type"] == flat_type for record in hdb_records)]
    if not all_flat_types:
        all_flat_types = HDB_FLAT_TYPES

    for town in all_towns:
        for flat_type in all_flat_types:
            keyed[(town, flat_type)] = []
            counts[(town, flat_type)] = 0

    for row in hdb_records:
        town = row.get("town")
        flat_type = row.get("flat_type")
        if town not in all_towns or flat_type not in all_flat_types:
            continue
        rent = row.get("median_rent", row.get("rent"))
        if rent is None:
            continue
        if isinstance(rent, str):
            rent = float(rent)
        keyed[(town, flat_type)].append(float(rent))
        counts[(town, flat_type)] += int(row.get("approval_count", 1))

    towns = []
    for town in all_towns:
        for flat_type in all_flat_types:
            med = median_or_none(keyed[(town, flat_type)])
            towns.append(
                {
                    "town": town,
                    "flat_type": flat_type,
                    "median_rent": med,
                    "approval_count": counts[(town, flat_type)],
                }
            )

    return {
        "towns": towns,
        "town_names": all_towns,
        "flat_types": all_flat_types,
    }


def aggregate_market_snapshot(
    transaction_records: list[dict],
    listing_records: list[dict],
    hdb_records: list[dict],
) -> dict:
    return {
        "condo": aggregate_condo_snapshot(transaction_records, listing_records),
        "hdb": aggregate_hdb_snapshot(hdb_records),
    }
