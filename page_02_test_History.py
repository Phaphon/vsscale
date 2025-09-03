import tkinter as tk
from tkinter import ttk
import mysql.connector
from page_99_Utils import create_centered_popup, create_password_popup, create_confirm_popup
from vsscale_label import print_label

ROWS_PER_PAGE = 5

class HistoryPage(tk.Frame):
    def __init__(self, master, go_back):
        super().__init__(master)

        self.current_page = 0
        self.headers = ["แก้ไข", "รหัสสินค้า", "Batch ID", "เลขสินค้า", "Resource", "น้ำหนัก", "ปริ้น"]

        # เชื่อมต่อฐานข้อมูลและดึงข้อมูลจริง
        self.data = self.fetch_data_from_db()

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

    def fetch_data_from_db(self):
        """ดึงข้อมูลจากตาราง pd_item ใน rpisql"""
        conn = mysql.connector.connect(
            host="localhost",
            user="root",           # 🔹 เปลี่ยนถ้ามี user เฉพาะ
            password="1234",
            database="rpisql"
        )
        cursor = conn.cursor()

        query = """
        SELECT pd_item_id, pd_batch_id, pd_item_number, resource_id, pd_weight 
        FROM pd_item
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return rows  # คืนข้อมูลออกมาเป็น list ของ tuple

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
                command=lambda rd=row_data: self.print_popup(rd)
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
        batch_var    = tk.StringVar(value=row_data[1])
        number_var   = tk.StringVar(value=row_data[2])
        resource_var = tk.StringVar(value=row_data[3])
        weight_var   = tk.StringVar(value=row_data[4])

        # --- UI ---
        tk.Label(popup, text="แก้ไข", font=("Arial", 14, "bold")).pack(pady=6)
        content = tk.Frame(popup)
        content.pack(expand=True, fill="both", padx=16, pady=6)

        tk.Label(content, text="รหัสสินค้า:").grid(row=0, column=0, sticky="e", padx=5, pady=6)
        tk.Entry(content, textvariable=id_var, state="readonly", readonlybackground="white")\
            .grid(row=0, column=1, sticky="we", padx=5, pady=6)

        tk.Label(content, text="Batch:").grid(row=1, column=0, sticky="e", padx=5, pady=6)
        tk.Entry(content, textvariable=batch_var, state="readonly", readonlybackground="white")\
            .grid(row=1, column=1, sticky="we", padx=5, pady=6)

        tk.Label(content, text="เลขสินค้า:").grid(row=2, column=0, sticky="e", padx=5, pady=6)
        tk.Entry(content, textvariable=number_var).grid(row=2, column=1, sticky="we", padx=5, pady=6)

        tk.Label(content, text="Resource:").grid(row=3, column=0, sticky="e", padx=5, pady=6)
        tk.Entry(content, textvariable=resource_var).grid(row=3, column=1, sticky="we", padx=5, pady=6)

        tk.Label(content, text="น้ำหนัก:").grid(row=4, column=0, sticky="e", padx=5, pady=6)
        tk.Entry(content, textvariable=weight_var, state="readonly", readonlybackground="white")\
            .grid(row=4, column=1, sticky="we", padx=5, pady=6)

        content.grid_columnconfigure(1, weight=1)

        # --- Buttons ---
        btns = tk.Frame(popup)
        btns.pack(pady=10)
        tk.Button(btns, text="❌ ยกเลิก", width=10, command=popup.destroy).pack(side="left", padx=8)

        def confirm_save():
            def do_save():
                # 🔹 ตอนนี้ยังไม่เขียน Update DB นะ
                popup.destroy()

            create_password_popup(
                popup,
                correct_password="4321",
                message="กรุณาใส่รหัสผ่านเพื่อยืนยันการแก้ไข",
                confirm_callback=do_save
            )

        tk.Button(btns, text="✔ บันทึก", width=10, command=confirm_save).pack(side="left", padx=8)

        popup.show()
        popup.transient(self)
        popup.grab_set()

    def print_popup(self, row_data):
        def do_print():
            print_label(
                port="/dev/ttyUSB0",
                baud=9600,
                header_text="Header",
                table_text="Table",
                product_name=row_data[2],
                pd_item_number=row_data[0],
                pd_date="2025-08-17",
                mat_size="Size",
                mat_grade="Grade",
                pd_weight=row_data[4],
                pd_item_remark="",
            )

        create_confirm_popup(self, message=f"ยืนยันการพิมพ์ป้าย {row_data[2]} ?", confirm_callback=do_print)
