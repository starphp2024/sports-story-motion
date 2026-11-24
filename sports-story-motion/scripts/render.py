#!/usr/bin/env python3
"""Render a motion-graphics timeline to a portrait MP4 and UTF-8 SRT."""
import argparse
from bisect import bisect_right
from functools import lru_cache
import json
import math
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory

from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageFilter, ImageFont, features

FONT = Path(__file__).resolve().parents[1] / "assets" / "fonts" / "Kanit-Bold.ttf"
EASING = {
    "linear": lambda t: t,
    "smooth": lambda t: t * t * (3 - 2 * t),
    "out": lambda t: 1 - (1 - t) ** 3,
    "in": lambda t: t ** 3,
}
LANCZOS = Image.Resampling.LANCZOS
CAMERA_FIELDS = {"x", "y", "zoom", "tilt", "bearing"}
LAYER_FIELDS = {"x", "y", "scale", "angle", "opacity", "progress", "height"}


def mix(a, b, p):
    return a + (b - a) * p


def clamp(t):
    return max(0.0, min(1.0, t))


def animate(base, keys, t):
    if not keys:
        return base
    a = base.copy()
    start = 0
    for key in keys:
        b = {**a, **{k: v for k, v in key.items() if k not in ("at", "ease")}}
        end = key["at"]
        if t < end:
            p = EASING[key.get("ease", "smooth")](clamp((t - start) / (end - start)))
            return {k: mix(a[k], v, p) for k, v in b.items()}
        a, start = b, end
    return a


@lru_cache(maxsize=32)
def load_image(path):
    with Image.open(path) as src:
        return src.convert("RGBA")


@lru_cache(maxsize=64)
def load_font(path, size):
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)


@lru_cache(maxsize=256)
def text_sprite(text, font_path, size, color, outline, stroke, box):
    font = load_font(font_path, size)
    measure = ImageDraw.Draw(Image.new("L", (1, 1)))
    spacing = round(size * .15)
    left, top, right, bottom = measure.multiline_textbbox(
        (0, 0), text, font=font, spacing=spacing, align="center", stroke_width=stroke
    )
    px, py = (round(size * .39), round(size * .22)) if box else (2, 2)
    sprite = Image.new("RGBA", (math.ceil(right-left)+2*px, math.ceil(bottom-top)+2*py))
    draw = ImageDraw.Draw(sprite)
    if box:
        draw.rounded_rectangle((0, 0, sprite.width-1, sprite.height-1), radius=py, fill=box)
    draw.multiline_text(
        (px-left, py-top), text, font=font, fill=color, spacing=spacing, align="center",
        stroke_width=stroke, stroke_fill=outline
    )
    return sprite


def paste(canvas, sprite, center, opacity=1):
    if opacity <= 0:
        return
    if opacity < 1:
        sprite = sprite.copy()
        sprite.putalpha(sprite.getchannel("A").point(lambda value: round(value * opacity)))
    x, y = center
    canvas.alpha_composite(sprite, (round(x - sprite.width / 2), round(y - sprite.height / 2)))


class Path2D:
    def __init__(self, points):
        self.points = points
        self.distances = [0.0]
        for a, b in zip(points, points[1:]):
            self.distances.append(self.distances[-1] + math.dist(a, b))
        self.length = self.distances[-1]

    def position(self, distance):
        distance = max(0.0, min(self.length, distance))
        i = min(len(self.points) - 2, bisect_right(self.distances, distance) - 1)
        a, b = self.points[i:i+2]
        span = self.distances[i+1] - self.distances[i]
        p = (distance - self.distances[i]) / span if span else 0
        return mix(a[0], b[0], p), mix(a[1], b[1], p)

    def slice(self, start, end):
        return [
            self.position(start),
            *self.points[bisect_right(self.distances, start):bisect_right(self.distances, end)],
            self.position(end),
        ]


