import tkinter
from tkinter import ttk
import os
import sys
sys.coinit_flags = 2
from tkinter import filedialog, scrolledtext
import threading
from main import single_ple
import func
import datetime
import logger

class Application(tkinter.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.master = master
        self.master.geometry("600x700")
        self.master.title(u"PLEスペクトル測定")

        self.create_widgets()
    
    def create_widgets(self):
        self.label_minWL = tkinter.Label(text=u'励起光最短中心波長')
        self.label_minWL.place(x=10, y=10)
        self.entry_minWL = tkinter.Entry(width=7)
        self.entry_minWL.insert(tkinter.END, '785')
        self.entry_minWL.place(x=190, y=10)
        self.unit_minWL = tkinter.Label(text=u'nm')
        self.unit_minWL.place(x=250, y=10)

        self.label_maxWL = tkinter.Label(text=u'励起光最長中心波長')
        self.label_maxWL.place(x=10, y=50)
        self.entry_maxWL = tkinter.Entry(width=7)
        self.entry_maxWL.insert(tkinter.END, '785')
        self.entry_maxWL.place(x=190, y=50)
        self.unit_maxWL = tkinter.Label(text=u'nm')
        self.unit_maxWL.place(x=250, y=50)
        
        self.label_stepWL = tkinter.Label(text=u'励起光中心波長間隔')
        self.label_stepWL.place(x=10, y=90)
        self.entry_stepWL = tkinter.Entry(width=7)
        self.entry_stepWL.insert(tkinter.END, '1')
        self.entry_stepWL.place(x=190, y=90)
        self.unit_stepWL = tkinter.Label(text=u'nm')
        self.unit_stepWL.place(x=250, y=90)

        self.label_widthWL = tkinter.Label(text=u'励起光波長幅')
        self.label_widthWL.place(x=10, y=130)
        self.entry_widthWL = tkinter.Entry(width=7)
        self.entry_widthWL.insert(tkinter.END, '1')
        self.entry_widthWL.place(x=190, y=130)
        self.unit_widthWL = tkinter.Label(text=u'nm')
        self.unit_widthWL.place(x=250, y=130)

        self.label_exposure = tkinter.Label(text=u'露光時間')
        self.label_exposure.place(x=10, y=170)
        self.entry_exposure = tkinter.Entry(width=7, text='120')
        self.entry_exposure.insert(tkinter.END, '120')
        self.entry_exposure.place(x=190, y=170)
        self.unit_exposure = tkinter.Label(text=u'秒')
        self.unit_exposure.place(x=250, y=170)

        self.label_power = tkinter.Label(text=u'サンプル照射パワー')
        self.label_power.place(x=10, y=210)
        self.entry_power = tkinter.Entry(width=7)
        self.entry_power.insert(tkinter.END, '2')
        self.entry_power.place(x=190, y=210)
        self.unit_power = tkinter.Label(text=u'mW')
        self.unit_power.place(x=250, y=210)

        self.label_savefolderpath = tkinter.Label(text=u'保存先')
        self.label_savefolderpath.place(x=10, y=260)
        self.entry_savefolderpath = tkinter.Entry(width=40)
        self.entry_savefolderpath.insert(tkinter.END, 'C:\\Users\\optics\\individual')
        self.entry_savefolderpath.place(x=120, y=260)
        self.button_browse = tkinter.Button(text=u'参照', width=10)
        self.button_browse.bind("<1>", self.call_get_path)
        self.button_browse.place(x=410, y=260)

        self.button_start = tkinter.Button(text=u'スタート', width=30)
        self.button_start.bind("<1>", self.call_pack_single_ple)
        self.button_start.place(x=20, y=650)

        self.pb = ttk.Progressbar(self.master, orient="horizontal", length=200, mode="indeterminate")
        self.pb.place(x=30, y=360)

        self.msg = tkinter.StringVar(value="値を設定してスタートを押してください")
        self.label_msg = tkinter.Label(textvariable=self.msg)
        self.label_msg.place(x=20, y=310)

        self.log_scrolltxt = scrolledtext.ScrolledText(self.master, wrap=tkinter.WORD, width=50, height=10)
        self.log_scrolltxt.place(x=20, y=400)

    def call_get_path(self, event)->None:
        file = filedialog.askdirectory(initialdir="C:\\Users\\optics\\individual")
        self.entry_savefolderpath.delete(0,tkinter.END)
        self.entry_savefolderpath.insert(tkinter.END, file)
    
    def call_pack_single_ple(self, event)->None:
        try:
            power = float(self.entry_power.get()) * 0.001
            minWL = int(self.entry_minWL.get())
            maxWL = int(self.entry_maxWL.get())
            stepWL = int(self.entry_stepWL.get())
            widthWL = int(self.entry_widthWL.get())
            exposure = int(self.entry_exposure.get())
            savefolderpath = self.entry_savefolderpath.get()
        except:
            self.msg.set("数字を入力してください")
            return
        if power < 0.0 or power > 4.0 or minWL < 400 or minWL > 850 or maxWL < 400 or maxWL > 850 or stepWL < 0 or stepWL > 400 or widthWL < 1 or widthWL > 100 or exposure < 0 or exposure > 1000 or minWL > maxWL:
            self.msg.set("正しい値を入力してください")
            return
        if not os.path.exists(savefolderpath):
            self.msg.set("保存先が存在しません")
            return
        thread1 = threading.Thread(target=self.pack_single_ple, args=(power, minWL, maxWL, stepWL, widthWL, exposure, savefolderpath))
        thread1.start()
    
    def pack_single_ple(self, power:float, minWL:int, maxWL:int, stepWL:int, widthWL:int, exposure:int, savefolderpath:str)->None:
        starttime = datetime.datetime.now()
        endtime = starttime + datetime.timedelta(seconds= (func.waittime4exposure(exposure) +10) * (((maxWL - minWL) / stepWL) + 1) + 120)#120秒はなんとなくの初期化時間
        self.button_start["state"] = tkinter.DISABLED
        self.logger = logger.Logger(log_file_path=os.path.join(savefolderpath, "log.txt"), timestamp_flag=True, log_scroll=self.log_scrolltxt)
        self.msg.set("計測中...\n" + "開始時刻:" + starttime.strftime("%Y/%m/%d %H:%M:%S") + "\n" + "終了予定時刻:" + endtime.strftime("%Y/%m/%d %H:%M:%S"))
        self.pb.start(10)
        try:
            single_ple(power, minWL, maxWL, stepWL, widthWL, exposure, savefolderpath, self.logger)
        except:
            self.msg.set("データ取得中にエラーが発生しました")
            self.pb.stop()
            self.button_start["state"] = tkinter.NORMAL
            return
        self.pb.stop()
        self.msg.set("計測完了!")
        self.button_start["state"] = tkinter.NORMAL
        return

if __name__ == "__main__":
    root = tkinter.Tk()
    app = Application(master=root)
    app.mainloop()