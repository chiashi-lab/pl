import tkinter
from tkinter import ttk
import sys
sys.coinit_flags = 2
from tkinter import filedialog, scrolledtext
import threading
from measurment import Hyperspectral_Measurement
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

        self.button_calc_ex_wl = tkinter.Button(text=u'計算', width=10)
        self.button_calc_ex_wl.place(x=410, y=90)
        self.button_calc_ex_wl.bind("<1>", self.calc_ex_wl)

        self.label_minemissionwavelength = tkinter.Label(text=u'AOTF最短中心波長')
        self.label_minemissionwavelength.place(x=10, y=150)
        self.entry_minemissionwavelength = tkinter.Entry(width=7)
        self.entry_minemissionwavelength.insert(tkinter.END, '1200')
        self.entry_minemissionwavelength.place(x=190, y=150)
        self.unit_minemissionwavelength = tkinter.Label(text=u'nm')
        self.unit_minemissionwavelength.place(x=250, y=150)

        self.label_maxemissionwavelength = tkinter.Label(text=u'AOTF最長中心波長')
        self.label_maxemissionwavelength.place(x=10, y=190)
        self.entry_maxemissionwavelength = tkinter.Entry(width=7)
        self.entry_maxemissionwavelength.insert(tkinter.END, '1500')
        self.entry_maxemissionwavelength.place(x=190, y=190)
        self.unit_maxemissionwavelength = tkinter.Label(text=u'nm')
        self.unit_maxemissionwavelength.place(x=250, y=190)

        self.label_stepemissionwavelength = tkinter.Label(text=u'AOTF中心波長間隔')
        self.label_stepemissionwavelength.place(x=10, y=230)
        self.entry_stepemissionwavelength = tkinter.Entry(width=7)
        self.entry_stepemissionwavelength.insert(tkinter.END, '10')
        self.entry_stepemissionwavelength.place(x=190, y=230)
        self.unit_stepemissionwavelength = tkinter.Label(text=u'nm')
        self.unit_stepemissionwavelength.place(x=250, y=230)

        self.button_calc_em_wl = tkinter.Button(text=u'計算', width=10)
        self.button_calc_em_wl.place(x=410, y=230)
        self.button_calc_em_wl.bind("<1>", self.calc_em_wl)

        self.label_LFexpName = tkinter.Label(text=u'LFのexp名')
        self.label_LFexpName.place(x=10, y=290)
        self.entry_LFexpName = tkinter.Entry(width=25)
        self.entry_LFexpName.insert(tkinter.END, 'Exp-10000ms')
        self.entry_LFexpName.place(x=190, y=290)

        self.label_exposuretime = tkinter.Label(text=u'露光時間')
        self.label_exposuretime.place(x=10, y=330)
        self.entry_exposuretime = tkinter.Entry(width=7, text='10')
        self.entry_exposuretime.insert(tkinter.END, '10000')
        self.entry_exposuretime.place(x=190, y=330)
        self.unit_exposuretime = tkinter.Label(text=u'ミリ秒')
        self.unit_exposuretime.place(x=250, y=330)

        self.button_calc_time = tkinter.Button(text=u'計算', width=10)
        self.button_calc_time.place(x=410, y=330)
        self.button_calc_time.bind("<1>", self.calc_time)

        self.label_targetpower = tkinter.Label(text=u'サンプル照射パワー')
        self.label_targetpower.place(x=10, y=370)
        self.entry_targetpower = tkinter.Entry(width=7)
        self.entry_targetpower.insert(tkinter.END, '2')
        self.entry_targetpower.place(x=190, y=370)
        self.unit_targetpower = tkinter.Label(text=u'mW')
        self.unit_targetpower.place(x=250, y=370)

        self.label_path = tkinter.Label(text=u'保存先')
        self.label_path.place(x=10, y=410)
        self.entry_path = tkinter.Entry(width=40)
        self.entry_path.insert(tkinter.END, 'C:\\Users\\optics\\individual')
        self.entry_path.place(x=120, y=410)
        self.button_path = tkinter.Button(text=u'参照', width=10)
        self.button_path.bind("<1>", self.get_path)
        self.button_path.place(x=410, y=410)

        self.button_start = tkinter.Button(text=u'スタート', width=30)
        self.button_start.bind("<1>", self.call_pack_hyperspectra)
        self.button_start.place(x=20, y=850)

        self.pb = ttk.Progressbar(self.master, orient="horizontal", length=200, mode="indeterminate")
        self.pb.place(x=30, y=550)

        self.msg = tkinter.StringVar(value="値を設定してスタートを押してください")
        self.label_msg = tkinter.Label(textvariable=self.msg)
        self.label_msg.place(x=20, y=500)

        self.log_scrolltxt = scrolledtext.ScrolledText(self.master, wrap=tkinter.WORD, width=60, height=10)
        self.log_scrolltxt.place(x=20, y=600)

        self.hyperspectra_measurement_obj = Hyperspectral_Measurement()

    def get_path(self, event):
        if self.button_path["state"] == tkinter.DISABLED:
            return
        self.button_path["state"] = tkinter.DISABLED

        file = filedialog.askdirectory(initialdir="C:\\Users\\optics\\individual")
        self.entry_path.delete(0, tkinter.END)
        self.entry_path.insert(tkinter.END, file.replace("/", "\\"))

        self.button_path["state"] = tkinter.NORMAL
        return

    def calc_ex_wl(self, event):
        if self.button_calc_ex_wl["state"] == tkinter.DISABLED:
            return
        self.button_calc_ex_wl["state"] = tkinter.DISABLED
        try:
            minexWL = int(self.entry_minexcitewavelength.get())
            maxexWL = int(self.entry_maxexcitewavelength.get())
            stepexWL = int(self.entry_stepexcitewavelength.get())
        except Exception as e:
            print(e)
            self.msg.set(f"値を正しく入力してください\n{e}")
            self.button_calc_ex_wl["state"] = tkinter.NORMAL
            return
        if minexWL < 700 or minexWL > 850 or maxexWL < 700 or maxexWL > 850 or stepexWL <= 0 or stepexWL > 400 or minexWL > maxexWL:
            self.msg.set("正しい値を入力してください")
            self.button_calc_ex_wl["state"] = tkinter.NORMAL
            return
        exwavelengthlist = np.arange(minexWL, maxexWL + stepexWL, stepexWL)
        exwavelengthlist = exwavelengthlist.tolist()
        self.msg.set(f"励起光波長は{exwavelengthlist}nmです")
        self.button_calc_ex_wl["state"] = tkinter.NORMAL
        return

    def calc_em_wl(self, event):
        if self.button_calc_em_wl["state"] == tkinter.DISABLED:
            return
        self.button_calc_em_wl["state"] = tkinter.DISABLED
        try:
            minemWL = int(self.entry_minemissionwavelength.get())
            maxemWL = int(self.entry_maxemissionwavelength.get())
            stepemWL = int(self.entry_stepemissionwavelength.get())
        except Exception as e:
            print(e)
            self.msg.set(f"値を正しく入力してください\n{e}")
            self.button_calc_em_wl["state"] = tkinter.NORMAL
            return
        if minemWL < 900 or minemWL > 1500 or maxemWL < 900 or maxemWL > 1500 or stepemWL <= 0 or stepemWL > 600 or minemWL > maxemWL:
            self.msg.set("正しい値を入力してください")
            self.button_calc_em_wl["state"] = tkinter.NORMAL
            return
        emwavelengthlist = np.arange(minemWL, maxemWL + stepemWL, stepemWL)
        emwavelengthlist = emwavelengthlist.tolist()
        self.msg.set(f"AOTF波長は{emwavelengthlist}nmです")
        self.button_calc_em_wl["state"] = tkinter.NORMAL
        return

    def calc_time(self, event):
        if self.button_calc_time["state"] == tkinter.DISABLED:
            return
        self.button_calc_time["state"] = tkinter.DISABLED
        try:
            minexWL = int(self.entry_minexcitewavelength.get())
            maxexWL = int(self.entry_maxexcitewavelength.get())
            stepexWL = int(self.entry_stepexcitewavelength.get())
            minemWL = int(self.entry_minemissionwavelength.get())
            maxemWL = int(self.entry_maxemissionwavelength.get())
            stepemWL = int(self.entry_stepemissionwavelength.get())
            exposure = int(self.entry_exposuretime.get())
        except Exception as e:
            print(e)
            self.msg.set(f"値を正しく入力してください\n{e}")
            self.button_calc_time["state"] = tkinter.NORMAL
            return
        if exposure < 0 or minexWL < 700 or minexWL > 850 or maxexWL < 700 or maxexWL > 850 or stepexWL <= 0 or stepexWL > 400 or minemWL < 900 or minemWL > 1500 or maxemWL < 900 or maxemWL > 1500 or stepemWL <= 0 or stepemWL > 600 or minexWL > maxexWL or minemWL > maxemWL:
            self.msg.set("正しい値を入力してください")
            self.button_calc_time["state"] = tkinter.NORMAL
            return
        # 計測時間の計算
        pred_h, pred_m, pred_s = None, None, None
        pred_h, pred_m, pred_s = func.get_h_m_s((func.waittime4exposure(exposure / 1000) + 60) * len(np.arange(minexWL, maxexWL + stepexWL, stepexWL)) * len(np.arange(minemWL, maxemWL + stepemWL, stepemWL)) + 80)
        if pred_h is None and pred_m is None and pred_s is None:
            msg = "計測にかかる時間は不明です"
        else:
            msg = f"計測にかかる時間は約{pred_h}時間{pred_m}分{pred_s}秒です"
        
        # 波長リストと計測時間の表示
        self.msg.set(f"{msg}")
        self.button_calc_time["state"] = tkinter.NORMAL
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
            minemWL = int(self.entry_minemissionwavelength.get())
            maxemWL = int(self.entry_maxemissionwavelength.get())
            stepemWL = int(self.entry_stepemissionwavelength.get())
            exposure = int(self.entry_exposuretime.get())
            expname = str(self.entry_LFexpName.get())
            path = self.entry_path.get()
        except Exception as e:
            print(e)
            self.msg.set(f"値を正しく入力してください\n{e}")
            self.button_start["state"] = tkinter.NORMAL
            return
        if power < 0.0 or power > 4.0 or exposure < 0 or minexWL < 700 or minexWL > 850 or maxexWL < 700 or maxexWL > 850 or stepexWL <= 0 or stepexWL > 400 or minemWL < 900 or minemWL > 1500 or maxemWL < 900 or maxemWL > 1500 or stepemWL <= 0 or stepemWL > 600 or minexWL > maxexWL or minemWL > maxemWL:
            self.msg.set("正しい値を入力してください")
            self.button_start["state"] = tkinter.NORMAL
            return
        if not os.path.exists(path):
            self.msg.set("保存先が存在しません")
            self.button_start["state"] = tkinter.NORMAL
            return
        thread1 = threading.Thread(target=self.pack_hyperspectra, args=(power, minexWL, maxexWL, stepexWL, exposure, path, minemWL, maxemWL, stepemWL, expname))
        thread1.start()

    def pack_hyperspectra(self, power:float, minexciteWL:int, maxexciteWL:int, stepexciteWL:int, exposure:int, path:str, minemissionWL:int, maxemissionWL:int, stepemissionWL:int, expname:str)->None:
        starttime = datetime.datetime.now()
        endtime = starttime + datetime.timedelta(seconds= (func.waittime4exposure(exposure / 1000) + 60) * len(np.arange(minexciteWL, maxexciteWL + stepexciteWL, stepexciteWL)) * len(np.arange(minemissionWL, maxemissionWL + stepemissionWL, stepemissionWL)) + 80)
        self.logger = logger.Logger(log_file_path=os.path.join(path, "log.txt"), timestamp_flag=True, log_scroll=self.log_scrolltxt)
        self.msg.set("計測中...\n" + "開始時刻:" + starttime.strftime("%Y/%m/%d %H:%M:%S") + "\n" + "終了予定時刻:" + endtime.strftime("%Y/%m/%d %H:%M:%S"))
        self.pb.start(10)
        try:
            self.hyperspectra_measurement_obj.get_hyperspectra(power, minexciteWL, maxexciteWL, stepexciteWL, exposure, path, minemissionWL, maxemissionWL, stepemissionWL, self.logger, expname)
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