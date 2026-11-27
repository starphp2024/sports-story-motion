# Sports Story Motion v2.0.0

สกิลสำหรับทำสารคดีแผนที่ภาษาไทยแนวตั้ง 9:16 ใช้ได้กับเรื่องกีฬา ภูมิศาสตร์ ประวัติศาสตร์ และท่องเที่ยว รองรับ Google Antigravity, Codex และ Claude

- ใช้ภาพดาวเทียมสีเต็มจอและไฮไลต์พื้นที่ตามจังหวะพากย์
- แพน ซูม และเอียงกล้องบนแผนที่ พร้อมป้าย โลโก้ เส้นทาง และวัตถุเคลื่อนไหว
- ส่งออก MP4 1080×1920 พร้อมซับ Kanit และ SRT แยก

## ดาวน์โหลด

- [ZIP ปลั๊กอินสำหรับ Antigravity และ Codex](https://github.com/hirok-th/sports-story-motion/raw/refs/heads/main/downloads/Sports-Story-Motion-v2-Plugins.zip)
- [ZIP สกิลสำหรับ Claude](https://github.com/hirok-th/sports-story-motion/raw/refs/heads/main/downloads/Sports-Story-Motion-Claude-v2.zip)
- [วิดีโอตัวอย่าง 13.5 วินาที](https://github.com/hirok-th/sports-story-motion/raw/refs/heads/main/downloads/Sports-Story-Motion-2D-3D-Preview.mp4)

## Google Antigravity

### ติดตั้งจาก GitHub ผ่าน Terminal

เปิด PowerShell หรือ Terminal ที่มี Antigravity CLI (`agy`) แล้วรัน

```powershell
agy plugin install https://github.com/hirok-th/sports-story-motion
agy plugin list
```

### ติดตั้งใน Antigravity App หรือ IDE บน Windows โดยใช้ File Explorer

1. ดาวน์โหลดและแตก ZIP ปลั๊กอิน แล้วเปิดโฟลเดอร์ด้านในชื่อ `Sports-Story-Motion-v2-Plugins` ที่มี `README-TH.md`
2. เปิดโฟลเดอร์ `plugins` แล้วคัดลอกโฟลเดอร์ `sports-story-motion` ทั้งโฟลเดอร์
3. กด **Win + R** พิมพ์ `%USERPROFILE%` แล้วกด Enter สร้างโฟลเดอร์ `.gemini\config\plugins` ตามลำดับหากยังไม่มี แล้ววางโฟลเดอร์ที่คัดลอก
4. เช็กว่ามีไฟล์ `%USERPROFILE%\.gemini\config\plugins\sports-story-motion\plugin.json` แล้วเปิด Antigravity ใหม่
5. ใน **App** เปิด **Customizations → Installed** ส่วนใน **IDE** เปิด **Customizations** ในแถบ Agent เพื่อดูสกิลที่โหลดไว้

### เรียกใช้งาน

ใน Antigravity App หรือ CLI พิมพ์ `/sports-story-motion` แล้วตามด้วยโจทย์ของคุณ ใน IDE พิมพ์ “ใช้ Sports Story Motion v2” ตามด้วยโจทย์ได้เลย

[คู่มือปลั๊กอิน Antigravity](https://antigravity.google/docs/plugins)

## Codex

เปิด PowerShell หรือ Terminal ที่มี Codex CLI แล้วรัน

```powershell
codex plugin marketplace add hirok-th/sports-story-motion
codex plugin add sports-story-motion@sports-story-motion
```

เปิด Codex ใหม่ แล้วพิมพ์ `/plugins` ใน Codex CLI เพื่อเช็กการติดตั้ง จากนั้นเปิด `/skills` เพื่อเลือกสกิล หรือเริ่มข้อความด้วย `$sports-story-motion:sports-story-motion`

ถ้าติดตั้งจาก ZIP ที่ดาวน์โหลด ให้เปิด Terminal ในโฟลเดอร์ที่มี `README-TH.md` แล้วรัน

```powershell
codex plugin marketplace add .
codex plugin add sports-story-motion@sports-story-motion-local
```

[คู่มือปลั๊กอิน Codex](https://learn.chatgpt.com/docs/cli/reference)

## Claude

ไปที่ **Customize → Skills → + Create skill → Upload a skill** แล้วเลือก ZIP สำหรับ Claude ที่ดาวน์โหลด เปิดใช้งานสกิล `sports-story-motion` แล้วเปิดแชตใหม่และระบุชื่อสกิลในข้อความ หากต้องการรันโค้ด ให้เปิด **Settings → Capabilities → Create and edit files** หรือ **Code execution and file creation** ตามชื่อเมนูที่ปรากฏ

[คู่มือ Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude)

## ตัวอย่างคำสั่ง

> ใช้ Sports Story Motion v2 สร้างคลิปสารคดีแนวตั้ง 45 วินาที เรื่อง “ทำไมเรือสินค้าต้องผ่านช่องแคบมะละกา?” เขียนบทพากย์ไทย ให้พื้นที่ขึ้นสีตรงจังหวะที่กล่าวถึง เอียงกล้องช่วงซูมเข้า ให้เรือวิ่งตามลูกศร แล้วส่งออก MP4 1080×1920 พร้อมซับ Kanit และไฟล์ SRT

แนบแผนที่ฐาน โลโก้ PNG และเสียงพากย์ WAV หรือ MP3 ตามที่มี หากมีเสียงพากย์จริง ให้ระบุว่าต้องการซิงก์คิวภาพและซับกับไฟล์เสียงที่แนบ

## เรนเดอร์บน Windows

ติดตั้ง Python 3.10 ขึ้นไป และ FFmpeg ที่มี `libx264` และอยู่บน PATH จากซอร์สใน repo ให้เปิด PowerShell ในโฟลเดอร์ `skills/sports-story-motion` ที่มี `SKILL.md` แล้วรัน

```powershell
py -m pip install -r requirements.txt
py -c "from PIL import features; print(features.check('raqm'))"
py scripts/render.py assets/demo/timeline.json preview.mp4
```

การตรวจ `raqm` ควรแสดง `True` เพื่อรองรับการจัดรูปอักษรไทย จะได้ `preview.mp4` และ `preview.srt` สำหรับงานใหม่ให้เปลี่ยนพาธไทม์ไลน์เป็นไฟล์ JSON ของงานนั้น

[คู่มือไทม์ไลน์และเครดิตสื่อ](skills/sports-story-motion/references/timeline.md)
