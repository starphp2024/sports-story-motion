#!/usr/bin/env python3
"""Sports Story Motion: inspect tools, validate projects and import reviewed AI Studio audio."""
import argparse
import hashlib
import importlib.util
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def write(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

def probe(path):
    run = subprocess.run(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(path)],
                         capture_output=True,text=True,check=True)
    return json.loads(run.stdout)

def local(root, name):
    path=(root/name).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("missing file or path outside project: "+str(name))
    return path

def finite(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)

def point(value):
    return isinstance(value,list) and len(value)==2 and all(finite(x) for x in value) and -180<=value[0]<=180 and -85.05112878<=value[1]<=85.05112878

def validate(path, animation_only=False):
    p=read(path);root=Path(path).resolve().parent
    if p.get("schema_version")!=3:
        raise ValueError("schema_version must be 3; use render.py for the original v2 timeline")
    if p.get("aspect") not in ("9:16","16:9") or p.get("fps")!=30:
        raise ValueError("v3 accepts 9:16 or 16:9 at 30fps (legacy render.py also supports 60fps)")
    if not finite(p.get("duration")) or not 1<=p["duration"]<=600:
        raise ValueError("duration must be 1–600 seconds")
    if not p.get("title_screen") or not p.get("question") or not p.get("answer_screen"):
        raise ValueError("provide one question, a short opening title and an answer")
    if not point(p.get("origin")):
        raise ValueError("origin needs WGS84 [longitude,latitude]")
    if not 1<=p["terrain"]["vertical_exaggeration"]<=20:
        raise ValueError("terrain vertical_exaggeration must be 1–20 and recorded explicitly")
    camera=p.get("camera",[])
    times=[x["at"] for x in camera]
    if len(camera)<2 or times[0]!=0 or any(not finite(t) or t<0 or t>p["duration"] for t in times) or any(a>=b for a,b in zip(times,times[1:])):
        raise ValueError("camera keys must increase from 0 and fit the actual audio duration")
    for key in camera:
        if not point(key["center"]) or not finite(key["span_km"]) or key["span_km"]<=0 or not 0<=key["tilt"]<=65:
            raise ValueError("invalid camera center/span/tilt")
    def interval(item):
        if not all(finite(item.get(k)) for k in ("start","end")) or not 0<=item["start"]<item["end"]<=p["duration"]+.00001:
            raise ValueError("cue outside actual duration: "+str(item))
    ids=set()
    for route in p.get("routes",[]):
        interval(route)
        if route["id"] in ids:raise ValueError("duplicate route id")
        ids.add(route["id"])
        if route.get("kind") not in ("actual","illustrative"):
            raise ValueError("route.kind must distinguish actual from illustrative")
        if len(route["points"])<2 or not all(point(q) for q in route["points"]) or len(set(map(tuple,route["points"])))<2:
            raise ValueError("route needs distinct WGS84 points")
        if route["kind"]=="actual" and (not route.get("source") or not route.get("verified")):
            raise ValueError("actual routes need a verified source; do not present an illustrative connector as a navigable route")
    for obj in p.get("objects",[]):
        interval(obj)
        if obj.get("route") not in ids:raise ValueError("moving object refers to a missing route")
        if obj.get("asset"):local(root,obj["asset"])
        elif not (SKILL/"assets/icons"/(obj["icon"]+".svg")).is_file():raise ValueError("missing icon")
    for marker in p.get("markers",[]):
        interval(marker)
        if not point(marker["location"]):raise ValueError("invalid marker coordinate")
        if marker.get("asset"):local(root,marker["asset"])
        elif not (SKILL/"assets/icons"/(marker["icon"]+".svg")).is_file():raise ValueError("missing marker icon")
    for country in p.get("countries",[]):
        interval(country)
        if not point(country["location"]) or not country["start"]<=country["flag_at"]<country["zoom_at"]<country["end"]:
            raise ValueError("country order must be locate, highlight, flag hold, then zoom")
        zoom_keys=[(a,b) for a,b in zip(camera,camera[1:]) if abs(a["at"]-country["zoom_at"])<1/p["fps"] and b["span_km"]<a["span_km"]]
        if not zoom_keys:raise ValueError("country zoom_at must match the start of a real camera zoom interval")
        if country["zoom_at"]-country["flag_at"]<1:
            raise ValueError("hold the country flag at least one second before zoom")
        if country.get("flag"):local(root,country["flag"])
        elif not (SKILL/"assets/flags"/(country["code"]+".svg")).is_file():raise ValueError("add the correct flag asset")
    for label in p.get("labels",[]):
        interval(label)
        if not point(label["location"]):raise ValueError("invalid label coordinate")
    if p.get("mechanism"):interval(p["mechanism"])
    last=0
    for cue in p.get("captions",[]):
        interval(cue)
        if cue["start"]<last or not cue.get("text","").strip():
            raise ValueError("captions must be ordered, nonempty and nonoverlapping")
        last=cue["end"]
        if max(map(len,cue["text"].splitlines()))>44 or len(cue["text"].splitlines())>2:
            raise ValueError("split captions into at most two short Thai lines; check actual rendered width")
    wm=p.get("watermark")
    if wm:
        interval(wm);local(root,wm["file"])
        if wm.get("requested") is not True or not 0<wm["width"]<=.4 or not 0<=wm["opacity"]<=1:
            raise ValueError("watermark needs an explicit user request, original file and sensible size/opacity")
    if not animation_only:
        a=p.get("audio")
        if not a or a.get("provider")!="google-ai-studio":
            raise ValueError("final render requires real Google AI Studio narration; use --animation-only for a marked incomplete preview")
        audio=local(root,a["file"])
        if a.get("sha256")!=sha(audio):
            raise ValueError("audio changed: re-import and review captions/visual cues")
        if not a.get("voice_observed") or not a.get("model_observed"):
            raise ValueError("record the model and voice actually seen in AI Studio")
        if not all(a.get(k) is True for k in ("listened","captions_reviewed","visual_cues_reviewed")):
            raise ValueError("listen to the real audio and review pronunciation, subtitles and visual cues before final rendering")
        if p.get("sync",{}).get("audio_sha256")!=a["sha256"]:
            raise ValueError("visual timing has not been tied to this exact audio")
        if not p.get("captions"):raise ValueError("final needs subtitles derived from the actual narration")
        info=probe(audio)
        if not any(s["codec_type"]=="audio" for s in info["streams"]):raise ValueError("no audio stream")
        duration=float(info["format"]["duration"])
        if abs(p["duration"]-duration)>1/p["fps"]+.01:
            raise ValueError("video duration must match measured narration; do not trim a final sentence")
        detection=subprocess.run(["ffmpeg","-hide_banner","-i",str(audio),"-af","volumedetect","-f","null","-"],
                                 capture_output=True,text=True,check=True).stderr
        match=re.search(r"max_volume: (-?[\d.]+) dB",detection)
        if not match or float(match.group(1))<-45:
            raise ValueError("narration is silent or too quiet")
        if float(match.group(1))>=0:
            raise ValueError("audio reaches full scale; inspect clipping and lower/limit the mix")
    return p

