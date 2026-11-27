#!/usr/bin/env python3
"""Build separate, inspectable platform ZIPs from the canonical skill."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/"skills/sports-story-motion"
SKIP={"node_modules",".cache","__pycache__","geo","media"}
def files(folder):
    return sorted(p for p in folder.rglob("*") if p.is_file() and not (set(p.relative_to(folder).parts)&SKIP) and p.name!="geo.json" and not p.name.endswith((".pyc",".candidate.json")))
def build(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    common=[ROOT/"README.md",*files(ROOT/"docs")]
    records=[]
    for platform in ("Claude-Skill","Claude-Code","Codex","Antigravity"):
        target=out/("Sports-Story-Motion-3.0.0-"+platform+".zip")
        entries={}
        for source in files(SKILL):
            rel=source.relative_to(SKILL).as_posix()
            entries["sports-story-motion/"+("" if platform=="Claude-Skill" else "skills/sports-story-motion/")+rel]=source.read_bytes()
        if platform!="Claude-Skill":
            for source in common:entries["sports-story-motion/"+source.relative_to(ROOT).as_posix()]=source.read_bytes()
            manifests={"Claude-Code":[".claude-plugin/plugin.json",".claude-plugin/marketplace.json"],"Codex":["plugin.json",".codex-plugin/plugin.json",".agents/plugins/marketplace.json"],"Antigravity":[".antigravity-plugin/plugin.json"]}
            for name in manifests[platform]:entries["sports-story-motion/"+name]=(ROOT/name).read_bytes()
        with ZipFile(target,"w",ZIP_DEFLATED) as archive:
            for name,content in sorted(entries.items()):archive.writestr(name,content)
        with ZipFile(target) as archive:
            if archive.testzip():raise ValueError("invalid ZIP")
            expected="sports-story-motion/"+("" if platform=="Claude-Skill" else "skills/sports-story-motion/")+"SKILL.md"
            assert expected in archive.namelist() and all(not n.startswith("/") and ".." not in n.split("/") for n in archive.namelist())
        records.append({"file":target.name,"bytes":target.stat().st_size,"sha256":hashlib.sha256(target.read_bytes()).hexdigest(),"platform":platform,"install_test":"see CI logs; ZIP structure checked here"})
    (out/"packages.json").write_text(json.dumps(records,indent=2)+"\n",encoding="utf-8")
    return records
if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("output",nargs="?",default=str(ROOT/"dist"))
    print(json.dumps(build(parser.parse_args().output),indent=2))
