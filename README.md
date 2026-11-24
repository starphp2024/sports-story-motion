# Sports Story Motion

Claude Skill สำหรับทำสารคดีแผนที่ภาษาไทยแนวตั้ง 9:16 ใช้ได้กับเรื่องภูมิศาสตร์ ประวัติศาสตร์ ท่องเที่ยว และกีฬา โดยใช้ Python กับ FFmpeg เรนเดอร์วิดีโอ

- แผนที่ดาวเทียมสีเต็มจอและขอบเขตพื้นที่ที่ขึ้นสีตามจังหวะพากย์
- กล้องแพน ซูม และเปลี่ยนจากมุมบนเป็นมุมเอียง พร้อมป้าย โลโก้ และวัตถุเคลื่อนไหว
- ส่งออก MP4 1080×1920 พร้อมซับ Kanit และไฟล์ SRT แยก

## ดาวน์โหลดเวอร์ชัน 2.0.0

- [ZIP สำหรับติดตั้งใน Claude](https://github.com/starphp2024/sports-story-motion/raw/v2.0.0/downloads/Sports-Story-Motion-Claude-v2.zip)
- [วิดีโอตัวอย่าง 13.5 วินาที](https://github.com/starphp2024/sports-story-motion/raw/v2.0.0/downloads/Sports-Story-Motion-2D-3D-Preview.mp4)

## ติดตั้งใน Claude

ไปที่ **Customize → Skills → + Create skill → Upload a skill** แล้วเลือก ZIP สำหรับ Claude จากลิงก์ด้านบน จากนั้นเปิดใช้งาน `sports-story-motion` หากต้องการรันโค้ด ให้เปิด **Settings → Capabilities → Create and edit files** หรือ **Code execution and file creation** ตามชื่อเมนูที่ปรากฏ [คู่มือ Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude)

เปิดแชตใหม่ แล้วลองพิมพ์

> ใช้ sports-story-motion ทำคลิปสารคดีแนวตั้ง 45 วินาที หัวข้อ “ทำไมเรือสินค้าต้องผ่านช่องแคบมะละกา?” เขียนบทพากย์ไทย ให้แต่ละพื้นที่ขึ้นสีตรงจังหวะที่กล่าวถึง แพนและเอียงกล้อง ให้เรือวิ่งตามลูกศร ใส่โลโก้ที่แนบกับซับไทย Kanit ตัวหนา แล้วส่งออก MP4 1080×1920 กับ SRT

แนบแผนที่ฐาน โลโก้ PNG และเสียงพากย์ WAV/MP3 ตามที่มี สำหรับการเรนเดอร์ใน Claude สภาพแวดล้อมต้องมี Python, Pillow พร้อม RAQM และ FFmpeg

## เรนเดอร์บน Windows

ติดตั้ง Python 3.10 ขึ้นไปและ FFmpeg ที่มี libx264 และอยู่บน PATH เปิด PowerShell ในโฟลเดอร์ `sports-story-motion` ที่มี `SKILL.md` แล้วรัน

```powershell
py -m pip install -r requirements.txt
py scripts/render.py assets/demo/timeline.json preview.mp4
```

จะได้ `preview.mp4` และ `preview.srt` สำหรับงานใหม่ให้เปลี่ยนพาธไทม์ไลน์เป็นไฟล์ JSON ที่ Claude สร้าง อ่านวิธีกำหนดกล้อง พื้นที่ โลโก้ เสียง และแหล่งที่มาของสื่อใน [คู่มือไทม์ไลน์](sports-story-motion/references/timeline.md)
