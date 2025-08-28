import tkinter as tk
from tkinter import ttk
from page_99_Utils import create_centered_popup, create_password_popup, create_confirm_popup
from vsscale_label import print_label

ROWS_PER_PAGE = 5

class HistoryPage(tk.Frame):
    def __init__(self, master, go_back):
        super().__init__(master)

        self.current_page = 0
        self.headers = ["แก้ไข", "เลขรายการ", "เลขย่อ", "ผู้ผลิต", "สินค้า", "น้ำหนัก", "ปริ้น"]

        self.data = [
            [i, f"AB{i:02d}", f"บริษัท{i%5 or 5}", f"สินค้า{i%4 or 4}", f"{10+i}kg"]
            for i in range(1, 21)
        ]

        tk.Button(self, text="← กลับ", command=go_back).pack(anchor="w", padx=10, pady=10)
        self.table_frame = tk.Frame(self, bd=2, relief="groove", padx=10, pady=10)
        self.table_frame.pack(expand=True, fill="both", padx=20, pady=20)

        nav = tk.Frame(self)
        nav.pack(pady=10)
        self.prev_btn = tk.Button(nav, text="←", width=3, command=self.prev_page)
        self.prev_btn.pack(side="left")
        self.page_label = tk.Label(nav, text="")
        self.page_label.pack(side="left", padx=6)
        self.next_btn = tk.Button(nav, text="→", width=3, command=self.next_page)
        self.next_btn.pack(side="left")

        self.display_table()

    def display_table(self):
        for w in self.table_frame.winfo_children():
            w.destroy()

        for col, text in enumerate(self.headers):
            tk.Label(
                self.table_frame, text=text, font=("Arial", 10, "bold"),
                borderwidth=1, relief="solid", width=12
            ).grid(row=0, column=col, sticky="nsew")

        start = self.current_page * ROWS_PER_PAGE
        end = start + ROWS_PER_PAGE
        page_rows = self.data[start:end]

        for r, row_data in enumerate(page_rows, start=1):
            tk.Button(
                self.table_frame, text="✎",
                command=lambda rd=row_data: self.show_popup(rd)
            ).grid(row=r, column=0, sticky="nsew")

            for c, value in enumerate(row_data, start=1):
                tk.Label(
                    self.table_frame, text=value,
                    borderwidth=1, relief="solid", width=12
                ).grid(row=r, column=c, sticky="nsew")

            tk.Button(
                self.table_frame, text="🖨",
                command=lambda rd=row_data: self.print_popup(rd)  # เรียก function ใหม่
            ).grid(row=r, column=len(self.headers)-1, sticky="nsew")

        for c in range(len(self.headers)):
            self.table_frame.grid_columnconfigure(c, weight=1)

        total_pages = (len(self.data) + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE
        self.page_label.config(text=f"{self.current_page+1}/{total_pages}")
        self.prev_btn.config(state="normal" if self.current_page > 0 else "disabled")
        self.next_btn.config(state="normal" if self.current_page < total_pages-1 else "disabled")

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.display_table()

    def next_page(self):
        total_pages = (len(self.data) + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE
        if self.current_page < total_pages-1:
            self.current_page += 1
            self.display_table()

    def show_popup(self, row_data):
        popup = create_centered_popup(self, 400, 250, title="แก้ไข")

        # --- StringVar ---
        id_var       = tk.StringVar(value=str(row_data[0]))
        abbr_var     = tk.StringVar(value=row_data[1])
        producer_var = tk.StringVar(value=row_data[2])
        product_var  = tk.StringVar(value=row_data[3])
        weight_var   = tk.StringVar(value=row_data[4])

        # --- UI ---
        tk.Label(popup, text="แก้ไข", font=("Arial", 14, "bold")).pack(pady=6)
        content = tk.Frame(popup)
        content.pack(expand=True, fill="both", padx=16, pady=6)

        product_values  = sorted({row[3] for row in self.data})
        producer_values = sorted({row[2] for row in self.data})

        tk.Label(content, text="เลขรายการ:").grid(row=0, column=0, sticky="e", padx=5, pady=6)
        tk.Entry(content, textvariable=id_var, state="readonly", readonlybackground="white")\
            .grid(row=0, column=1, columnspan=3, sticky="we", padx=5, pady=6)

        tk.Label(content, text="เลขย่อ:").grid(row=1, column=0, sticky="e", padx=5, pady=6)
        tk.Entry(content, textvariable=abbr_var).grid(row=1, column=1, sticky="we", padx=5, pady=6)

        tk.Label(content, text="สินค้า:").grid(row=1, column=2, sticky="e", padx=5, pady=6)
        ttk.Combobox(content, values=product_values, state="readonly", textvariable=product_var)\
            .grid(row=1, column=3, sticky="we", padx=5, pady=6)

        tk.Label(content, text="ผู้ผลิต:").grid(row=2, column=0, sticky="e", padx=5, pady=6)
        ttk.Combobox(content, values=producer_values, state="readonly", textvariable=producer_var)\
            .grid(row=2, column=1, sticky="we", padx=5, pady=6)

        tk.Label(content, text="น้ำหนัก:").grid(row=2, column=2, sticky="e", padx=5, pady=6)
        tk.Entry(content, textvariable=weight_var, state="readonly", readonlybackground="white")\
            .grid(row=2, column=3, sticky="we", padx=5, pady=6)

        content.grid_columnconfigure(1, weight=1)
        content.grid_columnconfigure(3, weight=1)

        # --- Buttons ---
        btns = tk.Frame(popup)
        btns.pack(pady=10)
        tk.Button(btns, text="❌ ยกเลิก", width=10, command=popup.destroy).pack(side="left", padx=8)


        def confirm_save():
            def do_save():
                row_data[1] = abbr_var.get()
                row_data[2] = producer_var.get()
                row_data[3] = product_var.get()
                self.display_table()
                popup.destroy()  # ปิด popup หลักหลังบันทึก

            create_password_popup(
                popup,
                correct_password="4321",  # ตั้งรหัสได้เอง
                message="กรุณาใส่รหัสผ่านเพื่อยืนยันการแก้ไข",
                confirm_callback=do_save
            )

        tk.Button(btns, text="✔ บันทึก", width=10, command=confirm_save).pack(side="left", padx=8)

        # --- แสดง popup หลังสร้าง widget ทั้งหมด ---
        popup.show()
        popup.transient(self)
        popup.grab_set()

    def print_popup(self, row_data):
        """
        แสดง confirm popup ก่อนปริ้น
        """
        def do_print():
            # 🔹 MOCK: ยังไม่ต่อเครื่องปริ้นจริง
            # พอมีเครื่องปริ้นจริง ให้เอาคอมเม้นต์ด้านล่างออก
            print_label(
                port="/dev/ttyUSB0",   # ตัวอย่าง port
                baud=9600,
                header_text="Header",
                table_text="Table",
                product_name=row_data[3],
                pd_item_number=row_data[0],
                pd_date="2025-08-17",
                mat_size="Size",
                mat_grade="Grade",
                pd_weight=row_data[4],
                pd_item_remark="",
            )

        create_confirm_popup(self, message=f"ยืนยันการพิมพ์ป้าย {row_data[3]} ?", confirm_callback=do_print)
