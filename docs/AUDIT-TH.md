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
- ช่วงแรก local tools ตอบช้า ต่อมาอ่าน skill ผู้ช่วยและรัน Python/FFmpeg ได้; native Chrome เปิด AI Studio ได้ แต่ browser host ไม่มี และมีผู้ใช้งาน Chrome พร้อมกัน จึงพักการควบคุมเพื่อรอการประสาน
- local checkout อยู่ใน Windows Temp เพราะสร้างโฟลเดอร์ที่ home root ไม่ได้; Git clone สำเร็จด้วย OpenSSL backend โดยยังตรวจใบรับรองตามปกติ
- local Python ที่ทดสอบไม่มี RAQM จึงไม่รับรองซับไทยของ renderer เดิมบนเครื่องนี้; v3 ใช้ Chromium shaping
- CI รอบแรก unit/regression และแพ็ก ZIP ผ่าน Windows/Linux; renderer install ล้มเพราะ ubuntu-latest เปลี่ยนเป็น 26.04 ที่ Playwright 1.58.2 ไม่รองรับ จึง pin งาน render เป็น Ubuntu 24.04
- ยังไม่มีเสียงจากบัญชี Google AI Studio ที่เข้าถึงได้ ไม่เดาชื่อเสียงหรือเปลี่ยนบริการ
- animation-only ไม่มีเสียงพากย์ จึงยังไม่สมบูรณ์ ไม่ใช่ demo final และ SRT ว่างไม่ใช่ซับส่งมอบ
- ต้องมีภาพนิ่ง/คลิปช่วงเปิด ช่วงซูม และไอคอนเพื่อเทียบรายละเอียดต้นฉบับ
- ต้องฟังเสียงจริง ตรวจคำอ่าน จัดคิวซับ/ภาพ เรนเดอร์และดู MP4 final ก่อนส่งมอบครบ

คงความสามารถเดิมและชื่อ skill ไม่รวมกับ GeoMotion Thai
