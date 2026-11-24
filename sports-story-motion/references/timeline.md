# Timeline and setup

## Create a project

Start with `assets/demo/timeline.json`. Place the job JSON and media together and update paths relative to the JSON. Use forward slashes in JSON paths on Windows. You can point to a map JPG, a photo, an illustration, a logo PNG with transparency, or user-supplied WAV/MP3. The demo includes actual club crests, an archival illustration card with a team photograph, and synthesized sound effects. Orange and gold highlight metropolitan counties. The city labels and crests identify the two cities and their clubs. The glowing line is an illustrative connector.

Use Python 3.10+ and Pillow with RAQM so Thai vowels and marks shape correctly. Install an FFmpeg build with libx264 and make it reachable on PATH. On Windows, `winget install -e --id Gyan.FFmpeg` is one way to install FFmpeg. Open a new terminal afterwards. From the skill folder run:

```powershell
py -m pip install -r requirements.txt
py scripts/render.py assets/demo/timeline.json preview.mp4
```

## JSON fields

| Field | How it works |
|---|---|
| `scenes` | Ordered list of scenes. Each needs `seconds` and a `background`. |
| `background` | Set exactly one of `image` (JPG/PNG), `color` (hex), or `sequence` (directory of portrait JPG/PNG frames). An image may also use the RGBA `tint` field, for example `#17151288`. |
| `camera` | Keys with local scene time `at` and any of `x`, `y`, `zoom`, `tilt`, and `bearing`. Center defaults to `.5, .5`, zoom to `1`, and angles to zero. Tilt is 0–58° and bearing rotates clockwise. The camera clamps its footprint to the image, so add room around the main subject. |
| `transition` | Local scene's entrance crossfade in seconds, overlapping the tail of the previous scene. Subtract overlaps when timing the full video and audio. |
| `layers` | Scene-local draw order, back to front. `overlays` at the document level use global time and screen coordinates. |
| `captions` | Ordered, nonoverlapping entries with global `start`, `end`, and `text`. Explicit `\n` breaks help Thai. Override position or style via `caption_style` or per caption. These entries are the SRT source. |
| `audio` | An optional audio file with final narration and/or a mixed bed. It is padded or trimmed to video duration. |

Coordinate origin is top left. For `space: "map"`, use 0 to 1 fractions of the original background still that move with pan and zoom. For `space: "screen"` (default), use 0 to 1 fractions of the output frame. Size for image overlays is a fraction of output width. Font, stroke, dash, and arrow sizing follow a 1080-pixel-wide reference. Text and image sizes are screen-relative even when their centers follow the map. At `tilt: 0` the image is overhead. Tilt and bearing project the same map image and its map-space overlays through a perspective camera. Raised region geometry is separate from the terrain depicted in the satellite image.

## Layers and motion

| Layer | Main fields |
|---|---|
| `image` | `file`, `width`, `x`, `y`. Use transparent PNGs for logos or cutouts. |
| `text` | `text`, `x`, `y`. Optional `style` fields `size`, `stroke`, `color`, `outline`, `box`, `font`. Alternate fonts should support the intended script. |
| `area` | `points` as `[[x,y], ...]` or `polygons` as an array of polygons with an outer ring followed by optional holes. Include `fill`, optional `outline`, `width`, `glow`, and `texture` (0–1). Use RGBA hex for translucent highlighting, for example `#ff4610f0`. Animate map-space `height` from 0 to roughly 30–60 reference pixels during tilt to reveal shaded sides. |
| `route` | `points`, `color`, `width`. Optional `dash: [on, off]`, `dash_speed` in reference pixels per second, `glow` RGBA, and `arrow: true`. |
| Moving object | Add `follow` to an image with the same point list as its route. Animate `progress` from 0 to 1. `orient: true` turns an illustration whose original forward direction is right. Leave extra route points at bends for smoother turning. |

