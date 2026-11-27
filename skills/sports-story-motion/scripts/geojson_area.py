#!/usr/bin/env python3
"""Convert a GeoJSON WGS84 polygon to normalized coordinates on a Web Mercator still."""
import argparse
import json
import math
from pathlib import Path

RADIUS = 6378137


def mercator(lon, lat):
    if not -180 <= lon <= 180 or not -85.05113 <= lat <= 85.05113:
        raise ValueError("coordinates must use WGS84 longitude and latitude")
    return RADIUS*math.radians(lon), RADIUS*math.asinh(math.tan(math.radians(lat)))


def project(lon, lat, bounds):
    left, bottom, right, top = bounds
    x, y = mercator(lon, lat)
    return [round((x-left)/(right-left), 7), round((top-y)/(top-bottom), 7)]


def polygon_parts(document):
    kind = document["type"]
    if kind == "Polygon":
        return [document["coordinates"]]
    if kind == "MultiPolygon":
        return document["coordinates"]
    if kind == "Feature":
        return polygon_parts(document["geometry"])
    if kind == "FeatureCollection":
        return [part for feature in document["features"] for part in polygon_parts(feature)]
    raise ValueError(f"expected polygon geometry, found {kind}")


def convert(document, bounds):
    left, bottom, right, top = bounds
    if not left < right or not bottom < top:
        raise ValueError("image bounds must be ordered west, south, east, north")
    polygons = []
    for part in polygon_parts(document):
        polygon = []
        for ring in part:
            if ring and ring[0] == ring[-1]:
                ring = ring[:-1]
            points = [project(lon, lat, bounds) for lon, lat, *_ in ring]
            if len(set(map(tuple, points))) >= 3:
                polygon.append(points)
            elif not polygon:
                break
        if polygon:
            polygons.append(polygon)
    if not polygons:
        raise ValueError("no nonempty polygons in the input")
    return polygons


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    bounds = parser.add_mutually_exclusive_group(required=True)
    bounds.add_argument("--bounds", nargs=4, type=float, metavar=("WEST", "SOUTH", "EAST", "NORTH"),
                        help="image extent in EPSG:3857 meters")
    bounds.add_argument("--lonlat-bounds", nargs=4, type=float, metavar=("WEST", "SOUTH", "EAST", "NORTH"),
                        help="image extent in WGS84 longitude/latitude, for a Web Mercator raster")
    parser.add_argument("--where", nargs=2, metavar=("FIELD", "VALUE"), help="choose a single GeoJSON feature")
    args = parser.parse_args()
    try:
        document = json.loads(args.source.read_text(encoding="utf-8-sig"))
        if args.where:
            field, value = args.where
            if document["type"] != "FeatureCollection":
                raise ValueError("--where needs a FeatureCollection")
            matches = [feature for feature in document["features"]
                       if str(feature["properties"].get(field)) == value]
            if len(matches) != 1:
                raise ValueError(f"--where matched {len(matches)} features, expected one")
            document = matches[0]
        extent = args.bounds
        if args.lonlat_bounds:
            west, south, east, north = args.lonlat_bounds
            extent = (*mercator(west, south), *mercator(east, north))
        area = {"type": "area", "space": "map", "polygons": convert(document, extent),
                "fill": "#ff4a15ed", "outline": "#ffe2ab", "texture": .25}
        args.output.write_text(json.dumps(area, ensure_ascii=False, separators=(",", ":"))+"\n", encoding="utf-8")
    except (KeyError, TypeError, ValueError, OSError) as error:
        parser.exit(1, f"Boundary conversion failed: {error}\n")


if __name__ == "__main__":
    main()
