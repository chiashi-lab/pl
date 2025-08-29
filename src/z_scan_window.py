import tkinter
from tkinter import ttk
import sys
sys.coinit_flags = 2
from tkinter import filedialog, scrolledtext
import threading
from measurment import dev_Zscan_image_Measurement
from driver.focus_adjuster_driver import Focus_adjuster
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
        self.master.geometry("900x900")
        self.master.title(u"NIR画像のzマッピング撮影")
        self.create_widgets()
        self.focus_adjuster = Focus_adjuster(config.AUTOFOCUSCOMPORT)

    def create_widgets(self):#arduino操作コントローラーの追加
        self.label_wavelength = tkinter.Label(text=u'励起光中心波長')
        self.label_wavelength.place(x=10, y=10)
        self.entry_wavelength = tkinter.Entry(width=7)
        self.entry_wavelength.insert(tkinter.END, '785')
        self.entry_wavelength.place(x=190, y=10)
        self.unit_wavelength = tkinter.Label(text=u'nm')
        self.unit_wavelength.place(x=250, y=10)

        self.label_LFexpName = tkinter.Label(text=u'LFのexp名')
        self.label_LFexpName.place(x=10, y=50)
        self.entry_LFexpName = tkinter.Entry(width=25)
        self.entry_LFexpName.insert(tkinter.END, 'Exp-5000ms')
        self.entry_LFexpName.place(x=190, y=50)

        self.label_exposuretime = tkinter.Label(text=u'露光時間')
        self.label_exposuretime.place(x=10, y=170)
        self.entry_exposuretime = tkinter.Entry(width=7, text='120')
        self.entry_exposuretime.insert(tkinter.END, '5000')
        self.entry_exposuretime.place(x=190, y=170)
        self.unit_exposuretime = tkinter.Label(text=u'ミリ秒')
        self.unit_exposuretime.place(x=250, y=170)

        self.label_targetpower = tkinter.Label(text=u'サンプル照射パワー')
        self.label_targetpower.place(x=10, y=210)
        self.entry_targetpower = tkinter.Entry(width=7)
        self.entry_targetpower.insert(tkinter.END, '1')
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

        self.label_numberofsteps = tkinter.Label(text=u'データ取得地点の個数')
        self.label_numberofsteps.place(x=10, y=400)
        self.entry_numberofsteps = tkinter.Entry(width=8)
        self.entry_numberofsteps.insert(tkinter.END, '1')
        self.entry_numberofsteps.place(x=170, y=400)

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

        self.pos = tkinter.IntVar()
        self.pos.set(0)
        self.label_zpos = ttk.Label(textvariable=self.pos)
        self.label_zpos.place(x=700, y=130)
        self.label_zpos_text = tkinter.Label(text=u'現在のZ位置')
        self.label_zpos_text.place(x=570, y=130)
        self.label_zpos_unit = tkinter.Label(text=u'um/4')
        self.label_zpos_unit.place(x=800, y=130)

        self.button_20micro = ttk.Button(text="20um", command=self.call_move_20um)
        self.button_20micro.place(x=700, y=10)

        self.button_1micro = ttk.Button(text="1um", command=self.call_move_1um)
        self.button_1micro.place(x=700, y=50)

        self.button_quarter = ttk.Button(text="1/4um", command=self.call_move_quarter)
        self.button_quarter.place(x=700, y=90)

        self.button_m_quarter = ttk.Button(text="-1/4um", command=self.call_move_m_quarter)
        self.button_m_quarter.place(x=700, y=160)

        self.button_m_1micro = ttk.Button(text="-1um", command=self.call_move_m_1micro)
        self.button_m_1micro.place(x=700, y=200)

        self.button_m_20micro = ttk.Button(text="-20um", command=self.call_move_m_20um)
        self.button_m_20micro.place(x=700, y=240)

        self.label_startzpos = tkinter.Label(text=u'開始点Z位置')
        self.label_startzpos.place(x=570, y=310)
        self.entry_startzpos = tkinter.Entry(width=8)
        self.entry_startzpos.insert(tkinter.END, '0')
        self.entry_startzpos.place(x=690, y=310)
        self.button_startzpos = tkinter.Button(text=u'取得', width=5)
        self.button_startzpos.bind("<1>", self.get_zpos_start)
        self.button_startzpos.place(x=800, y=310)

        self.label_endzpos = tkinter.Label(text=u'終了点Z位置')
        self.label_endzpos.place(x=570, y=360)
        self.entry_endzpos = tkinter.Entry(width=8)
        self.entry_endzpos.insert(tkinter.END, '0')
        self.entry_endzpos.place(x=690, y=360)
        self.button_endzpos = tkinter.Button(text=u'取得', width=5)
        self.button_endzpos.bind("<1>", self.get_zpos_end)
        self.button_endzpos.place(x=800, y=360)

        self.scan_image_measurement_obj = dev_Zscan_image_Measurement()

    def get_path(self, event):
        if self.button_path["state"] == tkinter.DISABLED:
            return
        self.button_path["state"] = tkinter.DISABLED

        file = filedialog.askdirectory(initialdir="C:\\Users\\optics\\individual")
        self.entry_path.delete(0, tkinter.END)
        self.entry_path.insert(tkinter.END, file.replace("/", "\\"))

        self.button_path["state"] = tkinter.NORMAL
        return

    def calc_measurement_interval(self, event):
        if self.button_calc_measurement_interval["state"] == tkinter.DISABLED:
            return
        self.button_calc_measurement_interval["state"] = tkinter.DISABLED
        try:
            numberofsteps = int(self.entry_numberofsteps.get())
            startpos = int(self.entry_startzpos.get())
            endpos = int(self.entry_endzpos.get())
        except Exception as e:
            print(e)
            self.msg.set(f"値を正しく入力してください\n{e}")
            self.button_calc_measurement_interval["state"] = tkinter.NORMAL
            return
        if numberofsteps < 2:
            self.msg.set("測定箇所は2箇所以上必要です")
            self.button_calc_measurement_interval["state"] = tkinter.NORMAL
            return
        distance = abs(endpos - startpos) / 4 #umに変換
        interval = distance / (numberofsteps - 1)
        self.msg.set(f"測定間隔は{interval:.2f}umです")
        self.button_calc_measurement_interval["state"] = tkinter.NORMAL
        return

    def get_zpos_start(self, event):
        if self.button_startzpos["state"] == tkinter.DISABLED:
            return
        self.button_startzpos["state"] = tkinter.DISABLED
        self.button_endzpos["state"] = tkinter.DISABLED
        try:
            zpos = self.focus_adjuster.position
        except Exception as e:
            print(e)
            self.msg.set(f"Z位置を取得中にエラーが発生しました\n{e}")
        else:
            self.entry_startzpos.delete(0, tkinter.END)
            self.entry_startzpos.insert(tkinter.END, str(zpos))
            self.msg.set("開始点Z位置を取得しました")
        self.button_startzpos["state"] = tkinter.NORMAL
        self.button_endzpos["state"] = tkinter.NORMAL

    def get_zpos_end(self, event):
        if self.button_endzpos["state"] == tkinter.DISABLED:
            return
        self.button_startzpos["state"] = tkinter.DISABLED
        self.button_endzpos["state"] = tkinter.DISABLED
        try:
            zpos = self.focus_adjuster.position
        except Exception as e:
            print(e)
            self.msg.set(f"Z位置を取得中にエラーが発生しました\n{e}")
        else:
            self.entry_endzpos.delete(0, tkinter.END)
            self.entry_endzpos.insert(tkinter.END, str(zpos))
            self.msg.set("終了点Z位置を取得しました")
        self.button_startzpos["state"] = tkinter.NORMAL
        self.button_endzpos["state"] = tkinter.NORMAL

    def call_move_20um(self) -> None:
        if self.button_20micro["state"] == "disabled":
            return
        thread = threading.Thread(target=self.move, args=(4 * 20,))
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

    def call_move_m_20um(self) -> None:
        if self.button_m_20micro["state"] == "disabled":
            return
        thread = threading.Thread(target=self.move, args=(-4 * 20,))
        thread.start()

    def move(self, move_value: int) -> None:
        self.button_20micro.configure(state="disabled")
        self.button_1micro.configure(state="disabled")
        self.button_quarter.configure(state="disabled")
        self.button_m_quarter.configure(state="disabled")
        self.button_m_1micro.configure(state="disabled")
        self.button_m_20micro.configure(state="disabled")

        self.focus_adjuster.move_by(move_value, block=True)
        self.pos.set(self.focus_adjuster.position)

        self.button_20micro.configure(state="normal")
        self.button_1micro.configure(state="normal")
        self.button_quarter.configure(state="normal")
        self.button_m_quarter.configure(state="normal")
        self.button_m_1micro.configure(state="normal")
        self.button_m_20micro.configure(state="normal")
    
    def call_pack_scan_ple(self, event):#変更
        if self.button_start["state"] == tkinter.DISABLED:
            return
        self.button_start["state"] = tkinter.DISABLED
        try:
            power = float(self.entry_targetpower.get()) * 0.001
            wl = int(self.entry_wavelength.get())
            expname = str(self.entry_LFexpName.get())
            exposure = int(self.entry_exposuretime.get())
            path = self.entry_path.get()
            numberofsteps = int(self.entry_numberofsteps.get())
            startzpos = int(self.entry_startzpos.get())
            endzpos = int(self.entry_endzpos.get())
        except Exception as e:
            print(e)
            self.msg.set(f"値を正しく入力してください\n{e}")
            self.button_start["state"] = tkinter.NORMAL
            return
        if power < 0.0 or power > 4.0 or wl < 700 or wl > 850 or exposure < 0:
            self.msg.set("正しい値を入力してください")
            self.button_start["state"] = tkinter.NORMAL
            return
        if numberofsteps < 2:
            self.msg.set("測定箇所は2箇所以上必要です")
            self.button_start["state"] = tkinter.NORMAL
            return
        if not os.path.exists(path):
            self.msg.set("保存先が存在しません")
            self.button_start["state"] = tkinter.NORMAL
            return
        thread1 = threading.Thread(target=self.pack_scan_ple, args=(power, wl, expname, exposure, path, numberofsteps, startzpos, endzpos))
        thread1.start()

    def pack_scan_ple(self, power, wl, expname, exposure, path, numberofsteps, startzpos, endzpos):
        starttime = datetime.datetime.now()
        endtime = starttime + datetime.timedelta(seconds= (func.waittime4exposure(exposure/1000) + 5) * numberofsteps + 120)#120秒はなんとなくの初期化時間
        self.button_start["state"] = tkinter.DISABLED
        self.logger = logger.Logger(log_file_path=os.path.join(path, "log.txt"), timestamp_flag=True, log_scroll=self.log_scrolltxt)
        self.msg.set("計測中...\n" + "開始時刻:" + starttime.strftime("%Y/%m/%d %H:%M:%S") + "\n" + "終了予定時刻:" + endtime.strftime("%Y/%m/%d %H:%M:%S"))
        self.pb.start(10)
        try:
            self.scan_image_measurement_obj.scan_image(power, wl, expname, exposure, path, numberofsteps, startzpos, endzpos, self.focus_adjuster, self.logger)
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