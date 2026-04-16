#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from nus_lease.constants import DISTRICT_NAMES, PLANNING_AREA_TO_DISTRICT
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


def nearest_assignment(
    centroid: tuple[float, float],
    planning_area: str,
    assigned_subzones: list[dict],
) -> str | None:
    same_area = [subzone for subzone in assigned_subzones if subzone["planning_area"] == planning_area]
    if not same_area:
        return None

    def distance_sq(candidate: dict) -> float:
        x1, y1 = centroid
        x2, y2 = candidate["centroid"]
        return (x1 - x2) ** 2 + (y1 - y2) ** 2

    return min(same_area, key=distance_sq)["district"]


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
        default=Path("data/processed/subzone_district_assignments.json"),
        help="Output subzone assignment debug JSON.",
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
    for subzone in subzones:
        if subzone["district_counts"]:
            district = subzone["district_counts"].most_common(1)[0][0]
            method = "transaction-majority"
        else:
            district = nearest_assignment(subzone["centroid"], subzone["planning_area"], assigned_subzones)
            if district:
                method = "nearest-subzone"
            else:
                district = PLANNING_AREA_TO_DISTRICT.get(subzone["planning_area"])
                method = "planning-area-fallback"
        subzone["district"] = district
        subzone["method"] = method
        if district:
            assigned_subzones.append(subzone)

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

    assignment_debug = {
        "meta": {
            "subzone_count": len(subzones),
            "assigned_subzone_count": len(assigned_subzones),
            "unique_transaction_points": len(unique_points),
            "unmatched_transaction_points": unmatched_points,
        },
        "records": [
            {
                "subzone_name": subzone["subzone_name"],
                "planning_area": subzone["planning_area"],
                "district": subzone.get("district"),
                "method": subzone.get("method"),
                "district_counts": dict(subzone["district_counts"]),
            }
            for subzone in subzones
        ],
    }

    args.out_geojson.parent.mkdir(parents=True, exist_ok=True)
    args.out_points.parent.mkdir(parents=True, exist_ok=True)
    args.out_assignments.parent.mkdir(parents=True, exist_ok=True)
    args.out_geojson.write_text(json.dumps(district_geojson, ensure_ascii=False, indent=2), encoding="utf-8")
    args.out_points.write_text(json.dumps({"records": district_point_rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    args.out_assignments.write_text(json.dumps(assignment_debug, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote district polygons to {args.out_geojson}")
    print(f"Wrote district label points to {args.out_points}")
    print(f"Wrote assignment debug file to {args.out_assignments}")


if __name__ == "__main__":
    main()
