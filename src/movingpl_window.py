import tkinter
from tkinter import ttk
import sys
sys.coinit_flags = 2
from tkinter import filedialog
import threading
from concurrent.futures import ThreadPoolExecutor
from main import moving_pl
from driver.prior import Proscan
import config

class Application(tkinter.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.master.geometry("600x700")
        self.master.title(u"ちくちくPL君")
        self.create_widgets()

    def create_widgets(self):
        self.label_minwavelength = tkinter.Label(text=u'励起光最短中心波長')
        self.label_minwavelength.place(x=10, y=10)
        self.entry_minwavelength = tkinter.Entry(width=7)
        self.entry_minwavelength.insert(tkinter.END, '500')
        self.entry_minwavelength.place(x=150, y=10)
        self.unit_minwavelength = tkinter.Label(text=u'nm')
        self.unit_minwavelength.place(x=210, y=10)

        self.label_maxwavelength = tkinter.Label(text=u'励起光最長中心波長')
        self.label_maxwavelength.place(x=10, y=50)
        self.entry_maxwavelength = tkinter.Entry(width=7)
        self.entry_maxwavelength.insert(tkinter.END, '800')
        self.entry_maxwavelength.place(x=150, y=50)
        self.unit_maxwavelength = tkinter.Label(text=u'nm')
        self.unit_maxwavelength.place(x=210, y=50)

        self.label_stepwavelength = tkinter.Label(text=u'励起光中心波長間隔')
        self.label_stepwavelength.place(x=10, y=90)
        self.entry_stepwavelength = tkinter.Entry(width=7)
        self.entry_stepwavelength.insert(tkinter.END, '10')
        self.entry_stepwavelength.place(x=150, y=90)
        self.unit_stepwavelength = tkinter.Label(text=u'nm')
        self.unit_stepwavelength.place(x=210, y=90)

        self.label_wavelengthwidth = tkinter.Label(text=u'励起光波長幅')
        self.label_wavelengthwidth.place(x=10, y=130)
        self.entry_wavelengthwidth = tkinter.Entry(width=7)
        self.entry_wavelengthwidth.insert(tkinter.END, '10')
        self.entry_wavelengthwidth.place(x=150, y=130)
        self.unit_wavelengthwidth = tkinter.Label(text=u'nm')
        self.unit_wavelengthwidth.place(x=210, y=130)

        self.label_integrationtime = tkinter.Label(text=u'露光時間')
        self.label_integrationtime.place(x=10, y=170)
        self.entry_integrationtime = tkinter.Entry(width=7, text='120')
        self.entry_integrationtime.insert(tkinter.END, '120')
        self.entry_integrationtime.place(x=150, y=170)
        self.unit_integrationtime = tkinter.Label(text=u'秒')
        self.unit_integrationtime.place(x=210, y=170)

        self.label_targetpower = tkinter.Label(text=u'サンプル照射パワー')
        self.label_targetpower.place(x=10, y=210)
        self.entry_targetpower = tkinter.Entry(width=7)
        self.entry_targetpower.insert(tkinter.END, '2')
        self.entry_targetpower.place(x=150, y=210)
        self.unit_targetpower = tkinter.Label(text=u'mW')
        self.unit_targetpower.place(x=210, y=210)

        self.label_path = tkinter.Label(text=u'保存先')
        self.label_path.place(x=10, y=280)
        self.entry_path = tkinter.Entry(width=40)
        self.entry_path.insert(tkinter.END, 'C:\\Users\\optics\\individuall')
        self.entry_path.place(x=120, y=280)
        self.button_path = tkinter.Button(text=u'参照', width=10)
        self.button_path.bind("<1>", self.get_path)
        self.button_path.place(x=410, y=280)

        self.label_startpos = tkinter.Label(text=u'開始位置')
        self.label_startpos.place(x=10, y=340)
        self.entry_startpos_x = tkinter.Entry(width=10)
        self.entry_startpos_x.insert(tkinter.END, '0')
        self.entry_startpos_x.place(x=130, y=340)
        self.entry_startpos_y = tkinter.Entry(width=10)
        self.entry_startpos_y.insert(tkinter.END, '0')
        self.entry_startpos_y.place(x=270, y=340)
        self.button_startpos = tkinter.Button(text=u'位置取得', width=7)
        self.button_startpos.bind("<1>", self.getpos_start)
        self.button_startpos.place(x=400, y=340)

        self.label_endpos = tkinter.Label(text=u'終了位置')
        self.label_endpos.place(x=10, y=400)
        self.entry_endpos_x = tkinter.Entry(width=10)
        self.entry_endpos_x.insert(tkinter.END, '0')
        self.entry_endpos_x.place(x=130, y=400)
        self.entry_endpos_y = tkinter.Entry(width=10)
        self.entry_endpos_y.insert(tkinter.END, '0')
        self.entry_endpos_y.place(x=270, y=400)
        self.button_endpos = tkinter.Button(text=u'位置取得', width=7)
        self.button_endpos.bind("<1>", self.getpos_end)
        self.button_endpos.place(x=400, y=400)

        self.label_numberofsteps = tkinter.Label(text=u'データ取得地点の個数')
        self.label_numberofsteps.place(x=10, y=470)
        self.entry_numberofsteps = tkinter.Entry(width=8)
        self.entry_numberofsteps.insert(tkinter.END, '1')
        self.entry_numberofsteps.place(x=170, y=470)

        self.button_start = tkinter.Button(text=u'スタート', width=30)
        self.button_start.bind("<1>", self.call_pack_movingpl)
        self.button_start.place(x=20, y=630)

        self.pb = ttk.Progressbar(root, orient="horizontal", length=200, mode="indeterminate")
        self.pb.place(x=30, y=570)

        self.msg = tkinter.StringVar(value="Please close other applications to initialize")
        self.label_msg = tkinter.Label(textvariable=self.msg)
        self.label_msg.place(x=20, y=530)

    def get_path(self, event):
        file = filedialog.askdirectory(initialdir="C:\\Users\\optics\\individual")
        self.entry_path.delete(0, tkinter.END)
        self.entry_path.insert(tkinter.END, file)
    
    def call_pack_movingpl(self, event):
        thread1 = threading.Thread(target=moving_pl, args=(float(self.entry_targetpower.get())*0.001, int(self.entry_minwavelength.get()), int(self.entry_maxwavelength.get()), int(self.entry_stepwavelength.get()), int(self.entry_wavelengthwidth.get()), int(self.entry_integrationtime.get()), self.entry_path.get(), [int(self.entry_startpos_x.get()), int(self.entry_startpos_y.get())], [int(self.entry_endpos_x.get()), int(self.entry_endpos_y.get())], int(self.entry_numberofsteps.get())))
        thread1.start()

    def pack_movingpl(self, targetpower:float, minwavelength:int, maxwavelength:int, stepwavelength:int, wavelengthwidth:int, integrationtime:int, path:str, startpos:tuple, endpos:tuple, numberofsteps:int)->None:
        self.button_start["state"] = tkinter.DISABLED
        self.msg.set("Experiment is running")
        self.pb.start()
        moving_pl(targetpower, minwavelength, maxwavelength, stepwavelength, wavelengthwidth, integrationtime, path, startpos, endpos, numberofsteps)
        self.pb.stop()
        self.msg.set("Experiment is done")
        self.button_start["state"] = tkinter.NORMAL

    def get_pos(self):
        stage = Proscan(config.PRIORCOMPORT)
        return stage.get_pos()
    
    def getpos_start(self, event):
        self.button_startpos["state"] = tkinter.DISABLED
        self.msg.set("Getting position...")
        self.pb.start()
        executer = ThreadPoolExecutor(max_workers=1)
        pos = executer.submit(self.get_pos)
        pos = pos.result()
        self.entry_startpos_x.delete(0, tkinter.END)
        self.entry_startpos_x.insert(tkinter.END, str(pos[0]))
        self.entry_startpos_y.delete(0, tkinter.END)
        self.entry_startpos_y.insert(tkinter.END, str(pos[1]))
        self.button_startpos["state"] = tkinter.NORMAL
        self.msg.set("Position is gotten")
        self.pb.stop()
    
    def getpos_end(self, event):
        self.button_endpos["state"] = tkinter.DISABLED
        self.msg.set("Getting position...")
        self.pb.start()
        executer = ThreadPoolExecutor(max_workers=1)
        pos = executer.submit(self.get_pos)
        pos = pos.result()
        self.entry_endpos_x.delete(0, tkinter.END)
        self.entry_endpos_x.insert(tkinter.END, str(pos[0]))
        self.entry_endpos_y.delete(0, tkinter.END)
        self.entry_endpos_y.insert(tkinter.END, str(pos[1]))
        self.msg.set("Position is gotten")
        self.button_endpos["state"] = tkinter.NORMAL

if __name__ == '__main__':
    root = tkinter.Tk()
    app = Application(master=root)
    app.mainloop()