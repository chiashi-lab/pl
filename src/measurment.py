from driver.horiba import ihr320, Symphony
from driver.ophir import juno
from driver.prior import Proscan
from driver.sigmakoki import shutter
from driver.thorlab import ThorlabStage, FlipMount, thorlabspectrometer
from driver.focus_adjuster_driver import Focus_adjuster
from driver.zaber import zaber_linear_actuator
from driver.princeton import PrincetonCamera
from logger import Logger
import config
from power_dict import PowerDict
import threading
import time
import datetime
import func
import numpy as np
import os
import pandas as pd
import warnings

from typing import List, Tuple

def pid_control_power(targetpower:float, powermeter:juno, NDfilter:ThorlabStage, eps:float = 0.1, logger:Logger = None, max_retry:int = 50, NDinitpos:int = config.NDINITPOS) -> Tuple[List, bool]:
    '''
    PID制御を用いて目標パワーに制御する関数
    args:
        targetpower(float): 目標パワー[W]
        wavelength(int): 現在の波長[nm]
        powermeter(juno): パワーメーターの自作ドライバークラス
        NDfilter(ThorlabStage): NDフィルターがついているthorlabステージの自作ドライバークラス
        eps(float): 目標パワーの許容誤差[W]
    return:
        poslog(List): NDフィルターの位置のログ
        bool: 目標パワーに到達したかどうか
    '''
    # パワーメータの値が安定するまで待機時間が必要なので，波長やパワーを変更した後には待機時間を設ける
    poslog =[]
    r = config.EXCITEPOWERPIDNORMALIZATION / (targetpower * 1000)
    Kp = config.EXCITEPOWERPIDKP * r
    Ki = config.EXCITEPOWERPIDKI * r
    Kd = config.EXCITEPOWERPIDKD * r
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
    if abs(prev_ndpos - NDfilter.get_position()) > 1.0e5:
        time.sleep(3) #NDフィルターの位置が大きく変わった場合は，安定するまで長めに待機時間を設ける
    time.sleep(2)#最初の熱緩和待機時間.初回はやや長めに待つ
    # PID制御first
    logger.log("PID power control fist start")
    for i in range(max_retry):
        logger.log(f"first {i}th retry of PID power control")
        time.sleep(2)#毎回の熱緩和待機時間.3A-FSの公称応答時間は1.8sである．
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
        warnings.warn("cant choone power")
        return poslog, False
    
    # PID制御second
    for i in range(max_retry):
        logger.log(f"second {i}th retry of PID power control")
        time.sleep(3)#毎回の熱緩和待機時間.3A-FSの公称応答時間は1.8sである．2nd resolverでは長めに待機時間を設けている
        nowndstep = NDfilter.get_position()
        measuredpower = powermeter.get_latestdata()
        nowpower = measuredpower * func.ndstep2ratio(nowndstep)
        logger.log(f"measured power: {measuredpower}")
        logger.log(f"predicted current power: {nowpower}")
        logger.log(f"now step: {nowndstep}")

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
            logger.log("Already at target power")
            return poslog, True
    # max_retry回繰り返しても目標パワーに到達しなかった場合
    logger.log(f"Failed to control power by {max_retry} times")
    logger.log(f"current power: {nowpower}")
    logger.log(f"current ND filter position: {nowndstep}")
    return poslog, False

def pid_control_wavelength(targetwavelength:int, TiSap_actuator:zaber_linear_actuator, spectrometer:thorlabspectrometer, logger:Logger, eps:float = 0.2, max_retry:int = 40) -> Tuple[List, bool]:
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
    Kp = config.EXCITEWAVELENGTHPIDKP
    Ki = config.EXCITEWAVELENGTHPIDKI
    Kd = config.EXCITEWAVELENGTHPIDKD
    dt = 1.0
    acc = 0.0
    diff = 0.0
    prev = 0.0
    poslog = []

    logger.log(f"wavelength control start for {targetwavelength}nm")
    TiSap_actuator.move_to(func.wavelength2tisp_pos(targetwavelength)) # 事前に取得したリニアアクチュエータ位置と波長の関係から一次関数の関係にあることがわかっている(tisp.ipynbにフィッティング結果がある)．このフィッティング式から目標波長に対応するアクチュエータ位置を計算して移動する.この処理はフィードバック制御ではない

    # ここからPID制御
    for i in range(max_retry):
        time.sleep(0.05)  # 分光器やアクチュエータが落ち着くまで若干待つ
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

