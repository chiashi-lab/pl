import tkinter
from tkinter import ttk
import sys
sys.coinit_flags = 2
from tkinter import filedialog, scrolledtext
import threading
from measurment import hyperspectral_Measurement
from driver.prior import Proscan
import config
import func
import datetime
import gc
import os
import logger
import numpy as np

class Application(tkinter.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.master.geometry("600x900")
        self.master.title(u"ハイパースペクトル画像の撮影")
        self.create_widgets()

    def create_widgets(self):
        self.label_minexcitewavelength = tkinter.Label(text=u'励起光最短中心波長')
        self.label_minexcitewavelength.place(x=10, y=10)
        self.entry_minexcitewavelength = tkinter.Entry(width=7)
        self.entry_minexcitewavelength.insert(tkinter.END, '785')
        self.entry_minexcitewavelength.place(x=190, y=10)
        self.unit_minexcitewavelength = tkinter.Label(text=u'nm')
        self.unit_minexcitewavelength.place(x=250, y=10)

        self.label_maxexcitewavelength = tkinter.Label(text=u'励起光最長中心波長')
        self.label_maxexcitewavelength.place(x=10, y=50)
        self.entry_maxexcitewavelength = tkinter.Entry(width=7)
        self.entry_maxexcitewavelength.insert(tkinter.END, '785')
        self.entry_maxexcitewavelength.place(x=190, y=50)
        self.unit_maxexcitewavelength = tkinter.Label(text=u'nm')
        self.unit_maxexcitewavelength.place(x=250, y=50)

        self.label_stepexcitewavelength = tkinter.Label(text=u'励起光中心波長間隔')
        self.label_stepexcitewavelength.place(x=10, y=90)
        self.entry_stepexcitewavelength = tkinter.Entry(width=7)
        self.entry_stepexcitewavelength.insert(tkinter.END, '1')
        self.entry_stepexcitewavelength.place(x=190, y=90)
        self.unit_stepexcitewavelength = tkinter.Label(text=u'nm')
        self.unit_stepexcitewavelength.place(x=250, y=90)

        self.button_calcwl = tkinter.Button(text=u'計算', width=10)
        self.button_calcwl.place(x=410, y=90)
        self.button_calcwl.bind("<1>", self.calcwl)


        self.label_exposuretime = tkinter.Label(text=u'露光時間')
        self.label_exposuretime.place(x=10, y=170)
        self.entry_exposuretime = tkinter.Entry(width=7, text='120')
        self.entry_exposuretime.insert(tkinter.END, '120')
        self.entry_exposuretime.place(x=190, y=170)
        self.unit_exposuretime = tkinter.Label(text=u'秒')
        self.unit_exposuretime.place(x=250, y=170)

        self.label_targetpower = tkinter.Label(text=u'サンプル照射パワー')
        self.label_targetpower.place(x=10, y=210)
        self.entry_targetpower = tkinter.Entry(width=7)
        self.entry_targetpower.insert(tkinter.END, '2')
        self.entry_targetpower.place(x=190, y=210)
        self.unit_targetpower = tkinter.Label(text=u'mW')
        self.unit_targetpower.place(x=250, y=210)

        self.label_path = tkinter.Label(text=u'保存先')
        self.label_path.place(x=10, y=260)
        self.entry_path = tkinter.Entry(width=40)
        self.entry_path.insert(tkinter.END, 'C:\\Users\\optics\\individual')
        self.entry_path.place(x=120, y=260)
        self.button_path = tkinter.Button(text=u'参照', width=10)
        self.button_path.bind("<1>", self.get_path)
        self.button_path.place(x=410, y=260)

        self.button_calc_measurement_interval = tkinter.Button(text=u'計算', width=7)
        self.button_calc_measurement_interval.bind("<1>", self.calc_measurement_interval)
        self.button_calc_measurement_interval.place(x=400, y=400)

        self.button_start = tkinter.Button(text=u'スタート', width=30)
        self.button_start.bind("<1>", self.call_pack_scan_ple)
        self.button_start.place(x=20, y=850)

        self.pb = ttk.Progressbar(self.master, orient="horizontal", length=200, mode="indeterminate")
        self.pb.place(x=30, y=550)

        self.msg = tkinter.StringVar(value="値を設定してスタートを押してください")
        self.label_msg = tkinter.Label(textvariable=self.msg)
        self.label_msg.place(x=20, y=500)

        self.log_scrolltxt = scrolledtext.ScrolledText(self.master, wrap=tkinter.WORD, width=60, height=10)
        self.log_scrolltxt.place(x=20, y=600)

        self.hyperspectra_measurement_obj = hyperspectral_Measurement()

    def get_path(self, event):
        if self.button_path["state"] == tkinter.DISABLED:
            return
        self.button_path["state"] = tkinter.DISABLED

        file = filedialog.askdirectory(initialdir="C:\\Users\\optics\\individual")
        self.entry_path.delete(0, tkinter.END)
        self.entry_path.insert(tkinter.END, file)

        self.button_path["state"] = tkinter.NORMAL
        return

    def calcwl(self, event):
        if self.button_calcwl["state"] == tkinter.DISABLED:
            return
        self.button_calcwl["state"] = tkinter.DISABLED
        try:
            minWL = int(self.entry_minexwavelength.get())
            maxWL = int(self.entry_maxexwavelength.get())
            stepWL = int(self.entry_stepexwavelength.get())
            wavelengthlist = np.arange(minWL, maxWL + stepWL, stepWL)
            wavelengthlist = wavelengthlist.tolist()
        except Exception as e:
            print(e)
            self.msg.set(f"値を正しく入力してください\n{e}")
            self.button_calcwl["state"] = tkinter.NORMAL
            return
        if minWL < 700 or minWL > 850 or maxWL < 700 or maxWL > 850 or stepWL <= 0 or stepWL > 400 or minWL > maxWL:
            self.msg.set("正しい値を入力してください")
            self.button_calcwl["state"] = tkinter.NORMAL
            return
        self.msg.set(f"励起光波長は{wavelengthlist}nmです")
        self.button_calcwl["state"] = tkinter.NORMAL
        return
    

    
    def call_pack_hyperspectra(self, event):
        if self.button_start["state"] == tkinter.DISABLED:
            return
        self.button_start["state"] = tkinter.DISABLED
        try:
            power = float(self.entry_targetpower.get()) * 0.001
            minexWL = int(self.entry_minexcitewavelength.get())
            maxexWL = int(self.entry_maxexcitewavelength.get())
            stepexWL = int(self.entry_stepexcitewavelength.get())
            exposure = int(self.entry_exposuretime.get())
            path = self.entry_path.get()
        except Exception as e:
            print(e)
            self.msg.set(f"値を正しく入力してください\n{e}")
            self.button_start["state"] = tkinter.NORMAL
            return
        if power < 0.0 or power > 4.0 or minexWL < 700 or minexWL > 850 or maxexWL < 700 or maxexWL > 850 or stepexWL <= 0 or stepexWL > 400 or exposure < 0 or exposure > 1000 or minexWL > maxexWL:
            self.msg.set("正しい値を入力してください")
            self.button_start["state"] = tkinter.NORMAL
            return
        if not os.path.exists(path):
            self.msg.set("保存先が存在しません")
            self.button_start["state"] = tkinter.NORMAL
            return
        thread1 = threading.Thread(target=self.pack_scan_ple, args=(power, minexWL, maxexWL, stepexWL, exposure, path))
        thread1.start()

    def pack_hyperspectra(self, power:float, minexciteWL:int, maxexciteWL:int, stepexciteWL:int, exposure:int, path:str, minemissionWL:int, maxemissionWL:int, stepemissionWL:int)->None:
        starttime = datetime.datetime.now()
        endtime = starttime + datetime.timedelta(seconds= (func.waittime4exposure(exposure) +10) * (((maxexciteWL - minexciteWL) / stepexciteWL) + 1) * (((maxemissionWL - minemissionWL) / stepemissionWL) + 1 + 120))#120秒はなんとなくの初期化時間
        self.button_start["state"] = tkinter.DISABLED
        self.logger = logger.Logger(log_file_path=os.path.join(path, "log.txt"), timestamp_flag=True, log_scroll=self.log_scrolltxt)
        self.msg.set("計測中...\n" + "開始時刻:" + starttime.strftime("%Y/%m/%d %H:%M:%S") + "\n" + "終了予定時刻:" + endtime.strftime("%Y/%m/%d %H:%M:%S"))
        self.pb.start(10)
        try:
            self.hyperspectra_measurement_obj.get_hyperspectra(power, minexciteWL, maxexciteWL, stepexciteWL, exposure, path, minemissionWL, maxemissionWL, stepemissionWL, self.logger)
        except Exception as e:
            print(e)
            self.msg.set(f"データ取得中にエラーが発生しました\n{e}")
            self.pb.stop()
            self.button_start["state"] = tkinter.NORMAL
            return
        self.pb.stop()
        self.msg.set("データ取得完了!")
        self.button_start["state"] = tkinter.NORMAL
        return


if __name__ == '__main__':
    root = tkinter.Tk()
    app = Application(master=root)
    app.mainloop()