class MapCamera:
    """Project a satellite raster and raised overlays through one perspective camera."""

    def __init__(self, size, source_size, state):
        self.w, self.h = size
        self.sw, self.sh = source_size
        self.mx, self.my = self.w/2, self.h/2
        self.distance = self.h * 1.8
        tilt = math.radians(state["tilt"])
        self.sine, self.cosine = math.sin(tilt), math.cos(tilt)
        bearing = math.radians(state["bearing"])
        self.sin_b, self.cos_b = math.sin(bearing), math.cos(bearing)
        corners = [self.ground(x-self.mx, y-self.my)
                   for x, y in ((0, 0), (0, self.h), (self.w, 0), (self.w, self.h))]
        xs, ys = zip(*corners)
        self.fit = max(self.w/self.sw * state["zoom"], self.h/self.sh * state["zoom"],
                       (max(xs)-min(xs))/self.sw, (max(ys)-min(ys))/self.sh)
        self.cx = max(-min(xs)/self.fit, min(self.sw-max(xs)/self.fit, state["x"]*self.sw))
        self.cy = max(-min(ys)/self.fit, min(self.sh-max(ys)/self.fit, state["y"]*self.sh))

    def ground(self, dx, dy):
        denominator = self.cosine + dy*self.sine/self.distance
        x = dx*self.cosine/denominator
        y = dy/denominator
        return self.cos_b*x + self.sin_b*y, -self.sin_b*x + self.cos_b*y

    def project(self, u, v, height=0):
        x, y = (u*self.sw-self.cx)*self.fit, (v*self.sh-self.cy)*self.fit
        bx, by = self.cos_b*x-self.sin_b*y, self.sin_b*x+self.cos_b*y
        z = height*self.w/1080
        depth = max(.15, 1 - (by*self.sine+z*self.cosine)/self.distance)
        return self.mx+bx/depth, self.my+(by*self.cosine-z*self.sine)/depth

    def raster(self, source):
        # Invert ground projection with one projective transform, sampled by Pillow.
        k = self.sine/self.distance
        d = self.cosine-self.my*k
        if not k and not self.sin_b and self.cos_b == 1:
            box = (self.cx-self.mx/self.fit, self.cy-self.my/self.fit,
                   self.cx+self.mx/self.fit, self.cy+self.my/self.fit)
            return source.transform((self.w, self.h), Image.Transform.EXTENT, box, Image.Resampling.BICUBIC)
        a, b = self.cos_b*self.cosine/self.fit, self.sin_b/self.fit
        e, f = -self.sin_b*self.cosine/self.fit, self.cos_b/self.fit
        coeff = (a/d, (b+self.cx*k)/d, self.cx-(a*self.mx+b*self.my)/d,
                 e/d, (f+self.cy*k)/d, self.cy-(e*self.mx+f*self.my)/d, 0, k/d)
        return source.transform((self.w, self.h), Image.Transform.PERSPECTIVE, coeff, Image.Resampling.BICUBIC)


