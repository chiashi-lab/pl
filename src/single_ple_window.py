import tkinter
from tkinter import ttk
import os
import sys
sys.coinit_flags = 2
from tkinter import filedialog, scrolledtext
import threading
from measurment import Single_Ple_Measurement
import func
import datetime
import logger
import numpy as np

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

        self.button_calcwl = tkinter.Button(text=u'計算', width=10)
        self.button_calcwl.place(x=410, y=90)
        self.button_calcwl.bind("<1>", self.calcwl)

        self.background = tkinter.BooleanVar()
        self.background.set(False)
        self.checkbutton_background = tkinter.Checkbutton(text=u'都度バックグラウンド取得', variable=self.background)
        self.checkbutton_background.place(x=10, y=130)

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

        self.label_savefolderpath = tkinter.Label(text=u'保存先フォルダ')
        self.label_savefolderpath.place(x=10, y=260)
        self.entry_savefolderpath = tkinter.Entry(width=40)
        self.entry_savefolderpath.insert(tkinter.END, 'C:\\Users\\optics\\individual')
        self.entry_savefolderpath.place(x=120, y=260)
        self.button_savefolderpath = tkinter.Button(text=u'参照', width=10)
        self.button_savefolderpath.bind("<1>", self.call_get_path)
        self.button_savefolderpath.place(x=410, y=260)

        self.button_start = tkinter.Button(text=u'スタート', width=30)
        self.button_start.bind("<1>", self.call_pack_single_ple)
        self.button_start.place(x=20, y=650)

        self.pb = ttk.Progressbar(self.master, orient="horizontal", length=200, mode="indeterminate")
        self.pb.place(x=30, y=360)

        self.msg = tkinter.StringVar(value="値を設定してスタートを押してください")
        self.label_msg = tkinter.Label(textvariable=self.msg)
        self.label_msg.place(x=20, y=310)

        self.log_scrolltxt = scrolledtext.ScrolledText(self.master, wrap=tkinter.WORD, width=60, height=10)
        self.log_scrolltxt.place(x=20, y=400)

        self.single_ple_measurement_obj = Single_Ple_Measurement()

    def call_get_path(self, event)->None:
        if self.button_savefolderpath["state"] == tkinter.DISABLED:
            return
        self.button_savefolderpath["state"] = tkinter.DISABLED
        file = filedialog.askdirectory(initialdir="C:\\Users\\optics\\individual")
        self.entry_savefolderpath.delete(0,tkinter.END)
        self.entry_savefolderpath.insert(tkinter.END, file)
        self.button_savefolderpath["state"] = tkinter.NORMAL

    def calcwl(self, event) -> None:
        if self.button_calcwl["state"] == tkinter.DISABLED:
            return
        self.button_calcwl["state"] = tkinter.DISABLED

        # 入力値のバリデーション
        try:
            minWL = int(self.entry_minWL.get())
            maxWL = int(self.entry_maxWL.get())
            stepWL = int(self.entry_stepWL.get())
            wavelenghlist = np.arange(minWL, maxWL + stepWL, stepWL)
            wavelenghlist = wavelenghlist.tolist()
        except Exception as e:
            print(e)
            self.msg.set(f"数字を入力してください\n{e}")
            self.button_calcwl["state"] = tkinter.NORMAL
            return
        if minWL < 700 or minWL > 850 or maxWL < 700 or maxWL > 850 or stepWL <= 0 or stepWL > 400 or minWL > maxWL:
            self.msg.set("正しい値を入力してください")
            self.button_calcwl["state"] = tkinter.NORMAL
            return

        # 計測時間の計算
        pred_h, pred_m, pred_s = None, None, None
        try:
            exposure = int(self.entry_exposure.get())
            background = bool(self.background.get())
            pred_h, pred_m, pred_s = func.get_h_m_s((func.waittime4exposure(exposure) * (2 if background else 1) + 60) * len(wavelenghlist) + 80)
        except Exception as e:
            pass
        if pred_h is None and pred_m is None and pred_s is None:
            msg = "計測にかかる時間は不明です"
        else:
            msg = f"計測にかかる時間は約{pred_h}時間{pred_m}分{pred_s}秒です"
        
        # 波長リストと計測時間の表示
        self.msg.set(f"励起光波長は{wavelenghlist}nmです\n{msg}")
        self.button_calcwl["state"] = tkinter.NORMAL
        return
    
    def call_pack_single_ple(self, event)->None:
        if self.button_start["state"] == tkinter.DISABLED:
            return
        self.button_start["state"] = tkinter.DISABLED

        # 入力値のバリデーション
        try:
            power = float(self.entry_power.get()) * 0.001
            minWL = int(self.entry_minWL.get())
            maxWL = int(self.entry_maxWL.get())
            stepWL = int(self.entry_stepWL.get())
            background = bool(self.background.get())
            exposure = int(self.entry_exposure.get())
            savefolderpath = self.entry_savefolderpath.get()
            _  = np.arange(minWL, maxWL + stepWL, stepWL)  # 波長リストの計算
        except Exception as e:
            print(e)
            self.msg.set(f"数字を入力してください\n{e}")
            self.button_start["state"] = tkinter.NORMAL
            return
        if power < 0.0 or power > 4.0 or minWL < 700 or minWL > 850 or maxWL < 700 or maxWL > 850 or stepWL <= 0 or stepWL > 400 or exposure < 0 or exposure > 1000 or minWL > maxWL:
            self.msg.set("正しい値を入力してください")
            self.button_start["state"] = tkinter.NORMAL
            return
        if not os.path.exists(savefolderpath):
            self.msg.set("保存先が存在しません")
            self.button_start["state"] = tkinter.NORMAL
            return

        # スレッドを使用して計測を開始
        thread1 = threading.Thread(target=self.pack_single_ple, args=(power, minWL, maxWL, stepWL, background, exposure, savefolderpath))
        thread1.start()
    
    def pack_single_ple(self, power:float, minWL:int, maxWL:int, stepWL:int, background:bool, exposure:int, savefolderpath:str)->None:
        starttime = datetime.datetime.now()
        endtime = starttime + datetime.timedelta(seconds= (func.waittime4exposure(exposure) * (2 if background else 1) + 60) * len(np.arange(minWL, maxWL + stepWL, stepWL)) + 80)#120秒はなんとなくの初期化時間
        self.button_start["state"] = tkinter.DISABLED
        self.logger = logger.Logger(log_file_path=os.path.join(savefolderpath, "log.txt"), timestamp_flag=True, log_scroll=self.log_scrolltxt)
        self.msg.set("計測中...\n" + "開始時刻:" + starttime.strftime("%Y/%m/%d %H:%M:%S") + "\n" + "終了予定時刻:" + endtime.strftime("%Y/%m/%d %H:%M:%S"))
        self.pb.start(10)
        try:
            self.single_ple_measurement_obj.single_ple(power, minWL, maxWL, stepWL, background, exposure, savefolderpath, self.logger)
        except Exception as e:
            print(e)
            self.msg.set(f"データ取得中にエラーが発生しました\n{e}")
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