from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from .aggregation import bedroom_bucket, listing_layout_bucket, normalize_district

DISTRICT_PATTERN = re.compile(r"\bD(?:ISTRICT\s*)?(\d{2})\b", re.IGNORECASE)
MONEY_PATTERN = re.compile(r"(?:S\$|\$)\s*([\d,]+(?:\.\d+)?)")
BED_PATTERN = re.compile(r"\b(studio|\d+)\s*(?:bed|bedroom|bedrooms)\b", re.IGNORECASE)
BATH_PATTERN = re.compile(r"\b(\d+)\s*(?:bath|bathroom|bathrooms)\b", re.IGNORECASE)
SQFT_PATTERN = re.compile(r"\b([\d,]+)\s*sq\.?\s*ft\b|\b([\d,]+)\s*sqft\b", re.IGNORECASE)
DATE_PATTERN = re.compile(r"Listed on\s+([A-Za-z]{3,9}\s+\d{1,2},\s+\d{4})", re.IGNORECASE)


class PropertyGuruBlocked(RuntimeError):
    pass


@dataclass
class PropertyGuruSnapshot:
    source_url: str
    fetched_at: str
    html_path: Path


def fetch_search_pages(
    urls: list[str],
    output_dir: Path,
    headless: bool = True,
    storage_state: str | None = None,
    wait_ms: int = 8000,
) -> list[PropertyGuruSnapshot]:
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshots = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        context_kwargs = {"locale": "en-SG", "timezone_id": "Asia/Singapore"}
        if storage_state:
            context_kwargs["storage_state"] = storage_state
        context = browser.new_context(**context_kwargs)
        page = context.new_page()
        page.set_extra_http_headers({"Accept-Language": "en-SG,en;q=0.9"})
        for index, url in enumerate(urls, start=1):
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(wait_ms)
            except PlaywrightError as exc:
                raise PropertyGuruBlocked(f"Failed to load {url}: {exc}") from exc
            title = page.title().strip()
            body_text = page.locator("body").inner_text()[:400]
            if "security verification" in body_text.lower() or title.lower() == "just a moment...":
                raise PropertyGuruBlocked(
                    "PropertyGuru presented a Cloudflare challenge. "
                    "Use a real browser session and export HTML manually or pass a warmed storage state."
                )
            slug = re.sub(r"[^a-z0-9]+", "-", url.lower()).strip("-")[-80:]
            html_path = output_dir / f"{index:03d}-{slug}.html"
            html_path.write_text(page.content(), encoding="utf-8")
            snapshots.append(
                PropertyGuruSnapshot(
                    source_url=url,
                    fetched_at=datetime.now(UTC).isoformat(),
                    html_path=html_path,
                )
            )
        context.close()
        browser.close()
    return snapshots


def _walk_json(node: Any):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk_json(value)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_json(item)


def _normalize_price(raw: Any) -> float | None:
    if raw is None:
        return None
    match = MONEY_PATTERN.search(str(raw))
    if match:
        return float(match.group(1).replace(",", ""))
    text = str(raw).replace(",", "").strip()
    try:
        return float(text)
    except ValueError:
        return None


def _extract_script_candidates(soup: BeautifulSoup) -> list[dict]:
    candidates = []
    for script in soup.find_all("script"):
        text = script.string or script.get_text()
        if not text:
            continue
        if script.get("type") == "application/ld+json":
            try:
                payload = json.loads(text)
            except json.JSONDecodeError:
                continue
            for node in _walk_json(payload):
                if any(key in node for key in ["price", "numberOfRooms", "numberOfBedrooms", "offers", "floorSize"]):
                    candidates.append(node)
            continue
        if "__NEXT_DATA__" in text:
            payload_match = re.search(r'__NEXT_DATA__"\s*type="application/json">\s*(\{.*\})\s*<', text, re.S)
            if not payload_match:
                continue
            try:
                payload = json.loads(payload_match.group(1))
            except json.JSONDecodeError:
                continue
            for node in _walk_json(payload):
                if any(key in node for key in ["price", "bedrooms", "bathrooms", "propertyType", "listingType"]):
                    candidates.append(node)
    return candidates