class Renderer:
    def __init__(self, job, root, size, fps):
        self.job, self.root, self.size, self.fps = job, root, size, fps
        self.w, self.h = size
        self.unit = self.w / 1080
        self.scenes = job["scenes"]
        self.sequences = {
            i: sequence_files(root, scene["background"]["sequence"])
            for i, scene in enumerate(self.scenes) if "sequence" in scene["background"]
        }
        self.starts = []
        self.ends = []
        end = 0
        for scene in self.scenes:
            start = end - round(scene.get("transition", 0) * fps)
            end = start + round(scene["seconds"] * fps)
            self.starts.append(start)
            self.ends.append(end)
        self.frames = self.ends[-1]
        self.captions = job.get("captions", [])

    def px(self, value):
        return max(1, round(value * self.unit))

    def file(self, name):
        return str((self.root / name).resolve())

    def background(self, index, t):
        scene = self.scenes[index]
        bg = scene["background"]
        if "color" in bg:
            return Image.new("RGBA", self.size, bg["color"]), self.screen
        if index in self.sequences:
            files = self.sequences[index]
            number = min(len(files)-1, math.floor(t*bg.get("fps", self.fps) + 1e-7))
            with Image.open(files[number]) as source:
                if source.width*16 != source.height*9:
                    raise ValueError(f"sequence frame must be 9:16: {files[number].name}")
                canvas = source.convert("RGBA").resize(self.size, LANCZOS)
            return canvas, self.screen
        source = load_image(self.file(bg["image"]))
        cam = animate({"x": .5, "y": .5, "zoom": 1, "tilt": 0, "bearing": 0}, scene.get("camera"), t)
        camera = MapCamera(self.size, source.size, cam)
        canvas = camera.raster(source)
        if "tint" in bg:
            canvas = Image.alpha_composite(canvas, Image.new("RGBA", self.size, bg["tint"]))
        return canvas, camera.project

    def screen(self, x, y, height=0):
        return x * self.w, y * self.h

    def layer(self, canvas, item, t, map_xy, terrain=None):
        if t < item.get("start", 0) or t >= item.get("end", math.inf):
            return
        state = animate(
            {"x": item.get("x", .5), "y": item.get("y", .5), "scale": 1, "angle": 0,
             "opacity": item.get("opacity", 1), "progress": item.get("progress", 1),
             "height": item.get("height", 0)},
            item.get("keys"), t
        )
        alpha = clamp(state["opacity"])
        if alpha <= 0:
            return
        project = map_xy if item.get("space") == "map" else self.screen
        height = state["height"]
        xy = lambda x, y: project(x, y, height)
        position = xy(state["x"], state["y"])
        if "follow" in item:
            track = Path2D([xy(*p) for p in item["follow"]])
            distance = clamp(state["progress"]) * track.length
            position = track.position(distance)
            if item.get("orient", False):
                before, after = track.position(distance - 2), track.position(distance + 2)
                state["angle"] -= math.degrees(math.atan2(after[1]-before[1], after[0]-before[0]))
        kind = item["type"]
        if kind == "image":
            layer = load_image(self.file(item["file"]))
            scale = item["width"] * self.w * state["scale"] / layer.width
            if scale > 0:
                layer = layer.resize(
                    (max(1, round(layer.width*scale)), max(1, round(layer.height*scale))), LANCZOS
                )
                if state["angle"]:
                    layer = layer.rotate(state["angle"], resample=Image.Resampling.BICUBIC, expand=True)
                paste(canvas, layer, position, alpha)
        elif kind == "text":
            style = item.get("style", {})
            sprite = text_sprite(
                item["text"], self.file(style["font"]) if "font" in style else str(FONT),
                self.px(style.get("size", 50)), style.get("color", "#ffffff"),
                style.get("outline", "#13151c"), self.px(style.get("stroke", 3)) if style.get("stroke", 3) else 0,
                style.get("box")
            )
            if state["scale"] > 0 and state["scale"] != 1:
                sprite = sprite.resize(
                    tuple(max(1, round(d*state["scale"])) for d in sprite.size), LANCZOS
                )
            paste(canvas, sprite, position, alpha)
        elif kind == "area":
            self.area(canvas, terrain or canvas, item, project, height, alpha)
        else:
            overlay = Image.new("RGBA", self.size)
            draw = ImageDraw.Draw(overlay)
            points = [xy(*p) for p in item["points"]]
            self.route(draw, points, item, state, t)
            paste(canvas, overlay, (self.w/2, self.h/2), alpha)

    def area(self, canvas, terrain, item, project, height, opacity):
        polygons = item["polygons"] if "polygons" in item else [[item["points"]]]
        top = [[[project(*point, height) for point in ring] for ring in part] for part in polygons]
        base = [[[project(*point) for point in ring] for ring in part] for part in polygons]
        coordinates = [xy for groups in (top, base) for part in groups for ring in part for xy in ring]
        xs, ys = zip(*coordinates)
        margin = self.px(23) if item.get("glow") else self.px(item.get("width", 2))+2
        left = max(0, math.floor(min(xs))-margin)
        top_y = max(0, math.floor(min(ys))-margin)
        right = min(self.w, math.ceil(max(xs))+margin)
        bottom = min(self.h, math.ceil(max(ys))+margin)
        if left >= right or top_y >= bottom:
            return
        box = (left, top_y, right, bottom)
        size = (right-left, bottom-top_y)

        def local(ring):
            return [(x-left, y-top_y) for x, y in ring]

        mask = Image.new("L", size)
        draw_mask = ImageDraw.Draw(mask)
        for part in top:
            draw_mask.polygon(local(part[0]), fill=255)
            for hole in part[1:]:
                draw_mask.polygon(local(hole), fill=0)
        overlay = Image.new("RGBA", size)
        color = ImageColor.getcolor(item["fill"], "RGBA")
        if item.get("glow"):
            halo = Image.new("RGBA", size, item["glow"])
            glow_alpha = ImageColor.getcolor(item["glow"], "RGBA")[3]
            edge = mask.filter(ImageFilter.GaussianBlur(self.px(7)))
            halo.putalpha(edge.point(lambda v: round(v*glow_alpha/255)))
            overlay.alpha_composite(halo)
        if height > 0 and item.get("space") == "map":
            draw_side = ImageDraw.Draw(overlay)
            faces = []
            for low_part, high_part in zip(base, top):
                for low, high in zip(low_part, high_part):
                    low, high = local(low), local(high)
                    for n, a in enumerate(low):
                        j = (n+1) % len(low)
                        b = low[j]
                        sx, sy = high[n][0]-a[0], high[n][1]-a[1]
                        if abs(sx)+abs(sy) > .1:
                            shade = .47 + .15*abs(b[0]-a[0])/max(1,math.dist(a,b))
                            faces.append(((a[1]+b[1])/2, (a, b, high[j], high[n]), shade))
            for _, face, shade in sorted(faces, key=lambda face:face[0]):
                draw_side.polygon(face, fill=tuple(round(c*shade) for c in color[:3])+(color[3],))
        surface = Image.new("RGBA", size, color)
        texture = item.get("texture", 0)
        if texture:
            luminance = terrain.crop(box).convert("L").point(lambda value: round(255-texture*(210-value*.65)))
            surface = ImageChops.multiply(surface.convert("RGB"), luminance.convert("RGB")).convert("RGBA")
        surface.putalpha(mask.point(lambda v: round(v*color[3]/255)))
        overlay.alpha_composite(surface)
        if item.get("outline"):
            stroke = ImageDraw.Draw(overlay)
            for part in top:
                for ring in part:
                    path = local(ring)
                    stroke.line(path+[path[0]], fill=item["outline"], width=self.px(item.get("width", 2)),
                                joint="curve")
        paste(canvas, overlay, (left+size[0]/2, top_y+size[1]/2), opacity)

    def route(self, draw, points, item, state, t):
        path = Path2D(points)
        end = path.length * clamp(state["progress"])
        if end <= 0:
            return
        width = self.px(item.get("width", 6))
        dash = item.get("dash")
        segments = []
        if dash:
            length, gap = [self.px(v) for v in dash]
            period = length + gap
            offset = (t * self.unit * item.get("dash_speed", 0)) % period
            start = offset - period
            while start < end:
                a, b = max(0, start), min(end, start + length)
                if a < b:
                    segments.append(path.slice(a, b))
                start += period
        else:
            segments.append(path.slice(0, end))
        if item.get("glow"):
            for seg in segments:
                draw.line(seg, fill=item["glow"], width=width + self.px(13), joint="curve")
        for seg in segments:
            draw.line(seg, fill=item.get("color", "#ffffff"), width=width, joint="curve")
        if item.get("arrow"):
            x, y = path.position(end)
            u, v = path.position(max(0, end - self.px(36)))
            angle = math.atan2(y-v, x-u)
            length, half = self.px(25), self.px(11)
            bx, by = x - length*math.cos(angle), y - length*math.sin(angle)
            dx, dy = -half*math.sin(angle), half*math.cos(angle)
            draw.polygon([(x, y), (bx+dx, by+dy), (bx-dx, by-dy)], fill=item.get("color", "#ffffff"))

    def scene(self, index, frame):
        scene = self.scenes[index]
        t = (frame - self.starts[index]) / self.fps
        canvas, xy = self.background(index, t)
        layers = scene.get("layers", [])
        terrain = canvas.copy() if any(item.get("texture") for item in layers) else None
        for item in layers:
            self.layer(canvas, item, t, xy, terrain)
        return canvas

    def frame(self, frame):
        index = bisect_right(self.starts, frame) - 1
        current = self.scene(index, frame)
        overlap = self.ends[index-1] - self.starts[index] if index else 0
        if overlap and frame < self.ends[index-1]:
            progress = (frame - self.starts[index]) / overlap
            current = Image.blend(self.scene(index-1, frame), current, EASING["smooth"](progress))
        t = frame / self.fps
        for item in self.job.get("overlays", []):
            self.layer(current, item, t, self.screen)
        for caption in self.captions:
            if caption["start"] <= t < caption["end"]:
                entry = {
                    "type": "text", "x": .47, "y": .675, "text": caption["text"],
                    **self.job.get("caption_style", {}), **caption,
                }
                self.layer(current, entry, t, self.screen)
                break
        return current.convert("RGB")


