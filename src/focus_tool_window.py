import tkinter
from tkinter import ttk, messagebox
import time
import sys
import config
sys.coinit_flags = 2
import threading
from driver.focus_adjuster_driver import Focus_adjuster
import logger

class Application(tkinter.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.master = master
        self.master.geometry("500x500")
        self.master.title(u"Focus Tool")
        self.create_widgets()
        self.focus_adjuster = Focus_adjuster(config.AUTOFOCUSCOMPORT)

    def create_widgets(self):
        self.pos = tkinter.IntVar()
        self.pos.set(0)
        self.label_pos = ttk.Label(textvariable=self.pos)
        self.label_pos.place(x=100, y=130)

        self.button_5micro = ttk.Button(text="5um", command=self.call_move_5um)
        self.button_5micro.place(x=100, y=10)

        self.button_1micro = ttk.Button(text="1um", command=self.call_move_1um)
        self.button_1micro.place(x=100, y=50)

        self.button_quarter = ttk.Button(text="1/4um", command=self.call_move_quarter)
        self.button_quarter.place(x=100, y=90)

        self.button_m_quarter = ttk.Button(text="-1/4um", command=self.call_move_m_quarter)
        self.button_m_quarter.place(x=100, y=160)

        self.button_m_1micro = ttk.Button(text="-1um", command=self.call_move_m_1micro)
        self.button_m_1micro.place(x=100, y=200)

        self.button_m_5micro = ttk.Button(text="-5um", command=self.call_move_m_5um)
        self.button_m_5micro.place(x=100, y=240)


        self.log_scrolltext = tkinter.scrolledtext.ScrolledText(width=60, height=10)
        self.log_scrolltext.place(x=10, y=360)

        self.logger = logger.Logger(log_file_path=None, log_scroll=self.log_scrolltext)

    def call_move_5um(self) -> None:
        if self.button_5micro["state"] == "disabled":
            return
        thread = threading.Thread(target=self.move, args=(4 * 5,))
        thread.start()

    def call_move_1um(self) -> None:
        if self.button_1micro["state"] == "disabled":
            return
        thread = threading.Thread(target=self.move, args=(4 * 1,))
        thread.start()

    def call_move_quarter(self) -> None:
        
        if self.button_quarter["state"] == "disabled":
            return
        thread = threading.Thread(target=self.move, args=(1,))
        thread.start()

    def call_move_m_quarter(self) -> None:
        if self.button_m_quarter["state"] == "disabled":
            return
        thread = threading.Thread(target=self.move, args=(-1,))
        thread.start()

    def call_move_m_1micro(self) -> None:
        if self.button_m_1micro["state"] == "disabled":
            return
        thread = threading.Thread(target=self.move, args=(-4 * 1,))
        thread.start()

    def call_move_m_5um(self) -> None:
        if self.button_m_5micro["state"] == "disabled":
            return
        thread = threading.Thread(target=self.move, args=(-4 * 5,))
        thread.start()

    def move(self, move_value: int) -> None:
        self.button_5micro.configure(state="disabled")
        self.button_1micro.configure(state="disabled")
        self.button_quarter.configure(state="disabled")
        self.button_m_quarter.configure(state="disabled")
        self.button_m_1micro.configure(state="disabled")
        self.button_m_5micro.configure(state="disabled")

        self.focus_adjuster.move_by(move_value, block=True)
        self.pos.set(self.focus_adjuster.position)

        self.button_5micro.configure(state="normal")
        self.button_1micro.configure(state="normal")
        self.button_quarter.configure(state="normal")
        self.button_m_quarter.configure(state="normal")
        self.button_m_1micro.configure(state="normal")
        self.button_m_5micro.configure(state="normal")

if __name__ == "__main__":
    root = tkinter.Tk()
    app = Application(master=root)
    app.mainloop()