def autofocus(objective_lens:Focus_adjuster, symphony:Symphony, savedirpath:str, exposuretime:int, logger:Logger, range_dense_search:int = 200, range_sparse_search:int|None = None) -> int:
    '''
    symphonyで検出したSiのPLピークをもとにオートフォーカスを行う関数
    args:
        objective_lens(Focus_adjuster): フォーカス調整用の自作ドライバークラス
        symphony(Symphony): Symphonyカメラの自作ドライバークラス
        savedirpath(str): データを保存するディレクトリのパス
        exposuretime(int): 露光時間[s]
        logger(Logger): 自作ロガークラス
        range_dense_search(int): 密なサーチ範囲[internal steps]。目標位置から±range_dense_searchの範囲でサーチを行う. range_dense_search = 200の場合は±200 internal steps = 50umの範囲でサーチを行う
        range_sparse_search(int|None): 疎なサーチ範囲[internal steps]。目標位置から±range_sparse_searchの範囲でサーチを行う。Noneの場合は疎なサーチは行わない range_sparse_search = 400の場合は±400 internal steps = 100umの範囲でサーチを行う
    return:
        optimal(int): 最適なフォーカス位置[internal steps]。1step = 0.25um
    '''
    start_time = time.time()
    symphony.set_exposuretime(exposuretime)
    symphony.set_config_savetofiles(savedirpath)
    center_dense_search = objective_lens.position
    # sparse search
    if range_sparse_search:
        logger.log("sparse serch start")
        logger.log(f"pos before search:{objective_lens.position}")
        maxvl = 0
        maxpos = 0
        for pos in range(objective_lens.position - range_sparse_search, objective_lens.position + range_sparse_search + 100, 100):
            objective_lens.set_rpm(20)
            objective_lens.move_to(pos)
            symphony.start_exposure(block=True)
            os.rename(os.path.join(savedirpath, "IMAGE0001_0001_AREA1_1.txt"), os.path.join(savedirpath, f"sparse_{pos}.txt"))
            df = pd.read_csv(os.path.join(savedirpath, f"sparse_{pos}.txt"), sep='\t', comment='#', header=None)
            value = df[1].max()
            logger.log(f"now pos:{pos}, value of Si PL:{value}")
            if value > maxvl:
                maxpos = pos
                maxvl = value
        logger.log(f"max pos(center dense search):{maxpos}, value of Si PL:{maxvl}")      
        center_dense_search = maxpos
    # dense search
    logger.log("dense search start")
    min_ol = -1 * range_dense_search + center_dense_search
    max_ol = range_dense_search + center_dense_search
    iter_ol = 0
    while max_ol - min_ol > 5:
        if iter_ol % 3 == 0:
            objective_lens.set_rpm(objective_lens._clamp(int((max_ol - min_ol)/7), 2, 20))
        iter_ol += 1

        mid1_ol = min_ol + (max_ol - min_ol) / 3
        mid2_ol = max_ol - (max_ol - min_ol) / 3

        objective_lens.move_to(mid1_ol)
        symphony.start_exposure(block=True)
        os.rename(os.path.join(savedirpath, "IMAGE0001_0001_AREA1_1.txt"), os.path.join(savedirpath, f"dense_{mid1_ol}.txt"))
        df = pd.read_csv(os.path.join(savedirpath, f"dense_{mid1_ol}.txt"), sep='\t', comment='#', header=None)
        value1_ol = df[1].max()
        logger.log(f"now pos:{mid1_ol}, value of Si PL:{value1_ol}")

        objective_lens.move_to(mid2_ol)
        symphony.start_exposure(block=True)
        os.rename(os.path.join(savedirpath, "IMAGE0001_0001_AREA1_1.txt"), os.path.join(savedirpath, f"dense_{mid2_ol}.txt"))
        df = pd.read_csv(os.path.join(savedirpath, f"dense_{mid2_ol}.txt"), sep='\t', comment='#', header=None)
        value2_ol = df[1].max()
        logger.log(f"now pos:{mid2_ol}, value of Si PL:{value2_ol}")

        if value1_ol < value2_ol:
            min_ol = mid1_ol
        else:
            max_ol = mid2_ol
    optimal = int((min_ol + max_ol) / 2)
    objective_lens.move_to(optimal)
    logger.log(f"autofocus at {optimal}")
    logger.log(f"autofocus take {time.time()- start_time}sec")
    return optimal

