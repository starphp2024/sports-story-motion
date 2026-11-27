# ติดตั้ง Sports Story Motion v3 บน Windows

ตรวจเอกสารผู้ผลิต 27 พฤศจิกายน 2026 โค้ดอยู่บน branch feat/thai-documentary-toolkit-v3 ยังไม่ merge เข้า main
รายการทดสอบจริงดู CI และ AUDIT-TH.md การสร้าง ZIP ไม่ได้ยืนยันว่าเปิดใช้งานในทุกแอปสำเร็จแล้ว

## เลือกให้ตรงโปรแกรม

| โปรแกรมที่จะใช้ | ไฟล์ |
|---|---|
| Claude ในเว็บ/แอป ช่องแชตปกติ | Claude-Skill.zip |
| Claude Code ใน PowerShell หรือแท็บ Code แบบ local | Claude-Code.zip |
| Codex CLI หรือแอป Codex | Codex.zip |
| Google Antigravity App/CLI/IDE | Antigravity.zip |

ไฟล์จริงขึ้นต้น Sports-Story-Motion-3.0.0- ตามด้วยชื่อในตาราง
ดาวน์โหลดจาก Artifacts ของ [workflow ที่สำเร็จ](https://github.com/hirok-th/sports-story-motion/actions) ต้องลงชื่อเข้า GitHub เพื่อโหลด artifact
แตก ZIP artifact ชั้นนอกก่อน จึงจะเห็น ZIP ติดตั้งแต่ละแพลตฟอร์ม อย่าอัปโหลด ZIP ชั้นนอก
ถ้ายังไม่มี artifact สำเร็จ แปลว่ายังสร้างแพ็กเกจไม่สำเร็จ ไม่ใช่ไฟล์พร้อมติดตั้งที่ทดสอบแล้ว

## เตรียมซอร์สสำหรับทำงานและเรนเดอร์

เปิด PowerShell (ปุ่ม Start พิมพ์ PowerShell แล้วเปิด) ใช้ Git ที่ติดตั้งแล้ว:
    git clone --branch feat/thai-documentary-toolkit-v3 https://github.com/hirok-th/sports-story-motion.git sports-story-motion-v3
    cd sports-story-motion-v3

หากไม่มี Git ใช้ [ZIP ซอร์ส branch นี้](https://github.com/hirok-th/sports-story-motion/archive/refs/heads/feat/thai-documentary-toolkit-v3.zip) แล้วคลิกขวา Extract All เปิดโฟลเดอร์ที่มี README.md
ใน File Explorer คลิกช่องพาธ พิมพ์ powershell แล้ว Enter เพื่อเปิด PowerShell ในโฟลเดอร์นั้น

## Claude เว็บ/แชตในแอป

1. เปิด Claude และลงชื่อเข้าใช้
2. เปิด Settings > Capabilities เปิด Code execution and file creation (บางหน้าตาใช้ชื่อ Create and edit files)
3. ไป Customize > Skills กด + แล้ว + Create skill > Upload a skill
4. เลือก ZIP Claude-Skill โดยตรง ไม่ต้องแตก ZIP นี้
5. เปิดใช้ sports-story-motion แล้วเปิดแชตใหม่ พิมพ์ “ใช้ sports-story-motion ตรวจเครื่องมือและทำ storyboard สารคดีแผนที่ภาษาไทยเรื่องคลองปานามา”
6. ควรได้ผลตรวจความพร้อมกับแผนเรื่อง การมี skill ไม่ได้หมายความว่าแชตมี Chromium/FFmpeg หรือควบคุมบัญชี AI Studio ได้ ถ้าขาด ให้ดาวน์โหลดโปรเจกต์และเรนเดอร์ด้วยวิธีใน USAGE-TH.md

องค์กรอาจต้องเปิด Skills และ code execution โดยผู้ดูแล ดู [คู่มือ Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude)

## Claude Code CLI / desktop Code local

แตก ZIP Claude-Code เปิด PowerShell ในโฟลเดอร์ที่มี .claude-plugin และ skills แล้วตรวจ:
    claude plugin validate .
    claude --plugin-dir .

ใน session ที่เปิด พิมพ์:
    /sports-story-motion:sports-story-motion ตรวจเครื่องมือก่อนสร้างสารคดีแผนที่ไทย

คำสั่ง --plugin-dir เป็นการโหลด local สำหรับทดสอบ หากต้องการติดตั้งจาก marketplace ของโฟลเดอร์นี้:
    claude plugin marketplace add .
    claude plugin install sports-story-motion@sports-story-motion

เปิด session ใหม่และดูรายการ plugin/skill ที่ client แสดง
อย่าใช้ marketplace จาก main เพื่อคาดหวัง v3 จนกว่าจะ merge branch นี้
[เอกสาร Claude Code](https://code.claude.com/docs/en/plugins/install)

## Codex CLI / Codex desktop

เปิด PowerShell ที่มี Codex CLI:
    codex plugin marketplace add hirok-th/sports-story-motion --ref feat/thai-documentary-toolkit-v3
    codex plugin add sports-story-motion@sports-story-motion

หรือแตก ZIP Codex แล้วเปิด PowerShell ในโฟลเดอร์ที่มี .agents, plugin.json และ skills:
    codex plugin marketplace add .
    codex plugin add sports-story-motion@sports-story-motion

เปิด Codex ใหม่ ตรวจ /plugins และ /skills แล้วเรียก:
    $sports-story-motion:sports-story-motion ตรวจเครื่องมือและทำสารคดีแผนที่ภาษาไทย

หากมี marketplace ชื่อเดียวกันจากรุ่นเก่าอยู่แล้ว อ่านข้อความ CLI ก่อนเปลี่ยน source อย่าคิดว่าคำสั่ง add อัปเกรด source เดิมให้เสมอ
แอป desktop ใช้แหล่ง local marketplace ตามการตั้งค่าและเวอร์ชัน ไม่ใช่การอัปโหลด Claude ZIP
[Codex CLI](https://learn.chatgpt.com/docs/cli/reference) / [manifest และ marketplace](https://developers.openai.com/plugins/build/plugins)

## Google Antigravity App/CLI/IDE

แตก ZIP Antigravity แล้วเปิด PowerShell ในโฟลเดอร์ที่มี .antigravity-plugin และ skills ใช้ CLI ที่ลงชื่อเข้าใช้แล้ว:
    agy plugin validate --strict .
    agy plugin install .
    agy plugin list

ควรเห็น sports-story-motion ในรายการ จากนั้นเปิด Antigravity ใหม่
App: เปิด Customizations > Installed
IDE: เปิด Customizations ในแถบ Agent
App/CLI: เรียก /sports-story-motion ตามด้วยโจทย์; IDE ระบุชื่อ skill ในข้อความและตรวจว่าโหลดแล้ว

ถ้าไม่มี agy CLI ให้คัดลอกโฟลเดอร์ plugin ทั้งโฟลเดอร์ไปที่:
    %USERPROFILE%\.gemini\config\plugins\sports-story-motion
ภายในต้องมี .antigravity-plugin\plugin.json และ skills\sports-story-motion\SKILL.md
กด Win+R พิมพ์ %USERPROFILE% แล้ว Enter เพื่อเปิดตำแหน่งเริ่มต้น สร้างโฟลเดอร์ตามลำดับถ้ายังไม่มี อย่าให้ซ้อนเป็น sports-story-motion\sports-story-motion
อีกทางเลือกสำหรับเฉพาะ skill: คัดลอกโฟลเดอร์ skill ไป %USERPROFILE%\.gemini\config\skills\sports-story-motion
เลือกติดตั้งวิธีเดียวเพื่อลด skill ชื่อซ้ำ
[คู่มือ Antigravity](https://antigravity.google/docs/plugins) / [skill locations](https://antigravity.google/docs/skills)

## macOS / Linux

ใช้โครงสร้างแพ็กเกจเดียวกับแพลตฟอร์มนั้น เปลี่ยนพาธ Windows เป็น / และใช้ python3 แทน py
CLI คำสั่งเหมือนในเอกสารผู้ผลิต แต่ยังต้องติดตั้ง FFmpeg/Node/Chromium ให้ระบบนั้น
CI ตรวจ Linux และ Windows; macOS และการเปิดแอปจริงยังไม่ถือว่าทดสอบแล้ว
