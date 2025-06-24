import tkinter
from tkinter import ttk
import sys
sys.coinit_flags = 2
sys.path.append('../')
import threading
from driver.ophir import juno
from driver.thorlab import ThorlabStage, FlipMount, thorlabspectrometer
from driver.sigmakoki import shutter
from driver.zaber import zaber_linear_actuator
from logger import Logger
import config
from power_dict import PowerDict
import matplotlib.pyplot as plt
import time
import func
from typing import List, Tuple

def pid_control_wavelength(targetwavelength:int, TiSap_actuator:zaber_linear_actuator, spectrometer:thorlabspectrometer, logger:Logger, e_kp, e_ki, e_kd, eps:float = 0.5, max_retry:int = 40) -> Tuple[List, bool]:
    '''
    PID制御を用いて目標波長に制御する関数
    args:
        targetwavelength(int): 目標波長[nm]
        TiSap_actuator(zaber_linear_actuator): TiSapのアクチュエータの自作ドライバークラス
        spectrometer(thorlabspectrometer): スペクトロメータの自作ドライバークラス
        logger(Logger): 自作ロガークラス
        eps(float): 目標波長の許容誤差[nm]
        max_retry(int): PID制御が失敗した場合の最大リトライ回数
    return:
        None
    '''
    # PID制御のパラメータ. PIDゲインはsrc/config.pyに記述されている
    Kp = float(e_kp.get())
    Ki = float(e_ki.get())
    Kd = float(e_kd.get())
    dt = 1.0
    acc = 0.0
    diff = 0.0
    prev = 0.0
    poslog = []

    logger.log(f"wavelength control start for {targetwavelength}nm")
    TiSap_actuator.move_to(func.wavelength2tisp_pos(targetwavelength)) # 事前に取得したリニアアクチュエータ位置と波長の関係から一次関数の関係にあることがわかっている(tisp.ipynbにフィッティング結果がある)．このフィッティング式から目標波長に対応するアクチュエータ位置を計算して移動する.この処理はフィードバック制御ではない

    # ここからPID制御
    for i in range(max_retry):
        time.sleep(0.05)  #分光器やアクチュエータが落ち着くまで若干待つ#########################
        nowstep = TiSap_actuator.get_position()
        nowwavelength = spectrometer.get_peak()
        logger.log(f"{i}th retry of PID wavelength control")
        logger.log(f"current wavelength: {nowwavelength}")
        logger.log(f"current step: {nowstep}")
        if nowwavelength < targetwavelength - eps or targetwavelength + eps < nowwavelength:#目標波長に到達していない場合
            error = nowwavelength - targetwavelength
            acc += (error + prev) * dt /2
            diff = (error - prev) / dt
            tostep = nowstep + Kp * error + Ki * acc + Kd * diff
            logger.log(f"target step: {tostep}")
            TiSap_actuator.move_to(tostep)
            prev = error
            poslog.append(tostep)
        else:#目標波長に到達したら終了
            logger.log("Already at target wavelength")
            return poslog, True
    # max_retry回繰り返しても目標波長に到達しなかった場合
    logger.log(f"Failed to control wavelength by {max_retry} times")
    logger.log(f"current wavelength: {nowwavelength}")
    return poslog, False

