import time
import tkinter as tk
from tkinter import ttk
from page_99_Utils import (
    create_confirm_popup,
    get_db_connection,
    reset_db_connection,
    read_station_id,
    show_info_popup,
    GLOBAL_STYLE as GS,
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

        # -------------------------------
        # ตั้งค่า column ให้คอลัมน์ 3 (ช่องน้ำหนัก) กว้างเป็นพิเศษ
        # -------------------------------
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(2, weight=1)
        form_frame.columnconfigure(3, weight=1, minsize=200)  # คอลัมน์ 3 สำหรับน้ำหนัก


        # -------------------------------
        # แถว 1 — ปุ่มกด
        # -------------------------------
        def go_back_action():
            # ปิด dropdown ของ combobox ทั้งหมดที่อาจเปิดอยู่ (safety)
            try:
                AutocompleteCombobox.destroy_all_popups()
            except Exception:
                pass

            # reset inputs (ซึ่งตอนนี้ไม่จำเป็นต้องตรวจสอบ hasattr อีก)
            self.reset_inputs()

            go_back()


        btn_frame = tk.Frame(form_frame, bg=self.COLOR_WHITE)
        btn_frame.grid(row=0, column=0, columnspan=4, pady=25)

        btn_zero = tk.Button(
            btn_frame, text="⚖ ปรับศูนย์", command=self.zero_weight,
            bg="#b5dcff", fg=self.COLOR_TEXT, activebackground="#d3ebff",
            **self.BUTTON_STYLE
        )
        btn_zero.pack(side="left", padx=(0, 40))

        btn_cancel = tk.Button(
            btn_frame, text="❌ ยกเลิก", command=go_back_action,
            bg="#ffb5b5", fg="#003366", activebackground="#ffd6d6",
            **self.BUTTON_STYLE
        )
        btn_cancel.pack(side="left", padx=(35, 15))

        btn_save = tk.Button(
            btn_frame, text="✔ บันทึก", command=self.confirm_save,
            bg="#b5dcff", fg="#003366", activebackground="#d3ebff",
            **self.BUTTON_STYLE
        )
        btn_save.pack(side="left", padx=(20, 0))


        # -------------------------------
        # แถว 2 — เลขย่อ + สินค้า
        # -------------------------------
        tk.Label(form_frame, text="เลขย่อ:", **self.LABEL_STYLE).grid(row=1, column=0, sticky="e", padx=5, pady=8)
        tk.Entry(form_frame, textvariable=self.abbr_var, **self.ENTRY_STYLE).grid(row=1, column=1, sticky="we", padx=5, pady=8)

        tk.Label(form_frame, text="สินค้า:", **self.LABEL_STYLE).grid(row=1, column=2, sticky="e", padx=5, pady=8)
        self.product_entry = AutocompleteCombobox(
            form_frame,
            values=sorted(self.mat_map.values()) if self.mat_map else [],
            textvariable=self.product_var, entry_font=self.FONT_ENTRY,
            listbox_font=self.FONT_ENTRY
        )
        self.product_entry.grid(row=1, column=3, sticky="we", padx=5, pady=8)


        # -------------------------------
        # แถว 3 — ผู้ผลิต + น้ำหนัก (ช่องใหญ่ขึ้น)
        # -------------------------------
        tk.Label(form_frame, text="ผู้ผลิต:", **self.LABEL_STYLE).grid(row=2, column=0, sticky="e", padx=5, pady=8)
        self.producer_entry = AutocompleteCombobox(
            form_frame,
            values=sorted(self.emp_map.values()) if self.emp_map else [],
            textvariable=self.producer_var, entry_font=self.FONT_ENTRY,
            listbox_font=self.FONT_ENTRY
        )
        self.producer_entry.grid(row=2, column=1, sticky="we", padx=5, pady=8)

        # Label น้ำหนัก (ฟอนต์ใหญ่ขึ้น)
        tk.Label(
            form_frame, 
            text="น้ำหนัก:", 
            font=GS["FONT_WEIGHT_LABEL"],
            bg=form_frame.cget("bg"), 
            fg=self.COLOR_TEXT
        ).grid(row=2, column=2, sticky="e", padx=5, pady=8)

        # ทำ copy ENTRY_STYLE แล้วลบ font ออก
        weight_style = self.ENTRY_STYLE.copy()
        weight_style.pop("font", None)   # เอา font ออกเพื่อไม่ให้ซ้ำ

        # ช่องแสดงน้ำหนัก (ใหญ่ขึ้น + ฟอนต์ใหญ่ขึ้น)
        self.weight_entry = tk.Entry(
            form_frame,
            textvariable=self.weight_display_var,
            state="readonly",
            font=GS["FONT_WEIGHT_VALUE"],          # ฟอนต์ใหญ่ขึ้น
            readonlybackground=self.COLOR_WHITE,
            justify="center",                      # จัดกลางให้เด่น
            width=10, 
            **weight_style                           # ใช้ style ที่ลบ font ออกแล้ว
        )
        self.weight_entry.grid(
            row=2, column=3,
            sticky="we",
            padx=5, pady=8,
            ipadx=40,   # ขยายความกว้าง
            ipady=10    # ขยายความสูง
        )



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

        # --- 1) ตรวจว่ากรอกข้อมูลครบไหม ---
        missing_fields = []

        if not abbr or abbr.strip() == "":
            missing_fields.append("เลขย่อสินค้า")

        if not product_name or product_name.strip() == "":
            missing_fields.append("ชื่อสินค้า")

        if not producer_name or producer_name.strip() == "":
            missing_fields.append("ชื่อผู้ผลิต")

        if missing_fields:
            msg = "กรุณากรอกข้อมูลให้ครบทุกช่อง:\n- " + "\n- ".join(missing_fields)
            show_info_popup(self, "ข้อมูลไม่ครบ", msg)
            print("⚠️ ข้อมูลไม่ครบ:", missing_fields)
            return


        # --- 2) ตรวจว่าชื่อสินค้าและผู้ผลิตต้องตรงตามฐานข้อมูล (dropdown) ---
        product_id = self.mat_map_reverse.get(product_name.strip())
        producer_id = self.emp_map_reverse.get(producer_name.strip())

        invalid_fields = []

        if product_id is None:
            invalid_fields.append("ชื่อสินค้าไม่ตรงกับข้อมูลในระบบ")

        if producer_id is None:
            invalid_fields.append("ชื่อผู้ผลิตไม่ตรงกับข้อมูลในระบบ")

        if invalid_fields:
            msg = "ไม่สามารถบันทึกได้ เนื่องจาก:\n- " + "\n- ".join(invalid_fields)
            show_info_popup(self, "ข้อมูลไม่ถูกต้อง", msg)
            print("⚠️ ข้อมูลไม่ถูกต้อง:", invalid_fields)
            return

        # --- ถ้าผ่านทุกเงื่อนไข ก็ไปทำส่วนบันทึกได้เลย ---
        print("✓ ข้อมูลถูกต้อง พร้อมบันทึก")


        try: #สร้างชุดตัวเลข pd_batch_id และ หมายเลข pd_item_number ใหม่
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
            show_info_popup(self, "สำเร็จ", "บันทึกข้อมูลเรียบร้อยแล้ว")
            print(f"✅ เพิ่มข้อมูลสำเร็จ: {batch_number}-{item_count:03d}, {abbr}, {product_name}, {producer_name}, {weight}")
            self.reset_inputs()

        except Exception as e:
            show_info_popup(self, "ผิดพลาด", f"ไม่สามารถบันทึกข้อมูลได้:\n{e}")
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
