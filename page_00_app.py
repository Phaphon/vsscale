import tkinter as tk
from page_01_Home import HomePage
from page_02_History import HistoryPage
from page_03_Add import AddPage
from page_04_Setting import SettingPage
from page_99_Utils import center_window, create_password_popup, load_config, get_password


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # ---------- Window Settings ----------
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        load_config()
        self.title("VSScale UI")
        self.configure(bg="#f4faff")

        # ---------- Container ----------
        self.container = tk.Frame(self, bg="#f4faff")
        self.container.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Store frames (only one active at a time)
        self.frames = {}
        self.current_page = None

        # ---------- Create only Home page first (Lazy Load) ----------
        self.show_frame("Home")

        # ---------- Window behavior ----------
        self.withdraw()
        self.update_idletasks()
        center_window(self, 800, 500)
        self.deiconify()

        self.lift()
        self.focus_force()
        self.after(200, lambda: self.attributes("-topmost", False))
        self.attributes("-topmost", True)
        self.after(500, self.force_fullscreen)

    def force_fullscreen(self):
        try:
            self.attributes("-fullscreen", True)
            self.lift()
            self.focus_force()
            self.attributes("-topmost", True)
            self.after(300, lambda: self.attributes("-topmost", False))
        except:
            pass

    # ============================================================
    #                  Lazy Load Frame Creator
    # ============================================================
    def create_frame(self, name):

            if name == "Home":
                return HomePage(
                    self.container,
                    go_to_history=lambda: self.show_frame("History"),
                    go_to_add=lambda: self.show_frame("Add"),
                    go_to_setting=lambda: self.open_settings()
                )

            elif name == "History":
                return HistoryPage(
                    self.container,
                    go_back=lambda: self.show_frame("Home")
                )

            elif name == "Add":
                return AddPage(
                    self.container,
                    go_back=lambda: self.show_frame("Home")
                )

            elif name == "Setting":
                return SettingPage(
                    self.container,
                    go_back=lambda: self.show_frame("Home")
                )

            else:
                raise ValueError(f"Unknown page: {name}")


    # ============================================================
    #                  Frame Switching (Lazy Load)
    # ============================================================
    def show_frame(self, name):

        # 1) ถ้ามีหน้าเดิม → เรียก on_hide() → ลบทิ้ง
        if self.current_page is not None:
            old_frame = self.frames[self.current_page]

            if hasattr(old_frame, "on_hide"):
                old_frame.on_hide()

            old_frame.destroy()
            del self.frames[self.current_page]

        # 2) สร้างหน้าใหม่ทุกครั้ง
        new_frame = self.create_frame(name)
        self.frames[name] = new_frame

        new_frame.grid(row=0, column=0, sticky="nsew")
        new_frame.tkraise()

        # 3) เรียก on_show() ของหน้าใหม่
        if hasattr(new_frame, "on_show"):
            new_frame.on_show()

        self.current_page = name

    # ============================================================
    #               Password Protected Setting Page
    # ============================================================
    def open_settings(self):
        def do_open():
            self.show_frame("Setting")

        create_password_popup(
            self,
            correct_password=get_password("settings"),
            message="กรุณาใส่รหัสผ่านเพื่อเข้า Settings",
            confirm_callback=do_open
        )


if __name__ == "__main__":
    app = App()
    app.mainloop()