class Single_Ple_Measurement():
    def __init__(self) -> None:
        self.reset()
    
    def reset(self) -> None:
        self.flipshut = None
        self.shut = None
        self.mypowerdict = None 
        self.NDfilter = None
        self.powermeter = None
        self.symphony = None
        self.tisp_linear_actuator = None
        self.spectrometer = None
        self.logger = None

    def single_ple(self, targetpower:float, minwavelength:int, maxwavelength:int, stepwavelength:int, background:bool, exposuretime:int, path:str, logger:Logger) -> None:
        '''
        PLEスペクトルを取得する関数
        args:
            targetpower(float): 目標パワー[W]
            minwavelength(int): 最小励起中心波長[nm]
            maxwavelength(int): 最大励起中心波長[nm]
            stepwavelength(int): 中心励起波長のステップ[nm]
            background(bool): バックグラウンドを都度取得するかどうか
            wavelengthwidth(int): 励起波長の幅[nm]
            exposuretime(int): 露光時間[s]
            path(str): データを保存するディレクトリのパス
        return:
            None
        '''
        self.targetpower = targetpower
        self.minwavelength = minwavelength
        self.maxwavelength = maxwavelength
        self.stepwavelength = stepwavelength
        self.background = background
        self.exposuretime = exposuretime
        self.path = path
        self.logger = logger

        self.logger.log("Experiment started at " + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
        self.logger.log("Experiment Condition")
        self.logger.log(f"targetpower:{targetpower}")
        self.logger.log(f"minimum excite center wavelength:{minwavelength}")
        self.logger.log(f"maximum excite center wavelength:{maxwavelength}")
        self.logger.log(f"excite center wavelength step:{stepwavelength}")
        self.logger.log(f"exposure time:{exposuretime}")
        self.wavelengthlist = np.arange(minwavelength, maxwavelength + stepwavelength, stepwavelength)
        self.logger.log("")
        self.logger.log("excited wavelength list")
        for wavelength in self.wavelengthlist:
            self.logger.log(str(wavelength))
        self.logger.log("")

        if not os.path.exists(self.path):
            os.makedirs(self.path)
            self.logger.log(f"make dir at {self.path}")

        if self.flipshut is None:
            self.flipshut = FlipMount()
        self.flipshut.close()
        self.logger.log("flipshut is closed")

        if self.shut is None:
            self.shut = shutter(config.SHUTTERCOMPORT)
        self.shut.close(2)
        self.logger.log("shutter is closed")

        self.mypowerdict = PowerDict()

        if self.NDfilter is None:
            self.NDfilter = ThorlabStage(home=True)
        self.NDfilter.move_to(0, block=True)
        self.logger.log(f"stage is at {self.NDfilter.get_position()}")

        self.flipshut.open()
        self.logger.log("flipshut is opened")

        if self.powermeter is None:
            self.powermeter = juno()
        self.powermeter.open()
        self.powermeter.set_range(0)
        self.logger.log("powermeter is opened")

        if self.symphony is None:
            self.symphony = Symphony()
        self.symphony.Initialize()
        self.symphony.set_exposuretime(exposuretime)
        self.symphony.set_config_savetofiles(self.path)
        self.logger.log("symphony is initialized")

        if self.tisp_linear_actuator is None:
            self.tisp_linear_actuator = zaber_linear_actuator()
        self.logger.log("TiSap actuator is initialized")

        if self.spectrometer is None:
            self.spectrometer = thorlabspectrometer()
        self.logger.log("spectrometer is initialized")

        for wavelength in self.wavelengthlist:
            self.logger.log(f"start wavelength control at {wavelength}")
            pid_control_wavelength(targetwavelength=wavelength, TiSap_actuator=self.tisp_linear_actuator, spectrometer=self.spectrometer, logger=logger)
            self.logger.log(f"start power control at {wavelength} for {targetpower}")
            pid_control_power(targetpower=targetpower, powermeter=self.powermeter, NDfilter=self.NDfilter, eps=targetpower*config.EPSRATIO, logger=logger, NDinitpos=self.mypowerdict.get_nearest(wavelength, targetpower))
            self.mypowerdict.add(wavelength, targetpower, self.NDfilter.get_position())
            self.logger.log(f"start to get PL spectra at {wavelength}nm")
            self.shut.open(2)
            self.symphony.start_exposure(block=True)
            self.shut.close(2)
            os.rename(os.path.join(self.path, "IMAGE0001_0001_AREA1_1.txt"), os.path.join(self.path, f"{wavelength}.txt"))
            self.logger.log(f"PL spectra at {wavelength}nm is saved")

            if background:
                self.logger.log(f"start to get background spectra at {wavelength}nm")
                self.shut.close(2)
                self.symphony.start_exposure(block=True)
                os.rename(os.path.join(self.path, "IMAGE0001_0001_AREA1_1.txt"), os.path.join(self.path, f"background_{wavelength}.txt"))
                self.logger.log(f"background spectra at {wavelength}nm is saved")

        self.shut.close(2)
        self.flipshut.close()
        self.logger.log("Experiment finished at " + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))


