# ตรวจโปรเจกต์ตั้งต้นและขอบเขต v3

ต้นทาง: commit 60ec81447e54de65aae3bea492092243b38f6ff7
branch: feat/thai-documentary-toolkit-v3
ตรวจเอกสารทางการ: 27 พฤศจิกายน 2026

## ใช้ต่อ

- render.py: กล้อง raster, GeoJSON area, route/follow/orient, keyframes, crossfade, MP4/SRT และ Kanit RAQM
- geojson_area.py: WGS84 ไป Web Mercator สำหรับภาพที่ทราบ bounds
- ฟอนต์และใบอนุญาต, demo เก่า, credits/reference เดิม
- marketplace Codex และ skills/sports-story-motion

## เพิ่ม

- renderer v3 สร้าง mesh จาก DEM จริงพร้อมแสงและกล้อง; แยกจาก 2.5D เดิม
- ชื่อ 5, Hook 3 พร้อมภาพ, คำถามเดียวและคำตอบก่อนจบ
- ปานามา: เรือเดียวต่อเนื่องและ editorial connector ที่บอกว่าไม่ใช่ร่องเดินเรือ
- ตรวจ runtime, เตรียมข้อมูล, นำเข้าเสียง/SRT จริงและ checksum, คิว, ผสมเสียง, renderer และรายงาน
- SVG 13 แบบ, ธงปานามา, source metadata/credits
- Claude Code/Antigravity adapters และ portable Codex manifest
- ZIP แยกสี่ชนิดและคู่มือไทย, regression และ CI Windows/Linux + Chromium/WebGL/FFmpeg

## ข้อจำกัดที่พบจริง

- Facebook reel และ YouTube Shorts เปิดดูวิดีโอไม่ได้ ไม่อ้างว่าได้ดูหรือเทียบสไตล์สำเร็จ
- PowerShell, Node REPL และ browser ของ session ไม่ตอบสนอง การอ่าน local SKILL.md ของ skill ผู้ช่วยก็ไม่สำเร็จ ใช้ GitHub connector พัฒนาและ CI ตรวจแทน ไม่อ้างว่าทดสอบบนเครื่องผู้ใช้แล้ว
- ยังไม่มีเสียงจากบัญชี Google AI Studio ที่เข้าถึงได้ ไม่เดาชื่อเสียงหรือเปลี่ยนบริการ
- animation-only ไม่มีเสียงพากย์ จึงยังไม่สมบูรณ์ ไม่ใช่ demo final และ SRT ว่างไม่ใช่ซับส่งมอบ
- ต้องมีภาพนิ่ง/คลิปช่วงเปิด ช่วงซูม และไอคอนเพื่อเทียบรายละเอียดต้นฉบับ
- ต้องฟังเสียงจริง ตรวจคำอ่าน จัดคิวซับ/ภาพ เรนเดอร์และดู MP4 final ก่อนส่งมอบครบ

คงความสามารถเดิมและชื่อ skill ไม่รวมกับ GeoMotion Thai
