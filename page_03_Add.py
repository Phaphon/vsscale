# page_03_Add.py
import tkinter as tk
from tkinter import ttk
from page_99_Utils import create_confirm_popup, create_password_popup
# Mock database
PRODUCTS = ["สินค้าA", "สินค้าB", "สินค้าC"]
PRODUCERS = ["บริษัท1", "บริษัท2", "บริษัท3"]

# สำหรับ weight controller (mock)
from vsscale_weight_controller import read_weight, set_zero  # จะต้องมีไฟล์นี้

class AddPage(tk.Frame):
    def __init__(self, master, go_back):
        super().__init__(master)

        # --- 1. ชื่อหน้า ---
        tk.Label(self, text="เพิ่มรายการ", font=("Arial", 18, "bold"))\
            .pack(pady=10)

        # --- กรอบ content ---
        content = tk.Frame(self, padx=20, pady=10)
        content.pack(expand=True, fill="both")

        # --- StringVar สำหรับ input ---
        self.abbr_var = tk.StringVar()
        self.product_var = tk.StringVar()
        self.producer_var = tk.StringVar()
        self.weight_var = tk.StringVar(value=str(read_weight()))

        # --- 2 & 3. เลขย่อ และ สินค้า ---
        tk.Label(content, text="เลขย่อ:").grid(row=0, column=0, sticky="e", padx=5, pady=6)
        tk.Entry(content, textvariable=self.abbr_var)\
            .grid(row=0, column=1, sticky="we", padx=5, pady=6)

        tk.Label(content, text="สินค้า:").grid(row=0, column=2, sticky="e", padx=5, pady=6)
        ttk.Combobox(content, values=PRODUCTS, state="readonly", textvariable=self.product_var)\
            .grid(row=0, column=3, sticky="we", padx=5, pady=6)

        # --- 4 & 5. ผู้ผลิต และ น้ำหนัก ---
        tk.Label(content, text="ผู้ผลิต:").grid(row=1, column=0, sticky="e", padx=5, pady=6)
        ttk.Combobox(content, values=PRODUCERS, state="readonly", textvariable=self.producer_var)\
            .grid(row=1, column=1, sticky="we", padx=5, pady=6)

        tk.Label(content, text="น้ำหนัก:").grid(row=1, column=2, sticky="e", padx=5, pady=6)
        tk.Entry(content, textvariable=self.weight_var, state="readonly", readonlybackground="white")\
            .grid(row=1, column=3, sticky="we", padx=5, pady=6)

        # --- 6. ปุ่มปรับศูนย์ ---
        tk.Button(content, text="ปรับศูนย์", width=12, command=self.zero_weight)\
            .grid(row=2, column=0, columnspan=2, pady=10)

        # --- 7 & 8. ปุ่มยกเลิก / บันทึก ---
        btns = tk.Frame(content)
        btns.grid(row=2, column=2, columnspan=2, pady=10)

        tk.Button(btns, text="❌ ยกเลิก", width=10, command=go_back).pack(side="left", padx=8)
        tk.Button(btns, text="✔ บันทึก", width=10, command=self.save_record).pack(side="left", padx=8)
        #tk.Button(btns, text="✔ บันทึก", width=10, command=self.confirm_save).pack(side="left", padx=8)

        # ให้ column ขยายได้
        for c in range(4):
            content.grid_columnconfigure(c, weight=1)

    def zero_weight(self):
        set_zero()
        self.weight_var.set(str(read_weight()))

    def save_record(self):
        """ แสดง popup ก่อนบันทึกจริง """
        def do_save():
            abbr = self.abbr_var.get()
            product = self.product_var.get()
            producer = self.producer_var.get()
            weight = self.weight_var.get()

            if not abbr or not product or not producer:
                print("⚠️ ข้อมูลไม่ครบถ้วน")
                return

            # ✅ INSERT เข้า Database (คุณต้องใส่โค้ดเชื่อมต่อ SQL Server จริง ๆ ตรงนี้)
            print("💾 กำลังบันทึกลงฐานข้อมูล:", abbr, product, producer, weight)

            # ✅ สั่งพิมพ์ Label
            print("🖨️ สั่งพิมพ์ Label สำหรับ:", abbr, product, producer, weight)

            # เคลียร์ค่า input หลังบันทึก
            self.abbr_var.set("")
            self.product_var.set("")
            self.producer_var.set("")
            self.weight_var.set(str(read_weight()))

        # ใช้ popup ยืนยัน
        create_confirm_popup(self, message="ยืนยันการบันทึกข้อมูลใหม่นี้?", confirm_callback=do_save)