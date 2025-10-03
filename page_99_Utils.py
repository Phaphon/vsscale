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

def save_config():
    """บันทึกค่า config ปัจจุบันลงไฟล์"""
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
                "database": db_config.get("database", "")
            }
            print("Connecting to DB with:", conn_cfg)  # debug
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
    return db_config.get("station", "1")

_weight = 0
def read_weight():
    return _weight

def set_zero():
    global _weight
    _weight = 0

# โหลด config ตอนเริ่มต้นโมดูล
load_config()