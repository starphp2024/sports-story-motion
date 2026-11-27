# ผลตรวจส่งมอบ Sports Story Motion v3

วันที่: 27 พฤศจิกายน 2026
สถานะรวม: Skill/Plugin และ renderer พร้อมตรวจใช้งาน; คลิป final ยังไม่สมบูรณ์เพราะขาดเสียง Google AI Studio และซับจากเสียงจริง

## หลักฐานที่ผ่าน

[CI รอบสำเร็จ](https://github.com/hirok-th/sports-story-motion/actions/runs/46034013048)
commit ที่ทดสอบ core renderer: 37e9e8a6eace1d6273fe5d3089a426d3a51fb267

| รายการ | ผล / ขอบเขต |
|---|---|
| 14 tests บน Windows/Linux CI | ผ่าน รวม legacy renderer/RAQM, การถอด DEM, ลำดับธง/ซูม, route provenance, audio checksum/review และ ZIP |
| local Windows | ผ่าน 13 tests; ข้าม legacy RAQM 1 เพราะ runtime นี้ไม่มี RAQM |
| Claude Code 2.1.332 บน Linux CI | validate ผ่าน, marketplace พาธเต็มติดตั้งได้, plugin scope project ติดตั้งและ enabled:true ที่ version 3.0.0 |
| Codex CLI 0.172.0 บน Linux CI | marketplace/plugin add ผ่าน, installed:true, enabled:true, version 3.0.0 |
| Antigravity | schema ทางการผ่าน; ยังไม่ได้ติดตั้ง/เปิดใช้งานแอปหรือ native agy CLI |
| Claude chat / desktop GUI และ Codex GUI | ยังไม่ได้ทดสอบการติดตั้งผ่านหน้าจอจริง |
| ฟอนต์ | Kanit โหลดจริงใน Chromium; ตรวจภาพ layout 9:16 และ 16:9 สระ/วรรณยุกต์และกรอบซับจากภาพทดสอบ |
| ภูมิประเทศ | DEM mesh จริงจาก Terrarium, ขยายสูง 4 เท่า; ไม่ใช้การเอียง raster แทน terrain |
| MP4 จาก CI | H.264 1080×1920, 30fps, 780 เฟรม, 26.000 วินาที; ffprobe/count และ FFmpeg decode ทั้งไฟล์ผ่าน |
| ภาพ | ตรวจ PNG มุมกว้าง/ธงและภาพใกล้จากไฟล์ 1080 จริง; ตรวจ layout กลไกและซับด้วยภาพแยก |
| เสียง/ซับจริง | ยังไม่มี จึงไม่รับรองคำอ่าน การซิงก์ หรือ audio mix และไม่เรียกคลิปนี้ว่างานสมบูรณ์ |

MP4 ทดสอบ SHA-256:
e14d3a15d3dfa66b32129b806056c30224e94a7e1df68cf5684f6108315a1a37

## ไฟล์ส่งมอบ

- ZIP แยก Claude-Skill, Claude-Code, Codex, Antigravity; packages.json บันทึก hash ของไฟล์ที่สร้าง
- ซอร์สและคู่มือใน branch feat/thai-documentary-toolkit-v3; ไม่ merge เข้า main
- Panama-Editable-Project.zip มี project.json, geo.json, แผนที่/DEM ที่ใช้กับงาน CI, บทและ storyboard; ใช้ร่วมกับ renderer ของ skill
- Panama-Animation-Test-1080p.mp4 และ .qa.json เป็น animation-only ไม่มีเสียง
- ไม่ส่ง SRT ว่างว่าเป็นซับจริง; ต้องสร้าง SRT จากเสียงที่ใช้จริงก่อน final
- [ดาวน์โหลดแพ็กเกจ CI](https://github.com/hirok-th/sports-story-motion/actions/runs/46034013048/artifacts/15216135792)
- [ดาวน์โหลด MP4/ภาพ/ข้อมูลและ diagnostics จาก CI](https://github.com/hirok-th/sports-story-motion/actions/runs/46034013048/artifacts/15215154590)

## ข้อจำกัดที่ยังเหลือ

1. เปิด AI Studio บัญชีที่ลงชื่อเข้าใช้ได้แล้ว แต่ native tool แจ้งว่ามีผู้ใช้งาน Chrome พร้อมกัน จึงรอการประสานก่อนสร้าง/ดาวน์โหลดเสียง ไม่เปลี่ยนผู้ให้บริการ
2. Facebook/YouTube ตัวอย่างเปิดดูวิดีโอไม่ได้ ยังไม่มีการเทียบรายละเอียดสไตล์ ต้องได้ภาพนิ่ง/คลิปช่วงเปิด ซูม และไอคอน
3. ภาพ NASA เป็น composite ปี 2004 ไม่ใช่ภาพปัจจุบันหรือภาพรายละเอียดระดับห้องประตูน้ำ; ชั้นทะเลสาบใช้ polygon จริงจาก Natural Earth และระดับน้ำ nominal 26 เมตร ไม่ใช่ค่ามาตรวัดสด
4. เส้นสีเหลืองเป็น editorial connector ไม่ใช่ร่องเดินเรือ ขอบเขตประเทศเป็นแผนที่ทั่วไป 1:50m
5. ยังไม่ได้เปิดชม final พร้อมเสียงใน player และตรวจภาษาไทย/จังหวะเสียงจริงทั้งหมด; automated decode ไม่แทนการฟัง/ดู
6. ยังไม่ได้ส่ง public plugin directory; ไม่มีการเลือกรูปแบบ LICENSE ใหม่ให้สื่อเดิม และ listing icon ยังไม่เตรียม

ขั้นต่อไป: สร้างเสียง AI Studio → ฟัง/แก้คำอ่าน → ตั้งคิวภาพและ SRT จากไฟล์นั้น → เรนเดอร์มีเสียง → เปิดดู/ฟังทั้งคลิปและบันทึกผล ก่อนรายงานว่า demo สมบูรณ์
