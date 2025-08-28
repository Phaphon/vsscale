import tkinter as tk

def create_centered_popup(master, width, height, title=""):

    # สร้าง popup แต่ซ่อนไว้ก่อน
    popup = tk.Toplevel(master)
    popup.withdraw()
    popup.title(title)

    # ปิด cross = destroy
    popup.protocol("WM_DELETE_WINDOW", popup.destroy)

    # ฟังก์ชันสำหรับแสดงจริง (หลังจากสร้าง widget เสร็จแล้ว)
    def show():
        popup.update_idletasks()  # ให้ layout คำนวณเสร็จ
        screen_w = popup.winfo_screenwidth()
        screen_h = popup.winfo_screenheight()
        x = (screen_w // 2) - (width // 2)
        y = (screen_h // 2) - (height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")
        popup.deiconify()   # แสดงจริง
        popup.lift()        # เอามาไว้ข้างหน้า
        popup.focus_force()

    # เพิ่ม method show() ให้ popup เอง
    popup.show = show

    return popup

def center_window(win, width, height):
    """ใช้กับ root หรือ Toplevel ก็ได้"""
    win.update_idletasks()
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = (screen_w // 2) - (width // 2)
    y = (screen_h // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

def create_confirm_popup(parent, message="ยืนยัน?", confirm_callback=None):
    """
    สร้าง popup ยืนยันกลางหน้าจอ
    parent           : master ของ popup
    message          : ข้อความแสดง
    confirm_callback : ฟังก์ชันที่จะรันเมื่อกดตกลง
    """
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

    # จัดกลางหน้าจอ
    confirm.update_idletasks()
    w, h = 260, 120
    x = (confirm.winfo_screenwidth() // 2) - (w // 2)
    y = (confirm.winfo_screenheight() // 2) - (h // 2)
    confirm.geometry(f"{w}x{h}+{x}+{y}")
    confirm.deiconify()

    return confirm

def create_password_popup(parent, correct_password, message="กรุณาใส่รหัสผ่าน", confirm_callback=None):
    """
    สร้าง popup ใส่รหัสผ่าน
    parent           : master ของ popup
    correct_password : รหัสผ่านที่ถูกต้อง
    message          : ข้อความแสดง
    confirm_callback : ฟังก์ชันที่จะรันเมื่อรหัสผ่านถูกต้อง
    """
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

    # จัดกลางหน้าจอ
    popup.update_idletasks()
    w, h = 300, 160
    x = (popup.winfo_screenwidth() // 2) - (w // 2)
    y = (popup.winfo_screenheight() // 2) - (h // 2)
    popup.geometry(f"{w}x{h}+{x}+{y}")
    popup.deiconify()

    return popup

