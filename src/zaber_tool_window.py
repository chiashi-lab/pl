import tkinter
from tkinter import ttk, messagebox
import time
import sys
import config
sys.coinit_flags = 2
import threading
from driver.zaber import zaber_linear_actuator
import logger

class Application(tkinter.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.master = master
        self.master.geometry("400x300")
        self.master.title(u"zaber_tool")
        self.create_widgets()

        self.zaber_linear_actuator = zaber_linear_actuator()
        if self.zaber_linear_actuator._check_home():
            self.msg.set("zaber is homed")
        else:
            self.msg.set("zaber is not homed")
            self.scale_position.configure(state="disabled")
            self.button_set_position.configure(state="disabled")
        self.positon_var.set(self.zaber_linear_actuator.get_position())

    def create_widgets(self):
        self.msg = tkinter.StringVar(value="")
        self.label_msg = ttk.Label(textvariable=self.msg)
        self.label_msg.place(x=10, y=150)

        self.button_home = ttk.Button(text="Home", width=20)
        self.button_home.bind("<Button-1>", self.call_home)
        self.button_home.place(x=10, y=10)

        self.positon_var = tkinter.DoubleVar()

        self.scale_position_label = ttk.Label(textvariable=self.positon_var)
        self.scale_position_label.place(x=250, y=50)

        self.scale_position = ttk.Scale(from_=0.0, to=25.4, length=200, variable=self.positon_var)
        self.scale_position.place(x=10, y=50)

        self.button_set_position = ttk.Button(text="Set Position", width=20)
        self.button_set_position.bind("<Button-1>", self.call_set_position)
        self.button_set_position.place(x=10, y=100)

    def call_home(self, event) -> None:
        if self.button_home["state"] == "disabled":
            return
        self.button_home.configure(state="disabled")
        res = messagebox.askyesno("Home", "本当にhomeしますか？")
        if res:
            thread_home = threading.Thread(target=self.home)
            thread_home.start()
        else:
            self.button_home.configure(state="normal")
            return
    
    def call_set_position(self, event) -> None:
        if self.button_set_position["state"] == "disabled" or self.scale_position["state"] == "disabled":
            return
        self.scale_position.configure(state="disabled")
        self.button_set_position.configure(state="disabled")
        position = self.positon_var.get()
        self.msg.set(f"zaber is moving to {position:.2f}")
        if position < 14.0:
            res = messagebox.askyesno("zaber", f"ソケットが外れる可能性があります．\n本当に{position:.2f}に移動しますか？")
            if not res:
                self.scale_position.configure(state="normal")
                self.button_set_position.configure(state="normal")
                return
            
        if position > config.ZABERMAXLIMIT:
            res = messagebox.askyesno("zaber", f"複屈折フィルター破壊の恐れがあります．\n本当に{position:.2f}に移動しますか？")
            if not res:
                self.scale_position.configure(state="normal")
                self.button_set_position.configure(state="normal")
                return
        thread_set_position = threading.Thread(target=self.set_position)
        thread_set_position.start()
    
    def home(self) -> None:
        self.zaber_linear_actuator._home()
        self.positon_var.set(self.zaber_linear_actuator.get_position())
        self.scale_position.configure(state="normal")
        self.button_set_position.configure(state="normal")
        self.button_home.configure(state="normal")
        self.msg.set("zaber is homed")
    
    def set_position(self) -> None:
        position = self.positon_var.get()
        self.zaber_linear_actuator._move_to(position)
        moved_position = self.zaber_linear_actuator.get_position()
        self.msg.set(f"zaber is moved to {moved_position:.2f}")
        self.positon_var.set(moved_position)
        self.scale_position.configure(state="normal")
        self.button_set_position.configure(state="normal")




if __name__ == "__main__":
    root = tkinter.Tk()
    app = Application(master=root)
    app.mainloop()