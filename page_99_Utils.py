import tkinter as tk
import mysql.connector
import json, os


# ให้ชี้ไปที่ไฟล์ config ภายในโฟลเดอร์โปรเจกต์เสมอ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
#CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

# page_00_style.py

GLOBAL_STYLE = {
    "bg_main": "#e6f0ff",      # สีพื้นหลังของหน้าใหญ่ (Page)
    "bg_frame": "#ffffff",     # สีพื้นหลังเฟรม
    "bg_header": "#cce0ff",    # สี header ตาราง
    "bg_row_even": "#ffffff",
    "bg_row_odd": "#f2f9ff",

    "fg_text": "#004080",
    "fg_header": "#004080",

    "font_normal": ("Segoe UI", 14),
    "font_small": ("Segoe UI", 12),
    "font_bold": ("Segoe UI", 14, "bold"),
    "FONT_WEIGHT_LABEL": ("Segoe UI", 28, "bold"),
    "FONT_WEIGHT_VALUE": ("Segoe UI", 32),

    "button_bg": "#ffffff",
    "button_fg": "#004080",
    "button_active": "#c9e4ff",

    "entry_bg": "#f0f8ff",
}

# ===== Popup utilities (themed) =====
def create_centered_popup(master, width, height, title=""):
    popup = tk.Toplevel(master)
    popup.withdraw()
    popup.title(title)
    popup.configure(bg=GLOBAL_STYLE["bg_main"])  # 💠 พื้นหลังอ่อนฟ้า
    popup.protocol("WM_DELETE_WINDOW", popup.destroy)

    def show():
        popup.update_idletasks()
        screen_w = popup.winfo_screenwidth()
        screen_h = popup.winfo_screenheight()
        x = (screen_w // 2) - (width // 2)
        y = (screen_h // 2) - (height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")
        popup.deiconify()
        popup.lift()
        popup.focus_force()

    popup.show = show
    return popup

def center_window(win, width, height):
    win.update_idletasks()
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = (screen_w // 2) - (width // 2)
    y = (screen_h // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

def create_confirm_popup(parent, message="ยืนยัน?", confirm_callback=None):
    confirm = tk.Toplevel(parent)
    confirm.withdraw()
    confirm.title("ยืนยัน")
    confirm.configure(bg="#f4faff")
    confirm.transient(parent)
    confirm.grab_set()
    confirm.focus_force()

    # ข้อความ
    tk.Label(
        confirm, text=message, 
        font=("Segoe UI", 12), 
        bg="#f4faff", fg="#003366"
    ).pack(pady=15, padx=20)

    # ปุ่ม
    def on_confirm():
        if confirm_callback:
            confirm_callback()
        confirm.destroy()

    btns = tk.Frame(confirm, bg="#f4faff")
    btns.pack(pady=10)

    style_btn = {
        "width": 10,
        "font": ("Segoe UI", 10, "bold"),
        "relief": "flat",
        "bd": 0,
        "cursor": "hand2",
        "activebackground": "#d3ebff"
    }

    tk.Button(btns, text="ยกเลิก", bg="#d0e7ff", fg="#003366", command=confirm.destroy, **style_btn).pack(side="left", padx=8)
    tk.Button(btns, text="ตกลง", bg="#b5dcff", fg="#003366", command=on_confirm, **style_btn).pack(side="left", padx=8)

    confirm.update_idletasks()
    w, h = 280, 150
    x = (confirm.winfo_screenwidth() // 2) - (w // 2)
    y = (confirm.winfo_screenheight() // 2) - (h // 2)
    confirm.geometry(f"{w}x{h}+{x}+{y}")
    confirm.deiconify()

    return confirm

def create_password_popup(parent, correct_password, message="กรุณาใส่รหัสผ่าน", confirm_callback=None):
    popup = tk.Toplevel(parent)
    popup.withdraw()
    popup.title("รหัสผ่าน")
    popup.configure(bg="#f4faff")
    popup.transient(parent)
    popup.grab_set()
    popup.focus_force()

    # หัวข้อ
    tk.Label(
        popup, text=message, 
        font=("Segoe UI", 12), 
        bg="#f4faff", fg="#003366"
    ).pack(pady=(15, 5))

    # ช่องกรอก
    pw_var = tk.StringVar()
    entry = tk.Entry(
        popup, textvariable=pw_var, show="*", 
        width=22, font=("Segoe UI", 11),
        relief="solid", bd=1, highlightbackground="#b5dcff", highlightcolor="#66b3ff"
    )
    entry.pack(pady=6)
    entry.focus_set()

    msg_label = tk.Label(popup, text="", font=("Segoe UI", 10), fg="red", bg="#f4faff")
    msg_label.pack()

    def on_confirm():
        if pw_var.get() == correct_password:
            if confirm_callback:
                confirm_callback()
            popup.destroy()
        else:
            msg_label.config(text="รหัสผ่านไม่ถูกต้อง")
            pw_var.set("")
            entry.focus_set()

    btns = tk.Frame(popup, bg="#f4faff")
    btns.pack(pady=15)

    style_btn = {
        "width": 10,
        "font": ("Segoe UI", 10, "bold"),
        "relief": "flat",
        "bd": 0,
        "cursor": "hand2",
        "activebackground": "#d3ebff"
    }

    tk.Button(btns, text="ยกเลิก", bg="#d0e7ff", fg="#003366", command=popup.destroy, **style_btn).pack(side="left", padx=8)
    tk.Button(btns, text="ตกลง", bg="#b5dcff", fg="#003366", command=on_confirm, **style_btn).pack(side="left", padx=8)

    popup.update_idletasks()
    w, h = 320, 190
    x = (popup.winfo_screenwidth() // 2) - (w // 2)
    y = (popup.winfo_screenheight() // 2) - (h // 2)
    popup.geometry(f"{w}x{h}+{x}+{y}")
    popup.deiconify()

    return popup

def show_info_popup(parent, title="แจ้งเตือน", message=""):
    popup = tk.Toplevel(parent)
    popup.title(title)
    popup.geometry("360x180")
    popup.configure(bg="white")
    popup.grab_set()  # บังคับให้กด popup ก่อน

    tk.Label(
        popup, text=message, font=(GLOBAL_STYLE["font_normal"]),
        bg="white", fg="#003366", wraplength=320
    ).pack(pady=25)

    tk.Button(
        popup, text="ปิด", font=(GLOBAL_STYLE["font_bold"]),
        width=10, bg="#b5dcff", fg="#003366",
        command=popup.destroy
    ).pack(pady=5)

# ===== ค่าตั้งต้นแบบปลอดภัย (ไม่ใส่รหัสผ่านจริง) =====
DEFAULT_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "rpisql",
    "station": "1",
    "settings_password": "",
    "history_password": ""
}

db_config = {}
connection = None

def load_config():
    """โหลดค่า config จากไฟล์ ถ้าไม่มีไฟล์ให้สร้างไฟล์เปล่าพร้อมค่า default"""
    global db_config
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                db_config = json.load(f)
        except Exception as e:
            print(f"⚠ โหลด config ล้มเหลว: {e}")
            db_config = DEFAULT_CONFIG.copy()
    else:
        db_config = DEFAULT_CONFIG.copy()
        save_config()  # สร้างไฟล์ใหม่ทันที

def save_config(new_config=None):
    """บันทึกค่า config ปัจจุบันลงไฟล์"""
    global db_config
    if new_config is not None:
        db_config.update(new_config)
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(db_config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠ บันทึก config ล้มเหลว: {e}")


def set_db_config(host, user, password, database, station,
                  settings_password=None, history_password=None):
    """อัปเดตค่า config แล้วบันทึก"""
    global db_config
    db_config.update({
        "host": host,
        "user": user,
        "password": password,
        "database": database,
        "station": station
    })
    if settings_password is not None:
        db_config["settings_password"] = settings_password
    if history_password is not None:
        db_config["history_password"] = history_password
    save_config()

def get_password(which):
    if which == "settings":
        return db_config.get("settings_password", "")
    if which == "history":
        return db_config.get("history_password", "")
    return ""

def get_db_connection():
    global connection
    if connection is None or not connection.is_connected():
        try:
            conn_cfg = {
                "host": db_config.get("host", "localhost"),
                "user": db_config.get("user", "root"),
                "password": db_config.get("password", ""),
                "database": db_config.get("database", ""),
            }
            print("Connecting to DB with:", conn_cfg)  # debug
            print(db_config)
            connection = mysql.connector.connect(**conn_cfg)
        except mysql.connector.Error as e:
            print(f"❌ Database connection error: {e}")
            connection = None
    return connection

def reset_db_connection():
    """ปิดและเปิดการเชื่อมต่อใหม่"""
    global connection
    if connection and connection.is_connected():
        connection.close()
    connection = None
    return get_db_connection()

# ===== Station =====
def read_station_id():
    return db_config.get("station", "2")#Default station2

# โหลด config ตอนเริ่มต้นโมดูล
load_config()

# ===== Autocomplete Combobox =====
from tkinter import ttk


import tkinter as tk
from tkinter import ttk


class AutocompleteCombobox(ttk.Frame):
    """
    Autocomplete Combobox (ปรับปรุง)
    - ป้องกัน popup ลอยตามมาที่หน้าอื่น
    - ปิด popup ทุกอันเมื่อ destroy หรือเปลี่ยนหน้า
    - popup จะสร้างเฉพาะเมื่อ widget visible
    - พิมพ์แล้วแสดง dropdown แต่ไม่แย่ง focus จาก Entry
    - กดลูกศร (Up/Down) จะนำ focus ไปยัง listbox เพื่อเลื่อนรายการ
    """

    _OPEN_INSTANCES = set()

    def __init__(self, master=None, values=None, textvariable=None,
                 entry_font=None, listbox_font=None, listbox_maxheight=6, **kwargs):
        super().__init__(master, **kwargs)

        self.values = list(values or [])
        self.filtered = self.values.copy()
        self.var = textvariable or tk.StringVar()
        self.entry_font = entry_font
        self.listbox_font = listbox_font
        self.listbox_maxheight = listbox_maxheight

        # สถานะช่วยคุมพฤติกรรม
        self._active = False
        self._opened_from_typing = False  # ถ้าเปิดจากการพิมพ์ -> อย่าแย่ง focus
        self._registered_click = False

        self.columnconfigure(0, weight=1)

        # Entry
        self.entry = ttk.Entry(self, textvariable=self.var)
        self.entry.grid(row=0, column=0, sticky="nsew", padx=(0, 3))
        if self.entry_font:
            self.entry.config(font=self.entry_font)

        # เปิด dropdown อัตโนมัติเมื่อพิมพ์ (KeyRelease ใช้เพื่อตัดปัญหา focus หลุด)
        self.entry.bind("<KeyRelease>", self._on_key_release)

        # Bind ลูกศรที่ entry เพื่อให้กดแล้วย้ายไป listbox
        self.entry.bind("<Down>", self._entry_down)
        self.entry.bind("<Up>", self._entry_up)
        self.entry.bind("<Return>", self._entry_enter)
        self.entry.bind("<Escape>", lambda e: self.close())

        # Dropdown button
        self.btn = ttk.Button(self, text="▼", width=2, command=self.toggle)
        self.btn.grid(row=0, column=1, sticky="ns")

        # Popup
        self.popup = None
        self.listbox = None

        # Close popup when widget destroyed
        self.bind("<Destroy>", self._on_self_destroy)
        self.entry.bind("<Destroy>", self._on_self_destroy)

        # Global click-outside detection (bind on root once)
        root = self.entry.winfo_toplevel()
        # register bind once per root if not already (avoid duplicate handlers)
        try:
            if not getattr(root, "_autocomplete_bound", False):
                root.bind_all("<Button-1>", self._click_outside, add="+")
                root._autocomplete_bound = True
        except Exception:
            # fallback - still bind directly
            root.bind_all("<Button-1>", self._click_outside, add="+")

    # ---------------------------
    # Class helpers
    # ---------------------------
    @classmethod
    def close_all(cls, except_instance=None):
        for inst in list(cls._OPEN_INSTANCES):
            try:
                if inst is not except_instance:
                    inst.close()
            except Exception:
                pass

    @classmethod
    def destroy_all_popups(cls):
        for inst in list(cls._OPEN_INSTANCES):
            inst.close()
        cls._OPEN_INSTANCES.clear()

    def _register_open(self):
        AutocompleteCombobox._OPEN_INSTANCES.add(self)

    def _unregister_open(self):
        AutocompleteCombobox._OPEN_INSTANCES.discard(self)

    # ---------------------------
    # Key / typing handler
    # ---------------------------
    def _on_key_release(self, event):
        # ปุ่มที่ไม่ควรทริก autocomplete ระหว่างพิมพ์
        ignore_keys = {"Up", "Down", "Left", "Right", "Return", "Escape", "Tab"}

        if event.keysym in ignore_keys:
            # ถ้ากดลูกศร (Down/Up) ให้ไป focus listbox (ถ้ามี) ผ่าน handler entry bind
            return

        # ถ้า widget ไม่แสดง -> ปิด popup
        if not self.winfo_ismapped():
            self.close()
            return

        # update filtered list ตามข้อความปัจจุบัน
        text = (self.var.get() or "").lower()
        if not text:
            self.filtered = self.values
        else:
            self.filtered = [v for v in self.values if text in v.lower()]

        if self.filtered:
            # เปิด popup โดยบอกว่า "เปิดจากการพิมพ์" เพื่อไม่แย่ง focus
            self._opened_from_typing = True
            self.open()
            # เคลียร์ flag เล็กน้อยหลัง delay เล็กๆ (ให้การเปิดเสร็จ)
            self.after(80, lambda: setattr(self, "_opened_from_typing", False))
        else:
            self.close()

    # ---------------------------
    # Popup handling
    # ---------------------------
    def toggle(self):
        if self.popup and self.popup.winfo_exists():
            self.close()
        else:
            self.filtered = self.values
            # toggle via button → ให้ focus ไปที่ listbox (ปกติ)
            self._opened_from_typing = False
            self.open()

    def open(self):
        # ตรวจสอบว่า widget ยัง mapped (visible)
        if not self.winfo_ismapped():
            return

        # ปิด popup อื่นก่อน เพื่อให้มีแค่หนึ่งเปิด
        AutocompleteCombobox.close_all(except_instance=self)

        if not self.filtered:
            self.close()
            return

        # สร้าง popup ถ้ายังไม่มี
        if not self.popup or not self.popup.winfo_exists():
            parent_top = self.entry.winfo_toplevel()
            self.popup = tk.Toplevel(parent_top)
            # ทำให้เป็น owned by top-level ของแอพ (ลดปัญหา popup ติดค้างหน้าต่างอื่น)
            try:
                self.popup.transient(parent_top)
            except Exception:
                pass
            self.popup.overrideredirect(True)

            self.listbox = tk.Listbox(self.popup, activestyle="none")
            if self.listbox_font:
                self.listbox.config(font=self.listbox_font)
            self.listbox.pack(fill="both", expand=True)

            # Listbox events (เมื่อ listbox มี focus)
            self.listbox.bind("<<ListboxSelect>>", self._select)
            self.listbox.bind("<Return>", self._lb_enter)
            self.listbox.bind("<Down>", self._lb_down)
            self.listbox.bind("<Up>", self._lb_up)

            # ถ้าคลิกใน listbox ด้วยเมาส์ -> อย่าให้ global click ปิดทันที
            self.listbox.bind("<Button-1>", lambda e: None)

        # เติมรายการ
        self.listbox.delete(0, tk.END)
        for v in self.filtered:
            self.listbox.insert(tk.END, v)

        # ตำแหน่งและขนาด
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        width = max(self.entry.winfo_width() + self.btn.winfo_width(), 120)
        visible = min(self.listbox_maxheight, len(self.filtered))
        self.listbox.config(height=visible)
        h = self.listbox.winfo_reqheight()
        try:
            self.popup.geometry(f"{width}x{h}+{x}+{y}")
        except Exception:
            self.popup.geometry(f"+{x}+{y}")
        self.popup.deiconify()
        self.popup.lift()

        # register
        self._register_open()

        # focus listbox only when NOT opened from typing (i.e. opened by button or arrow)
        # we still call _focus_listbox_safely so the code centralizes selection logic
        self.after(10, self._focus_listbox_safely)

    def close(self):
        self._unregister_open()
        if self.listbox:
            try:
                self.listbox.destroy()
            except Exception:
                pass
            self.listbox = None
        if self.popup:
            try:
                if self.popup.winfo_exists():
                    self.popup.destroy()
            except Exception:
                pass
            self.popup = None

    # ---------------------------
    # Focus logic (central)
    # ---------------------------
    def _focus_listbox_safely(self):
        """
        Focus listbox only when appropriate:
        - ถ้า popup เปิดมาจากการพิมพ์ -> อย่าแย่ง focus (ผู้ใช้กำลังพิมพ์)
        - ถ้าต้องการให้ listbox ได้ focus (เช่น กดปุ่ม dropdown หรือกดลูกศรลง) → ให้ focus
        """
        if not (self.listbox and self.popup and self.popup.winfo_exists()):
            return

        # ถ้ามาเพราะ typing → ไม่แย่ง focus
        if getattr(self, "_opened_from_typing", False):
            # แต่ยังต้อง ensure selection แรกถูกเลือก (highlight) เพื่อให้เห็นตัวเลือก
            try:
                if self.listbox.size() > 0:
                    self.listbox.selection_clear(0, tk.END)
                    self.listbox.selection_set(0)
                    self.listbox.activate(0)
            except Exception:
                pass
            return

        # ปกติให้ focus ไปที่ listbox เพื่อให้ลูกศรทำงานทันที
        try:
            self.listbox.focus_force()
            if self.listbox.size() > 0:
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(0)
                self.listbox.activate(0)
        except Exception:
            pass

    # ---------------------------
    # Listbox selection / navigation
    # ---------------------------
    def _select(self, event=None):
        if self.listbox:
            cur = self.listbox.curselection()
            if cur:
                self.var.set(self.listbox.get(cur[0]))
        self.close()
        # คืน focus ให้ entry เพื่อให้พิมพ์ต่อได้
        self.after(1, lambda: self.entry.focus_force())
        self.after(2, lambda: self.entry.icursor(tk.END))

    # เมื่อกด ↓ ขณะ entry มี focus → เปิด popup (ถ้าปิดอยู่) แล้วย้าย focus ไป listbox
    def _entry_down(self, event):
        # ถ้าไม่มีรายการให้แสดงก็เปิดและ return
        self.filtered = self.filtered or self.values
        self._opened_from_typing = False
        self.open()
        # ให้หลังเล็กน้อยแล้ว focus listbox เพื่อให้ลูกศรทำงาน
        self.after(5, self._focus_listbox_safely)
        return "break"

    # เมื่อกด ↑ ขณะ entry มี focus → เปิด popup แล้วให้ไป select รายการสุดท้าย
    def _entry_up(self, event):
        self.filtered = self.filtered or self.values
        self._opened_from_typing = False
        self.open()
        # เลือกตัวสุดท้ายก่อน focus
        self.after(5, lambda: (
            self.listbox.selection_clear(0, tk.END),
            self.listbox.selection_set(max(0, self.listbox.size()-1)) if self.listbox else None,
            self.listbox.activate(max(0, (self.listbox.size()-1))) if self.listbox else None,
            self._focus_listbox_safely()
        ))
        return "break"

    def _entry_enter(self, event):
        if self.filtered:
            self.var.set(self.filtered[0])
        self.close()
        self.after(1, lambda: self.entry.focus_force())
        self.after(2, lambda: self.entry.icursor(tk.END))
        return "break"

    def _lb_down(self, event):
        if not self.listbox:
            return "break"
        size = self.listbox.size()
        cur = self.listbox.curselection()
        idx = cur[0] + 1 if cur else 0
        if idx >= size:
            idx = size - 1
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(idx)
        self.listbox.activate(idx)
        self.listbox.see(idx)
        return "break"

    def _lb_up(self, event):
        if not self.listbox:
            return "break"
        size = self.listbox.size()
        cur = self.listbox.curselection()
        idx = cur[0] - 1 if cur else 0
        if idx < 0:
            idx = 0
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(idx)
        self.listbox.activate(idx)
        self.listbox.see(idx)
        return "break"

    def _lb_enter(self, event):
        self._select()
        return "break"

    # ---------------------------
    # Click outside to close
    # ---------------------------
    def _click_outside(self, event):
        # ถ้าไม่มี popup อะไรให้ทำ
        if not getattr(self, "popup", None):
            return

        # ถ้าคลิกบน entry / button / listbox ของ instance นี้ -> ไม่ต้องปิด
        widget = event.widget
        if widget in (self.entry, self.btn, self.listbox):
            return

        # ถ้าคลิกในพื้นที่ popup -> ไม่ปิด
        try:
            if self.popup and self.popup.winfo_exists():
                x1 = self.popup.winfo_rootx()
                y1 = self.popup.winfo_rooty()
                x2 = x1 + self.popup.winfo_width()
                y2 = y1 + self.popup.winfo_height()
                if x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2:
                    return
        except Exception:
            pass

        # ถ้าคลิกในพื้นที่ top-level เจ้าของ (เช่น popup แก้ไข) -> อย่าปิด
        try:
            parent_top = self.entry.winfo_toplevel()
            px1 = parent_top.winfo_rootx()
            py1 = parent_top.winfo_rooty()
            px2 = px1 + parent_top.winfo_width()
            py2 = py1 + parent_top.winfo_height()
            if px1 <= event.x_root <= px2 and py1 <= event.y_root <= py2:
                return
        except Exception:
            pass

        # มิฉะนั้นปิด
        self.close()

    # ---------------------------
    # Destroy / misc
    # ---------------------------
    def _on_self_destroy(self, event=None):
        # เมื่อ widget ถูกทำลาย ให้ปิด popup แน่นอน
        self.close()

    # ---------------------------
    # External API
    # ---------------------------
    def set_values(self, values):
        self.values = list(values or [])
        self.filtered = self.values.copy()

    def set_fonts(self, entry_font=None, listbox_font=None):
        if entry_font:
            self.entry_font = entry_font
            self.entry.config(font=entry_font)
        if listbox_font:
            self.listbox_font = listbox_font
            if self.listbox:
                self.listbox.config(font=listbox_font)
