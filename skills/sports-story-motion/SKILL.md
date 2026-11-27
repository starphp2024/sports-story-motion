---
name: sports-story-motion
description: Build Thai map-led documentaries on any topic for Reels, Shorts and TikTok. Use for full-color satellite imagery, cue-driven geographic highlights, overhead-to-tilted maps, location-anchored logos and labels, moving routes and illustrations, and MP4 with bold Thai captions and SRT.
---

# Map-led motion documentaries

Apply this visual workflow to the user's subject. The bundled Liverpool–Manchester project demonstrates timing, geographic anchoring, and visual layering.

1. **Plan the cues.** Inspect reference footage or stills for presentation and timing. Write the Thai narration, then create a cue sheet with the spoken phrase, region, camera position, visual action, start/end time, and source. A spoken reference to a place triggers a reveal of that region. Reuse the visual workflow across geographic explainers, travel, history, news, and sports. Obtain subject-specific facts and assets anew.
2. **Set up a real base map.** Use a full-color satellite still with known bounds for geographic anchors. Use verified boundaries at the appropriate scale. Express WGS84 locations on a Web Mercator still with [scripts/geojson_area.py](scripts/geojson_area.py). Confirm shorelines, visible boundaries, names, and placement against the cited source. Treat an illustrated connector separately from an actual traveled route.
3. **Reveal the place and build depth.** Start overhead with `tilt: 0`. Near the mention of a place, fade its region in over roughly 0.35–0.8 seconds. Use contrasting saturated colors, a translucent fill, and a restrained brighter outline. Preserve visible satellite texture. Hold the current place long enough to read. Then ease `tilt` to 30–46° and optionally raise selected regions using `height`. Keep the area, line, symbols and place labels registered to the same map; use `space: "map"`. Keep captions and channel branding in screen space.
4. **Add logos and illustrations at their cues.** Source the actual identifier for the entity being discussed, such as a club badge, emblem, landmark, or vehicle. Ask for the channel's PNG only if channel branding is needed and no logo was supplied. Use the supplied transparent PNG or a credited asset. Keep a relevant logo's original shape and colors. Ease in photos and illustrations when the narration mentions them. Use a small frame and a sourced caption for archive images. Animate route progress and pulse, or move a cutout along the same coordinates with `follow`.
5. **Render and align.** Read [references/timeline.md](references/timeline.md) and adapt [assets/demo/timeline.json](assets/demo/timeline.json). Use the included renderer for motion and FFmpeg for MP4. Sync to actual narration when provided, or deliver a Thai voice script with the visual cues. Keep subtitles short at comfortable reading size, use white Kanit Bold and a dark outline, and leave room for the platform UI. Output the editable JSON, 1080×1920 MP4 and UTF-8 SRT. Use Google Flow only when requested.
6. **Verify the result.** Render a flat frame, the high point of the area reveal, a tilted frame, and an illustration frame. Check caption/label separation and legibility, map registration, attribution, source use, timing, and audio. Run the full render and inspect the file with ffprobe. When the runtime lacks FFmpeg, deliver the source files and a local render command.

## Run the demo

From the folder containing this file, using Python 3.10+ and FFmpeg with H.264 on PATH:

```sh
python -m pip install -r requirements.txt
python scripts/render.py assets/demo/timeline.json preview.mp4
```

Use `--preview` for 540×960, `--frame 9.7` with a PNG filename for a still, or `--fps 60` for 60 fps. The bundled demo has sound effects and Thai captions. Assign the finished narration or mixed audio to `audio` in a production timeline.

Earth Studio portrait stills and exported frame sequences are optional inputs. See the timeline reference for hand-keying overlays on an already animated sequence and maintaining the official on-frame credits.
