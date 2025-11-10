import tkinter as tk
import mysql.connector
import json, os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

# ===== Popup utilities =====
def create_centered_popup(master, width, height, title=""):
    popup = tk.Toplevel(master)
    popup.withdraw()
    popup.title(title)
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
    confirm.transient(parent)
    confirm.grab_set()
    confirm.focus_force()

    tk.Label(confirm, text=message, font=("Arial", 12)).pack(pady=10)

    def on_confirm():
        if confirm_callback:
            confirm_callback()
        confirm.destroy()

    btns = tk.Frame(confirm)
    btns.pack(pady=10)
    tk.Button(btns, text="ยกเลิก", width=10, command=confirm.destroy).pack(side="left", padx=6)
    tk.Button(btns, text="ตกลง", width=10, command=on_confirm).pack(side="left", padx=6)

    confirm.update_idletasks()
    w, h = 260, 120
    x = (confirm.winfo_screenwidth() // 2) - (w // 2)
    y = (confirm.winfo_screenheight() // 2) - (h // 2)
    confirm.geometry(f"{w}x{h}+{x}+{y}")
    confirm.deiconify()

    return confirm

def create_password_popup(parent, correct_password, message="กรุณาใส่รหัสผ่าน", confirm_callback=None):
    popup = tk.Toplevel(parent)
    popup.withdraw()
    popup.title("รหัสผ่าน")
    popup.transient(parent)
    popup.grab_set()
    popup.focus_force()

    tk.Label(popup, text=message, font=("Arial", 12)).pack(pady=10)

    pw_var = tk.StringVar()
    entry = tk.Entry(popup, textvariable=pw_var, show="*", width=20)
    entry.pack(pady=5)
    entry.focus_set()

    msg_label = tk.Label(popup, text="", font=("Arial", 10), fg="red")
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

    btns = tk.Frame(popup)
    btns.pack(pady=10)
    tk.Button(btns, text="ยกเลิก", width=10, command=popup.destroy).pack(side="left", padx=6)
    tk.Button(btns, text="ตกลง", width=10, command=on_confirm).pack(side="left", padx=6)

    popup.update_idletasks()
    w, h = 300, 160
    x = (popup.winfo_screenwidth() // 2) - (w // 2)
    y = (popup.winfo_screenheight() // 2) - (h // 2)
    popup.geometry(f"{w}x{h}+{x}+{y}")
    popup.deiconify()

    return popup


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

def save_config(new_config):
    """บันทึกค่า config ปัจจุบันลงไฟล์"""
    db_config.update(new_config)
    print("dabug Saving config in function save_config:", db_config)  # debug
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

#def get_db_connection():
#    """สร้างหรือดึง connection"""
#    global connection
#    if connection is None or not connection.is_connected():
#        conn_cfg = {k: db_config[k] for k in ["host", "user", "password", "database"]}
#        connection = mysql.connector.connect(**conn_cfg)
#    return connection

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

# ===== Station & Weight mock =====
def read_station_id():
    return db_config.get("station", "2")

_weight = 0
# def read_weight():
#     return _weight

# def set_zero():
#     global _weight
#     _weight = 0

# โหลด config ตอนเริ่มต้นโมดูล
load_config()

# ===== Autocomplete Combobox =====
from tkinter import ttk

class AutocompleteCombobox(ttk.Frame):
    """Entry + ปุ่ม dropdown + autocomplete listbox overlay (reusable)"""
    def __init__(self, master=None, values=None, textvariable=None, listbox_maxheight=5, **kwargs):
        super().__init__(master, **kwargs)
        self._values = list(values or [])
        self._filtered_values = self._values.copy()
        self.var = textvariable or tk.StringVar()

        # ✅ ใช้ grid layout แทน pack
        self.columnconfigure(0, weight=1)  # ให้ entry ขยายเต็มที่
        self.columnconfigure(1, weight=0)

        # Entry
        self.entry = ttk.Entry(self, textvariable=self.var)
        self.entry.grid(row=0, column=0, sticky="nsew")

        # Dropdown button
        self.btn = ttk.Button(self, text="▼", width=2, command=self._toggle_listbox)
        self.btn.grid(row=0, column=1, sticky="ns", padx=(2, 0))

        # overlay listbox (Toplevel)
        self._toplevel = None
        self._listbox = None
        self._listbox_maxheight = listbox_maxheight

        # events
        self.var.trace_add("write", self._on_var_change)
        self.entry.bind("<Down>", self._on_down)      # go to listbox
        self.entry.bind("<Return>", self._on_return)  # accept
        self.entry.bind("<Escape>", self._hide_listbox)
        # do NOT force focus in _on_var_change (prevents focus loss while typing)

        # hide when clicking elsewhere
        self.entry.bind("<FocusOut>", lambda e: self.after(120, self._hide_listbox))
        # ✅ ตรวจจับการคลิกนอก combobox หรือ dropdown
        self.bind_all("<Button-1>", self._on_click_outside, add="+")

    # update source dataset (optional)
    def set_values(self, values):
        self._values = list(values or [])
        self._filtered_values = self._values.copy()

    def _toggle_listbox(self):
        # toggle dropdown visibility
        if self._toplevel and tk.Toplevel.winfo_exists(self._toplevel):
            self._hide_listbox()
            return

        # show all values
        self._filtered_values = self._values
        if self._filtered_values:
            self._show_listbox()

            # ✅ บังคับ focus กลับที่ entry เพื่อให้ on_click_outside ทำงานได้
            self.entry.focus_set()


    def _on_var_change(self, *args):
        text = (self.var.get() or "").lower()
        if text == "":
            self._filtered_values = self._values
        else:
            self._filtered_values = [v for v in self._values if text in v.lower()]

        if self._filtered_values:
            self._show_listbox()
        else:
            self._hide_listbox()

    def _show_listbox(self):
        if not self._filtered_values:
            self._hide_listbox()
            return

        # create toplevel once
        if self._toplevel is None or not tk.Toplevel.winfo_exists(self._toplevel):
            parent_top = self.entry.winfo_toplevel()
            self._toplevel = tk.Toplevel(parent_top)
            self._toplevel.wm_overrideredirect(True)
            # don't grab focus here
            self._listbox = tk.Listbox(self._toplevel)
            self._listbox.pack(fill="both", expand=True)
            self._listbox.bind("<<ListboxSelect>>", self._on_listbox_select)
            self._listbox.bind("<Return>", self._on_return)
            self._listbox.bind("<FocusOut>", lambda e: self.after(120, self._hide_listbox))

        # fill data
        self._listbox.delete(0, tk.END)
        for v in self._filtered_values:
            self._listbox.insert(tk.END, v)

        # size & place under entry
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        width = max(self.entry.winfo_width(), 100)
        # compute height limited by number of visible items
        visible = min(self._listbox_maxheight, len(self._filtered_values))
        # estimate item height:
        item_h = self._listbox.winfo_reqheight() // max(1, self._listbox.size()) if self._listbox.size() else 20
        # safer: set height via geometry using listbox's requested height for visible items
        self._listbox.config(height=visible)
        self._toplevel.geometry(f"{width}x{self._listbox.winfo_reqheight()}+{x}+{y}")
        self._toplevel.deiconify()
        # Do NOT call focus_force() here — keeps typing smooth.

    def _hide_listbox(self, event=None):
        if self._toplevel and tk.Toplevel.winfo_exists(self._toplevel):
            try:
                self._toplevel.destroy()
            except:
                pass
        self._toplevel = None
        self._listbox = None

    def _on_listbox_select(self, event):
        if not self._listbox:
            return
        sel = self._listbox.curselection()
        if sel:
            val = self._listbox.get(sel[0])
            self.var.set(val)
            # put cursor to end in entry
            self.entry.icursor(tk.END)
        self._hide_listbox()

    def _on_down(self, event):
        # move focus to listbox when available
        if self._listbox:
            try:
                self._listbox.focus_set()
                self._listbox.selection_clear(0, tk.END)
                self._listbox.selection_set(0)
                self._listbox.activate(0)
            except:
                pass
            return "break"

    def _on_return(self, event):
        # if listbox has selection, use it; else use first filtered value
        if self._listbox:
            sel = self._listbox.curselection()
            if sel:
                val = self._listbox.get(sel[0])
                self.var.set(val)
            elif self._filtered_values:
                self.var.set(self._filtered_values[0])
        elif self._filtered_values:
            self.var.set(self._filtered_values[0])
        self.entry.icursor(tk.END)
        self._hide_listbox()
        return "break"

    def _on_click_outside(self, event):
        """Hide dropdown when clicking outside entry or dropdown"""
        if not self._toplevel:
            return

        # get widget clicked
        widget = event.widget

        # check if click is inside entry, button, or listbox
        if widget in (self.entry, self.btn, self._listbox):
            return

        # check if click is inside toplevel dropdown area
        if self._toplevel and tk.Toplevel.winfo_exists(self._toplevel):
            x1 = self._toplevel.winfo_rootx()
            y1 = self._toplevel.winfo_rooty()
            x2 = x1 + self._toplevel.winfo_width()
            y2 = y1 + self._toplevel.winfo_height()
            if x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2:
                return

        # otherwise, clicked outside → hide
        self._hide_listbox()
