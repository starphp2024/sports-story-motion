#!/usr/bin/env python3
"""Package the prepared Panama project without download caches or placeholder final audio."""
import argparse
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/"skills/sports-story-motion/assets/panama"
def build(output):
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    required=["project.json","geo.json","narration-th.txt","storyboard-th.md"]
    for name in required:
        if not (PROJECT/name).is_file():raise ValueError("prepare the demo first; missing "+name)
    entries=[PROJECT/name for name in required]
    entries+=sorted((PROJECT/"geo").glob("*.jpg"))
    if not entries[4:]:raise ValueError("prepared map textures missing")
    with ZipFile(output,"w",ZIP_DEFLATED) as archive:
        for file in entries:archive.write(file,"panama/"+file.relative_to(PROJECT).as_posix())
        archive.writestr("panama/README-TH.txt","โปรเจกต์แก้ไขได้สำหรับ Sports Story Motion v3\nมีแผนที่ DEM และบท แต่ยังไม่มีเสียง Google AI Studio และซับจากเสียงจริง\nใช้ renderer ของ skill กับ project.json ในโฟลเดอร์นี้: node renderer/render.mjs PATH/TO/panama/project.json output.mp4 --animation-only\nอ่านคู่มือ USAGE-TH.md ของ plugin ก่อนสร้าง final ห้ามรายงาน preview ไม่มีเสียงว่าเป็นคลิปสมบูรณ์\n")
    with ZipFile(output) as archive:
        if archive.testzip():raise ValueError("invalid ZIP")
    print(output)
if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("output",nargs="?",default="build/Panama-Editable-Project.zip")
    build(parser.parse_args().output)
