# Sports Story Motion v3

Skill และ Plugin สร้างสารคดีแผนที่/Infographic Animation ภาษาไทย สำหรับภูมิศาสตร์ ประวัติศาสตร์ การเดินทาง การค้า กีฬา และเรื่องที่อธิบายผ่านสถานที่ แยกจาก GeoMotion Thai

พัฒนาบน branch feat/thai-documentary-toolkit-v3 โดยเก็บ renderer และตัวอย่างเดิมไว้
**สถานะ: ชุดพัฒนาและงานทดสอบภาพ; demo final ยังรอเสียงจาก Google AI Studio และคิวซับจากเสียงจริง**

- [คู่มือติดตั้งภาษาไทยสำหรับ Windows](docs/INSTALL-TH.md)
- [เริ่มสร้างงาน/คำสั่งคัดลอก/แก้ปัญหา](docs/USAGE-TH.md)
- [ผลตรวจและข้อจำกัดที่พบ](docs/AUDIT-TH.md)
- [SKILL.md](skills/sports-story-motion/SKILL.md)
- [โครงเรื่องคลองปานามา](skills/sports-story-motion/assets/panama/storyboard-th.md)
- [รูปแบบโปรเจกต์ v3](skills/sports-story-motion/references/project-v3.md)
- [แหล่งข้อมูลและเครดิต](skills/sports-story-motion/references/data-sources.md)
- [CI และ ZIP/วิดีโอทดสอบ](https://github.com/hirok-th/sports-story-motion/actions)

## สิ่งที่เพิ่ม

- ระบบคิดชื่อโพสต์ 5 แบบ หัวข้อบนจอ Hook 3 แบบพร้อมภาพ คำถามเดียวและคำตอบก่อนจบ
- renderer ใหม่ใช้ mesh จาก DEM จริง พร้อมแสง กล้องเหนือแผนที่สู่มุมเอียง และพิกัดร่วมสำหรับธง ป้าย เส้นทาง และวัตถุ
- ลำดับประเทศมุมกว้าง → ไฮไลต์ → ธงและพักภาพ → ซูม → terrain
- ไอคอน SVG ชุดเดียวกัน 13 แบบและธงปานามา
- นำเข้าเสียง Google AI Studio จริง ตรวจ hash คิวซับ/ภาพ และความยาวที่วัดจากไฟล์ ไม่กะจากจำนวนคำ
- Kanit ฝังซับ + SRT, โลโก้เฉพาะเมื่อสั่ง, technical QA และภาพตัวอย่าง
- แพ็กเกจแยก Claude Skill, Claude Code, Codex และ Antigravity พร้อมคู่มือไทย

## Runtime

Python 3.10+, Pillow/RAQM สำหรับ renderer เดิม, Node.js 22+, Playwright Chromium/WebGL2 และ FFmpeg/ffprobe/libx264
AI Studio ต้องใช้บัญชีและ browser tool ที่เข้าถึงได้จริง; ไม่รวมเสียง/โควตา/สิทธิ์บัญชีใน plugin

อ่านคู่มือก่อนติดตั้ง การมี manifest/ZIP ที่ถูกโครงสร้างไม่เท่ากับทดสอบติดตั้งทุกแอปแล้ว
GitHub Actions ตรวจ unit/regression บน Windows/Linux และทดสอบ renderer บน Linux ส่วนการใช้งานจริงบนแอปทั้งสามและเสียงยังต้องตรวจตามรายงาน

## สร้าง ZIP

เปิด PowerShell ที่ root ซึ่งมี README.md แล้วพิมพ์: python scripts/build_packages.py dist
จะได้ ZIP สี่แบบกับ packages.json ที่บันทึก SHA-256 ไม่ต้องใช้ ZIP เดียวกับทุกแพลตฟอร์ม

## ความสามารถเดิม

ยังใช้ scripts/render.py, geojson_area.py, assets/demo และ timeline reference เดิมได้
กล้องเอียงภาพ/ยกพื้นที่ใน v2 คือ 2.5D ไม่ใช่ DEM terrain
[README v2 เดิม](docs/README-v2.md) เก็บไว้เพื่ออ้างอิงประวัติ ไม่ใช่คู่มือติดตั้ง v3
