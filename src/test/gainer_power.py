import tkinter
from tkinter import ttk
import sys
sys.coinit_flags = 2
sys.path.append('../')
import threading
from measurment import pid_control_wavelength
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

def pid_control_power(targetpower: float, powermeter, NDfilter, eps: float, logger: Logger, NDinitpos: float, e_kp, e_ki, e_kd, max_retry: int = 40) -> None:
    """
    PID制御でNDフィルターを動かして目標パワーに調整する関数
    args:
        targetpower (float): 目標パワー(W)
        powermeter: パワーメーターのインスタンス
        NDfilter: NDフィルターのインスタンス
        eps (float): 許容誤差(W)
        logger (Logger): ロガーのインスタンス
        NDinitpos (float): NDフィルターの初期位置
        kp (float): PID制御の比例ゲイン
        ki (float): PID制御の積分ゲイン
        kd (float): PID制御の微分ゲイン
    """
    # パワーメータの値が安定するまで待機時間が必要なので，波長やパワーを変更した後には待機時間を設ける
    poslog =[]
    r = config.EXCITEPOWERPIDNORMALIZATION / (targetpower * 1000)
    Kp = r * float(e_kp.get())
    Ki = r * float(e_ki.get())
    Kd = r * float(e_kd.get())
    dt = 1.0
    acc = 0.0
    diff = 0.0
    prev = 0.0
    prev_ndpos = NDfilter.get_position()
    if NDinitpos != config.NDINITPOS:
        NDfilter.move_to(NDinitpos)
        poslog.append(NDinitpos)
    elif NDinitpos == config.NDINITPOS and NDfilter.get_position() < config.NDINITPOS:##ポジションが0に近いときは，透過率が高すぎてPID制御に時間がかかりすぎるので，透過率を下げる
        NDfilter.move_to(NDinitpos)
        poslog.append(NDinitpos)

    if abs(prev_ndpos - NDfilter.get_position()) > 1.0e5: #NDフィルターの位置が大きく変わるとレーザーパワーも大きく変わりレンジを跨ぐ際に計測値が不安定になるので長めに待つ
        time.sleep(3)
    time.sleep(2)#最初の熱緩和待機時間.初回はやや長めに待つ################################################
    # PID制御first
    logger.log("PID power control fist start")
    for i in range(max_retry):
        logger.log(f"first {i}th retry of PID power control")
        time.sleep(2)#毎回の熱緩和待機時間.3A-FSの公称応答時間は1.8sである．########################################
        nowndstep = NDfilter.get_position()
        measuredpower = powermeter.get_latestdata()
        nowpower = measuredpower * func.ndstep2ratio(nowndstep)
        logger.log(f"measured power: {measuredpower}")
        logger.log(f"predicted current power: {nowpower}")
        logger.log(f"now step: {nowndstep}")
        flag = False
        if nowpower < targetpower - eps or targetpower + eps < nowpower:
            error = nowpower - targetpower
            acc += (error + prev) * dt /2
            diff = (error - prev) / dt

            tostep = nowndstep + Kp * error + Ki * acc + Kd * diff
            logger.log(f"target step: {tostep}")
            NDfilter.move_to(tostep)
            poslog.append(tostep)
            logger.log(f"now step: {NDfilter.get_position()}\n")
            prev = error
        else:
            logger.log("first Already at target power")
            flag = True
            break
    
    if not flag:
        logger.log("cant choone power")

    return poslog, False

class Application(tkinter.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.master.geometry("500x500")
        self.master.title(u"励起パワーPIDゲイン試験機")
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
        
        self.label_power = tkinter.Label(text=u'目標パワー',state='disabled')
        self.label_power.place(x=30, y=160)
        self.entry_power = tkinter.Entry(width=7)
        self.entry_power.insert(tkinter.END, '1')
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
            power = float(self.entry_power.get()) * 0.001
            wavelength = int(self.entry_wavelength.get())
        except Exception as e:
            print(e)
            self.msg.set(f"値を正しく入力してください\n{e}")
            self.set_button["state"] = tkinter.NORMAL
            return
        if power < 0.0 or power > 4.0 or wavelength < 700 or wavelength > 850:
            self.msg.set("正しい値を入力して下さい")
            self.set_button["state"] = tkinter.NORMAL
            return
        thread1 = threading.Thread(target=self.choonepower, args=(power, wavelength))
        thread1.start()

    def initialize(self):
        try:
            self.msg.set("初期化中...")
            self.pb.start(10)

            self.flipshut = FlipMount()
            self.flipshut.close()
            self.logger.log("flipshut is closed")

            self.mypowerdict = PowerDict()

            self.NDfilter = ThorlabStage(home=True)
            self.NDfilter.move_to(0, block=True)
            self.logger.log(f"stage is at {self.NDfilter.get_position()}\n")

            self.powermeter = juno()
            self.powermeter.open()
            self.powermeter.set_range(0)
            self.logger.log("powermeter is opened")

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
        self.entry_power["state"] = "normal"
        self.label_power["state"] = "normal"
        self.unit_power["state"] = "normal"
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

    def choonepower(self, targetpower, centerwavelength):
        self.msg.set("波長の切替とパワーの調整中...")
        self.pb.start(10)
        try:
            self.flipshut.open()
            self.logger.log(f"start wavelength control at {centerwavelength}")
            pid_control_wavelength(targetwavelength=centerwavelength, TiSap_actuator=self.tisp, spectrometer=self.spectrometer, logger=self.logger)

            self.logger.log(f"start power control at {centerwavelength} for {targetpower}")
            poslog, _ = pid_control_power(
                targetpower=targetpower,
                powermeter=self.powermeter,
                NDfilter=self.NDfilter,
                eps=targetpower*config.EPSRATIO,
                logger=self.logger,
                NDinitpos=None,
                e_kp = self.entry_kp,
                e_ki = self.entry_ki,
                e_kd = self.entry_kd
            )
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
        self.msg.set(f"手動シャッター操作で照射してください.波長:{centerwavelength}nm,パワー:{targetpower*1000}mW")

if __name__ == "__main__":
    root = tkinter.Tk()
    app = Application(master=root)
    app.mainloop()