class Application(tkinter.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.master.geometry("500x500")
        self.master.title(u"励起光制御")
        self.create_widgets()
    
    def create_widgets(self):
        self.label_wavelength = tkinter.Label(text=u'励起光中心波長', state='disabled')
        self.label_wavelength.place(x=30, y=100)
        self.entry_wavelength = tkinter.Entry(width=7)
        self.entry_wavelength.insert(tkinter.END, '785')
        self.entry_wavelength["state"] = "disabled"
        self.entry_wavelength.place(x=140, y=100)
        self.unit_wavelength = tkinter.Label(text=u'nm', state='disabled')
        self.unit_wavelength.place(x=200, y=100)
        
        self.set_button = tkinter.Button(text=u'セット', width=20)
        self.set_button.bind("<1>", self.call_choonepower)
        self.set_button.place(x=20, y=220)
        self.set_button["state"] = tkinter.DISABLED

        self.init_button = tkinter.Button(text=u'初期化', width=20)
        self.init_button.bind("<1>", self.call_init)
        self.init_button.place(x=20, y=10)

        self.pb = ttk.Progressbar(self.master, orient="horizontal", length=200, mode="indeterminate")
        self.pb.place(x=30, y=310)

        self.msg = tkinter.StringVar(value="初期化してください")
        self.label_msg = tkinter.Label(textvariable=self.msg)
        self.label_msg.place(x=20, y=280)

        self.log_scrolltext = tkinter.scrolledtext.ScrolledText(width=60, height=10)
        self.log_scrolltext.place(x=10, y=360)
        
        self.logger = Logger(log_file_path=None, log_scroll=self.log_scrolltext)

        # --- ここからゲイン入力欄の追加 ---
        self.label_kp = tkinter.Label(text='Kp', state='disabled')
        self.label_kp.place(x=30, y=60)
        self.entry_kp = tkinter.Entry(width=7)
        self.entry_kp.insert(tkinter.END, '1.0')
        self.entry_kp["state"] = "disabled"
        self.entry_kp.place(x=70, y=60)

        self.label_ki = tkinter.Label(text='Ki', state='disabled')
        self.label_ki.place(x=150, y=60)
        self.entry_ki = tkinter.Entry(width=7)
        self.entry_ki.insert(tkinter.END, '0.0')
        self.entry_ki["state"] = "disabled"
        self.entry_ki.place(x=190, y=60)

        self.label_kd = tkinter.Label(text='Kd', state='disabled')
        self.label_kd.place(x=270, y=60)
        self.entry_kd = tkinter.Entry(width=7)
        self.entry_kd.insert(tkinter.END, '0.0')
        self.entry_kd["state"] = "disabled"
        self.entry_kd.place(x=310, y=60)
        # --- ここまで ---

    def call_init(self, event):
        if self.init_button["state"] == tkinter.DISABLED:
            return
        self.init_button["state"] = tkinter.DISABLED
        thread2 = threading.Thread(target=self.initialize)
        thread2.start()

    def call_choonepower(self, event):
        if self.set_button["state"] == tkinter.DISABLED:
            return
        self.set_button["state"] = tkinter.DISABLED
        try:
            wavelength = int(self.entry_wavelength.get())
        except Exception as e:
            print(e)
            self.msg.set(f"値を正しく入力してください\n{e}")
            self.set_button["state"] = tkinter.NORMAL
            return
        if wavelength < 700 or wavelength > 850:
            self.msg.set("正しい値を入力して下さい")
            self.set_button["state"] = tkinter.NORMAL
            return
        thread1 = threading.Thread(target=self.choonepower, args=(wavelength,))
        thread1.start()

    def initialize(self):
        try:
            self.msg.set("初期化中...")
            self.pb.start(10)

            self.flipshut = FlipMount()
            self.flipshut.close()
            self.logger.log("flipshut is closed")

            self.tisp = zaber_linear_actuator()
            self.logger.log("TiSap actuator is initialized")

            self.spectrometer = thorlabspectrometer()
            self.logger.log("spectrometer is initialized")
        except Exception as e:
            print(e)
            self.msg.set(f"初期化に失敗しました\n{e}")
            self.pb.stop()
            self.init_button["state"] = tkinter.NORMAL
            return

        self.set_button["state"] = tkinter.NORMAL
        self.init_button["state"] = tkinter.DISABLED
        self.entry_wavelength["state"] = "normal"
        self.label_wavelength["state"] = "normal"
        self.entry_kp["state"] = "normal"
        self.label_kp["state"] = "normal"
        self.entry_ki["state"] = "normal"
        self.label_ki["state"] = "normal"
        self.entry_kd["state"] = "normal"
        self.label_kd["state"] = "normal"
        # --- ここまで ---
        self.pb.stop()
        self.msg.set("初期化完了．値を設定してセットを押してください")

    def choonepower(self, centerwavelength):
        self.msg.set("波長の切替とパワーの調整中...")
        self.pb.start(10)
        try:
            self.flipshut.open()
            self.logger.log(f"start wavelength control at {centerwavelength}")
            poslog, _ = pid_control_wavelength(targetwavelength=centerwavelength, TiSap_actuator=self.tisp, spectrometer=self.spectrometer, logger=self.logger, 
                                                e_kp=self.entry_kp, e_ki=self.entry_ki, e_kd=self.entry_kd)
            plt.plot(poslog)
            plt.show()
        except Exception as e:
            print(e)
            self.msg.set(f"波長の切替とパワーの調整に失敗しました\n{e}")
            self.pb.stop()
            self.set_button["state"] = tkinter.NORMAL
            return
        self.pb.stop()
        self.set_button["state"] = tkinter.NORMAL
        self.msg.set(f"手動シャッター操作で照射してください.波長:{centerwavelength}nm")

if __name__ == "__main__":
    root = tkinter.Tk()
    app = Application(master=root)
    app.mainloop()