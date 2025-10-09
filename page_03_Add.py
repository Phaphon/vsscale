# page_03_Add.py
import time
import tkinter as tk
from tkinter import ttk
from page_99_Utils import (
    create_confirm_popup,
    get_db_connection,
    reset_db_connection,
    read_station_id
)
from vsscale_weight_controller_Ori import read_weight, set_zero

class AddPage(tk.Frame):
    def __init__(self, master, go_back):
        super().__init__(master)

        tk.Label(self, text="เพิ่มรายการ", font=("Arial", 18, "bold")).pack(pady=10)

        content = tk.Frame(self, padx=20, pady=10)
        content.pack(expand=True, fill="both")

        self.abbr_var = tk.StringVar()
        self.product_var = tk.StringVar()
        self.producer_var = tk.StringVar()
        self.weight_var = tk.StringVar(value=str(read_weight()))

        # --- เตรียมค่า Combobox จาก DB ---
        self.mat_map = {}
        self.mat_map_reverse = {}
        self.emp_map = {}
        self.emp_map_reverse = {}

        conn = None
        cur = None
        try:
            # รีเฟรช connection ทุกครั้งเพื่อใช้ค่าคอนฟิกล่าสุด
            reset_db_connection()
            conn = get_db_connection()
            cur = conn.cursor()

            # ดึงสินค้า
            cur.execute("SELECT mat_id, mat_label_name FROM materials")
            for mid, name in cur.fetchall():
                self.mat_map[mid] = name
                self.mat_map_reverse[name] = mid

            # ดึงผู้ผลิต
            cur.execute("SELECT emp_id, emp_name FROM v_emp")
            for eid, name in cur.fetchall():
                self.emp_map[eid] = name
                self.emp_map_reverse[name] = eid

        except Exception as e:
            print("❌ โหลดข้อมูลสินค้า/ผู้ผลิตล้มเหลว:", e)

        finally:
            # ป้องกัน error ถ้า conn หรือ cur ไม่ถูกสร้าง
            if cur:
                cur.close()
            if conn:
                conn.close()

        # --- Input Fields ---
        tk.Label(content, text="เลขย่อ:").grid(row=0, column=0, sticky="e", padx=5, pady=6)
        tk.Entry(content, textvariable=self.abbr_var).grid(row=0, column=1, sticky="we", padx=5, pady=6)

        tk.Label(content, text="สินค้า:").grid(row=0, column=2, sticky="e", padx=5, pady=6)
        ttk.Combobox(content, values=sorted(self.mat_map.values()), state="readonly",
                     textvariable=self.product_var).grid(row=0, column=3, sticky="we", padx=5, pady=6)

        tk.Label(content, text="ผู้ผลิต:").grid(row=1, column=0, sticky="e", padx=5, pady=6)
        ttk.Combobox(content, values=sorted(self.emp_map.values()), state="readonly",
                     textvariable=self.producer_var).grid(row=1, column=1, sticky="we", padx=5, pady=6)

        tk.Label(content, text="น้ำหนัก:").grid(row=1, column=2, sticky="e", padx=5, pady=6)
        tk.Entry(content, textvariable=self.weight_var, state="readonly",
                 readonlybackground="white").grid(row=1, column=3, sticky="we", padx=5, pady=6)

        # --- ปุ่มปรับศูนย์ ---
        tk.Button(content, text="ปรับศูนย์", width=12, command=self.zero_weight).grid(row=2, column=0, columnspan=2, pady=10)

        # --- ปุ่มยกเลิก/บันทึก ---
        btns = tk.Frame(content)
        btns.grid(row=2, column=2, columnspan=2, pady=10)
        tk.Button(btns, text="❌ ยกเลิก", width=10, command=go_back).pack(side="left", padx=8)
        tk.Button(btns, text="✔ บันทึก", width=10, command=self.confirm_save).pack(side="left", padx=8)

        for c in range(4):
            content.grid_columnconfigure(c, weight=1)

        self.update_weight_loop()

    def update_weight_loop(self):
        """อ่านน้ำหนักจากเครื่องชั่งและอัปเดตทุก 0.5 วินาที"""
        try:
            weight = read_weight()
            if weight is not None:
                self.weight_var.set(str(weight))
        except Exception as e:
            print("❌ อ่านน้ำหนักล้มเหลว:", e)
        finally:
            # เรียกตัวเองซ้ำทุก 500 ms
            self.after(500, self.update_weight_loop)

    def zero_weight(self):
        """ปรับศูนย์และอ่านน้ำหนักใหม่ทันที"""
        set_zero()
        weight = read_weight()
        if weight is not None:
            self.weight_var.set(str(weight))

    def confirm_save(self):
        """ แสดง popup ก่อนบันทึกจริง """
        create_confirm_popup(self, message="ยืนยันการบันทึกข้อมูลใหม่นี้?", confirm_callback=self.do_save)

    def do_save(self):
        abbr = self.abbr_var.get()
        product_name = self.product_var.get()
        producer_name = self.producer_var.get()
        weight = self.weight_var.get()

        if not abbr or not product_name or not producer_name:
            print("⚠️ ข้อมูลไม่ครบถ้วน")
            return

        # map ชื่อสินค้าและผู้ผลิตเป็น id
        product_id = self.mat_map_reverse.get(product_name)
        producer_id = self.emp_map_reverse.get(producer_name)

        if product_id is None or producer_id is None:
            print("⚠️ ไม่พบสินค้า หรือ ผู้ผลิตในฐานข้อมูล")
            return

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # --- 1) สร้าง pd_batch_id และ batch_number ---
            station_id = read_station_id()  # user_id หรือ station_id
            now = time.localtime()
            year = now.tm_year % 100
            month = now.tm_mon

            # หา sequence ล่าสุดของเดือนนี้
            cur.execute("SELECT batch_number FROM pd WHERE batch_number LIKE %s ORDER BY pd_batch_id DESC LIMIT 1",
                        (f"{year:02d}{month:02d}%",))
            last = cur.fetchone()
            seq = int(last[0][-3:]) + 1 if last else 1
            batch_number = f"{year:02d}{month:02d}{seq:03d}"

            # INSERT pd
            cur.execute("""
                INSERT INTO pd (batch_number, pd_pub_date, user_id, pd_status_id, pd_group_id)
                VALUES (%s, NOW(), %s, %s, %s)
            """, (batch_number, station_id, 1, None))
            pd_batch_id = cur.lastrowid

            # --- 2) INSERT pd_item ---
            cur.execute("""
                INSERT INTO pd_item (
                    pd_batch_id, pd_item_number, resource_id, result_id, pd_weight,
                    fac_id, emp_id, pd_item_status_id, pd_item_remark, on_stock
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                pd_batch_id,
                "",            # pd_item_number ว่าง
                product_id,
                product_id,
                weight,
                1,             # fac_id
                producer_id,
                1,             # pd_item_status_id
                abbr,
                0              # on_stock
            ))

            conn.commit()
            print("✅ เพิ่มข้อมูลสำเร็จ:", batch_number, abbr, product_name, producer_name, weight)

            # ล้าง input
            self.abbr_var.set("")
            self.product_var.set("")
            self.producer_var.set("")
            self.weight_var.set(str(read_weight()))

        except Exception as e:
            print("❌ เพิ่มข้อมูลล้มเหลว:", e)
        finally:
            cur.close()
            conn.close()
