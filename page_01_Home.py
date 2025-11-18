import tkinter as tk


class HomePage(tk.Frame):
    def __init__(self, master, go_to_history, go_to_add, go_to_setting):
        super().__init__(master, bg="#f4faff")

        # 🔹 กำหนด Layout หลัก
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 🔹 สไตล์ปุ่ม
        button_style = {
            "font": ("Segoe UI", 36, "bold"),
            "width": 12,
            "height": 2,
            "bg": "#b5dcff",
            "fg": "#003366",
            "relief": "flat",
            "bd": 0,
            "activebackground": "#d3ebff",
            "cursor": "hand2"
        }

        # ปุ่มประวัติ
        tk.Button(self, text="ประวัติ", command=go_to_history, **button_style).grid(
            row=0, column=0, padx=20, pady=30, sticky="nsew"
        )

        # ปุ่มเพิ่มรายการ
        tk.Button(self, text="เพิ่มรายการ", command=go_to_add, **button_style).grid(
            row=0, column=1, padx=20, pady=30, sticky="nsew"
        )

        # ปุ่มตั้งค่า (มุมขวาล่าง)
        setting_style = {
            "font": ("Segoe UI", 12, "bold"),
            "bg": "#d0e7ff",
            "fg": "#003366",
            "relief": "flat",
            "bd": 0,
            "cursor": "hand2",
            "activebackground": "#b5dcff"
        }
        tk.Button(self, text="⚙ ตั้งค่า", command=go_to_setting, **setting_style).grid(
            row=1, column=1, sticky="se", padx=20, pady=20
        )

        # 🔹 เพิ่มชื่อระบบด้านบน (optional)
        title = tk.Label(
            self,
            text="Home",
            font=("Segoe UI", 24, "bold"),
            bg="#f4faff",
            fg="#003366"
        )
        title.place(relx=0.5, rely=0.1, anchor="center")