def check_points(points, minimum, label):
    if len(points) < minimum or any(len(point) != 2 for point in points):
        raise ValueError(f"{label} needs at least {minimum} [x,y] points")
    if minimum == 2 and len({tuple(point) for point in points}) < 2:
        raise ValueError(f"{label} needs two distinct points")


def sequence_files(root, folder):
    files = sorted(path for path in (root / folder).iterdir()
                   if path.is_file() and path.suffix.lower() in {".png", ".jpeg", ".jpg"})
    if not files:
        raise ValueError(f"no image frames in {folder}")
    return files


def check_keys(keys, fields):
    times = [key["at"] for key in keys]
    if any(t < 0 for t in times) or any(a >= b for a, b in zip(times, times[1:])):
        raise ValueError("keyframe times must increase and start at or after zero")
    for key in keys:
        if key.get("ease", "smooth") not in EASING or key.keys() - fields - {"at", "ease"}:
            raise ValueError(f"unknown keyframe field or easing in {key}")


def check_layer(layer, root, allow_map):
    check_keys(layer.get("keys", []), LAYER_FIELDS)
    if any(not (0 <= row.get("height", 0) <= 250) for row in [layer, *layer.get("keys", [])]):
        raise ValueError("layer height must be 0–250 reference pixels")
    if layer.get("space", "screen") not in {"screen", "map"} or not allow_map and layer.get("space") == "map":
        raise ValueError("map placement needs an image background within the scene")
    kind = layer["type"]
    if kind == "image":
        if layer["width"] <= 0:
            raise ValueError("image width must be positive")
        load_image(str(root / layer["file"]))
    elif kind == "route":
        check_points(layer["points"], 2, "route")
        if "dash" in layer and (len(layer["dash"]) != 2 or min(layer["dash"]) <= 0):
            raise ValueError("route dash must contain two positive lengths")
    elif kind == "area":
        if "polygons" in layer:
            if not layer["polygons"] or any(not part for part in layer["polygons"]):
                raise ValueError("each area polygon needs at least one ring")
            for part in layer["polygons"]:
                for ring in part:
                    check_points(ring, 3, "area ring")
        else:
            check_points(layer["points"], 3, "area")
        if not 0 <= layer.get("texture", 0) <= 1:
            raise ValueError("area texture must be between 0 and 1")
        ImageColor.getcolor(layer["fill"], "RGBA")
    elif kind != "text" or not layer.get("text", "").strip():
        raise ValueError(f"unknown layer type or missing text in {layer}")
    if "follow" in layer:
        check_points(layer["follow"], 2, "follow")


