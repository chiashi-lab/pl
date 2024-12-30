import tkinter
from tkinter import ttk
import sys
sys.coinit_flags = 2
from tkinter import filedialog
import threading
from main import moving_pl
from driver.prior import Proscan
import config
import func
import datetime
import gc

class Application(tkinter.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.master.geometry("600x800")
        self.master.title(u"PLEマップのマッピング測定君")
        self.create_widgets()

    def create_widgets(self):
        self.label_minwavelength = tkinter.Label(text=u'励起光最短中心波長')
        self.label_minwavelength.place(x=10, y=10)
        self.entry_minwavelength = tkinter.Entry(width=7)
        self.entry_minwavelength.insert(tkinter.END, '785')
        self.entry_minwavelength.place(x=190, y=10)
        self.unit_minwavelength = tkinter.Label(text=u'nm')
        self.unit_minwavelength.place(x=250, y=10)

        self.label_maxwavelength = tkinter.Label(text=u'励起光最長中心波長')
        self.label_maxwavelength.place(x=10, y=50)
        self.entry_maxwavelength = tkinter.Entry(width=7)
        self.entry_maxwavelength.insert(tkinter.END, '786')
        self.entry_maxwavelength.place(x=190, y=50)
        self.unit_maxwavelength = tkinter.Label(text=u'nm')
        self.unit_maxwavelength.place(x=250, y=50)

        self.label_stepwavelength = tkinter.Label(text=u'励起光中心波長間隔')
        self.label_stepwavelength.place(x=10, y=90)
        self.entry_stepwavelength = tkinter.Entry(width=7)
        self.entry_stepwavelength.insert(tkinter.END, '1')
        self.entry_stepwavelength.place(x=190, y=90)
        self.unit_stepwavelength = tkinter.Label(text=u'nm')
        self.unit_stepwavelength.place(x=250, y=90)

        self.label_wavelengthwidth = tkinter.Label(text=u'励起光波長幅')
        self.label_wavelengthwidth.place(x=10, y=130)
        self.entry_wavelengthwidth = tkinter.Entry(width=7)
        self.entry_wavelengthwidth.insert(tkinter.END, '1')
        self.entry_wavelengthwidth.place(x=190, y=130)
        self.unit_wavelengthwidth = tkinter.Label(text=u'nm')
        self.unit_wavelengthwidth.place(x=250, y=130)

        self.label_integrationtime = tkinter.Label(text=u'露光時間')
        self.label_integrationtime.place(x=10, y=170)
        self.entry_integrationtime = tkinter.Entry(width=7, text='120')
        self.entry_integrationtime.insert(tkinter.END, '120')
        self.entry_integrationtime.place(x=190, y=170)
        self.unit_integrationtime = tkinter.Label(text=u'秒')
        self.unit_integrationtime.place(x=250, y=170)

        self.label_targetpower = tkinter.Label(text=u'サンプル照射パワー')
        self.label_targetpower.place(x=10, y=210)
        self.entry_targetpower = tkinter.Entry(width=7)
        self.entry_targetpower.insert(tkinter.END, '2')
        self.entry_targetpower.place(x=190, y=210)
        self.unit_targetpower = tkinter.Label(text=u'mW')
        self.unit_targetpower.place(x=250, y=210)

        self.label_path = tkinter.Label(text=u'保存先')
        self.label_path.place(x=10, y=280)
        self.entry_path = tkinter.Entry(width=40)
        self.entry_path.insert(tkinter.END, 'C:\\Users\\optics\\individual')
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
        self.button_startpos.bind("<1>", self.call_get_pos_start)
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
        self.button_endpos.bind("<1>", self.call_get_pos_end)
        self.button_endpos.place(x=400, y=400)

        self.label_numberofsteps = tkinter.Label(text=u'データ取得地点の個数')
        self.label_numberofsteps.place(x=10, y=470)
        self.entry_numberofsteps = tkinter.Entry(width=8)
        self.entry_numberofsteps.insert(tkinter.END, '1')
        self.entry_numberofsteps.place(x=170, y=470)

        self.autofocus = tkinter.BooleanVar()
        self.checkbox_autofocus = tkinter.Checkbutton(text=u'オートフォーカス', variable=self.autofocus)
        self.checkbox_autofocus.place(x=10, y=500)

        self.button_start = tkinter.Button(text=u'スタート', width=30)
        self.button_start.bind("<1>", self.call_pack_movingpl)
        self.button_start.place(x=20, y=750)

        self.pb = ttk.Progressbar(root, orient="horizontal", length=200, mode="indeterminate")
        self.pb.place(x=30, y=690)

        self.msg = tkinter.StringVar(value="値を設定してスタートを押してください")
        self.label_msg = tkinter.Label(textvariable=self.msg)
        self.label_msg.place(x=20, y=550)

    def get_path(self, event):
        file = filedialog.askdirectory(initialdir="C:\\Users\\optics\\individual")
        self.entry_path.delete(0, tkinter.END)
        self.entry_path.insert(tkinter.END, file)
    
    def call_pack_movingpl(self, event):
        try:
            power = float(self.entry_targetpower.get()) * 0.001
            minWL = int(self.entry_minwavelength.get())
            maxWL = int(self.entry_maxwavelength.get())
            stepWL = int(self.entry_stepwavelength.get())
            widthWL = int(self.entry_wavelengthwidth.get())
            exposure = int(self.entry_integrationtime.get())
            path = self.entry_path.get()
            startpos = [int(self.entry_startpos_x.get()), int(self.entry_startpos_y.get())]
            endpos = [int(self.entry_endpos_x.get()), int(self.entry_endpos_y.get())]
            numberofsteps = int(self.entry_numberofsteps.get())
            autofocus = bool(self.autofocus.get())
        except:
            self.msg.set("値を正しく入力してください")
            return
        if power < 0.0 or power > 4.0 or minWL < 400 or minWL > 850 or maxWL < 400 or maxWL > 850 or stepWL < 0 or stepWL > 400 or widthWL < 1 or widthWL > 100 or exposure < 0 or exposure > 1000 or minWL > maxWL or (maxWL - minWL) < stepWL:
            self.msg.set("正しい値を入力してください")
            return
        thread1 = threading.Thread(target=self.pack_movingpl, args=(power, minWL, maxWL, stepWL, widthWL, exposure, path, startpos, endpos, numberofsteps, autofocus))
        thread1.start()

    def pack_movingpl(self, power:float, minWL:int, maxWL:int, stepWL:int, widthWL:int, exposure:int, path:str, startpos:tuple, endpos:tuple, numberofsteps:int, autofocus:bool)->None:
        starttime = datetime.datetime.now()
        endtime = starttime + datetime.timedelta(seconds= (func.waittime4exposure(exposure) +10) * (((maxWL - minWL) / stepWL) + 1) * numberofsteps + 120)#120秒はなんとなくの初期化時間
        self.button_start["state"] = tkinter.DISABLED
        self.msg.set("計測中...\n" + "開始時刻:" + starttime.strftime("%Y/%m/%d %H:%M:%S") + "\n" + "終了予定時刻:" + endtime.strftime("%Y/%m/%d %H:%M:%S"))
        self.pb.start(10)
        try:
            moving_pl(power, minWL, maxWL, stepWL, widthWL, exposure, path, startpos, endpos, numberofsteps, autofocus)
        except:
            self.msg.set("データ取得中にエラーが発生しました")
            self.pb.stop()
            self.button_start["state"] = tkinter.NORMAL
            return
        self.pb.stop()
        self.msg.set("データ取得完了!")
        self.button_start["state"] = tkinter.NORMAL

    def get_pos(self)->None:
        self.res_get_pos = None
        stage = Proscan(config.PRIORCOMPORT)
        self.res_get_pos = stage.get_pos()
        del stage
        gc.collect()
        return
    
    def get_pos_start(self)->None:
        self.button_startpos["state"] = tkinter.DISABLED
        self.button_endpos["state"] = tkinter.DISABLED
        self.msg.set("計測開始地点のステージ位置を取得中...")
        self.pb.start(5)
        try:
            self.get_pos()
        except:
            self.msg.set("ステージ位置を取得中にエラーが発生しました")
        else:
            self.entry_startpos_x.delete(0, tkinter.END)
            self.entry_startpos_x.insert(tkinter.END, str(self.res_get_pos[0]))
            self.entry_startpos_y.delete(0, tkinter.END)
            self.entry_startpos_y.insert(tkinter.END, str(self.res_get_pos[1]))
            self.msg.set("開始ステージ位置を取得しました")
        self.button_startpos["state"] = tkinter.NORMAL
        self.button_endpos["state"] = tkinter.NORMAL
        self.pb.stop()
        return
    
    def get_pos_end(self):
        self.button_startpos["state"] = tkinter.DISABLED
        self.button_endpos["state"] = tkinter.DISABLED
        self.msg.set("計測終了地点のステージ位置を取得中...")
        self.pb.start(5)
        try:
            self.get_pos()
        except:
            self.msg.set("ステージ位置を取得中にエラーが発生しました")
        else:
            self.entry_endpos_x.delete(0, tkinter.END)
            self.entry_endpos_x.insert(tkinter.END, str(self.res_get_pos[0]))
            self.entry_endpos_y.delete(0, tkinter.END)
            self.entry_endpos_y.insert(tkinter.END, str(self.res_get_pos[1]))
            self.msg.set("終了ステージ位置を取得しました")
        self.button_startpos["state"] = tkinter.NORMAL
        self.button_endpos["state"] = tkinter.NORMAL
        self.pb.stop()
    
    def call_get_pos_start(self, event):
        thread_s = threading.Thread(target=self.get_pos_start)
        thread_s.start()
    
    def call_get_pos_end(self, event):
        thread_e = threading.Thread(target=self.get_pos_end)
        thread_e.start()


if __name__ == '__main__':
    root = tkinter.Tk()
    app = Application(master=root)
    app.mainloop()