import tkinter
from tkinter import ttk
import sys
sys.coinit_flags = 2
import threading
from main import pid_control_power
from driver.fianium import superchrome
from driver.ophir import juno
from driver.thorlab import ThorlabStage, FlipMount
from driver.sigmakoki import shutter
import config

class Application(tkinter.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.master.geometry("400x400")
        self.master.title(u"励起光照射君")
        self.create_widgets()
    
    def create_widgets(self):
        self.label_wavelength = tkinter.Label(text=u'励起光中心波長', state='disabled')
        self.label_wavelength.place(x=30, y=60)
        self.entry_wavelength = tkinter.Entry(width=7)
        self.entry_wavelength.insert(tkinter.END, '500')
        self.entry_wavelength["state"] = "disabled"
        self.entry_wavelength.place(x=140, y=60)
        self.unit_wavelength = tkinter.Label(text=u'nm', state='disabled')
        self.unit_wavelength.place(x=200, y=60)

        self.label_width = tkinter.Label(text=u'励起光波長幅', state='disabled')
        self.label_width.place(x=30, y=110)
        self.entry_width = tkinter.Entry(width=7)
        self.entry_width.insert(tkinter.END, '25')
        self.entry_width["state"] = "disabled"
        self.entry_width.place(x=140, y=110)
        self.unit_width = tkinter.Label(text=u'nm', state='disabled')
        self.unit_width.place(x=200, y=110)
        
        self.label_power = tkinter.Label(text=u'目標パワー',state='disabled')
        self.label_power.place(x=30, y=160)
        self.entry_power = tkinter.Entry(width=7)
        self.entry_power.insert(tkinter.END, '2')
        self.entry_power["state"] = "disabled"
        self.entry_power.place(x=140, y=160)
        self.unit_power = tkinter.Label(text=u'mW', state='disabled')
        self.unit_power.place(x=200, y=160)

        self.set_button = tkinter.Button(text=u'セット', width=20)
        self.set_button.bind("<1>", self.call_choonepower)
        self.set_button.place(x=20, y=220)
        self.set_button["state"] = tkinter.DISABLED

        self.init_button = tkinter.Button(text=u'初期化', width=20)
        self.init_button.bind("<1>", self.call_init)
        self.init_button.place(x=20, y=10)

        self.pb = ttk.Progressbar(root, orient="horizontal", length=200, mode="indeterminate")
        self.pb.place(x=30, y=310)

        self.msg = tkinter.StringVar(value="初期化してください")
        self.label_msg = tkinter.Label(textvariable=self.msg)
        self.label_msg.place(x=20, y=280)

    def call_init(self, event):
        thread2 = threading.Thread(target=self.initialize)
        thread2.start()

    def call_choonepower(self, event):
        try:
            power = float(self.entry_power.get()) * 0.001
            wavelength = int(self.entry_wavelength.get())
            width = int(self.entry_width.get())
        except:
            self.msg.set("Please input numbers")
            return
        if power < 0.0 or power > 4.0 or wavelength < 400 or wavelength > 850 or width < 1 or width > 100:
            self.msg.set("Please input correct values")
            return
        thread1 = threading.Thread(target=self.choonepower, args=(power, wavelength, width))
        thread1.start()

    def initialize(self):
        try:
            self.init_button["state"] = tkinter.DISABLED
            self.msg.set("初期化中...")
            self.pb.start(10)
            self.flipshut = FlipMount()
            self.flipshut.close()
            self.shut = shutter(config.SHUTTERCOMPORT)
            self.shut.close(2)

            self.laserchoone = superchrome()

            self.NDfilter = ThorlabStage(home=True)
            self.NDfilter.move_to(0, block=True)
            print(f"stage is at {self.NDfilter.get_position()}")

            self.powermeter = juno()
            self.powermeter.open()
            self.powermeter.set_range(3)
        except:
            self.msg.set("初期化に失敗しました")
            self.pb.stop()
            return

        self.set_button["state"] = tkinter.NORMAL
        self.init_button["state"] = tkinter.DISABLED
        self.entry_wavelength["state"] = "normal"
        self.label_wavelength["state"] = "normal"
        self.unit_wavelength["state"] = "normal"
        self.entry_width["state"] = "normal"
        self.label_width["state"] = "normal"
        self.unit_width["state"] = "normal"
        self.entry_power["state"] = "normal"
        self.label_power["state"] = "normal"
        self.unit_power["state"] = "normal"
        self.pb.stop()
        self.msg.set("初期化完了．値を設定してセットを押してください")

    def choonepower(self, targetpower, centerwavelength, wavelenghwidth):
        self.set_button["state"] = tkinter.DISABLED
        self.msg.set("波長の切替とパワーの調整中...")
        self.pb.start(10)
        try:
            self.flipshut.open()
            self.laserchoone.change_lwbw(wavelength=centerwavelength, bandwidth=wavelenghwidth)
            pid_control_power(targetpower=targetpower, wavelength=centerwavelength, powermeter=self.powermeter, NDfilter=self.NDfilter, eps=targetpower*config.EPSRATIO)
            self.shut.open(2)
        except:
            self.msg.set("波長の切替とパワーの調整に失敗しました")
            self.pb.stop()
            self.set_button["state"] = tkinter.NORMAL
            return
        self.pb.stop()
        self.set_button["state"] = tkinter.NORMAL
        self.msg.set(f"中心波長: {centerwavelength} nm, 波長幅: {wavelenghwidth} nm, 目標パワー: {targetpower} mWを照射中")

if __name__ == "__main__":
    root = tkinter.Tk()
    app = Application(master=root)
    app.mainloop()