def validate(job, root, fps):
    if not job["scenes"]:
        raise ValueError("add at least one scene")
    previous = previous_transition = 0
    frames = 0
    for scene in job["scenes"]:
        duration = round(scene["seconds"] * fps)
        transition = round(scene.get("transition", 0) * fps)
        if duration < 1 or transition < 0 or transition >= duration or transition > previous-previous_transition:
            raise ValueError("invalid scene duration or scene transition")
        frames += duration - transition
        previous, previous_transition = duration, transition
        bg = scene["background"]
        if sum(key in bg for key in ("image", "color", "sequence")) != 1:
            raise ValueError("provide an image, a color, or an image sequence for each background")
        if "image" in bg:
            load_image(str(root / bg["image"]))
        if "sequence" in bg:
            files = sequence_files(root, bg["sequence"])
            source_fps = bg.get("fps", fps)
            if source_fps <= 0 or len(files)/source_fps + 1e-6 < duration/fps:
                raise ValueError("image sequence is shorter than its scene or its fps is invalid")
            if scene.get("camera") or bg.get("tint"):
                raise ValueError("image sequence frames already have camera movement and color")
        check_keys(scene.get("camera", []), CAMERA_FIELDS)
        if any(key.get("zoom", 1) < 1 for key in scene.get("camera", [])):
            raise ValueError("camera zoom must be at least 1 to fill the frame")
        if any(not (0 <= key.get("tilt", 0) <= 58) for key in scene.get("camera", [])):
            raise ValueError("camera tilt must be 0–58 degrees")
        for layer in scene.get("layers", []):
            check_layer(layer, root, "image" in bg)
    for layer in job.get("overlays", []):
        check_layer(layer, root, False)
    last_end = 0
    for cue in job.get("captions", []):
        if not (last_end <= cue["start"] < cue["end"] <= frames/fps + 1e-6) or not cue["text"].strip():
            raise ValueError("captions must be in order, have text, and fit the video without overlap")
        last_end = cue["end"]
    if job.get("audio") and not (root / job["audio"]).is_file():
        raise ValueError(f"audio file not found: {job['audio']}")


