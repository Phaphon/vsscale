import tkinter as tk
from tkinter import ttk
from page_99_Utils import create_centered_popup, create_password_popup, create_confirm_popup, get_db_connection, get_password, get_db_connection, reset_db_connection
from vsscale_label_Ori import print_label

ROWS_PER_PAGE = 5

class HistoryPage(tk.Frame):
    def __init__(self, master, go_back):
        super().__init__(master)
        self.master = master
        self.current_page = 0
        self.headers = ["แก้ไข", "เลขรายการ", "เลขย่อ", "ผู้ผลิต", "สินค้า", "น้ำหนัก", "ปริ้น"]

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

        self.load_data()
        self.display_table()

    def load_data(self):
        """โหลดข้อมูลจาก DB และสร้าง mapping สำหรับชื่อสินค้า/ผู้ผลิต"""
        try:
            # รีเฟรช connection ทุกครั้งก่อนโหลดข้อมูล
            reset_db_connection()
            conn = get_db_connection()
            cursor = conn.cursor()

            # โหลดข้อมูลสินค้า
            cursor.execute("SELECT mat_id, mat_label_name FROM materials")
            mats = cursor.fetchall()
            self.mat_map = {m[0]: m[1] for m in mats}
            self.mat_map_reverse = {m[1]: m[0] for m in mats}

            # โหลดข้อมูลผู้ผลิต
            cursor.execute("SELECT emp_id, emp_name FROM v_emp")
            emps = cursor.fetchall()
            self.emp_map = {e[0]: e[1] for e in emps}
            self.emp_map_reverse = {e[1]: e[0] for e in emps}

            # โหลดข้อมูล pd_item
            cursor.execute("""
                SELECT
                    pd_item_id,
                    pd_item_number,
                    pd_item_remark,
                    emp_id,
                    result_id,
                    pd_weight
                FROM pd_item
                ORDER BY pd_item_id DESC
            """)
            rows = cursor.fetchall()

            self.data = []
            for row in rows:
                emp_name = self.emp_map.get(row[3], row[3])
                mat_name = self.mat_map.get(row[4], row[4])
                self.data.append([
                    row[0],
                    row[1],
                    row[2],
                    emp_name,
                    mat_name,
                    row[5],
                ])

        except Exception as e:
            print("❌ โหลดข้อมูลล้มเหลว:", e)
            self.data = []
        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass


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

            for c, value in enumerate(row_data[1:], start=1):
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
        popup = create_centered_popup(self, 500, 300, title="แก้ไข")

        id_var       = tk.StringVar(value=str(row_data[0]))  # pd_item_id
        num_var      = tk.StringVar(value=row_data[1])       # เลขรายการ
        abbr_var     = tk.StringVar(value=row_data[2])       # เลขย่อ
        producer_var = tk.StringVar(value=row_data[3])       # ผู้ผลิตชื่อ
        product_var  = tk.StringVar(value=row_data[4])       # สินค้าชื่อ
        weight_var   = tk.StringVar(value=row_data[5])       # น้ำหนัก

        # เตรียมค่ารายการสินค้าและผู้ผลิตสำหรับ Combobox
        product_values  = sorted(self.mat_map.values())
        producer_values = sorted(self.emp_map.values())

        # Layout Frame
        tk.Label(popup, text="แก้ไข", font=("Arial", 14, "bold")).pack(pady=6)
        content = tk.Frame(popup)
        content.pack(expand=True, fill="both", padx=16, pady=6)

        # ------------------------
        # แถว 0: เลขรายการ (Read-only)
        tk.Label(content, text="เลขรายการ:").grid(row=0, column=0, sticky="e", padx=5, pady=6)
        tk.Entry(content, textvariable=id_var, state="readonly", readonlybackground="white")\
            .grid(row=0, column=1, columnspan=3, sticky="we", padx=5, pady=6)

        # ------------------------
        # แถว 1: เลขย่อ
        tk.Label(content, text="เลขย่อ:").grid(row=1, column=0, sticky="e", padx=5, pady=6)
        tk.Entry(content, textvariable=abbr_var).grid(row=1, column=1, sticky="we", padx=5, pady=6)

        # สินค้า (Dropdown)
        tk.Label(content, text="สินค้า:").grid(row=1, column=2, sticky="e", padx=5, pady=6)
        ttk.Combobox(content, values=product_values, state="readonly", textvariable=product_var)\
            .grid(row=1, column=3, sticky="we", padx=5, pady=6)

        # ------------------------
        # แถว 2: ผู้ผลิต
        tk.Label(content, text="ผู้ผลิต:").grid(row=2, column=0, sticky="e", padx=5, pady=6)
        ttk.Combobox(content, values=producer_values, state="readonly", textvariable=producer_var)\
            .grid(row=2, column=1, sticky="we", padx=5, pady=6)

        # น้ำหนัก (Read-only)
        tk.Label(content, text="น้ำหนัก:").grid(row=2, column=2, sticky="e", padx=5, pady=6)
        tk.Entry(content, textvariable=weight_var, state="readonly", readonlybackground="white")\
            .grid(row=2, column=3, sticky="we", padx=5, pady=6)

        # ------------------------
        content.grid_columnconfigure(1, weight=1)
        content.grid_columnconfigure(3, weight=1)

        # ------------------------
        # Save function
        def confirm_save():
            def do_save():
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()

                    emp_id = self.emp_map_reverse.get(producer_var.get(), producer_var.get())
                    mat_id = self.mat_map_reverse.get(product_var.get(), product_var.get())

                    cursor.execute("""
                        UPDATE pd_item
                        SET pd_item_number=%s, pd_item_remark=%s, emp_id=%s, result_id=%s
                        WHERE pd_item_id=%s
                    """, (num_var.get(), abbr_var.get(), emp_id, mat_id, id_var.get()))
                    conn.commit()
                except Exception as e:
                    print("❌ แก้ไขข้อมูล DB ล้มเหลว:", e)
                finally:
                    cursor.close()
                    conn.close()

                # อัปเดตตาราง
                row_data[1] = num_var.get()
                row_data[2] = abbr_var.get()
                row_data[3] = producer_var.get()
                row_data[4] = product_var.get()
                self.display_table()
                popup.destroy()

            create_password_popup(
                popup,
                correct_password=get_password("history"),
                message="กรุณาใส่รหัสผ่านเพื่อยืนยันการแก้ไข",
                confirm_callback=do_save
            )

        # ------------------------
        btns = tk.Frame(popup)
        btns.pack(pady=10)
        tk.Button(btns, text="❌ ยกเลิก", width=10, command=popup.destroy).pack(side="left", padx=8)
        tk.Button(btns, text="✔ บันทึก", width=10, command=confirm_save).pack(side="left", padx=8)

        popup.show()
        popup.transient(self)
        popup.grab_set()

    def print_popup(self, row_data):
        """แสดง confirm popup ก่อนปริ้น"""
        def do_print():
            print_label(
                port="/dev/ttySC1",
                baud=115200,
                header_text="header_747_270.bmp",
                table_text="table_vj_mono_2_270.bmp",
                product_name=row_data[3],
                pd_item_number=row_data[1],
                pd_date="2099-99-99",
                mat_size="Size",
                mat_grade="Grade",
                pd_weight=row_data[5],
                pd_item_remark="",
            )

        create_confirm_popup(self, message=f"ยืนยันการพิมพ์ป้าย {row_data[3]} ?", confirm_callback=do_print)
