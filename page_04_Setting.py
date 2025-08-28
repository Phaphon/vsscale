import tkinter as tk

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

        # ===== Rows =====
        self.sql_ip_entry      = create_row(form_frame, "Sql Server IP")
        self.sql_user_entry    = create_row(form_frame, "Sql user name")
        self.sql_pw_entry      = create_row(form_frame, "Sql pw")
        self.station_id_entry  = create_row(form_frame, "Station ID", entry_width=15)
