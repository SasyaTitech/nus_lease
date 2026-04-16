from __future__ import annotations

import json
import os
import urllib.parse
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

import requests

from .aggregation import bedroom_bucket, normalize_district, segment_from_property_type
from .time_utils import quarter_refs_for_window, rolling_month_window

URA_TOKEN_URL = "https://eservice.ura.gov.sg/uraDataService/insertNewToken/v1"
URA_DATA_URL = "https://eservice.ura.gov.sg/uraDataService/invokeUraDS/v1"


class URAError(RuntimeError):
    pass


@dataclass
class URARentalClient:
    access_key: str

    def _request_json(self, url: str, headers: dict[str, str]) -> dict:
        merged_headers = {
            "Accept": "application/json",
            "User-Agent": "curl/8.5.0",
            **headers,
        }
        response = requests.get(url, headers=merged_headers, timeout=60)
        response.raise_for_status()
        try:
            return response.json()
        except json.JSONDecodeError as exc:
            raise URAError(f"URA returned a non-JSON response for {url}: {response.text[:240]}") from exc

    def get_daily_token(self) -> str:
        payload = self._request_json(URA_TOKEN_URL, {"AccessKey": self.access_key})
        token = payload.get("Result")
        if payload.get("Status") != "Success" or not token:
            raise URAError(f"URA token request failed: {payload}")
        return token

    def fetch_rental_contracts(self, ref_period: str, token: str) -> dict:
        query = urllib.parse.urlencode({"service": "PMI_Resi_Rental", "refPeriod": ref_period})
        url = f"{URA_DATA_URL}?{query}"
        payload = self._request_json(url, {"AccessKey": self.access_key, "Token": token})
        if payload.get("Status") != "Success":
            raise URAError(f"URA rental request failed for {ref_period}: {payload}")
        return payload


def load_access_key_from_env() -> str:
    access_key = os.environ.get("URA_ACCESS_KEY", "").strip()
    if not access_key:
        raise URAError("Missing URA_ACCESS_KEY. Register on URA and export the access key before fetching.")
    return access_key


def parse_ura_lease_month(value: str) -> date:
    if len(value) != 4 or not value.isdigit():
        raise ValueError(f"Invalid leaseDate: {value}")
    month = int(value[:2])
    year = 2000 + int(value[2:])
    return date(year, month, 1)


def flatten_rental_payload(payload: dict, fetched_at: datetime | None = None) -> list[dict]:
    rows = []
    fetched_at = fetched_at or datetime.now(UTC)
    for project_row in payload.get("Result", []):
        project = project_row.get("project")
        street = project_row.get("street")
        x_coord = project_row.get("x")
        y_coord = project_row.get("y")
        for rental in project_row.get("rental", []):
            lease_month = parse_ura_lease_month(rental["leaseDate"])
            property_type = rental.get("propertyType")
            rows.append(
                {
                    "source": "ura",
                    "fetched_at": fetched_at.isoformat(),
                    "lease_month": lease_month.isoformat(),
                    "project": project,
                    "street": street,
                    "x": x_coord,
                    "y": y_coord,
                    "district": normalize_district(rental.get("district")),
                    "property_type": property_type,
                    "segment": segment_from_property_type(property_type),
                    "bedrooms": rental.get("noOfBedRoom"),
                    "bedroom_bucket": bedroom_bucket(rental.get("noOfBedRoom")),
                    "rent": float(rental["rent"]),
                    "area_sqft_range": rental.get("areaSqft"),
                    "area_sqm_range": rental.get("areaSqm"),
                }
            )
    return rows


def fetch_recent_rentals(
    out_path: Path,
    months: int = 3,
    as_of: date | None = None,
) -> dict:
    as_of = as_of or date.today()
    access_key = load_access_key_from_env()
    client = URARentalClient(access_key)
    token = client.get_daily_token()
    ref_periods = quarter_refs_for_window(as_of, months)

    raw_payloads = []
    flattened_rows = []
    for ref_period in ref_periods:
        payload = client.fetch_rental_contracts(ref_period, token)
        raw_payloads.append({"ref_period": ref_period, "payload": payload})
        flattened_rows.extend(flatten_rental_payload(payload))

    window_start, window_end = rolling_month_window(as_of, months)
    filtered_rows = [
        row
        for row in flattened_rows
        if window_start <= date.fromisoformat(row["lease_month"]) <= window_end
    ]

    output = {
        "meta": {
            "source": "URA Private Residential Properties Rental Contract API",
            "as_of": as_of.isoformat(),
            "window_months": months,
            "window_start": window_start.isoformat(),
            "window_end": window_end.isoformat(),
            "ref_periods": ref_periods,
            "raw_record_count": len(flattened_rows),
            "filtered_record_count": len(filtered_rows),
        },
        "records": filtered_rows,
        "raw_payloads": raw_payloads,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    return output
