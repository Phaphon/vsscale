import tkinter as tk
from tkinter import ttk

mock_data = [
    {"id": i, "abbr": f"AB{i}", "producer": f"Producer {i}", "product": f"Product {i}", "weight": f"{100+i} kg"}
    for i in range(1, 21)
]

ROWS_PER_PAGE = 5


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VSScale UI")
        self.geometry("800x500")   # เล็กลงนิดนึง
        self.resizable(True, True) # เปิดให้ขยายได้

        self.frames = {}
        for F in (MainPage, HistoryPage, AddPage, SettingsPage):
            frame = F(self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # make window scalable
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.show_frame(MainPage)

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()


class MainPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        # layout grid
        self.grid_rowconfigure(0, weight=1)  # ปุ่มใหญ่ row 0
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ปุ่มใหญ่ซ้าย (ประวัติ)
        tk.Button(self, text="ประวัติ", font=("Arial", 14),
                  command=lambda: master.show_frame(HistoryPage)).grid(
            row=0, column=0, sticky="nsew", padx=10, pady=10
        )

        # ปุ่มใหญ่ขวา (เพิ่มรายการ)
        tk.Button(self, text="เพิ่มรายการ", font=("Arial", 14),
                  command=lambda: master.show_frame(AddPage)).grid(
            row=0, column=1, sticky="nsew", padx=10, pady=10
        )

        # สร้าง row แยกสำหรับปุ่มตั้งค่า (เล็กๆ มุมล่างขวา)
        self.grid_rowconfigure(1, weight=0)
        tk.Button(self, text="⚙ ตั้งค่า", font=("Arial", 10),
                  command=lambda: master.show_frame(SettingsPage)).grid(
            row=1, column=1, sticky="se", padx=10, pady=10
        )

class HistoryPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        # ปุ่มย้อนกลับ
        tk.Button(self, text="← กลับ", command=lambda: master.show_frame(MainPage)).pack(anchor="w", padx=10, pady=10)

        # กรอบตาราง (เพิ่ม padding รอบๆ)
        table_frame = tk.Frame(self, bd=2, relief="groove", padx=10, pady=10)
        table_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # mock data
        headers = ["แก้ไข", "เลขรายการ", "เลขย่อ", "ผู้ผลิต", "สินค้า", "น้ำหนัก", "ปริ้น"]
        data = [
            [1, "A01", "บริษัทX", "สินค้าA", "20kg"],
            [2, "B02", "บริษัทY", "สินค้าB", "15kg"],
            [3, "C03", "บริษัทZ", "สินค้าC", "30kg"],
            [4, "D04", "บริษัทK", "สินค้าD", "50kg"],
            [5, "E05", "บริษัทM", "สินค้าE", "12kg"],
        ]

        # สร้าง header
        for col, text in enumerate(headers):
            tk.Label(table_frame, text=text, font=("Arial", 10, "bold"), borderwidth=1, relief="solid", width=12).grid(
                row=0, column=col, sticky="nsew"
            )

        # สร้างข้อมูล
        for row, row_data in enumerate(data, start=1):
            # ปุ่มแก้ไข
            tk.Button(table_frame, text="✎", command=self.show_popup).grid(row=row, column=0, sticky="nsew")

            # คอลัมน์ข้อมูล
            for col, value in enumerate(row_data, start=1):
                tk.Label(table_frame, text=value, borderwidth=1, relief="solid", width=12).grid(
                    row=row, column=col, sticky="nsew"
                )

            # ปุ่มปริ้น
            tk.Button(table_frame, text="🖨", command=self.show_popup).grid(row=row, column=len(headers)-1, sticky="nsew")

        # ขยาย column เท่าๆ กัน
        for col in range(len(headers)):
            table_frame.grid_columnconfigure(col, weight=1)

        # แถวควบคุมการเปลี่ยนหน้า
        nav_frame = tk.Frame(self)
        nav_frame.pack(pady=10)

        tk.Button(nav_frame, text="←").pack(side="left")
        tk.Label(nav_frame, text="1/1").pack(side="left", padx=5)
        tk.Button(nav_frame, text="→").pack(side="left")

    def show_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Popup")
        popup.geometry("200x100")

        tk.Label(popup, text="Pop-up").pack(pady=10)
        tk.Button(popup, text="ปิด", command=popup.destroy).pack()


class AddPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Button(self, text="⬅ ย้อนกลับ", command=lambda: master.show_frame(MainPage)).pack(anchor="nw", padx=5, pady=5)
        tk.Label(self, text="หน้าเพิ่มรายการ (ยังไม่ทำ)", font=("Arial", 14)).pack(expand=True)


class SettingsPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Button(self, text="⬅ ย้อนกลับ", command=lambda: master.show_frame(MainPage)).pack(anchor="nw", padx=5, pady=5)
        tk.Label(self, text="หน้าตั้งค่า (ยังไม่ทำ)", font=("Arial", 14)).pack(expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()