Set `start` and `end` for visibility bounds. Add `keys` with strictly increasing `at` times and properties `x`, `y`, `scale`, `angle`, `opacity`, `progress`, and `height` (0–250 reference pixels). A text or image layer can use the same height to follow a raised area. Keep an important symbol or label inside a safe margin through the whole move. Unspecified properties carry forward. The easing on each destination key controls the interval leading up to it. Use `smooth` for drift, `out` for entrances, `linear` to keep a moving object's speed steady, and `in` to accelerate toward a cut. Start with `{"at":0,"opacity":0}` for a fade-in. For precise composition render a PNG at the key moment before rendering the whole video.

For a persistent channel logo, add an `image` to global `overlays` with your transparent PNG path and screen-relative placement. The sample uses real team crests as subjects documented by the clip. Keep captions around 65–72% of frame height and reserve space at the bottom and right side for the social app. Keep lettering away from bright graphics. Avoid moving every element at once. Let a key label hold long enough to read it.

## Fit a real boundary to an image

Export or obtain a WGS84 GeoJSON polygon, and use the actual EPSG:3857 image extent from the map export. Convert it into an area layer, then paste the returned object into the scene's `layers`.

```sh
python scripts/geojson_area.py boundary.geojson area.json --bounds WEST SOUTH EAST NORTH
```

`--where FIELD VALUE` selects a feature from a collection. `--lonlat-bounds` accepts west, south, east, north in degrees if those are the corners of a Web Mercator still. Bounds must reflect the final crop. For a globe or a perspective Earth Studio image, key overlays visually against the actual rendered frames.

## Google Earth Studio source option

Export a 1080×1920 still or a zero-padded portrait image sequence from Google Earth Studio. To use a sequence, set `"background": {"sequence":"earth-frames", "fps":30}`, match the actual source FPS and clip duration, and keep the frames in one folder in filename order. Sequence frames keep their embedded credits and authored camera. Use screen coordinates for overlays on a sequence. If a label has to follow a ground point through a moving shot, check it on multiple frames and key its x/y for the shot. Set the output FPS to the source FPS for one output frame per source frame.

Use the source's publication terms for the planned use. Choose Earth Studio's credit position before export and preserve all visible Google Earth and imagery provider credits. If using a still with a virtual camera move, check the credit through the entire shot. You can use a full portrait frame at zoom 1 to preserve its framing.

- [Google Earth Studio export instructions](https://earth.google.com/studio/docs/making-animations/rendering/)
- [Google Earth Studio attribution](https://earth.google.com/studio/docs/attribution/)
- [Google Geo Guidelines for Earth content](https://about.google/brand-resource-center/products-and-services/geo-guidelines/)

## Demo map attribution

Sentinel-2 cloudless by EOX IT Services GmbH (Contains modified Copernicus Sentinel data 2016 & 2017). The demo basemaps are color-graded crops of Web Mercator exports showing Great Britain and northwest England under CC BY 4.0. The example uses England’s boundary and metropolitan county boundaries for Merseyside and Greater Manchester. Shape coordinates are simplified for the video. Contains OS data © Crown copyright and database right and ONS data under the Open Government Licence.

- [Sentinel-2 cloudless](https://s2maps.eu/)
- [EOX](https://eox.at/)
- [EOX license and attribution](https://cloudless.eox.at/documentation/license)
- [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

- [England boundary · ONS Countries, December 2024 BUC](https://www.data.gov.uk/dataset/8580e329-83c9-4646-bf93-d0411f00c53a/countries-december-2024-boundaries-uk-buc)
- [Metropolitan county boundaries · ONS Upper Tier Local Authorities, December 2022 BGC](https://www.data.gov.uk/dataset/241ccfc9-9319-4ee2-9ef1-ddb422843fcf/counties-and-unitary-authorities-inc-metropolitan-counties-december-2022-boundaries-uk-bgc)
- [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)
- [Liverpool F.C. crest source](https://en.wikipedia.org/wiki/File:Liverpool_FC.svg) and [Manchester United F.C. crest source](https://en.wikipedia.org/wiki/File:Manchester_United_FC_crest.svg). The club marks are included as small editorial identifiers for the documented teams and are trademarks of the respective clubs.
- [Liverpool F.C. first-season team photograph, 1892–1893](https://commons.wikimedia.org/wiki/File:Liverpool_1892-1893.jpg). Public domain archival photo. The demo adds a cool tint and caption frame.
