---
name: sports-story-motion
description: Create Thai map documentaries and infographic animation about geography, history, travel, trade, sport and stories explained through places. Use for title and hook development, fact checking, country-and-flag reveals, anchored objects and routes, DEM terrain, Google AI Studio narration, Kanit captions and editable MP4/SRT projects.
---

# Sports Story Motion

Keep this skill separate from GeoMotion Thai. Never rename it or import that project's assumptions.
The folder containing this file is the skill root. Resolve bundled scripts/assets relative to it; media paths are relative to the project JSON.

## 1. Inspect before dependent work

- Read the brief, supplied assets and reachable references. State which videos were actually viewed. If inaccessible, request the missing opening/map/icon stills or short clip before designing a close match. Continue research/tooling. Never claim similarity without comparison.
- Run: python scripts/ssm.py doctor. Check Python, Node, FFmpeg/ffprobe, Kanit, Pillow RAQM for legacy, Chromium/WebGL2 for DEM, data availability and the user's authorized signed-in Google AI Studio browser. Do not assume all hosts expose these tools.
- Read [platforms](references/platforms.md) and [v3 format](references/project-v3.md). Probe missing capabilities and explain concrete blockers. A chat skill may plan while a local CLI renders; installation does not grant shell, WebGL, browser control or AI Studio access.
- Keep v2 timelines working with scripts/render.py. Its raster tilt and raised polygons are **2.5D**, not elevation terrain.

## 2. Research and develop the story

Verify place/country names, WGS84 coordinates, borders, routes, flags, numbers and current events with reliable primary sources. Record claim, source URL, check date and uncertainty.

Prepare five post titles, a separate short on-screen title, three hooks (question / surprising image or event / explicitly hypothetical situation), each opening visual, one main question and the answer viewers receive. Keep mobile titles short and accurate with no unverified numbers. When asked to choose, choose the clearest title/hook, briefly explain and continue.

Begin hook/title immediately within about 3–5 seconds, paired with an observable action. Give part of the answer early; each scene adds evidence, mechanism or consequence. Follow one continuous object when helpful. Pause for comprehension. Close the question fully. Add no page name, intro, CTA or repeated “wait until the end” unless requested.

Write Thai narration/storyboard. Use [Panama example](assets/panama/storyboard-th.md) as structure, never universal facts or fixed speech timing.

## 3. Create and listen to real narration

Use **Google AI Studio only**, with the user's authorized account/tools. Inspect the actual available model and voice list; never invent voice names. Direct a male Thai narrator toward a deep, serious, firm, energetic delivery: tight curious hook, slower mechanism explanation, clearly stressed answer, natural pauses, accurate names. Do not shout or read like a data list.

If tools/sign-in/quota block generation, state the blocker and continue independent work. Do not switch providers. Mark animation-only previews incomplete; never call them the completed clip.

Export the real audio, listen, correct content/pronunciation, then time captions and visuals against that exact file. Use [audio guide](references/audio-th.md) and [local caption editor](renderer/caption-editor.html). Never estimate final timings from word count. Import through scripts/ssm.py attach-audio. Review flags attest to work actually performed; they are not shortcuts around listening.

## 4. Prepare geography and objects

Default 1080×1920, 9:16, 30fps; support 1920×1080, 16:9. Let measured narration determine duration.
Use full-frame colorful detailed imagery, deep blue ocean and restrained orange/yellow/cyan highlights. Preserve mountains, rivers, coastlines, cities and credits. Verify labels/coordinates.

Country sequence: wide location → highlighted boundary at spoken mention → correct flag at its coordinate → reading hold → continuous pan/zoom/rotation → DEM terrain → labels/routes/objects. Use the same WGS84/Mercator transform for every geographic element. Flag precedes zoom.

prepare_geo.py downloads NASA imagery, Natural Earth borders and Mapzen Terrarium elevation with source URLs, timestamp and hashes. Baseline imagery is a 2004 composite, not current footage; use licensed higher-resolution imagery with matching bounds for city/street detail. Read [sources](references/data-sources.md).
True terrain requires a height mesh, recorded vertical exaggeration and lighting. Camera tilt/country extrusion is not DEM terrain. If only 2.5D works, state the mode and missing tools/data.

Bundled transparent SVGs cover ship, airplane, train, rail, car, port, city, building, dam, reservoir, flag, pin and arrow. They are a consistent original set, not reference-matched assets. Use user-supplied originals when requested. Do not use emoji for primary objects. Compare silhouette, proportions, perspective, edges, colors and shadows before claiming a match.
Reveal arrows/routes at speech cues. Distinguish actual routes (kind: actual, verified source) from explanatory connectors (kind: illustrative). Orient vehicles to paths; use smooth camera easing and avoid moving everything at once.

## 5. Compose and render

- Keep Kanit and OFL. Check Thai shaping/marks, explicit line breaks and actual caption width. Use short high-contrast captions in mobile-safe space; avoid essential labels/objects. Burn captions and export UTF-8 SRT from the same cues.
- Watermark only on explicit request using the supplied original. Preserve proportions/colors; expose position, width, opacity and interval. Required map credits are separate.
- Mix music below narration, effects at visible actions: scripts/mix_audio.py. Review for clipping, gaps and cut endings.
- Install: npm install --prefix renderer
- Install browser: npx --prefix renderer playwright install chromium
- Check WebGL: node renderer/selftest.mjs
- Prepare: python scripts/prepare_geo.py assets/panama/project.json
- Validate: python scripts/ssm.py validate PROJECT.json
- Final render: node renderer/render.mjs PROJECT.json OUTPUT.mp4
- Explicit incomplete visual test only: add --animation-only; add --preview for half resolution. Video/QA label missing narration. Do not fabricate timed narration captions.
- v2: read [timeline](references/timeline.md), then python scripts/render.py assets/demo/timeline.json preview.mp4. Existing still/sequence overlays and 60fps remain available there.

## 6. Inspect and deliver honestly

Inspect the actual MP4 in a player and ffprobe, representative frames, speech/caption sync, flag/place coordinates through camera motion, Thai marks/clipping, credits, opening-to-answer story, audio peaks/tail and safe areas.
Automated decode, stream/frame counts and caption bounds do not prove pronunciation, semantic geography or subjective visual quality. Record actual checks and limits.

Deliver platform-appropriate ZIPs, editable source/project and media manifest, Thai installation/troubleshooting guide, copyable prompts, MP4/matching SRT when completed, sources and limitations. Keep incomplete animation previews separate. Never report installation tested merely because a ZIP/manifest was generated.
