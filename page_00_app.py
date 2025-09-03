import tkinter as tk
from page_01_Home import HomePage
from page_02_test_History import HistoryPage
from page_03_Add import AddPage
from page_04_Setting import SettingPage
from page_99_Utils import center_window, create_password_popup  # ฟังก์ชันสำหรับจัดกลางหน้าจอ

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VSScale UI")    
        self.resizable(True, True)

        # สร้าง frames สำหรับแต่ละหน้า
        self.frames = {}
        self.frames["Home"] = HomePage(
            self,
            go_to_history=lambda: self.show_frame("History"),
            go_to_add=lambda: self.show_frame("Add"),
            go_to_setting=lambda: self.open_settings()
        )
        self.frames["History"] = HistoryPage(self, go_back=lambda: self.show_frame("Home"))
        self.frames["Add"] = AddPage(self, go_back=lambda: self.show_frame("Home"))
        self.frames["Setting"] = SettingPage(self, go_back=lambda: self.show_frame("Home"))

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ซ่อนหน้าต่างก่อนจัดกลาง
        self.withdraw()
        self.update_idletasks()  # ให้ geometry คำนวณเสร็จ
        center_window(self, 800, 500)  # จัดกลางหน้าจอ
        self.deiconify()  # แสดงหน้าต่าง

        # แสดงหน้าเริ่มต้น
        self.show_frame("Home")

    def open_settings(self):
        def do_open_settings():
            # โค้ดเปิดหน้า setting จริง ๆ
            self.show_frame("Setting")
            print("✅ เปิดหน้า Setting แล้ว")
        
        # แสดง popup ใส่รหัสผ่านสำหรับ Settings (ตัวอย่าง: "adminpass")
        create_password_popup(self, correct_password="adminpass", message="กรุณาใส่รหัสผ่านเพื่อเข้า Settings", confirm_callback=do_open_settings)

    def show_frame(self, name):
        self.frames[name].tkraise()


if __name__ == "__main__":
    app = App()
    app.mainloop()


"""
ถ้าฉันจะขอสรุปภาพรวมโปรแกรมของฉันตอนนี้ก่อนนะว่ามันประกอบไปด้วย
page_00_app.py เป็นไฟล์class App ที่ใช้รันตัวโปรแกรม
page_01_Home.py เป็นไฟล์ UI สำหรับหน้า main ที่จะเป็นทางผ่านไปสู่หน้า ประวัติ เพิ่มรายการ และการตั้งค่า
"""