def srt_time(t):
    seconds, ms = divmod(round(t * 1000), 1000)
    minutes, sec = divmod(seconds, 60)
    hour, minute = divmod(minutes, 60)
    return f"{hour:02}:{minute:02}:{sec:02},{ms:03}"


def render(renderer, output, audio):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise ValueError("FFmpeg was not found on PATH")
    with TemporaryDirectory(dir=output.parent) as work:
        tmp_video = Path(work) / "video.mp4"
        command = [
            ffmpeg, "-v", "error", "-nostdin", "-f", "rawvideo", "-pixel_format", "rgb24",
            "-video_size", f"{renderer.w}x{renderer.h}", "-framerate", str(renderer.fps),
            "-i", "pipe:0",
        ]
        if audio:
            command += ["-i", renderer.file(audio), "-map", "0:v:0", "-map", "1:a:0",
                        "-c:a", "aac", "-b:a", "160k", "-af", "apad"]
        command += [
            "-t", f"{renderer.frames / renderer.fps:.9f}", "-c:v", "libx264",
            "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            str(tmp_video),
        ]
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
        try:
            with process.stdin:
                for frame in range(renderer.frames):
                    process.stdin.write(renderer.frame(frame).tobytes())
            if process.wait():
                raise ValueError("FFmpeg failed to encode the video")
        except BaseException:
            if process.poll() is None:
                process.terminate()
            process.wait()
            raise
        subtitles = "\n\n".join(
            f"{n}\n{srt_time(cue['start'])} --> {srt_time(cue['end'])}\n{cue['text']}"
            for n, cue in enumerate(renderer.captions, 1)
        )
        tmp_srt = Path(work) / "video.srt"
        tmp_srt.write_text(subtitles + ("\n" if subtitles else ""), encoding="utf-8")
        tmp_video.replace(output)
        tmp_srt.replace(output.with_suffix(".srt"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("timeline", type=Path)
    parser.add_argument("output", type=Path, help="MP4 output, or PNG with --frame")
    parser.add_argument("--fps", type=int, choices=(30, 60), default=30)
    parser.add_argument("--preview", action="store_true", help="render at 540x960")
    parser.add_argument("--frame", type=float, help="render a single PNG at this time in seconds")
    args = parser.parse_args()
    try:
        if not features.check("raqm"):
            raise ValueError("install Pillow with RAQM support to shape Thai text")
        job = json.loads(args.timeline.read_text(encoding="utf-8-sig"))
        root = args.timeline.resolve().parent
        validate(job, root, args.fps)
        renderer = Renderer(job, root, (540, 960) if args.preview else (1080, 1920), args.fps)
        out = args.output.resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        if args.frame is not None:
            frame = round(args.frame * args.fps)
            if not 0 <= frame < renderer.frames or out.suffix.lower() != ".png":
                raise ValueError("--frame requires a time inside the video and a .png output")
            renderer.frame(frame).save(out)
        else:
            if out.suffix.lower() != ".mp4":
                raise ValueError("output filename must end in .mp4")
            render(renderer, out, job.get("audio"))
        print(out)
    except (KeyError, TypeError, OSError, ValueError) as error:
        parser.exit(1, f"Render failed: {error}\n")


if __name__ == "__main__":
    main()
