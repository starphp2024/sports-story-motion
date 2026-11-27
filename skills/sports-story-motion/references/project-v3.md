# Editable project format v3

Keep project.json, geo.json, geo/ and media/ together. Paths inside the project are relative to its folder. The canonical example is assets/panama/project.json. Everything is editable; keep an untouched original copy.

| Field | Meaning |
|---|---|
| schema_version | 3; use legacy render.py for older timelines |
| topic / title_screen / answer_screen / question | Topic, short mobile title, answer and one main question |
| duration / fps / aspect | Measured audio duration rounded up to a frame / 30 / 9:16 or 16:9 |
| origin | WGS84 [longitude,latitude] local scene origin |
| colors | ocean, highlight and route colors |
| maps | id, WGS84 bounds [west,south,east,north], XYZ zoom; terrain:true and dem_zoom for height data |
| terrain | mode:dem-mesh and vertical_exaggeration (1–20); record the real value |
| countries | Natural Earth ADM0_A3 code, Thai name, WGS84 location, start, flag_at, zoom_at, end; optional project-relative flag file |
| camera | Increasing absolute seconds at, center [lon,lat], span_km, tilt in degrees, bearing; smooth easing; no word-count retiming |
| routes | id, kind actual/illustrative, WGS84 points, reveal start/end, color; actual requires verified:true and source URL |
| objects | icon or supplied asset, route id, start/end, screen width; follows path and turns in projected screen direction |
| labels | text, location [lon,lat], start/end |
| mechanism | Optional Panama lock schematic start/end; not terrain or a scale model |
| captions | Nonoverlapping start/end/text in absolute seconds from actual audio; max two short lines |
| audio | Imported Google AI Studio file, measured duration, SHA-256, actual observed model/voice and real review flags |
| sync | Exact audio SHA-256 used for visual-cue review |
| watermark | null by default; if requested: requested:true, file, x,y,width as frame fractions, opacity,start,end |
| sources | Claim/source records |
| route_note | Visible explanation of route accuracy |
| render_status | Preview or final input; renderer reports encode/review status separately |

prepare_geo.py creates matching texture/height arrays and source records. Terrain vertices and geographic anchors share Mercator coordinates; height uses metres with latitude scale correction and explicit exaggeration. Moving objects use ground-path distance, then terrain height and the current camera projection. Label/icon size remains screen-relative.

The default terrain grid is 129×129. Blue Marble imagery lacks lock-scale detail. Add higher-resolution licensed imagery with correct Mercator bounds as a separate input layer rather than upscaling and claiming more detail. Antimeridian is not supported in a single bounds rectangle.

The current infographic renderer has one continuous geographic shot and an optional lock schematic. For other specialized mechanisms, extend the player or compose a verified sequence through the legacy renderer. It does not automatically invent a new mechanism from a topic string.

render.mjs writes MP4, SRT, six sample PNGs and .qa.json. It refuses final export without reviewed, hash-linked AI Studio audio and SRT. The QA status remains awaiting-human-review after a successful encode. Do not confuse technical success with content approval.