class Scan_PLE_Measurement():
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.flipshut = None
        self.shut = None
        self.mypowerdict = None
        self.NDfilter = None
        self.powermeter = None
        self.symphony = None
        self.priorstage = None
        self.tisp_linear_actuator = None
        self.spectrometer = None

    def scan_ple(self, targetpower:float, minwavelength:int, maxwavelength:int, stepwavelength:int, exposuretime:int, path:str, startpos:tuple, endpos:tuple, numberofsteps:int, check_autofocus:bool, sweep:bool, logger:Logger) -> None:
        '''
        args:
            targetpower(float): 目標パワー[W]
            minwavelength(int): 最小励起中心波長[nm]
            maxwavelength(int): 最大励起中心波長[nm]
            stepwavelength(int): 中心励起波長のステップ[nm]
            exposuretime(int): 露光時間[s]
            path(str): データを保存するディレクトリのパス
            startpos(tuple): 移動開始位置[x,y]
            endpos(tuple): 移動終了位置[x,y]
            numberofsteps(int): 移動ステップ数
        return:
            None
        '''
        self.poslist =[np.linspace(startpos[0], endpos[0], numberofsteps), np.linspace(startpos[1], endpos[1], numberofsteps)]
        self.poslist = list(self.poslist)
        self.poslist = [[int(x) for x in y] for y in self.poslist]

        self.slit_vector = np.array([endpos[0]-startpos[0], endpos[1]-startpos[1]])
        self.slit_1um_vector = self.slit_vector / np.linalg.norm(self.slit_vector) * 100
        self.slit_10um_vector = self.slit_1um_vector * 10

        self.slit_orthogonal_vector = np.array([-self.slit_vector[1], self.slit_vector[0]])
        self.slit_orthogonal_1um_vector = self.slit_orthogonal_vector / np.linalg.norm(self.slit_orthogonal_vector) * 100
        self.slit_orthogonal_10um_vector = self.slit_orthogonal_1um_vector * 10

        self.logger = logger

        self.logger.log("Experiment started at " + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
        self.logger.log("Experiment Condition")
        self.logger.log(f"targetpower:{targetpower}")
        self.logger.log(f"minimum excite center wavelength:{minwavelength}")
        self.logger.log(f"maximum excite center wavelength:{maxwavelength}")
        self.logger.log(f"excite center wavelength step:{stepwavelength}")
        self.logger.log(f"exposure time:{exposuretime}")
        self.logger.log(f"sweep is {sweep}")

        self.wavelengthlist = np.arange(minwavelength, maxwavelength + stepwavelength, stepwavelength)
        self.logger.log("")
        self.logger.log("wave length list")
        for wavelength in self.wavelengthlist:
            logger.log(str(wavelength))
        self.logger.log("")
        self.logger.log(f"start position:{startpos}")
        self.logger.log(f"end position:{endpos}")
        self.logger.log(f"number of steps:{numberofsteps}")
        self.logger.log(f"position interval:{np.linalg.norm(self.slit_vector)/(numberofsteps-1)}" if numberofsteps > 1 else "position interval:0")
        self.logger.log("")
        for i in range(numberofsteps):
            self.logger.log(f"position {i}:{self.poslist[0][i], self.poslist[1][i]}")
        self.logger.log("")

        if not os.path.exists(path):
            os.makedirs(path)
            self.logger.log(f"make dir at {path}")

        if self.flipshut is None:
            self.flipshut = FlipMount()
        self.flipshut.close()
        self.logger.log("flipshut is closed")

        if self.shut is None:
            self.shut = shutter(config.SHUTTERCOMPORT)
        self.shut.close(2)
        self.logger.log("shutter is closed")

        self.mypowerdict = PowerDict()

        if self.NDfilter is None:
            self.NDfilter = ThorlabStage(home=True)
        self.NDfilter.move_to(0, block=True)
        self.logger.log(f"stage is at {self.NDfilter.get_position()}")

        self.flipshut.open()
        self.logger.log("flipshut is opened")

        self.powermeter = juno()
        self.powermeter.open()
        self.powermeter.set_range(0)
        self.logger.log("powermeter is opened")

        self.symphony = Symphony()
        self.symphony.Initialize()
        self.symphony.set_exposuretime(exposuretime)
        self.symphony.set_config_savetofiles(path)
        self.logger.log("symphony is initialized")

        self.priorstage = Proscan(config.PRIORCOMPORT)
        self.logger.log("priorstage is initialized")

        self.tisp_linear_actuator = zaber_linear_actuator()
        self.logger.log("TiSap actuator is initialized")

        self.spectrometer = thorlabspectrometer()
        self.logger.log("spectrometer is initialized")

        if check_autofocus:
            self.logger.log("setting up for autofocus")
            self.logger.log("wave length is moving to 750nm")
            pid_control_wavelength(targetwavelength=750, TiSap_actuator=self.tisp_linear_actuator, spectrometer=self.spectrometer, logger=logger)
            self.logger.log("power is moving to 0.001W")
            pid_control_power(targetpower=0.003, powermeter=self.powermeter, NDfilter=self.NDfilter, eps=targetpower*config.EPSRATIO, logger=logger)
            self.mypowerdict.add(750, 0.003, self.NDfilter.get_position())

            self.objective_lens = Focus_adjuster(config.AUTOFOCUSCOMPORT)
            self.logger.log("arduino is initialized")

            autofocuslog_startpos_path = os.path.join(path, "autofocus_log_startpos")
            if not os.path.exists(autofocuslog_startpos_path):
                os.makedirs(autofocuslog_startpos_path)
            self.logger.log("start autofocus at start position")
            self.logger.log(f"auto focus log is saved at {autofocuslog_startpos_path}")
            self.logger.log(f"stage is moving to {startpos - self.slit_10um_vector + self.slit_orthogonal_10um_vector}")
            self.priorstage.move_to(*(startpos - self.slit_10um_vector + self.slit_orthogonal_10um_vector))
            self.shut.open(2)
            self.start_height = autofocus(objective_lens=self.objective_lens, symphony=self.symphony, savedirpath=autofocuslog_startpos_path, exposuretime=3, logger=logger, range_dense_search=100, range_sparse_search=400)
            self.shut.close(2)

            autofocuslog_endpos_path = os.path.join(path, "autofocus_log_endpos")
            if not os.path.exists(autofocuslog_endpos_path):
                os.makedirs(autofocuslog_endpos_path)
            logger.log("start autofocus at end position")
            logger.log(f"auto focus log is saved at {autofocuslog_endpos_path}")
            logger.log(f"stage is moving to {endpos + self.slit_10um_vector + self.slit_orthogonal_10um_vector}")
            self.priorstage.move_to(*(endpos + self.slit_10um_vector + self.slit_orthogonal_10um_vector))
            self.shut.open(2)
            self.end_height = autofocus(objective_lens=self.objective_lens, symphony=self.symphony, savedirpath=autofocuslog_endpos_path, exposuretime=3, logger=logger, range_dense_search=100, range_sparse_search=400)
            self.shut.close(2)

            self.height_func = func.make_linear_from_two_points(0, self.start_height, numberofsteps-1, self.end_height)
            self.symphony.set_exposuretime(exposuretime)


        for posidx in range(numberofsteps):
            nowposx = self.poslist[0][posidx]
            nowposy = self.poslist[1][posidx]
            logger.log(f"stage is moving to {posidx}:{nowposx, nowposy}")
            self.priorstage.move_to(nowposx, nowposy)

            savedirpath = os.path.join(path, f"pos{posidx}_x{nowposx}_y{nowposy}")
            if not os.path.exists(savedirpath):
                os.makedirs(savedirpath)
                self.logger.log(f"make dir at {savedirpath}")
            self.symphony.set_config_savetofiles(savedirpath)

            if check_autofocus:
                self.logger.log(f"obejctive lens is moving to {self.height_func(posidx)}")
                self.objective_lens.move_to(self.height_func(posidx))

            for wavelength in self.wavelengthlist:
                logger.log(f"start wavelength control at {wavelength}")
                pid_control_wavelength(targetwavelength=wavelength, TiSap_actuator=self.tisp_linear_actuator, spectrometer=self.spectrometer, logger=logger)
                logger.log(f"start power control at {wavelength} for {targetpower}")
                pid_control_power(targetpower=targetpower, powermeter=self.powermeter, NDfilter=self.NDfilter, eps=targetpower*config.EPSRATIO, logger=logger, NDinitpos=self.mypowerdict.get_nearest(wavelength, targetpower))
                self.mypowerdict.add(wavelength, targetpower, self.NDfilter.get_position())
                self.logger.log(f"start to get PL spectra at {wavelength}")
                self.shut.open(2)
                if sweep:
                    pos1 = [nowposx, nowposy] - self.slit_orthogonal_1um_vector
                    pos1 = [int(x) for x in pos1]
                    pos2 = [nowposx, nowposy] + self.slit_orthogonal_1um_vector
                    pos2 = [int(x) for x in pos2]
                    comeandgothread = threading.Thread(target=self.comeandgo, args=(pos1, pos2, exposuretime), daemon=True)#計測地点の前後1umを往復しながら計測
                    comeandgothread.start()
                self.symphony.start_exposure(block=True)
                if sweep:
                    comeandgothread.join()
                self.shut.close(2)
                os.rename(os.path.join(savedirpath, "IMAGE0001_0001_AREA1_1.txt"), os.path.join(savedirpath, f"{wavelength}.txt"))
        self.shut.close(2)
        self.flipshut.close()

        self.logger.log("Experiment finished at " + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

    def comeandgo(self, pos1:tuple, pos2:tuple, comeandgotime:float) -> None:
        '''
        指定した時間かそれよりも長い時間だけ指定した位置を往復する関数
        args:
            pos1(tuple): 往復する位置1[x,y]
            pos2(tuple): 往復する位置2[x,y]
            exposuretime(float): 露光時間[s]
        return:
            None
        '''
        starttime = time.time()
        while True:
            nowtime = time.time()
            if nowtime - starttime >= comeandgotime:
                return
            self.priorstage.move_to(pos1[0], pos1[1])

            nowtime = time.time()
            if nowtime - starttime >= comeandgotime:
                return
            self.priorstage.move_to(pos2[0], pos2[1])

class dev_Scan_PLE_Measurement():
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.flipshut = None
        self.shut = None
        self.mypowerdict = None
        self.NDfilter = None
        self.powermeter = None
        self.symphony = None
        self.priorstage = None
        self.tisp_linear_actuator = None
        self.spectrometer = None

    def scan_ple(self, targetpower:float, minwavelength:int, maxwavelength:int, stepwavelength:int, searchwavelength:int, exposuretime:int, path:str, startpos:tuple, endpos:tuple, numberofsteps:int, check_autofocus:bool, sweep:bool, logger:Logger) -> None:
        '''
        args:
            targetpower(float): 目標パワー[W]
            minwavelength(int): 最小励起中心波長[nm]
            maxwavelength(int): 最大励起中心波長[nm]
            stepwavelength(int): 中心励起波長のステップ[nm]
            searchwavelength(int): 探索波長[nm]
            exposuretime(int): 露光時間[s]
            path(str): データを保存するディレクトリのパス
            startpos(tuple): 移動開始位置[x,y]
            endpos(tuple): 移動終了位置[x,y]
            numberofsteps(int): 移動ステップ数
        return:
            None
        '''
        self.prev_spectra = None
        self.prev_prev_spectra = None

        self.ple_poslist = []

        self.poslist =[np.linspace(startpos[0], endpos[0], numberofsteps), np.linspace(startpos[1], endpos[1], numberofsteps)]
        self.poslist = list(self.poslist)
        self.poslist = [[int(x) for x in y] for y in self.poslist]

        self.slit_vector = np.array([endpos[0]-startpos[0], endpos[1]-startpos[1]])
        self.slit_1um_vector = self.slit_vector / np.linalg.norm(self.slit_vector) * 100
        self.slit_10um_vector = self.slit_1um_vector * 10

        self.slit_orthogonal_vector = np.array([-self.slit_vector[1], self.slit_vector[0]])
        self.slit_orthogonal_1um_vector = self.slit_orthogonal_vector / np.linalg.norm(self.slit_orthogonal_vector) * 100
        self.slit_orthogonal_10um_vector = self.slit_orthogonal_1um_vector * 10

        self.logger = logger

        self.logger.log("Experiment started at " + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
        self.logger.log("Experiment Condition")
        self.logger.log(f"exposure time:{exposuretime}")
        self.logger.log(f"sweep is {sweep}")
        self.logger.log(f"targetpower:{targetpower}")
        self.logger.log(f"search wavelength:{searchwavelength}")

        self.logger.log(f"minimum excite center wavelength:{minwavelength}")
        self.logger.log(f"maximum excite center wavelength:{maxwavelength}")
        self.logger.log(f"excite center wavelength step:{stepwavelength}")
        self.wavelengthlist = np.arange(minwavelength, maxwavelength + stepwavelength, stepwavelength)
        self.logger.log("")
        self.logger.log("wave length list")
        for wavelength in self.wavelengthlist:
            logger.log(str(wavelength))
        self.logger.log("")
        self.logger.log(f"start position:{startpos}")
        self.logger.log(f"end position:{endpos}")
        self.logger.log(f"number of steps:{numberofsteps}")
        self.logger.log(f"position interval:{np.linalg.norm(self.slit_vector)/(numberofsteps-1)}" if numberofsteps > 1 else "position interval:0")
        self.logger.log("")
        for i in range(numberofsteps):
            self.logger.log(f"position {i}:{self.poslist[0][i], self.poslist[1][i]}")
        self.logger.log("")

        if not os.path.exists(path):
            os.makedirs(path)
            self.logger.log(f"make dir at {path}")

        if self.flipshut is None:
            self.flipshut = FlipMount()
        self.flipshut.close()
        self.logger.log("flipshut is closed")

        if self.shut is None:
            self.shut = shutter(config.SHUTTERCOMPORT)
        self.shut.close(2)
        self.logger.log("shutter is closed")

        self.mypowerdict = PowerDict()

        if self.NDfilter is None:
            self.NDfilter = ThorlabStage(home=True)
        self.NDfilter.move_to(0, block=True)
        self.logger.log(f"stage is at {self.NDfilter.get_position()}")

        self.flipshut.open()
        self.logger.log("flipshut is opened")

        self.powermeter = juno()
        self.powermeter.open()
        self.powermeter.set_range(0)
        self.logger.log("powermeter is opened")

        self.symphony = Symphony()
        self.symphony.Initialize()
        self.symphony.set_exposuretime(exposuretime)
        self.symphony.set_config_savetofiles(path)
        self.logger.log("symphony is initialized")

        self.priorstage = Proscan(config.PRIORCOMPORT)
        self.logger.log("priorstage is initialized")

        self.tisp_linear_actuator = zaber_linear_actuator()
        self.logger.log("TiSap actuator is initialized")

        self.spectrometer = thorlabspectrometer()
        self.logger.log("spectrometer is initialized")

        if check_autofocus:
            self.logger.log("setting up for autofocus")
            self.logger.log("wave length is moving to 750nm")
            pid_control_wavelength(targetwavelength=750, TiSap_actuator=self.tisp_linear_actuator, spectrometer=self.spectrometer, logger=logger)
            self.logger.log("power is moving to 0.001W")
            pid_control_power(targetpower=0.003, powermeter=self.powermeter, NDfilter=self.NDfilter, eps=targetpower*config.EPSRATIO, logger=logger)
            self.mypowerdict.add(750, 0.003, self.NDfilter.get_position())

            self.objective_lens = Focus_adjuster(config.AUTOFOCUSCOMPORT)
            self.logger.log("arduino is initialized")

            autofocuslog_startpos_path = os.path.join(path, "autofocus_log_startpos")
            if not os.path.exists(autofocuslog_startpos_path):
                os.makedirs(autofocuslog_startpos_path)
            self.logger.log("start autofocus at start position")
            self.logger.log(f"auto focus log is saved at {autofocuslog_startpos_path}")
            self.logger.log(f"stage is moving to {startpos - self.slit_10um_vector + self.slit_orthogonal_10um_vector}")
            self.priorstage.move_to(*(startpos - self.slit_10um_vector + self.slit_orthogonal_10um_vector))
            self.shut.open(2)
            self.start_height = autofocus(objective_lens=self.objective_lens, symphony=self.symphony, savedirpath=autofocuslog_startpos_path, exposuretime=3, logger=logger, range_dense_search=100, range_sparse_search=400)
            self.shut.close(2)

            autofocuslog_endpos_path = os.path.join(path, "autofocus_log_endpos")
            if not os.path.exists(autofocuslog_endpos_path):
                os.makedirs(autofocuslog_endpos_path)
            logger.log("start autofocus at end position")
            self.logger.log(f"auto focus log is saved at {autofocuslog_endpos_path}")
            logger.log(f"stage is moving to {endpos + self.slit_10um_vector + self.slit_orthogonal_10um_vector}")
            self.priorstage.move_to(*(endpos + self.slit_10um_vector + self.slit_orthogonal_10um_vector))
            self.shut.open(2)
            self.end_height = autofocus(objective_lens=self.objective_lens, symphony=self.symphony, savedirpath=autofocuslog_endpos_path, exposuretime=3, logger=logger, range_dense_search=100, range_sparse_search=400)
            self.shut.close(2)

            self.height_func = func.make_linear_from_two_points(0, self.start_height, numberofsteps-1, self.end_height)
            self.symphony.set_exposuretime(exposuretime)


        for posidx in range(numberofsteps):
            nowposx = self.poslist[0][posidx]
            nowposy = self.poslist[1][posidx]
            logger.log(f"stage is moving to {posidx}:{nowposx, nowposy}")
            self.priorstage.move_to(nowposx, nowposy)

            savedirpath = os.path.join(path, f"pos{posidx}_x{nowposx}_y{nowposy}")
            if not os.path.exists(savedirpath):
                os.makedirs(savedirpath)
                self.logger.log(f"make dir at {savedirpath}")
            self.symphony.set_config_savetofiles(savedirpath)

            if check_autofocus:
                self.logger.log(f"obejctive lens is moving to {self.height_func(posidx)}")
                self.objective_lens.move_to(self.height_func(posidx))

            logger.log(f"start wavelength control at {searchwavelength}")
            pid_control_wavelength(targetwavelength=searchwavelength, TiSap_actuator=self.tisp_linear_actuator, spectrometer=self.spectrometer, logger=logger)
            logger.log(f"start power control at {searchwavelength} for {targetpower}")
            pid_control_power(targetpower=targetpower, powermeter=self.powermeter, NDfilter=self.NDfilter, eps=targetpower*config.EPSRATIO, logger=logger, NDinitpos=self.mypowerdict.get_nearest(searchwavelength, targetpower))
            self.mypowerdict.add(searchwavelength, targetpower, self.NDfilter.get_position())
            self.logger.log(f"start to get PL spectra at {searchwavelength}")
            self.shut.open(2)
            if sweep:
                pos1 = [nowposx, nowposy] - self.slit_orthogonal_1um_vector
                pos1 = [int(x) for x in pos1]
                pos2 = [nowposx, nowposy] + self.slit_orthogonal_1um_vector
                pos2 = [int(x) for x in pos2]
                comeandgothread = threading.Thread(target=self.comeandgo, args=(pos1, pos2, exposuretime), daemon=True)#計測地点の前後1umを往復しながら計測
                comeandgothread.start()
            self.symphony.start_exposure(block=True)
            if sweep:
                comeandgothread.join()
            self.shut.close(2)
            os.rename(os.path.join(savedirpath, "IMAGE0001_0001_AREA1_1.txt"), os.path.join(savedirpath, f"{searchwavelength}.txt"))

            df = pd.read_csv(os.path.join(savedirpath, f"{searchwavelength}.txt"), comment='#', header=None, sep=None, engine='python')
            self.now_spectra = df[1].to_numpy()
            if self.prev_spectra is not None and self.prev_prev_spectra is not None and self.now_spectra is not None:# 直前2回のスペクトルが取得されている場合（=最初の二回以外）に直前2回のスペクトルの平均と今回のスペクトルの平均の差を計算
                avg_now_spectra = np.mean(self.now_spectra[:300])
                avg_prev_spectra = np.mean(self.prev_spectra[:300])
                avg_prev_prev_spectra = np.mean(self.prev_prev_spectra[:300])
                diff_now2prev = np.abs(avg_now_spectra - ((avg_prev_spectra + avg_prev_prev_spectra) / 2))

                if diff_now2prev > 50:# 直前2回のスペクトルの平均との差が大きい場合
                    logger.log(f"SWCNT like spectra detected at{nowposx, nowposy}")
                    self.ple_poslist.append([nowposx, nowposy])
                    logger.log(f"diff_now2prev:{diff_now2prev}")
                    logger.log("start to get PLE spectra")

                    for wavelength in self.wavelengthlist:
                        logger.log(f"start wavelength control at {wavelength}")
                        pid_control_wavelength(targetwavelength=wavelength, TiSap_actuator=self.tisp_linear_actuator, spectrometer=self.spectrometer, logger=logger)
                        logger.log(f"start power control at {wavelength} for {targetpower}")
                        pid_control_power(targetpower=targetpower, powermeter=self.powermeter, NDfilter=self.NDfilter, eps=targetpower*config.EPSRATIO, logger=logger, NDinitpos=self.mypowerdict.get_nearest(wavelength, targetpower))
                        self.mypowerdict.add(wavelength, targetpower, self.NDfilter.get_position())
                        self.logger.log(f"start to get PL spectra at {wavelength}")
                        self.shut.open(2)
                        if sweep:
                            comeandgothread = threading.Thread(target=self.comeandgo, args=(pos1, pos2, exposuretime), daemon=True)#計測地点の前後1umを往復しながら計測
                            comeandgothread.start()
                        self.symphony.start_exposure(block=True)
                        if sweep:
                            comeandgothread.join()
                        self.shut.close(2)
                        os.rename(os.path.join(savedirpath, "IMAGE0001_0001_AREA1_1.txt"), os.path.join(savedirpath, f"{wavelength}.txt"))#最初に取得したスペクトルを上書きする可能性があるので注意
            self.prev_prev_spectra = self.prev_spectra
            self.prev_spectra = self.now_spectra
        self.shut.close(2)
        self.flipshut.close()

        self.logger.log("Experiment finished at " + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
        self.logger.log("ple position list")
        for pos in self.ple_poslist:
            self.logger.log(pos)

    def comeandgo(self, pos1:tuple, pos2:tuple, exposuretime:float) -> None:
        '''
        2点間を往復しながら露光する関数
        '''
        starttime = time.time()
        while True:
            nowtime = time.time()
            if nowtime - starttime >= exposuretime:
                break

            self.priorstage.move_to(pos1[0], pos1[1])

            nowtime = time.time()
            if nowtime - starttime >= exposuretime:
                break

            self.priorstage.move_to(pos2[0], pos2[1])


class dev_Scan_image_Measurement():
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.flipshut = None
        self.shut = None
        self.mypowerdict = None
        self.NDfilter = None
        self.powermeter = None
        self.priorstage = None
        self.tisp_linear_actuator = None
        self.spectrometer = None
        self.camera = None

    def scan_image(self, targetpower:float, wavelength:int, experimentname:str, exposuretime:int, path:str, startpos:tuple, endpos:tuple, numberofsteps:int, startzpos:int, endzpos:int, focusadjuster:Focus_adjuster, logger:Logger) -> None:
        '''
        args:
            power(float): 目標パワー[W]
            wavelength(int): 中心励起波長[nm]
            experimentname(str): Light Fieldで読み込む実験名
            exposuretime(int): 露光時間[s]
            path(str): データを保存するディレクトリのパス
            startpos(tuple): 移動開始位置[x,y]
            endpos(tuple): 移動終了位置[x,y]
            numberofsteps(int): 移動ステップ数
            startzpos(int): z軸の移動開始位置
            endzpos(int): z軸の移動終了位置
            focusadjuster(Focus_adjuster): フォーカス調整用のオブジェクト
            logger(Logger): ロガーオブジェクト
        return:
            None
        '''
        self.poslist =[np.linspace(startpos[0], endpos[0], numberofsteps), np.linspace(startpos[1], endpos[1], numberofsteps)]
        self.poslist = list(self.poslist)
        self.poslist = [[int(x) for x in y] for y in self.poslist]

        self.slit_vector = np.array([endpos[0]-startpos[0], endpos[1]-startpos[1]])
        self.slit_1um_vector = self.slit_vector / np.linalg.norm(self.slit_vector) * 100
        self.slit_10um_vector = self.slit_1um_vector * 10

        self.slit_orthogonal_vector = np.array([-self.slit_vector[1], self.slit_vector[0]])
        self.slit_orthogonal_1um_vector = self.slit_orthogonal_vector / np.linalg.norm(self.slit_orthogonal_vector) * 100
        self.slit_orthogonal_10um_vector = self.slit_orthogonal_1um_vector * 10

        self.height_func = func.make_linear_from_two_points(0, startzpos, numberofsteps-1, endzpos)

        self.logger = logger
        self.logger.log("Experiment started at " + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
        self.logger.log("Experiment Condition")
        self.logger.log(f"targetpower:{targetpower}")
        self.logger.log(f"wavelength:{wavelength}")
        self.logger.log(f"exposure time:{exposuretime}")
        self.logger.log(f"start position:{startpos}")
        self.logger.log(f"end position:{endpos}")
        self.logger.log(f"number of steps:{numberofsteps}")
        self.logger.log(f"position interval:{np.linalg.norm(self.slit_vector)/(numberofsteps-1)}" if numberofsteps > 1 else "position interval:0")
        self.logger.log(f"start z position:{startzpos}")
        self.logger.log(f"end z position:{endzpos}")
        self.logger.log("")
        self.logger.log("position list")
        self.logger.log("index, x, y, distance")
        for i in range(numberofsteps):
            self.logger.log(f"{i}, {self.poslist[0][i]}, {self.poslist[1][i]}, {np.linalg.norm(np.array([self.poslist[0][i], self.poslist[1][i]]) - np.array(startpos)) / 100}")
        self.logger.log("")

        if not os.path.exists(path):
            os.makedirs(path)
            self.logger.log(f"make dir at {path}")

        if self.flipshut is None:
            self.flipshut = FlipMount()
        self.flipshut.close()
        self.logger.log("flipshut is closed")

        if self.shut is None:
            self.shut = shutter(config.SHUTTERCOMPORT)
        self.shut.close(2)
        self.logger.log("shutter is closed")
        self.mypowerdict = PowerDict()

        if self.NDfilter is None:
            self.NDfilter = ThorlabStage(home=True)
        self.NDfilter.move_to(0, block=True)
        self.logger.log(f"stage is at {self.NDfilter.get_position()}")

        self.powermeter = juno()
        self.powermeter.open()
        self.powermeter.set_range(0)
        self.logger.log("powermeter is opened")

        self.priorstage = Proscan(config.PRIORCOMPORT)
        self.logger.log("priorstage is initialized")

        self.tisp_linear_actuator = zaber_linear_actuator()
        self.logger.log("TiSap actuator is initialized")

        self.spectrometer = thorlabspectrometer()
        self.logger.log("spectrometer is initialized")

        self.camera = PrincetonCamera()
        self.camera.experiment.Load(experimentname)
        self.camera.online_export(enabled=True)
        self.camera.folder_path = path
        self.logger.log("camera is initialized")
        self.logger.log(f"Loaded experiment: {experimentname}")
        if int(self.camera.exposure_time) != int(exposuretime):
            self.logger.log(f"camera exposure time and your exposure time is different. camera exposure time is {self.camera.exposure_time}ms")
        else:
            self.logger.log(f"camera exposure time and your exposure time is same. camera exposure time is {self.camera.exposure_time}ms")
        self.logger.log("camera temp:" + ("Locked" if self.camera.temperature_status else "Unlocked"))

        self.flipshut.open()
        self.logger.log("flipshut is opened")

        for posidx in range(numberofsteps):
            nowposx = self.poslist[0][posidx]
            nowposy = self.poslist[1][posidx]
            logger.log(f"stage is moving to {posidx}:{nowposx, nowposy}")
            self.priorstage.move_to(nowposx, nowposy)

            file_name = f"pos{posidx}_x{nowposx}_y{nowposy}_dist{np.linalg.norm(np.array([nowposx, nowposy]) - np.array(startpos)) / 100}_z{self.height_func(posidx)}"
            if os.path.exists(os.path.join(path, file_name)):
                os.remove(os.path.join(path, file_name))
            self.camera.file_name = file_name

            if focusadjuster is not None:
                self.logger.log(f"obejctive lens is moving to {self.height_func(posidx)}")
                focusadjuster.move_to(self.height_func(posidx))

            logger.log(f"start wavelength control at {wavelength}")
            pid_control_wavelength(targetwavelength=wavelength, TiSap_actuator=self.tisp_linear_actuator, spectrometer=self.spectrometer, logger=logger)
            logger.log(f"start power control at {wavelength} for {targetpower}")
            pid_control_power(targetpower=targetpower, powermeter=self.powermeter, NDfilter=self.NDfilter, eps=targetpower*config.EPSRATIO, logger=logger, NDinitpos=self.mypowerdict.get_nearest(wavelength, targetpower))
            self.mypowerdict.add(wavelength, targetpower, self.NDfilter.get_position())
            self.logger.log(f"start to get PL spectra at {wavelength}")
            self.shut.open(2)
            self.camera.acquire(block=True)
            self.shut.close(2)

        self.shut.close(2)
        self.flipshut.close()
        self.logger.log("Experiment finished at " + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
