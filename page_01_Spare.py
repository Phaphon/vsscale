import tkinter as tk

class HomePage(tk.Frame):
    def __init__(self, master, go_to_history, go_to_add, go_to_setting):
        super().__init__(master)

        # layout grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        tk.Button(self, text="ประวัติ", font=("Arial", 14),
                  command=go_to_history).grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        tk.Button(self, text="เพิ่มรายการ", font=("Arial", 14),
                  command=go_to_add).grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.grid_rowconfigure(1, weight=0)
        tk.Button(self, text="⚙ ตั้งค่า", font=("Arial", 10),
                  command=go_to_setting).grid(row=1, column=1, sticky="se", padx=10, pady=10)