# Data, media and limitations

| Input | Source / credit | Limit |
|---|---|---|
| Imagery | NASA Blue Marble / NASA GIBS, 2004 composite | Historical 500m-class visualization. Separate city labels; individual streets, locks/buildings not guaranteed visible. Not current footage. |
| Elevation | Mapzen Terrain Tiles / AWS, SRTM and other open data | Terrarium RGB: R*256+G+B/256−32768 metres. Decode before interpolation. Water/narrow structures may be imperfect. |
| Borders | Natural Earth ne_50m_admin_0_countries | 1:50m generalization, public domain; not legal/street-scale borders. |
| Water | Natural Earth 1:10m lake polygon; Gatun ne_id 1159123579 | Lake surface is a nominal 26m illustration, not a live water-level reading. |
| Font | Kanit Bold | Keep OFL-Kanit.txt. Chromium HarfBuzz shaping; legacy requires Pillow RAQM. |
| Icons | original SVG toolkit set | Transparent consistent set; no comparison to inaccessible videos. |
| Panama flag | original SVG, four quadrants/two stars | Upper hoist white/blue-star, upper fly red, lower hoist blue, lower fly white/red-star; 3:2 aspect. Arrangement checked against [Panama Ministry of Government](https://www.mingob.gob.pa/simbolosdelanacion/bandera-nacional/), 2026-11-27. |
| Legacy demo | existing football/map assets | Preserved; credits in timeline.md. No relicensing of original media. |

- [NASA GIBS API](https://nasa-gibs.github.io/gibs-api-docs/access-basics/)
- [NASA media guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/)
- [Terrain formats](https://github.com/tilezen/joerd/blob/master/docs/formats.md)
- [Terrain registry](https://registry.opendata.aws/terrain-tiles/)
- [Natural Earth terms](https://www.naturalearthdata.com/about/terms-of-use/)
- [Natural Earth vector](https://github.com/nvkelso/natural-earth-vector)
- [Panama Canal Authority](https://pancanal.com/en/history-of-the-panama-canal/)

geo.json records each fetched URL, SHA-256 and retrieval date. Preserve visible credit. Recheck access and terms for newly selected imagery; do not inherit a blanket license assumption from old demos.

Texture/DEM share Web Mercator bounds. WGS84 overlays use the same transform. QA/project record height exaggeration. The actual displaced mesh is terrain 3D. The lock cross-section is a separate schematic, not DEM or a scale engineering simulation.

Split antimeridian regions; Web Mercator high-latitude bounds are rejected. At most 64 tiles per layer. Prepare geo.json/geo/ before offline rendering.
