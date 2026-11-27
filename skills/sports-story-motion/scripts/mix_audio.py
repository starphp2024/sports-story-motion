#!/usr/bin/env python3
"""Mix narration with a quiet music bed and timed effects; never creates/substitutes narration."""
import argparse
import json
import subprocess
from pathlib import Path

def mix(narration,output,music=None,effects=None,music_db=-27):
    if music_db > -18:
        raise ValueError("music must start at least 18 dB below narration; listen to the actual mix")
    spec=json.loads(Path(effects).read_text(encoding="utf-8")) if effects else []
    command=["ffmpeg","-hide_banner","-y","-i",str(narration)]
    if music:command+=["-stream_loop","-1","-i",str(music)]
    for effect in spec:
        command+=["-i",str(Path(effects).resolve().parent/effect["file"])]
    filters=["[0:a]asetpts=PTS-STARTPTS[voice]"];labels=["[voice]"];index=1
    if music:
        filters.append(f"[{index}:a]volume={music_db}dB,asetpts=PTS-STARTPTS[bed]");labels.append("[bed]");index+=1
    for n,effect in enumerate(spec):
        if effect["at"]<0 or effect.get("gain_db",-20)>-12:
            raise ValueError("effect time must be nonnegative and gain at most -12 dB")
        delay=round(effect["at"]*1000)
        filters.append(f"[{index}:a]volume={effect.get('gain_db',-20)}dB,adelay={delay}:all=1[sfx{n}]")
        labels.append(f"[sfx{n}]");index+=1
    filters.append("".join(labels)+f"amix=inputs={len(labels)}:duration=first:normalize=0,alimiter=limit=0.891:level=false[mix]")
    command+=["-filter_complex",";".join(filters),"-map","[mix]","-c:a","pcm_s16le",str(output)]
    subprocess.run(command,check=True)
    print("Mixed audio written. Listen and re-import this exact file; previous timing/review hashes are invalidated.")
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("narration",type=Path);p.add_argument("output",type=Path);p.add_argument("--music",type=Path);p.add_argument("--effects",type=Path);p.add_argument("--music-db",type=float,default=-27)
    a=p.parse_args();mix(a.narration,a.output,a.music,a.effects,a.music_db)
