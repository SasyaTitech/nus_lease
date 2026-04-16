#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from nus_lease.constants import DISTRICT_NAMES
from nus_lease.onemap import OneMapClient, OneMapError, load_token_from_env
from nus_lease.postal_districts import district_from_postal_code
from nus_lease.svy21 import SVY21


def load_payload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_polygons(geometry: dict) -> list[list[list[list[float]]]]:
    if geometry["type"] == "Polygon":
        return [geometry["coordinates"]]
    if geometry["type"] == "MultiPolygon":
        return geometry["coordinates"]
    return []


def polygon_bbox(polygons: list[list[list[list[float]]]]) -> tuple[float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []
    for polygon in polygons:
        for ring in polygon:
            for x_coord, y_coord in ring:
                xs.append(x_coord)
                ys.append(y_coord)
    return min(xs), min(ys), max(xs), max(ys)


def polygon_centroid(polygons: list[list[list[list[float]]]]) -> tuple[float, float]:
    xs: list[float] = []
    ys: list[float] = []
    for polygon in polygons:
        for ring in polygon:
            for x_coord, y_coord in ring:
                xs.append(x_coord)
                ys.append(y_coord)
    return sum(xs) / len(xs), sum(ys) / len(ys)


def point_in_ring(x_coord: float, y_coord: float, ring: list[list[float]]) -> bool:
    inside = False
    for index, (x1, y1) in enumerate(ring):
        x2, y2 = ring[(index + 1) % len(ring)]
        if (y1 > y_coord) == (y2 > y_coord):
            continue
        intersection_x = (x2 - x1) * (y_coord - y1) / (y2 - y1) + x1
        if x_coord < intersection_x:
            inside = not inside
    return inside


def point_in_polygons(x_coord: float, y_coord: float, polygons: list[list[list[list[float]]]]) -> bool:
    for polygon in polygons:
        if not point_in_ring(x_coord, y_coord, polygon[0]):
            continue
        if any(point_in_ring(x_coord, y_coord, hole) for hole in polygon[1:]):
            continue
        return True
    return False


def load_override_map(path: Path | None) -> dict[tuple[str, str], str]:
    if path is None or not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    overrides: dict[tuple[str, str], str] = {}
    for key, value in payload.items():
        if isinstance(value, str) and "|" in key:
            planning_area, subzone_name = key.split("|", 1)
            overrides[(planning_area, subzone_name)] = value.zfill(2)
        elif isinstance(value, dict):
            for subzone_name, district in value.items():
                if isinstance(district, str):
                    overrides[(key, subzone_name)] = district.zfill(2)
    return overrides


def transaction_majority(counts: Counter, min_points: int, min_share: float) -> tuple[str | None, float]:
    if not counts:
        return None, 0.0
    top_district, top_count = counts.most_common(1)[0]
    total = sum(counts.values())
    share = top_count / total if total else 0.0
    if total < min_points or share < min_share:
        return None, share
    return top_district, share


def distinct_points(points: list[tuple[float, float]], candidate: tuple[float, float], min_distance: float = 1e-4) -> bool:
    return all((point[0] - candidate[0]) ** 2 + (point[1] - candidate[1]) ** 2 >= min_distance**2 for point in points)


def representative_points(polygons: list[list[list[list[float]]]], count: int) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    centroid = polygon_centroid(polygons)
    if point_in_polygons(centroid[0], centroid[1], polygons):
        points.append(centroid)

    min_x, min_y, max_x, max_y = polygon_bbox(polygons)
    ratios = [0.2, 0.35, 0.5, 0.65, 0.8]
    for y_ratio in ratios:
        for x_ratio in ratios:
            if len(points) >= count:
                return points
            candidate = (
                min_x + (max_x - min_x) * x_ratio,
                min_y + (max_y - min_y) * y_ratio,
            )
            if point_in_polygons(candidate[0], candidate[1], polygons) and distinct_points(points, candidate):
                points.append(candidate)

    if not points and polygons and polygons[0] and polygons[0][0]:
        first = tuple(polygons[0][0][0])
        points.append(first)
    return points[:count]


def postal_majority_lookup(
    client: OneMapClient,
    polygons: list[list[list[list[float]]]],
    probe_count: int,
    buffer: int,
) -> tuple[str | None, list[dict]]:
    district_counts: Counter = Counter()
    evidence: list[dict] = []
    for longitude, latitude in representative_points(polygons, probe_count):
        for row in client.reverse_geocode(latitude, longitude, buffer=buffer):
            postal_code = row.get("POSTALCODE") or row.get("POSTAL")
            district = district_from_postal_code(postal_code)
            if not district:
                continue
            district_counts[district] += 1
            evidence.append(
                {
                    "longitude": longitude,
                    "latitude": latitude,
                    "postal_code": postal_code,
                    "district": district,
                    "road": row.get("ROAD"),
                    "block": row.get("BLOCK"),
                    "building_name": row.get("BUILDINGNAME"),
                }
            )
    if not district_counts:
        return None, evidence
    return district_counts.most_common(1)[0][0], evidence


def first_project_point_inside(
    district: str,
    district_polygons: list[list[list[list[float]]]],
    district_points: list[tuple[float, float]],
    fallback: tuple[float, float],
) -> tuple[float, float]:
    if not district_points:
        return fallback

    avg_lon = sum(point[0] for point in district_points) / len(district_points)
    avg_lat = sum(point[1] for point in district_points) / len(district_points)
    if point_in_polygons(avg_lon, avg_lat, district_polygons):
        return avg_lon, avg_lat

    def distance_sq(point: tuple[float, float]) -> float:
        return (point[0] - avg_lon) ** 2 + (point[1] - avg_lat) ** 2

    inside_points = [point for point in district_points if point_in_polygons(point[0], point[1], district_polygons)]
    if inside_points:
        return min(inside_points, key=distance_sq)
    return fallback


def main() -> None:
    parser = argparse.ArgumentParser(description="Build better district polygons from subzones and URA transaction points.")
    parser.add_argument(
        "--subzones",
        type=Path,
        default=Path("data/raw/subzone_boundaries.geojson"),
        help="Subzone boundary GeoJSON.",
    )
    parser.add_argument(
        "--transactions",
        type=Path,
        default=Path("data/raw/ura_private_rentals.json"),
        help="Normalized URA transaction file with x/y coordinates.",
    )
    parser.add_argument(
        "--fallback-points",
        type=Path,
        default=Path("data/raw/district_centroids.json"),
        help="Fallback district label points.",
    )
    parser.add_argument(
        "--overrides",
        type=Path,
        default=Path("data/config/subzone_district_overrides.json"),
        help="Optional manual override JSON keyed by 'PLANNING AREA|SUBZONE'.",
    )
    parser.add_argument(
        "--out-geojson",
        type=Path,
        default=Path("data/processed/district_boundaries.geojson"),
        help="Output district boundary GeoJSON.",
    )
    parser.add_argument(
        "--out-points",
        type=Path,
        default=Path("data/processed/district_label_points.json"),
        help="Output district label points JSON.",
    )
    parser.add_argument(
        "--out-assignments",
        type=Path,
        default=None,
        help="Optional debug JSON path for subzone assignments.",
    )
    parser.add_argument(
        "--min-transaction-points",
        type=int,
        default=5,
        help="Minimum number of URA points required to trust transaction-majority. Default: 5.",
    )
    parser.add_argument(
        "--min-transaction-share",
        type=float,
        default=0.6,
        help="Minimum winning share required to trust transaction-majority. Default: 0.6.",
    )
    parser.add_argument(
        "--use-onemap",
        action="store_true",
        help="Use OneMap reverse geocode to resolve subzones that fail transaction-majority.",
    )
    parser.add_argument(
        "--onemap-buffer",
        type=int,
        default=60,
        help="Reverse geocode buffer in meters. Default: 60.",
    )
    parser.add_argument(
        "--onemap-probe-count",
        type=int,
        default=5,
        help="Representative points to probe inside each unresolved subzone. Default: 5.",
    )
    args = parser.parse_args()

    subzone_payload = load_payload(args.subzones)
    transaction_payload = load_payload(args.transactions)
    fallback_points_payload = load_payload(args.fallback_points)

    fallback_points = {
        row["district"]: (float(row["longitude"]), float(row["latitude"]))
        for row in fallback_points_payload.get("records", [])
        if row.get("district") and row.get("longitude") is not None and row.get("latitude") is not None
    }
    override_map = load_override_map(args.overrides)

    onemap_client = None
    if args.use_onemap:
        try:
            onemap_client = OneMapClient(load_token_from_env())
        except OneMapError as exc:
            raise SystemExit(str(exc)) from exc

    subzones: list[dict] = []
    for feature in subzone_payload.get("features", []):
        planning_area = feature["properties"].get("PLN_AREA_N")
        subzone_name = feature["properties"].get("SUBZONE_N")
        polygons = extract_polygons(feature["geometry"])
        subzones.append(
            {
                "subzone_name": subzone_name,
                "planning_area": planning_area,
                "properties": feature["properties"],
                "polygons": polygons,
                "bbox": polygon_bbox(polygons),
                "centroid": polygon_centroid(polygons),
                "district_counts": Counter(),
            }
        )

    converter = SVY21()
    unique_points: dict[tuple[float, float], dict] = {}
    for row in transaction_payload.get("records", []):
        district = row.get("district")
        x_coord = row.get("x")
        y_coord = row.get("y")
        if not district or x_coord is None or y_coord is None:
            continue
        key = (float(x_coord), float(y_coord))
        point = unique_points.get(key)
        if point is None:
            latitude, longitude = converter.to_latlon(float(y_coord), float(x_coord))
            point = unique_points[key] = {
                "longitude": longitude,
                "latitude": latitude,
                "district_counts": Counter(),
            }
        point["district_counts"][district] += 1

    district_project_points: dict[str, list[tuple[float, float]]] = defaultdict(list)
    unmatched_points = 0
    for point in unique_points.values():
        longitude = point["longitude"]
        latitude = point["latitude"]
        district = point["district_counts"].most_common(1)[0][0]
        district_project_points[district].append((longitude, latitude))
        matched = False
        for subzone in subzones:
            min_x, min_y, max_x, max_y = subzone["bbox"]
            if not (min_x <= longitude <= max_x and min_y <= latitude <= max_y):
                continue
            if point_in_polygons(longitude, latitude, subzone["polygons"]):
                subzone["district_counts"][district] += 1
                matched = True
                break
        if not matched:
            unmatched_points += 1

    assigned_subzones: list[dict] = []
    unresolved_subzones: list[dict] = []
    for subzone in subzones:
        override_key = (subzone["planning_area"], subzone["subzone_name"])
        district = override_map.get(override_key)
        evidence: list[dict] = []
        confidence = 1.0 if district else 0.0
        total_points = sum(subzone["district_counts"].values())
        if district:
            method = "manual-override"
        else:
            district, confidence = transaction_majority(
                subzone["district_counts"],
                min_points=args.min_transaction_points,
                min_share=args.min_transaction_share,
            )
            if district:
                method = "transaction-majority"
            elif onemap_client is not None:
                district, evidence = postal_majority_lookup(
                    onemap_client,
                    subzone["polygons"],
                    probe_count=args.onemap_probe_count,
                    buffer=args.onemap_buffer,
                )
                method = "postal-majority" if district else "unassigned"
                confidence = 0.0
            else:
                method = "unassigned"
        subzone["district"] = district
        subzone["method"] = method
        subzone["confidence"] = confidence
        subzone["postal_evidence"] = evidence
        subzone["transaction_total"] = total_points
        if district:
            assigned_subzones.append(subzone)
        else:
            unresolved_subzones.append(subzone)

    grouped_polygons: dict[str, list[list[list[list[float]]]]] = defaultdict(list)
    grouped_centroids: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for subzone in assigned_subzones:
        grouped_polygons[subzone["district"]].extend(subzone["polygons"])
        grouped_centroids[subzone["district"]].append(subzone["centroid"])

    district_geojson = {
        "type": "FeatureCollection",
        "features": [],
    }
    district_point_rows = []
    for district in sorted(grouped_polygons):
        polygons = grouped_polygons[district]
        fallback_point = fallback_points.get(district)
        if fallback_point is None:
            centroid_candidates = grouped_centroids[district]
            avg_x = sum(item[0] for item in centroid_candidates) / len(centroid_candidates)
            avg_y = sum(item[1] for item in centroid_candidates) / len(centroid_candidates)
            fallback_point = (avg_x, avg_y)
        point_longitude, point_latitude = first_project_point_inside(
            district,
            polygons,
            district_project_points.get(district, []),
            fallback_point,
        )

        district_geojson["features"].append(
            {
                "type": "Feature",
                "properties": {
                    "name": district,
                    "district": district,
                    "district_name": DISTRICT_NAMES.get(district, district),
                },
                "geometry": {
                    "type": "MultiPolygon",
                    "coordinates": polygons,
                },
            }
        )
        district_point_rows.append(
            {
                "district": district,
                "district_name": DISTRICT_NAMES.get(district, district),
                "longitude": point_longitude,
                "latitude": point_latitude,
            }
        )

    args.out_geojson.parent.mkdir(parents=True, exist_ok=True)
    args.out_points.parent.mkdir(parents=True, exist_ok=True)
    args.out_geojson.write_text(json.dumps(district_geojson, ensure_ascii=False, indent=2), encoding="utf-8")
    args.out_points.write_text(json.dumps({"records": district_point_rows}, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote district polygons to {args.out_geojson}")
    print(f"Wrote district label points to {args.out_points}")
    print(
        f"Assigned {len(assigned_subzones)} / {len(subzones)} subzones; "
        f"left {len(unresolved_subzones)} intentionally unassigned."
    )
    if args.out_assignments is not None:
        assignment_debug = {
            "meta": {
                "subzone_count": len(subzones),
                "assigned_subzone_count": len(assigned_subzones),
                "unassigned_subzone_count": len(unresolved_subzones),
                "unique_transaction_points": len(unique_points),
                "unmatched_transaction_points": unmatched_points,
                "min_transaction_points": args.min_transaction_points,
                "min_transaction_share": args.min_transaction_share,
                "used_onemap": bool(onemap_client),
            },
            "records": [
                {
                    "subzone_name": subzone["subzone_name"],
                    "planning_area": subzone["planning_area"],
                    "district": subzone.get("district"),
                    "method": subzone.get("method"),
                    "confidence": subzone.get("confidence"),
                    "transaction_total": subzone.get("transaction_total"),
                    "district_counts": dict(subzone["district_counts"]),
                    "postal_evidence": subzone.get("postal_evidence", []),
                }
                for subzone in subzones
            ],
        }
        args.out_assignments.parent.mkdir(parents=True, exist_ok=True)
        args.out_assignments.write_text(json.dumps(assignment_debug, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote assignment debug file to {args.out_assignments}")


if __name__ == "__main__":
    main()
