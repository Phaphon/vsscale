import time
import tkinter as tk
from tkinter import ttk
from page_99_Utils import (
    create_confirm_popup,
    get_db_connection,
    reset_db_connection,
    read_station_id,
    AutocompleteCombobox
)


class AddPage(tk.Frame):
    def __init__(self, master, go_back):
        super().__init__(master, bg="#f4faff")
        # ----------------------------------
        # GLOBAL STYLE CONFIG
        # ----------------------------------
        self.FONT_HEADER = ("Segoe UI", 22, "bold")
        self.FONT_LABEL = ("Segoe UI", 18, "bold")
        self.FONT_ENTRY = ("Segoe UI", 18)
        self.FONT_BUTTON = ("Segoe UI", 18, "bold")

        self.COLOR_BG = "#f4faff"
        self.COLOR_WHITE = "white"
        self.COLOR_TEXT = "#003366"

        self.LABEL_STYLE = {
            "bg": self.COLOR_WHITE,
            "fg": self.COLOR_TEXT,
            "font": self.FONT_LABEL
        }

        self.ENTRY_STYLE = {
            "font": self.FONT_ENTRY,
            "bd": 1,
            "relief": "solid"
        }

        self.BUTTON_STYLE = {
            "font": self.FONT_BUTTON,
            "bd": 0,
            "relief": "flat",
            "cursor": "hand2",
            "width": 12,
            "height": 2
        }
        
        from vsscale_weight_controller import read_weight, set_zero
        self.read_weight = read_weight
        self.set_zero = set_zero
        
        # ---------------- UI ----------------
        # หัวข้อหลัก
        tk.Label(
            self, text="➕ เพิ่มรายการ", font=self.FONT_HEADER,
            bg=self.COLOR_BG, fg=self.COLOR_TEXT
        ).pack(pady=(20, 5))

        # กรอบเนื้อหา
        content = tk.Frame(self, bg=self.COLOR_WHITE, bd=1, relief="solid")
        content.pack(expand=True, fill="both", padx=40, pady=(5, 40))

        # === สร้างฟอร์มอยู่ตรงกลางของ content ===
        form_frame = tk.Frame(content, bg=self.COLOR_WHITE)
        form_frame.place(relx=0.5, rely=0.5, anchor="center")
        form_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # --- ตัวแปร ---
        # weight_var เก็บค่าจริง (ใช้กับ DB)
        self.abbr_var = tk.StringVar()
        self.product_var = tk.StringVar()
        self.producer_var = tk.StringVar()
        self.weight_var = tk.StringVar(value=str(self.read_weight()))
        # weight_display_var สำหรับแสดงบน UI เท่านั้น (จำนวนเต็ม)
        self.weight_display_var = tk.StringVar()
        self._update_weight_display_from_var()  # ตั้งค่าเริ่มต้นให้ display เป็นจำนวนเต็ม
        
        
        # --- โหลดข้อมูลจาก DB ---
        self.mat_map, self.mat_map_reverse = {}, {}
        self.emp_map, self.emp_map_reverse = {}, {}
        try:
            reset_db_connection()
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("SELECT mat_id, mat_label_name FROM materials")
            for mid, name in cur.fetchall():
                self.mat_map[mid] = name
                self.mat_map_reverse[name] = mid

            cur.execute("SELECT emp_id, emp_name FROM v_emp")
            for eid, name in cur.fetchall():
                self.emp_map[eid] = name
                self.emp_map_reverse[name] = eid

        except Exception as e:
            print("❌ โหลดข้อมูลสินค้า/ผู้ผลิตล้มเหลว:", e)
        finally:
            if cur: cur.close()
            if conn: conn.close()

        # --- Label + Input Styling (ใช้จาก config ด้านบน) ---
        # แถว 1
        tk.Label(form_frame, text="เลขย่อ:", **self.LABEL_STYLE).grid(row=0, column=0, sticky="e", padx=5, pady=8)
        tk.Entry(form_frame, textvariable=self.abbr_var, **self.ENTRY_STYLE).grid(row=0, column=1, sticky="we", padx=5, pady=8)

        tk.Label(form_frame, text="สินค้า:", **self.LABEL_STYLE).grid(row=0, column=2, sticky="e", padx=5, pady=8)
        self.product_entry = AutocompleteCombobox(
            form_frame,
            values=sorted(self.mat_map.values()) if self.mat_map else [],
            textvariable=self.product_var
        )
        self.product_entry.grid(row=0, column=3, sticky="we", padx=5, pady=8)

        # แถว 2
        tk.Label(form_frame, text="ผู้ผลิต:", **self.LABEL_STYLE).grid(row=1, column=0, sticky="e", padx=5, pady=8)
        self.producer_entry = AutocompleteCombobox(
            form_frame,
            values=sorted(self.emp_map.values()) if self.emp_map else [],
            textvariable=self.producer_var
        )
        self.producer_entry.grid(row=1, column=1, sticky="we", padx=5, pady=8)

        tk.Label(form_frame, text="น้ำหนัก:", **self.LABEL_STYLE).grid(row=1, column=2, sticky="e", padx=5, pady=8)
        tk.Entry(
            form_frame, textvariable=self.weight_display_var, state="readonly",
            readonlybackground=self.COLOR_WHITE, **self.ENTRY_STYLE
        ).grid(row=1, column=3, sticky="we", padx=5, pady=8)


        # --- ปุ่มปรับศูนย์ / ยกเลิก / บันทึก เรียงในบรรทัดเดียว ---
        def go_back_action():
            self.reset_inputs()
            go_back()

        btn_frame = tk.Frame(form_frame, bg=self.COLOR_WHITE)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=25)  # span ครอบทุกคอลัมน์เพื่อจัดกึ่งกลาง

        # ปุ่มปรับศูนย์
        btn_zero = tk.Button(
            btn_frame, text="⚖ ปรับศูนย์", command=self.zero_weight,
            bg="#b5dcff", fg=self.COLOR_TEXT, activebackground="#d3ebff",
            **self.BUTTON_STYLE
        )
        btn_zero.pack(side="left", padx=(0, 40))  # ช่องว่างมากระหว่างปรับศูนย์กับยกเลิก

        # ปุ่มยกเลิก
        btn_cancel = tk.Button(
            btn_frame, text="❌ ยกเลิก", command=go_back_action,
            bg="#ffb5b5", fg="#003366", activebackground="#ffd6d6",
            **self.BUTTON_STYLE
        )
        btn_cancel.pack(side="left", padx=(35, 15))  # ช่องว่างเล็กระหว่างยกเลิกกับบันทึก

        # ปุ่มบันทึก
        btn_save = tk.Button(
            btn_frame, text="✔ บันทึก", command=self.confirm_save,
            bg="#b5dcff", fg="#003366", activebackground="#d3ebff",
            **self.BUTTON_STYLE
        )
        btn_save.pack(side="left", padx=(20, 0))

    # ------------------------------- HELPERS ------------------------------- #
    def _update_weight_display_from_var(self):
        """
        แปลง self.weight_var (ค่าจริง) -> self.weight_display_var (จำนวนเต็มสำหรับแสดง)
        โดยไม่แก้ค่า self.weight_var
        """
        raw = self.weight_var.get()
        try:
            # แปลงเป็น float แล้วตัดทศนิยมด้วย int() (truncate)
            display = str(int(float(raw)))
        except Exception:
            display = raw  # ถ้าไม่ใช่ตัวเลข ให้แสดงเดิม
        self.weight_display_var.set(display)

    # ------------------------------- LOGIC ------------------------------- #

    def reset_inputs(self):
        self.abbr_var.set("")
        self.product_var.set("")
        self.producer_var.set("")
        self.weight_var.set(str(self.read_weight()))
        self._update_weight_display_from_var()
        if hasattr(self.product_entry, "_hide_listbox"): self.product_entry._hide_listbox()
        if hasattr(self.producer_entry, "_hide_listbox"): self.producer_entry._hide_listbox()

    def zero_weight(self):
        self.set_zero()
        w = self.read_weight()
        if w is not None:
            self.weight_var.set(str(w))
            self._update_weight_display_from_var()

    def confirm_save(self):
        create_confirm_popup(
            self, message="ยืนยันการบันทึกข้อมูลใหม่นี้?", confirm_callback=self.do_save
        )

    def do_save(self):
        abbr = self.abbr_var.get()
        product_name = self.product_var.get()
        producer_name = self.producer_var.get()
        weight = self.weight_var.get()

        if not abbr or not product_name or not producer_name:
            print("⚠️ ข้อมูลไม่ครบ")
            return

        product_id = self.mat_map_reverse.get(product_name)
        producer_id = self.emp_map_reverse.get(producer_name)
        if product_id is None or producer_id is None:
            print("⚠️ ไม่พบสินค้า หรือ ผู้ผลิตในฐานข้อมูล")
            return

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            user_id = read_station_id()

            # 1️⃣ ตรวจสอบว่า batch ล่าสุดของเดือนนี้คืออะไร
            cur.execute("""
                SELECT batch_number, pd_batch_id
                FROM pd
                WHERE YEAR(pd_pub_date) = YEAR(CURDATE())
                AND MONTH(pd_pub_date) = MONTH(CURDATE())
                ORDER BY pd_batch_id DESC
                LIMIT 1
            """)
            last_batch = cur.fetchone()

            now = time.localtime()
            yyMM = time.strftime("%y%m", now)

            if last_batch and last_batch[0].startswith(yyMM):
                # มี batch ของเดือนนี้อยู่แล้ว → ใช้ batch เดิม
                batch_number, pd_batch_id = last_batch
            else:
                # เดือนใหม่ หรือยังไม่มี batch → สร้าง batch ใหม่
                cur.execute("""
                    SELECT COUNT(pd_batch_id)
                    FROM pd
                    WHERE YEAR(pd_pub_date) = YEAR(CURDATE())
                    AND MONTH(pd_pub_date) = MONTH(CURDATE())
                """)
                count = cur.fetchone()[0] or 0
                batch_number = f"{yyMM}{count:03d}"

                cur.execute("""
                    INSERT INTO pd (batch_number, pd_pub_date, user_id, pd_status_id, pd_group_id)
                    VALUES (%s, NOW(), %s, %s, %s)
                """, (batch_number, user_id, 1, None))
                pd_batch_id = cur.lastrowid

            # 2️⃣ หาลำดับ item ล่าสุดใน batch นี้
            cur.execute("""
                SELECT COUNT(pd_item_id)
                FROM pd_item
                WHERE pd_batch_id = %s
            """, (pd_batch_id,))
            item_count = cur.fetchone()[0] or 0

            # 3️⃣ สร้างหมายเลข item ใหม่ เช่น 2511012-000
            pd_item_number = f"{batch_number}-{item_count:03d}"

            # 4️⃣ บันทึกข้อมูลลง pd_item
            cur.execute("""
                INSERT INTO pd_item (
                    pd_batch_id, pd_item_number, resource_id, result_id, pd_weight,
                    fac_id, emp_id, pd_item_status_id, pd_item_remark, on_stock
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                pd_batch_id, pd_item_number, product_id, product_id, weight,
                1, producer_id, 1, abbr, 0
            ))

            conn.commit()
            print(f"✅ เพิ่มข้อมูลสำเร็จ: {batch_number}-{item_count:03d}, {abbr}, {product_name}, {producer_name}, {weight}")
            self.reset_inputs()

        except Exception as e:
            print("❌ เพิ่มข้อมูลล้มเหลว:", e)

        finally:
            cur.close()
            conn.close()

    # ------------------------------- LOOP ------------------------------- #

    def start_weight_loop(self):
        self._running = True
        self.update_weight_loop()

    def stop_weight_loop(self):
        self._running = False

    def update_weight_loop(self):
        if not getattr(self, "_running", False):
            return
        try:
            w = self.read_weight()
            if w is not None:
                self.weight_var.set(str(w))
                self._update_weight_display_from_var()
        except Exception as e:
            print("❌ อ่านน้ำหนักล้มเหลว:", e)
        finally:
            self.after(500, self.update_weight_loop)
