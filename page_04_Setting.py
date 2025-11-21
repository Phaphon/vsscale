import tkinter as tk
from tkinter import messagebox
from page_99_Utils import db_config, save_config, CONFIG_FILE
import mysql.connector
import json

class SettingPage(tk.Frame):
    def __init__(self, master, go_back):
        super().__init__(master, bg="#f4faff")

        # ===== กรอบรวมทั้งหมด =====
        container = tk.Frame(self, bg="#f4faff")
        container.place(relx=0.5, rely=0.5, anchor="center")  # กึ่งกลางหน้าจอ

        # ===== ปุ่มย้อนกลับ =====
        tk.Button(
            container, text="⬅ ย้อนกลับ", command=go_back,
            bg="#b5dcff", fg="#003366", activebackground="#d3ebff",
            font=("Segoe UI", 11, "bold"), bd=0, relief="flat", cursor="hand2"
        ).pack(anchor="nw", padx=5, pady=5)

        # ===== ชื่อหน้า =====
        tk.Label(
            container, text="⚙ ตั้งค่า", font=("Segoe UI", 20, "bold"),
            bg="#f4faff", fg="#003366"
        ).pack(pady=(10, 20))

        # ===== กรอบหลักสำหรับฟอร์ม =====
        form_frame = tk.Frame(container, bg="white", bd=1, relief="solid")
        form_frame.pack(padx=20, pady=10, fill="both")
        form_frame.grid_columnconfigure(1, weight=1)

        # ฟังก์ชันช่วยสร้างแถว input
        def create_row(parent, label_text, entry_width=30):
            row = tk.Frame(parent, bg="white")
            row.pack(fill="x", pady=8)

            lbl = tk.Label(
                row, text=label_text, width=15, anchor="w",
                font=("Segoe UI", 12), bg="white", fg="#003366"
            )
            lbl.pack(side="left", padx=5)

            entry = tk.Entry(row, width=entry_width, font=("Segoe UI", 12), bd=1, relief="solid")
            entry.pack(side="left", padx=5, fill="x", expand=True)
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

        # ===== ปุ่มบันทึก =====
        tk.Button(
            container, text="บันทึก", font=("Segoe UI", 12, "bold"),
            bg="#b5dcff", fg="#003366", activebackground="#d3ebff",
            bd=0, relief="flat", cursor="hand2", width=15,
            command=self.save_settings
        ).pack(pady=(20, 10))

    def reload_entries_from_config(self):
        """โหลดค่าจาก config.json แล้วใส่กลับลงช่องกรอก"""
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception as e:
            print("⚠ reload_entries_from_config: ไม่สามารถอ่าน config ได้, ใช้ db_config แทน:", e)
            cfg = db_config

        # ล้างค่าก่อน
        self.sql_ip_entry.delete(0, tk.END)
        self.sql_user_entry.delete(0, tk.END)
        self.sql_pw_entry.delete(0, tk.END)
        self.station_id_entry.delete(0, tk.END)

        # ใส่ค่าปัจจุบันกลับ
        self.sql_ip_entry.insert(0, cfg.get("host", ""))
        self.sql_user_entry.insert(0, cfg.get("user", ""))
        # ใส่ password ที่อ่านได้ (ไม่ลบ)
        self.sql_pw_entry.insert(0, cfg.get("password", ""))
        self.station_id_entry.insert(0, cfg.get("station", ""))

    def save_settings(self):
        host = self.sql_ip_entry.get().strip()
        user = self.sql_user_entry.get().strip()
        pw   = self.sql_pw_entry.get().strip()
        station = self.station_id_entry.get().strip()
        database = "verp_dev"
        #database = "rpisql"

        new_config = {
            "host": host,
            "user": user,
            "password": pw,
            "database": database,
            "station": station
        }

        try:
            test_conn = mysql.connector.connect(
                host=host, user=user, password=pw, database=database, connect_timeout=5
            )
            test_conn.close()

            db_config.update(new_config)
            save_config(db_config)
            messagebox.showinfo("บันทึก", "✅ บันทึกการตั้งค่าและเชื่อมต่อใหม่เรียบร้อยแล้ว!")
        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"❌ เชื่อมต่อฐานข้อมูลไม่ได้:\n{e}")
            self.reload_entries_from_config()

    def on_show(self):
        self.reload_entries_from_config()

    def on_hide(self):
        pass