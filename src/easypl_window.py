import tkinter
from tkinter import ttk
import os
import sys
sys.coinit_flags = 2
from tkinter import filedialog
import threading
from main import pl

class Application(tkinter.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.master.geometry("600x500")
        self.master.title(u"簡単PL君")

        self.create_widgets()
    
    def create_widgets(self):
        self.label_minWL = tkinter.Label(text=u'励起光最短中心波長')
        self.label_minWL.place(x=10, y=10)
        self.entry_minWL = tkinter.Entry(width=7)
        self.entry_minWL.insert(tkinter.END, '500')
        self.entry_minWL.place(x=170, y=10)
        self.unit_minWL = tkinter.Label(text=u'nm')
        self.unit_minWL.place(x=230, y=10)

        self.label_maxWL = tkinter.Label(text=u'励起光最長中心波長')
        self.label_maxWL.place(x=10, y=50)
        self.entry_maxWL = tkinter.Entry(width=7)
        self.entry_maxWL.insert(tkinter.END, '800')
        self.entry_maxWL.place(x=170, y=50)
        self.unit_maxWL = tkinter.Label(text=u'nm')
        self.unit_maxWL.place(x=230, y=50)
        
        self.label_stepWL = tkinter.Label(text=u'励起光中心波長間隔')
        self.label_stepWL.place(x=10, y=90)
        self.entry_stepWL = tkinter.Entry(width=7)
        self.entry_stepWL.insert(tkinter.END, '10')
        self.entry_stepWL.place(x=170, y=90)
        self.unit_stepWL = tkinter.Label(text=u'nm')
        self.unit_stepWL.place(x=230, y=90)

        self.label_widthWL = tkinter.Label(text=u'励起光波長幅')
        self.label_widthWL.place(x=10, y=130)
        self.entry_widthWL = tkinter.Entry(width=7)
        self.entry_widthWL.insert(tkinter.END, '10')
        self.entry_widthWL.place(x=170, y=130)
        self.unit_widthWL = tkinter.Label(text=u'nm')
        self.unit_widthWL.place(x=230, y=130)

        self.label_exposure = tkinter.Label(text=u'露光時間')
        self.label_exposure.place(x=10, y=170)
        self.entry_exposure = tkinter.Entry(width=7, text='120')
        self.entry_exposure.insert(tkinter.END, '120')
        self.entry_exposure.place(x=170, y=170)
        self.unit_exposure = tkinter.Label(text=u'秒')
        self.unit_exposure.place(x=230, y=170)

        self.label_power = tkinter.Label(text=u'サンプル照射パワー')
        self.label_power.place(x=10, y=210)
        self.entry_power = tkinter.Entry(width=7)
        self.entry_power.insert(tkinter.END, '2')
        self.entry_power.place(x=170, y=210)
        self.unit_power = tkinter.Label(text=u'mW')
        self.unit_power.place(x=230, y=210)

        self.label_savefolderpath = tkinter.Label(text=u'保存先')
        self.label_savefolderpath.place(x=10, y=270)
        self.entry_savefolderpath = tkinter.Entry(width=40)
        self.entry_savefolderpath.insert(tkinter.END, 'C:\\Users\\optics\\individual')
        self.entry_savefolderpath.place(x=120, y=270)
        self.button_browse = tkinter.Button(text=u'参照', width=10)
        self.button_browse.bind("<1>", self.call_get_path)
        self.button_browse.place(x=410, y=270)

        self.button_start = tkinter.Button(text=u'スタート', width=30)
        self.button_start.bind("<1>", self.call_pack_pl)
        self.button_start.place(x=20, y=450)

        self.pb = ttk.Progressbar(root, orient="horizontal", length=200, mode="indeterminate")
        self.pb.place(x=30, y=370)

        self.msg = tkinter.StringVar(value="Please close other applications and set values")
        self.label_msg = tkinter.Label(textvariable=self.msg)
        self.label_msg.place(x=20, y=330)

    def call_get_path(self, event):
        iDir = os.path.abspath(os.path.dirname(__file__))
        file = filedialog.askdirectory(initialdir="C:\\Users\\optics\\individual")
        self.entry_savefolderpath.delete(0,tkinter.END)
        self.entry_savefolderpath.insert(tkinter.END, file)
    
    def call_pack_pl(self, event):
        thread1 = threading.Thread(target=self.pack_pl, args=(float(self.entry_power.get())*0.001, int(self.entry_minWL.get()), int(self.entry_maxWL.get()), int(self.entry_stepWL.get()), int(self.entry_widthWL.get()), int(self.entry_exposure.get()), self.entry_savefolderpath.get()))
        thread1.start()
    
    def pack_pl(self, power:float, minWL:int, maxWL:int, stepWL:int, widthWL:int, exposure:int, savefolderpath:str)->None:
        self.button_start["state"] = tkinter.DISABLED
        self.msg.set("Measuring...")
        self.pb.start(10)
        pl(power, minWL, maxWL, stepWL, widthWL, exposure, savefolderpath)
        self.pb.stop()
        self.msg.set("Finished!")
        self.button_start["state"] = tkinter.NORMAL

if __name__ == "__main__":
    root = tkinter.Tk()
    app = Application(master=root)
    app.mainloop()