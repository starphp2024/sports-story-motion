# สร้างคลิปและแก้ปัญหา (Windows)

## เริ่มจากหัวข้อ

คัดลอกไปในแอปที่ติดตั้ง skill แล้ว:

> ใช้ sports-story-motion สร้างสารคดีแผนที่ไทย 30 วินาที แนวตั้ง เรื่อง “คลองปานามา ทำไมเรือยักษ์ต้องถูกยกขึ้น?” ตรวจแหล่งข้อมูลก่อน เตรียมชื่อโพสต์ 5 แบบ หัวข้อบนจอ Hook 3 แบบพร้อมภาพ เลือกแบบที่ชัดที่สุดแล้วทำบทและ storyboard ใช้เสียง Google AI Studio จริง ซับ Kanit และไม่ใส่โลโก้

เรื่องอื่น:

> ใช้ sports-story-motion อธิบายว่าภูเขาเปลี่ยนเส้นทางการค้าอย่างไร ความยาวตามเสียงพากย์จริง 16:9 ตรวจพิกัดและแหล่งข้อมูล แยกเส้นทางจริงออกจากลูกศรอธิบาย ส่งโปรเจกต์แก้ไขได้ MP4 และ SRT

เริ่มจากคลิปเดโมก่อน อย่าปรับหลายอย่างพร้อมกัน
ต้องมี Python 3.10+ (ทดสอบ 3.12), Node.js 22+, FFmpeg ที่มี ffprobe/libx264 และอินเทอร์เน็ตตอนเตรียมข้อมูล/ติดตั้ง Chromium
ดาวน์โหลดจาก [Python](https://www.python.org/downloads/), [Node.js](https://nodejs.org/en/download), [FFmpeg](https://ffmpeg.org/download.html)
หากพิมพ์คำสั่งแล้ว “not recognized” ให้ติดตั้งโปรแกรมนั้นและเปิด PowerShell ใหม่ ไม่ต้องพิมพ์ทุกคำสั่งซ้ำลง Google

## เปิดที่โฟลเดอร์ skill

จาก root repository:
    cd skills/sports-story-motion
    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    .\.venv\Scripts\python.exe scripts/ssm.py doctor
    npm install --prefix renderer
    npx --prefix renderer playwright install chromium
    node renderer/selftest.mjs

ถ้า Windows บล็อกสคริปต์ Activate ให้เรียก .venv\Scripts\python.exe โดยตรงดังตัวอย่าง ไม่ต้องลดนโยบายความปลอดภัยระบบ
renderer จะเรียก Python ชื่อ python โดยค่าเริ่มต้น ตั้งเฉพาะ runtime ของงานนี้ก่อนเรียก node:
    $env:SSM_PYTHON = (Resolve-Path .\.venv\Scripts\python.exe).Path

ควรได้รายงานเวอร์ชัน FFmpeg/Node ฟอนต์ Kanit และ WebGL2 ถ้า raqm:false ห้ามใช้ renderer เดิมทำซับไทยโดยอ้างว่าถูกต้อง ให้แก้ Pillow/RAQM หรือใช้ Chromium renderer แล้วตรวจภาพจริง

## ทดสอบภาพโดยยังไม่สร้างเสียง

    .\.venv\Scripts\python.exe scripts/prepare_geo.py assets/panama/project.json
    .\.venv\Scripts\python.exe scripts/ssm.py validate assets/panama/project.json --animation-only
    node renderer/render.mjs assets/panama/project.json output/panama-animation-only.mp4 --animation-only --preview

ควรได้ MP4 540×960 มีข้อความ “ทดสอบภาพเคลื่อนไหว • ยังไม่มีเสียงพากย์”, ภาพ PNG และรายงาน QA
คลิปนี้ยังไม่สมบูรณ์ SRT ว่างที่เกิดจาก captions ว่างไม่ใช่ซับที่ส่งมอบแทนเสียงจริง
ตัด --preview ออกเพื่อทดสอบ 1080×1920 หรือเปลี่ยน aspect ใน project.json เป็น 16:9 เพื่อออก 1920×1080

## ทำคลิปมีเสียงและซับจริง

1. เปิด Google AI Studio ใน Chrome ใช้บัญชีที่ลงชื่อเข้าอยู่ เลือกหน้า Generate speech และ model/voice ที่เห็นจริง
2. ใช้บท assets/panama/narration-th.txt และคำกำกับใน references/audio-th.md สร้างและดาวน์โหลดเสียง ฟัง ตรวจชื่อ/คำอ่าน/ช่วงท้ายก่อนใช้
3. ดับเบิลคลิก renderer/caption-editor.html เลือกเสียง ฟังและตั้งซับจากเสียงจริง แล้วดาวน์โหลด narration.srt
4. เปิด assets/panama/project.json ด้วยโปรแกรมแก้ข้อความ แก้คิว camera/countries/routes/objects/labels/mechanism ให้ตรงเสียง รวม flag hold ก่อนซูม
5. คัดลอกเสียงและ SRT ไปในโฟลเดอร์งานหรือใช้พาธเต็ม นำเข้าโดยแทนชื่อ model/voice ด้านล่างด้วยค่าที่เห็นจริง:
    .\.venv\Scripts\python.exe scripts/ssm.py attach-audio assets/panama/project.json --audio "C:\งาน\panama.wav" --srt "C:\งาน\narration.srt" --voice "ชื่อเสียงที่เห็นจริง" --model "ชื่อโมเดลที่เห็นจริง" --listened --captions-reviewed --visual-cues-reviewed
6. ใช้ flags review เฉพาะเมื่อฟัง/ตรวจแล้วจริง ความยาวถูกวัดจากไฟล์เสียง หากคิวไม่พอดีจะมี candidate.json ให้แก้ โดยไม่ทับโปรเจกต์เดิมที่ยังใช้ได้
7. ตรวจและเรนเดอร์:
    .\.venv\Scripts\python.exe scripts/ssm.py validate assets/panama/project.json
    node renderer/render.mjs assets/panama/project.json output/panama.mp4

ได้ MP4 พร้อมฝัง Kanit, SRT UTF-8, PNG ตัวอย่างหกภาพ และ .qa.json
QA ระบุ encoded-awaiting-human-review เพราะยังต้องเปิดดูและฟังจริง การ decode ผ่านไม่รับรองคำอ่านไทยหรือความถูกต้องของทุกภาพ
เปลี่ยนเสียง/mix แล้วต้องนำเข้าและตรวจคิวใหม่

## เพลง เอฟเฟกต์ และลายน้ำ

ใช้ไฟล์ที่มีสิทธิ์ ห้ามเปลี่ยนแหล่งพากย์จาก AI Studio:
    .\.venv\Scripts\python.exe scripts/mix_audio.py "C:\งาน\panama.wav" "C:\งาน\mix.wav" --music "C:\งาน\music.wav" --music-db -27

effects เป็น JSON ที่ระบุ file,at,gain_db และเวลาตรงสิ่งที่เห็น เริ่มเบากว่าเสียงเล่า ฟัง mix แล้วนำเข้าไฟล์ mix ใหม่เพื่อให้ hash/คิวตรงกัน
watermark เป็น null โดยค่าเริ่มต้น ถ้าผู้ใช้แนบโลโก้และสั่ง จึงตั้ง requested:true,file,x,y,width,opacity,start,end โดยรักษาสัดส่วน/สีเดิม

## แก้ปัญหา

| อาการ | วิธีแก้ |
|---|---|
| ไม่พบ python/node/ffmpeg | ใช้ doctor ตรวจ PATH และเปิด terminal ใหม่หลังติดตั้ง; อย่าคิดว่า skill ติดตั้ง runtime ให้แล้ว |
| Chromium ไม่รองรับ Linux รุ่นใหม่ | CI ใช้ Ubuntu 24.04 สำหรับ Playwright 1.58.2; ใช้ runtime ที่รองรับหรือทดสอบอัปเดต dependency แยก |
| WebGL2 ไม่พร้อม | selftest ต้องผ่าน; renderer ใช้ ANGLE/SwiftShader fallback แต่ต้องทดสอบจริง ไม่ถือว่าเครื่องทุกเครื่องรองรับ |
| แผนที่/DEM ดาวน์โหลดไม่ได้ | ตรวจเครือข่าย URL ใน log และสิทธิ์ข้อมูล; ห้ามสร้าง DEM สมมติแล้วเรียก terrain จริง |
| ประเทศ/ธงไม่ขึ้น | ตรวจ ADM0_A3 กับ Natural Earth และไฟล์ธงต้นฉบับ; พิกัดต้องเป็น longitude ก่อน latitude |
| final ปฏิเสธเพราะไม่มีเสียง | สร้างเสียง Google AI Studio จริงและนำเข้า SRT ที่ฟัง/จัดเวลาแล้ว ไม่แก้ provider เพื่อหลอก validator |
| checksum ไม่ตรง | ไฟล์เสียงเปลี่ยน ต้องนำเข้าและตรวจซับ/ภาพใหม่ |
| ซับยาว/คิวเกินเสียง | แบ่งเป็นสองบรรทัดสั้นและแก้เวลาจากเสียงจริง ตรวจ PNG/MP4 ไม่ดูจำนวนอักษรอย่างเดียว |
| Kanit สระ/วรรณยุกต์ผิด | ตรวจ browser font load หรือ Pillow RAQM และภาพจริง; renderer เดิมต้อง raqm:true |
| logo ไม่ขึ้น | ต้องเป็นโลโก้ผู้ใช้สั่ง มี requested:true และพาธอยู่ในโปรเจกต์ |
| คลิปเก่าใช้ไม่ได้กับ v3 | ใช้ scripts/render.py กับ timeline v2 เดิม อย่าเปลี่ยน schema ด้วยการแก้เลขอย่างเดียว |

## ตรวจส่งมอบ

เปิด MP4 ตั้งแต่ต้นจนจบ ฟังเสียงจริง ตรวจตำแหน่ง/ธง/การซูม/วัตถุ ซับ Kanit และพื้นที่ปลอดภัย ตอบ Hook ครบ เครดิตอ่านได้ และไม่มีประโยคถูกตัด
ส่งไฟล์โปรเจกต์ JSON, geo.json/geo/ ที่เตรียมไว้, สื่อที่มีสิทธิ์, MP4/SRT และรายงานข้อจำกัดร่วมกัน