def parse_srt(path):
    document=Path(path).read_text(encoding="utf-8-sig").replace("\r\n","\n").strip()
    cues=[]
    def timecode(text):
        h,m,s,ms=map(int,re.split(r"[:,.]",text))
        if m>59 or s>59:raise ValueError("invalid SRT time")
        return h*3600+m*60+s+ms/1000
    for block in re.split(r"\n\s*\n",document):
        lines=block.splitlines()
        if not lines:continue
        if lines[0].strip().isdigit():lines=lines[1:]
        match=re.fullmatch(r"(\d{2,}:\d{2}:\d{2}[,.]\d{3}) --> (\d{2,}:\d{2}:\d{2}[,.]\d{3})",lines[0].strip())
        if not match or len(lines)<2:raise ValueError("invalid UTF-8 SRT block")
        cues.append({"start":timecode(match[1]),"end":timecode(match[2]),"text":"\n".join(lines[1:])})
    if not cues:raise ValueError("empty SRT")
    return cues

def attach(args):
    path=args.project.resolve();root=path.parent;p=read(path)
    source=args.audio.resolve();digest=sha(source)
    folder=root/"media";folder.mkdir(exist_ok=True)
    target=folder/("narration-"+digest[:12]+source.suffix.lower())
    if target.resolve()!=source:shutil.copyfile(source,target)
    p["audio"]={"provider":"google-ai-studio","file":target.relative_to(root).as_posix(),
                "sha256":digest,"voice_observed":args.voice,"model_observed":args.model,
                "listened":args.listened,"captions_reviewed":args.captions_reviewed,
                "visual_cues_reviewed":args.visual_cues_reviewed,
                "source_url":"https://aistudio.google.com/","provenance":"user-exported; provider not independently authenticated"}
    p["duration"]=math.ceil(float(probe(source)["format"]["duration"])*p["fps"])/p["fps"]
    p["captions"]=parse_srt(args.srt)
    if args.visual_cues_reviewed:p["sync"]={"audio_sha256":digest,"method":"human review against actual audio; no word-count timing"}
    else:p.pop("sync",None)
    # Save a recoverable candidate; never destroy a working project on failed validation.
    candidate=path.with_name(path.stem+".candidate.json");write(candidate,p)
    validate(candidate,animation_only=True)
    candidate.replace(path)
    print("Imported. Final validation still checks real audio, review flags and all cue ranges.")
    print(path)

def doctor():
    report={"python":sys.version,"ffmpeg":shutil.which("ffmpeg"),"ffprobe":shutil.which("ffprobe"),
            "node":shutil.which("node"),"npm":shutil.which("npm"),"kanit":(SKILL/"assets/fonts/Kanit-Bold.ttf").is_file(),
            "google_ai_studio":"not probed; requires the user's signed-in browser; no assumed TTS access",
            "browser_renderer":"run renderer/selftest.mjs after npm install and Playwright Chromium install"}
    try:
        from PIL import features
        report["pillow_raqm"]=features.check("raqm")
    except ImportError:report["pillow_raqm"]=False
    for name in ("ffmpeg","ffprobe","node"):
        if report[name]:
            r=subprocess.run([report[name],"-version" if name!="node" else "--version"],capture_output=True,text=True)
            report[name+"_version"]=r.stdout.splitlines()[:1]
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest="command",required=True)
    sub.add_parser("doctor")
    val=sub.add_parser("validate");val.add_argument("project",type=Path);val.add_argument("--animation-only",action="store_true")
    aud=sub.add_parser("attach-audio");aud.add_argument("project",type=Path)
    for name in ("audio","srt"):aud.add_argument("--"+name,type=Path,required=True)
    for name in ("voice","model"):aud.add_argument("--"+name,required=True)
    for flag in ("listened","captions-reviewed","visual-cues-reviewed"):aud.add_argument("--"+flag,action="store_true")
    args=parser.parse_args()
    try:
        if args.command=="doctor":doctor()
        elif args.command=="validate":
            validate(args.project,args.animation_only);print("Project valid ("+("incomplete animation preview" if args.animation_only else "audio linked; human final viewing still required")+")")
        else:attach(args)
    except (ValueError,OSError,KeyError,TypeError,subprocess.SubprocessError) as error:
        parser.exit(1,"Sports Story Motion: "+str(error)+"\n")

if __name__=="__main__":main()
