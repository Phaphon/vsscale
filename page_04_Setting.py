import tkinter as tk
import mysql
from tkinter import messagebox
from page_99_Utils import db_config , save_config

class SettingPage(tk.Frame):
    def __init__(self, master, go_back):
        super().__init__(master)

        # ===== ปุ่มย้อนกลับ =====
        tk.Button(self, text="⬅ ย้อนกลับ", command=go_back).pack(anchor="nw", padx=5, pady=5)

        # ===== ชื่อหน้า =====
        tk.Label(self, text="ตั้งค่า", font=("Arial", 16, "bold")).pack(pady=10)

        # ===== กรอบหลักสำหรับฟอร์ม =====
        form_frame = tk.Frame(self)
        form_frame.pack(expand=True)

        # ฟังก์ชันช่วยสร้างแถว input
        def create_row(parent, label_text, entry_width=30):
            row = tk.Frame(parent)
            row.pack(fill="x", pady=6)

            lbl = tk.Label(row, text=label_text, width=15, anchor="w", font=("Arial", 12))
            lbl.pack(side="left", padx=5)

            entry = tk.Entry(row, width=entry_width, font=("Arial", 12))
            entry.pack(side="left", padx=5)
            return entry

        # ===== สร้างช่องกรอก =====
        self.sql_ip_entry      = create_row(form_frame, "Sql Server IP")
        self.sql_user_entry    = create_row(form_frame, "Sql user name")
        self.sql_pw_entry      = create_row(form_frame, "Sql pw")
        self.station_id_entry  = create_row(form_frame, "Station ID", entry_width=15)

        # === เติมค่าปัจจุบันจาก db_config ===
        self.sql_ip_entry.insert(0, db_config.get("host", ""))
        self.sql_user_entry.insert(0, db_config.get("user", ""))
        self.sql_pw_entry.insert(0, db_config.get("password", ""))
        self.station_id_entry.insert(0, db_config.get("station", ""))

        # ===== โหลดค่า config ปัจจุบัน =====
        self.reload_entries_from_config()

        # ===== ปุ่มบันทึก =====
        tk.Button(self, text="💾 บันทึก", font=("Arial", 12, "bold"),
                  command=self.save_settings).pack(pady=15)

    def reload_entries_from_config(self):
        """โหลดค่าจาก config.json แล้วใส่กลับลงช่องกรอก"""
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            cfg = db_config  # fallback ใช้ค่าจากตัวแปรในหน่วยความจำ

        # ล้างค่าก่อน
        self.sql_ip_entry.delete(0, tk.END)
        self.sql_user_entry.delete(0, tk.END)
        self.sql_pw_entry.delete(0, tk.END)
        self.station_id_entry.delete(0, tk.END)

        # ใส่ค่าปัจจุบันกลับ
        self.sql_ip_entry.insert(0, cfg.get("host", ""))
        self.sql_user_entry.insert(0, cfg.get("user", ""))
        self.sql_pw_entry.insert(0, cfg.get("password", ""))
        self.station_id_entry.insert(0, cfg.get("station", ""))

    def save_settings(self):
        host = self.sql_ip_entry.get().strip()
        user = self.sql_user_entry.get().strip()
        pw   = self.sql_pw_entry.get().strip()
        station = self.station_id_entry.get().strip()

        new_config = {
            "host": host,
            "user": user,
            "password": pw,
            "database": "rpisql",
            "station": station
        }

        try:
            # ทดสอบการเชื่อมต่อชั่วคราวก่อนบันทึก
            test_conn = mysql.connector.connect(
                host=host, user=user, password=pw, database="rpisql"
            )
            test_conn.close()

            # ✅ เชื่อมต่อผ่านแล้ว ค่อยอัปเดตและบันทึก
            db_config.update(new_config)

            save_config(db_config)

            messagebox.showinfo("บันทึก", "✅ บันทึกการตั้งค่าและเชื่อมต่อใหม่เรียบร้อยแล้ว!")
        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"❌ เชื่อมต่อฐานข้อมูลไม่ได้:\n{e}")
            # โหลดค่าจาก config.json กลับไปในช่อง input
            self.reload_entries_from_config()