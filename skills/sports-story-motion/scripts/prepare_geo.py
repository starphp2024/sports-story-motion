#!/usr/bin/env python3
"""Fetch credited map imagery, real DEM and country boundaries for the offline renderer."""
import argparse
import hashlib
import io
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image

R = 6378137.0
LIMIT = 85.05112878
NASA = "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_ShadedRelief/default/2004-07-01/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpeg"
DEM = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
BOUNDARIES = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson"
LAKES = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_lakes.geojson"

def mercator(lon, lat):
    if not -180 <= lon <= 180 or not -LIMIT <= lat <= LIMIT:
        raise ValueError("WGS84 outside Web Mercator coverage")
    return R * math.radians(lon), R * math.asinh(math.tan(math.radians(lat)))

def tile_xy(lon, lat, z):
    return ((lon + 180) / 360 * 2**z,
            (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * 2**z)

def fetch(url, cache, records):
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / hashlib.sha256(url.encode()).hexdigest()
    if not path.exists():
        with urlopen(Request(url, headers={"User-Agent": "SportsStoryMotion/3.0 documentary toolkit"}), timeout=60) as response:
            body = response.read(40_000_001)
        if len(body) > 40_000_000:
            raise ValueError("asset exceeds 40 MB limit")
        path.write_bytes(body)
    body = path.read_bytes()
    records.append({"url": url, "sha256": hashlib.sha256(body).hexdigest()})
    return body

def mosaic(bounds, z, template, cache, records, size, elevation=False):
    west, south, east, north = bounds
    if not (-180 <= west < east <= 180 and -LIMIT <= south < north <= LIMIT):
        raise ValueError("bounds must be west,south,east,north; split antimeridian regions")
    x0, y0 = tile_xy(west, north, z)
    x1, y1 = tile_xy(east, south, z)
    left, top, right, bottom = math.floor(x0), math.floor(y0), math.ceil(x1), math.ceil(y1)
    if (right-left)*(bottom-top) > 64:
        raise ValueError("more than 64 tiles: reduce zoom or bounds")
    image = Image.new("F" if elevation else "RGB", ((right-left)*256, (bottom-top)*256))
    for y in range(top, bottom):
        for x in range(left, right):
            raw = fetch(template.format(z=z, x=x, y=y), cache, records)
            with Image.open(io.BytesIO(raw)) as tile:
                tile = tile.convert("RGB")
                if tile.size != (256, 256):
                    raise ValueError("expected 256px XYZ tiles")
                if elevation:
                    values = [r*256 + g + b/256 - 32768 for r,g,b in tile.getdata()]
                    tile = Image.new("F", (256,256))
                    tile.putdata(values)
                image.paste(tile, ((x-left)*256, (y-top)*256))
    crop = ((x0-left)*256, (y0-top)*256, (x1-left)*256, (y1-top)*256)
    return image.transform(size, Image.Transform.EXTENT, crop, Image.Resampling.BILINEAR)

def prepare(project_path):
    project_path = Path(project_path).resolve()
    p = json.loads(project_path.read_text(encoding="utf-8-sig"))
    root = project_path.parent
    out = root / "geo"
    out.mkdir(exist_ok=True)
    records = []
    cache = root / ".cache"
    maps = []
    for spec in p["maps"]:
        detail = spec.get("terrain", False)
        grid_size=spec.get('grid_size',129)
        if grid_size not in (65,129,257):raise ValueError('grid_size must be 65,129 or 257')
        size = (grid_size,grid_size)
        image = mosaic(spec["bounds"], spec["zoom"], NASA, cache, records, (1536,1536))
        image.save(out / (spec["id"] + ".jpg"), quality=94)
        data = {"id":spec["id"],"bounds":spec["bounds"],"texture":"geo/"+spec["id"]+".jpg"}
        if detail:
            dem = mosaic(spec["bounds"], spec.get("dem_zoom",9), DEM, cache, records, size, elevation=True)
            heights = [round(v,2) for v in dem.getdata()]
            if max(heights)-min(heights) < 5:
                raise ValueError("DEM is flat or invalid; do not call this terrain 3D")
            data.update({"grid":list(size),"elevation_m":heights,"mode":"dem-mesh",
                         "vertical_exaggeration":p["terrain"]["vertical_exaggeration"]})
        maps.append(data)
    country_data = json.loads(fetch(BOUNDARIES,cache,records))
    selected = []
    for country in p.get("countries",[]):
        matches = [x for x in country_data["features"] if
                   x["properties"].get("ADM0_A3")==country["code"]]
        if len(matches)!=1:
            raise ValueError("country boundary missing/ambiguous: "+country["code"])
        selected.append({"code":country["code"],"geometry":matches[0]["geometry"],
                         "source":BOUNDARIES,"scale":"Natural Earth 1:50m; not a legal boundary"})
    waters=[]
    if p.get("water_features"):
        lakes=json.loads(fetch(LAKES,cache,records))
        for spec in p["water_features"]:
            matches=[x for x in lakes["features"] if x["properties"].get("ne_id")==spec["ne_id"]]
            if len(matches)!=1:raise ValueError("water feature missing or ambiguous")
            waters.append({**spec,"geometry":matches[0]["geometry"],"source":LAKES})
    document = {"maps":maps,"countries":selected,"water_features":waters,"generated_at":datetime.now(timezone.utc).isoformat(),
                "credits":["Imagery: NASA Blue Marble / NASA GIBS (2004 composite)",
                           "Terrain Tiles: Mapzen / AWS Open Data (SRTM and other sources)",
                           "Boundaries: Natural Earth, public domain (1:50m)"],
                "sources":records}
    (root/"geo.json").write_text(json.dumps(document,ensure_ascii=False),encoding="utf-8")
    print(root/"geo.json")
    return document

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project",type=Path)
    args=parser.parse_args()
    prepare(args.project)