def _candidate_to_listing(candidate: dict, source_url: str) -> dict | None:
    url = candidate.get("url") or candidate.get("link")
    name = candidate.get("name") or candidate.get("title")
    bedrooms = candidate.get("numberOfRooms") or candidate.get("numberOfBedrooms") or candidate.get("bedrooms")
    bathrooms = candidate.get("numberOfBathroomsTotal") or candidate.get("bathrooms")
    floor_size = None
    if isinstance(candidate.get("floorSize"), dict):
        floor_size = candidate["floorSize"].get("value")
    else:
        floor_size = candidate.get("floorSize") or candidate.get("area")

    offers = candidate.get("offers") if isinstance(candidate.get("offers"), dict) else {}
    address = candidate.get("address") if isinstance(candidate.get("address"), dict) else {}
    location_text = " ".join(
        str(part)
        for part in [
            address.get("streetAddress"),
            address.get("addressLocality"),
            address.get("addressRegion"),
            candidate.get("location"),
            candidate.get("district"),
        ]
        if part
    )
    district = _extract_district(f"{name or ''} {location_text} {source_url}")
    price = _normalize_price(candidate.get("price") or offers.get("price"))
    if not price and not bedrooms and not bathrooms:
        return None
    return {
        "source": "propertyguru",
        "source_url": source_url,
        "url": url,
        "title": name,
        "district": district,
        "rent": price,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "size_sqft": floor_size,
        "property_type": candidate.get("propertyType") or candidate.get("@type"),
        "segment": "non-landed",
        "listed_on": None,
        "bedroom_bucket": bedroom_bucket(bedrooms),
        "layout_bucket": listing_layout_bucket(bedrooms, bathrooms),
    }


def _extract_district(text: str) -> str | None:
    match = DISTRICT_PATTERN.search(text)
    if match:
        return match.group(1)
    slug_match = re.search(r"-d(\d{2})(?:\b|/)", text, re.IGNORECASE)
    if slug_match:
        return slug_match.group(1)
    return None


def _extract_dom_candidates(soup: BeautifulSoup, source_url: str) -> list[dict]:
    listings = []
    selectors = [
        "article",
        "li",
        "[data-testid*='listing']",
        "[class*='listing-card']",
        "[class*='ListingCard']",
    ]
    seen = set()
    for selector in selectors:
        for node in soup.select(selector):
            text = " ".join(node.stripped_strings)
            if "$" not in text:
                continue
            if "bed" not in text.lower() and "studio" not in text.lower():
                continue
            anchor = node.find("a", href=True)
            href = anchor["href"] if anchor else None
            key = (href, text[:120])
            if key in seen:
                continue
            seen.add(key)

            price_match = MONEY_PATTERN.search(text)
            bed_match = BED_PATTERN.search(text)
            bath_match = BATH_PATTERN.search(text)
            size_match = SQFT_PATTERN.search(text)
            date_match = DATE_PATTERN.search(text)
            district = _extract_district(text) or _extract_district(source_url)
            if not price_match:
                continue
            bedrooms = None
            if bed_match:
                bedrooms = "0" if bed_match.group(1).lower() == "studio" else bed_match.group(1)
            listings.append(
                {
                    "source": "propertyguru",
                    "source_url": source_url,
                    "url": href,
                    "title": anchor.get_text(strip=True) if anchor else None,
                    "district": district,
                    "rent": float(price_match.group(1).replace(",", "")),
                    "bedrooms": bedrooms,
                    "bathrooms": bath_match.group(1) if bath_match else None,
                    "size_sqft": (size_match.group(1) or size_match.group(2)).replace(",", "") if size_match else None,
                    "property_type": "Condominium",
                    "segment": "non-landed",
                    "listed_on": date_match.group(1) if date_match else None,
                    "bedroom_bucket": bedroom_bucket(bedrooms),
                    "layout_bucket": listing_layout_bucket(bedrooms, bath_match.group(1) if bath_match else None),
                }
            )
    return listings


def parse_propertyguru_html(html_path: Path, source_url: str | None = None) -> dict:
    source_url = source_url or html_path.name
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")

    structured = []
    for candidate in _extract_script_candidates(soup):
        listing = _candidate_to_listing(candidate, source_url)
        if listing:
            structured.append(listing)

    dom = _extract_dom_candidates(soup, source_url)

    deduped = {}
    for row in structured + dom:
        if not row.get("rent"):
            continue
        key = row.get("url") or f"{row.get('title')}|{row.get('rent')}|{row.get('district')}|{row.get('bedrooms')}|{row.get('bathrooms')}"
        deduped[key] = row

    return {
        "meta": {
            "source_url": source_url,
            "parsed_at": datetime.now(UTC).isoformat(),
            "record_count": len(deduped),
            "district_hint": _extract_district(source_url),
        },
        "records": list(deduped.values()),
    }
