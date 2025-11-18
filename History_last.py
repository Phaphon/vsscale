import tkinter as tk
from tkinter import ttk
from page_99_Utils import (
    create_centered_popup,
    create_password_popup,
    create_confirm_popup,
    get_db_connection,
    get_password,
    reset_db_connection,
    AutocompleteCombobox,
    GLOBAL_STYLE as GS
    )
from vsscale_label import print_label


ROWS_PER_PAGE = 5

class HistoryPage(tk.Frame):
    def __init__(self, master, go_back):
        super().__init__(master, bg=GS["bg_main"])
        self.current_page = 0
        self.headers = ["แก้ไข", "เลขรายการ", "เลขย่อ", "ผู้ผลิต", "สินค้า", "น้ำหนัก", "ปริ้น"]

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton",
            font=GS["font_small"], padding=6,
            background=GS["bg_main"], relief="flat"
        )
        style.map("TButton",
            background=[("active", GS["button_active"]), ("pressed", GS["button_active"])]
        )
        style.configure("TLabel", font=GS["font_small"], background=GS["bg_frame"])
        style.configure("TFrame", background=GS["bg_frame"])

        # ----------------------
        # ปุ่มกลับ
        tk.Button(self, text="← กลับ", font=GS["font_bold"],
                  bg=GS["button_bg"], fg=GS["button_fg"], relief="flat",
                  command=go_back).pack(anchor="w", padx=20, pady=10)

        # ตารางกรอบ
        self.table_frame = tk.Frame(self, bd=2, relief="solid", bg=GS["bg_frame"])
        self.table_frame.pack(expand=True, fill="both", padx=20, pady=(0,20))

        # navigation
        nav_frame = tk.Frame(self, bg=GS["bg_main"])
        nav_frame.pack(pady=5)
        self.prev_btn = tk.Button(nav_frame, text="←", width=3, font=GS["font_bold"],
                                  bg=GS["button_bg"], fg=GS["button_fg"],
                                  relief="raised", command=self.prev_page)
        self.prev_btn.pack(side="left")

        self.page_label = tk.Label(nav_frame, text="", font=GS["font_bold"],
                                   bg=GS["bg_main"], fg=GS["fg_text"])
        self.page_label.pack(side="left", padx=6)

        self.next_btn = tk.Button(nav_frame, text="→", width=3, font=GS["font_bold"],
                                  bg=GS["button_bg"], fg=GS["button_fg"],
                                  relief="raised", command=self.next_page)
        self.next_btn.pack(side="left")

        # ช่องพิมพ์หมายเลขหน้า
        self.page_entry = tk.Entry(self, width=5, justify="center", font=GS["font_normal"],
                                   bg=GS["entry_bg"], fg=GS["fg_text"], bd=1, relief="solid")
        self.page_entry.pack(pady=(0, 10))
        self.page_entry.insert(0, "1")
        self.page_entry.bind("<Return>", self.go_to_page)

        self.load_data()
        self.display_table()

    def load_data(self):
        try:
            conn = reset_db_connection()
            cursor = conn.cursor()

            # โหลดสินค้า
            cursor.execute("SELECT mat_id, mat_label_name FROM materials")
            mats = cursor.fetchall()
            self.mat_map = {m[0]: m[1] for m in mats}
            self.mat_map_reverse = {m[1]: m[0] for m in mats}

            # โหลดผู้ผลิต
            cursor.execute("SELECT emp_id, emp_name FROM v_emp")
            emps = cursor.fetchall()
            self.emp_map = {e[0]: e[1] for e in emps}
            self.emp_map_reverse = {e[1]: e[0] for e in emps}

            # โหลด pd_item
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

        btn_col_width = 8
        data_col_width = 15

        # header
        for col, text in enumerate(self.headers):
            tk.Label(
                self.table_frame, text=text,
                font=GS["font_bold"],
                bg=GS["bg_header"], fg=GS["fg_header"],
                borderwidth=1, relief="solid",
                width=column_widths.get(col, data_col_width),
                padx=5, pady=12
            ).grid(row=0, column=col, sticky="nsew")

        start = self.current_page * ROWS_PER_PAGE
        end = start + ROWS_PER_PAGE
        page_rows = self.data[start:end]

        for r, row_data in enumerate(page_rows, start=1):
            bg_color = GS["bg_row_odd"] if r % 2 == 1 else GS["bg_row_even"]

            for c in range(len(self.headers)):

                if c == 0:
                    # ปุ่มแก้ไข
                    tk.Button(
                        self.table_frame, text="✎", font=GS["font_small"],
                        bg=GS["button_bg"], fg=GS["button_fg"],
                        activebackground=GS["button_active"],
                        relief="raised", width=btn_col_width,
                        command=lambda rd=row_data: self.show_popup(rd)
                    ).grid(row=r, column=c, sticky="nsew")

                elif c == len(self.headers)-1:
                    # ปุ่มปริ้น
                    tk.Button(
                        self.table_frame, text="พิมพ์", font=GS["font_small"],
                        bg=GS["button_bg"], fg=GS["button_fg"],
                        activebackground=GS["button_active"],
                        relief="raised", width=btn_col_width,
                        command=lambda rd=row_data: self.print_popup(rd)
                    ).grid(row=r, column=c, sticky="nsew")

                else:
                    # คอลัมน์น้ำหนัก → แปลงเป็นจำนวนเต็ม
                    if c == 5:
                        try:
                            display_value = str(int(float(row_data[c])))
                        except:
                            display_value = row_data[c]
                    else:
                        display_value = row_data[c]

                    tk.Label(
                        self.table_frame, text=display_value,
                        font=GS["font_normal"],
                        bg=bg_color, fg=GS["fg_text"],
                        borderwidth=1, relief="solid",
                        padx=5, pady=6,
                        width=data_col_width
                    ).grid(row=r, column=c, sticky="nsew")

        for c in range(len(self.headers)):
            self.table_frame.grid_columnconfigure(c, weight=1)
        for r in range(ROWS_PER_PAGE + 1):
            self.table_frame.grid_rowconfigure(r, weight=1)

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
        popup = create_centered_popup(self, 560, 360, title="แก้ไข")
        popup.configure(bg=GS["bg_frame"])

        id_var       = tk.StringVar(value=str(row_data[0]))
        num_var      = tk.StringVar(value=row_data[1])
        abbr_var     = tk.StringVar(value=row_data[2])
        producer_var = tk.StringVar(value=row_data[3])
        product_var  = tk.StringVar(value=row_data[4])
        weight_var   = tk.StringVar(value=row_data[5])

        product_values  = sorted(self.mat_map.values())
        producer_values = sorted(self.emp_map.values())

        tk.Label(popup, text="แก้ไข", font=GS["font_bold"], bg=GS["bg_frame"]).pack(pady=6)
        content = tk.Frame(popup, bg=GS["bg_frame"])
        content.pack(expand=True, fill="both", padx=16, pady=6)

        def L(text): return tk.Label(content, text=text, bg=GS["bg_frame"], font=GS["font_normal"])

        L("เลขรายการ:").grid(row=0, column=0, sticky="e", padx=5, pady=6)
        tk.Entry(content, textvariable=num_var, state="readonly",
                 readonlybackground=GS["bg_frame"], font=GS["font_normal"]
        ).grid(row=0, column=1, columnspan=3, sticky="we", padx=5, pady=6)

        L("เลขย่อ:").grid(row=1, column=0, sticky="e", padx=5, pady=6)
        tk.Entry(content, textvariable=abbr_var,
                 font=GS["font_normal"], bg=GS["entry_bg"]
        ).grid(row=1, column=1, sticky="we", padx=5, pady=6)

        L("สินค้า:").grid(row=1, column=2, sticky="e", padx=5, pady=6)
        product_widget = AutocompleteCombobox(
            content,
            values=product_values,
            textvariable=product_var,
            entry_font=GS["font_normal"],
            listbox_font=GS["font_small"],
            listbox_maxheight=8
        )
        product_widget.grid(row=1, column=3, sticky="we", padx=5, pady=6)

        L("ผู้ผลิต:").grid(row=2, column=0, sticky="e", padx=5, pady=6)
        producer_widget = AutocompleteCombobox(
            content,
            values=producer_values,
            textvariable=producer_var,
            entry_font=GS["font_normal"],
            listbox_font=GS["font_small"],
            listbox_maxheight=8
        )
        producer_widget.grid(row=2, column=1, sticky="we", padx=5, pady=6)

        L("น้ำหนัก:").grid(row=2, column=2, sticky="e", padx=5, pady=6)
        tk.Entry(content, textvariable=weight_var, state="readonly",
                 readonlybackground=GS["bg_frame"], font=GS["font_normal"]
        ).grid(row=2, column=3, sticky="we", padx=5, pady=6)

        content.grid_columnconfigure(1, weight=1)
        content.grid_columnconfigure(3, weight=1)

        # bottom buttons
        btns = tk.Frame(popup, bg=GS["bg_frame"])
        btns.pack(pady=10)
        tk.Button(btns, text="❌ ยกเลิก", width=10,
                  command=popup.destroy, bg=GS["button_bg"],
                  fg=GS["button_fg"], activebackground=GS["button_active"],
                  font=GS["font_normal"]
        ).pack(side="left", padx=8)

        tk.Button(btns, text="✔ บันทึก", width=10,
                  command=lambda: self._confirm_save(row_data, popup,
                                                     num_var, abbr_var,
                                                     producer_var, product_var),
                  bg=GS["button_bg"], fg=GS["button_fg"],
                  activebackground=GS["button_active"],
                  font=GS["font_normal"]
        ).pack(side="left", padx=8)

        popup.show()
        popup.transient(self)
        popup.grab_set()
        
    def print_popup(self, row_data):
        def do_print():
            pd_item_id = row_data[0]
            extra = self.get_print_detail_from_verp(pd_item_id)
            print_label(
                port="/dev/ttySC1",
                baud=115200,
                header_text="header_747_270.bmp",
                table_text="table_vj_mono_2_270.bmp",
                product_name=row_data[4],
                pd_item_number=row_data[1],
                pd_date=extra["pd_date"],
                mat_size=extra["mat_size"],
                mat_grade=extra["mat_grade"],
                pd_weight=row_data[5],
                pd_item_remark=row_data[2],
            )

        create_confirm_popup(self, message=f"ยืนยันการพิมพ์ป้าย {row_data[3]} ?", confirm_callback=do_print)

    def get_print_detail_from_verp(self, pd_item_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    DATE_FORMAT(pd.pd_pub_date, '%d/%m/%Y') AS pd_date,
                    tisi_size.tisi_size_text AS mat_size,
                    tisi_grade.tisi_grade_text AS mat_grade
                FROM pd_item
                LEFT JOIN materials ON materials.mat_id = pd_item.result_id
                LEFT JOIN pd ON pd.pd_batch_id = pd_item.pd_batch_id
                LEFT JOIN tisi_size ON tisi_size.tisi_size_id = materials.tisi_size_id
                LEFT JOIN tisi_grade ON tisi_grade.tisi_grade_id = materials.tisi_grade_id
                WHERE pd_item.pd_item_id = %s
            """, (pd_item_id,))
            row = cursor.fetchone()
            if row:
                return {"pd_date": row[0] or "-", "mat_size": row[1] or "-", "mat_grade": row[2] or "-"}
            else:
                return {"pd_date": "-", "mat_size": "-", "mat_grade": "-"}
        except Exception as e:
            print("❌ โหลดข้อมูล print detail จาก verp server ล้มเหลว:", e)
            return {"pd_date": "-", "mat_size": "-", "mat_grade": "-"}
        finally:
            try:
                cursor.close()
                conn.close()
            except:
                pass

    def go_to_page(self, event=None):
        try:
            total_pages = (len(self.data) + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE
            target_page = int(self.page_entry.get()) - 1
            if 0 <= target_page < total_pages:
                self.current_page = target_page
                self.display_table()
            else:
                print(f"⚠ หมายเลขหน้าไม่ถูกต้อง (1-{total_pages})")
        except ValueError:
            print("⚠ กรุณาพิมพ์ตัวเลขเท่านั้น")
