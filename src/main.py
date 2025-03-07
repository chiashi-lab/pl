from driver.horiba import ihr320, Symphony
from driver.ophir import juno
from driver.prior import Proscan
from driver.sigmakoki import shutter
from driver.thorlab import ThorlabStage, FlipMount, thorlabspectrometer
from driver.focus_adjuster_driver import Focus_adjuster
from driver.zaber import zaber_linear_actuator
from logger import Logger
import config
from power_dict import PowerDict
import time
import datetime
import func
import numpy as np
import os
import pandas as pd
import warnings


def pid_control_power(targetpower:float, powermeter:juno, NDfilter:ThorlabStage, eps:float = 0.1, logger:Logger = None, max_retry:int = 40, NDinitpos:int = config.NDINITPOS) -> list:
    '''
    PID制御を用いて目標パワーに制御する関数
    args:
        targetpower(float): 目標パワー[W]
        wavelength(int): 現在の波長[nm]
        powermeter(juno): パワーメーターの自作ドライバークラス
        NDfilter(ThorlabStage): NDフィルターがついているthorlabステージの自作ドライバークラス
        eps(float): 目標パワーの許容誤差[W]
    return:
        None
    '''
    # パワーメータの値が安定するまで待機時間が必要なので，波長やパワーを変更した後には待機時間を設ける
    poslog =[]
    r = config.EXCITEPOWERPIDNORMALIZATION
    Kp = config.EXCITEPOWERPIDKP * r
    Ki = config.EXCITEPOWERPIDKI * r
    Kd = config.EXCITEPOWERPIDKD * r
    dt = 1.0
    acc = 0.0
    diff = 0.0
    prev = 0.0
    if NDinitpos != config.NDINITPOS:
        NDfilter.move_to(NDinitpos)
        poslog.append(NDinitpos)
    elif NDinitpos == config.NDINITPOS and NDfilter.get_position() < config.NDINITPOS:##ポジションが0に近いときは，透過率が高すぎてPID制御に時間がかかりすぎるので，透過率を下げる
        NDfilter.move_to(NDinitpos)
        poslog.append(NDinitpos)
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
            logger.log("move start")
            logger.log(f"error: {error}")
            logger.log(f"acc: {acc}")
            logger.log(f"diff: {diff}")
            logger.log(f"target step: {tostep}")
            NDfilter.move_to(tostep)
            poslog.append(tostep)
            logger.log("move end")
            logger.log(f"now step: {NDfilter.get_position()}\n")
            prev = error
        else:
            logger.log("first Already at target power")
            flag = True
            break
    
    if not flag:
        logger.log("cant choone power")
        warnings.warn("cant choone power")
        return
    
    # PID制御second
    for i in range(max_retry):
        logger.log(f"second {i}th retry of PID power control")
        time.sleep(3)
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
            logger.log("move start")
            logger.log(f"error: {error}")
            logger.log(f"acc: {acc}")
            logger.log(f"diff: {diff}")
            logger.log(f"target step: {tostep}")
            NDfilter.move_to(tostep)
            poslog.append(tostep)
            logger.log("move end")
            logger.log(f"now step: {NDfilter.get_position()}\n")
            prev = error
        else:
            logger.log("Already at target power")
            return poslog

def pid_control_wavelength(targetwavelength:int, TiSap_actuator:zaber_linear_actuator, spectrometer:thorlabspectrometer, logger:Logger, eps:float = 2.0, max_retry:int = 40) -> None:
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

    logger.log(f"wavelength control start for {targetwavelength}nm")
    TiSap_actuator.move_to((1268 - targetwavelength) / 22.7) # 事前に取得したリニアアクチュエータ位置と波長の関係から一次関数の関係にあることがわかっている(tisp.ipynbにフィッティング結果がある)．このフィッティング式から目標波長に対応するアクチュエータ位置を計算して移動する.この処理はフィードバック制御ではない

    # ここからPID制御
    for i in range(max_retry):
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
            logger.log("move start")
            logger.log(f"error: {error}")
            logger.log(f"acc: {acc}")
            logger.log(f"diff: {diff}")
            logger.log(f"target step: {tostep}")
            TiSap_actuator.move_to(tostep)
            prev = error
        else:#目標波長に到達したら終了
            logger.log("Already at target wavelength")
            return
    # max_retry回繰り返しても目標波長に到達しなかった場合
    logger.log(f"Failed to control wavelength by {max_retry} times")
    logger.log(f"current wavelength: {nowwavelength}")
    return

def single_ple(targetpower:float, minwavelength:int, maxwavelength:int, stepwavelength:int, integrationtime:int, path:str, logger:Logger) -> None:
    '''
    PLEスペクトルを取得する関数
    args:
        targetpower(float): 目標パワー[W]
        minwavelength(int): 最小励起中心波長[nm]
        maxwavelength(int): 最大励起中心波長[nm]
        stepwavelength(int): 中心励起波長のステップ[nm]
        wavelengthwidth(int): 励起波長の幅[nm]
        integrationtime(int): 露光時間[s]
        path(str): データを保存するディレクトリのパス
    return:
        None
    '''
    logger.log("Experiment started at " + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
    logger.log("Experiment Condition")
    logger.log(f"targetpower:{targetpower}")
    logger.log(f"minimum excite center wavelength:{minwavelength}")
    logger.log(f"maximum excite center wavelength:{maxwavelength}")
    logger.log(f"excite center wavelength step:{stepwavelength}")
    logger.log(f"integration time:{integrationtime}")
    wavelengthlist = np.arange(minwavelength, maxwavelength + stepwavelength, stepwavelength)
    logger.log("")
    logger.log("excited wavelength list")
    for wavelength in wavelengthlist:
        logger.log(str(wavelength))
    logger.log("")

    if not os.path.exists(path):
        os.makedirs(path)
        logger.log(f"make dir at {path}")

    flipshut = FlipMount()
    flipshut.close()
    logger.log("flipshut is closed")

    shut = shutter(config.SHUTTERCOMPORT)
    shut.close(2)
    logger.log("shutter is closed")

    mypowerdict = PowerDict()

    NDfilter = ThorlabStage(home=True)
    NDfilter.move_to(0, block=True)
    logger.log(f"stage is at {NDfilter.get_position()}")

    flipshut.open()
    logger.log("flipshut is opened")

    powermeter = juno()
    powermeter.open()
    powermeter.set_range(0)
    logger.log("powermeter is opened")

    symphony = Symphony()
    symphony.Initialize()
    symphony.set_exposuretime(integrationtime)
    symphony.set_config_savetofiles(path)
    logger.log("symphony is initialized")

    tisp_linear_actuator = zaber_linear_actuator()
    logger.log("TiSap actuator is initialized")

    spectrometer = thorlabspectrometer()
    logger.log("spectrometer is initialized")

    for wavelength in wavelengthlist:
        logger.log(f"start wavelength control at {wavelength}")
        pid_control_wavelength(targetwavelength=wavelength, TiSap_actuator=tisp_linear_actuator, spectrometer=spectrometer, logger=logger)
        logger.log(f"start power control at {wavelength} for {targetpower}")
        pid_control_power(targetpower=targetpower, powermeter=powermeter, NDfilter=NDfilter, eps=targetpower*config.EPSRATIO, logger=logger, NDinitpos=mypowerdict.get_nearest(wavelength, targetpower))
        mypowerdict.add(wavelength, targetpower, NDfilter.get_position())
        logger.log(f"start to get PL spectra at {wavelength}nm")
        shut.open(2)
        symphony.start_exposure()
        time.sleep(func.waittime4exposure(integrationtime))#sympnoyとの時刻ずれを考慮して，露光時間よりも長めに待つ
        shut.close(2)
        os.rename(os.path.join(path, "IMAGE0001_0001_AREA1_1.txt"), os.path.join(path, f"{wavelength}.txt"))
        logger.log(f"PL spectra at {wavelength}nm is saved")
    
    shut.close(2)
    flipshut.close()
    logger.log("Experiment finished at " + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

def autofocus(objective_lens:Focus_adjuster, symphony:Symphony, savedirpath:str, exposuretime:int, logger:Logger, range_dense_search:int = 200, range_sparse_search:int|None = None) -> int:
    start_time = time.time()
    symphony.set_exposuretime(exposuretime)
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
            symphony.start_exposure()
            time.sleep(func.waittime4exposure(exposuretime))
            df = pd.read_csv(os.path.join(savedirpath, "IMAGE0001_0001_AREA1_1.txt"), sep='\t', comment='#', header=None)
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
        symphony.start_exposure()
        time.sleep(func.waittime4exposure(exposuretime))
        df = pd.read_csv(os.path.join(savedirpath, "IMAGE0001_0001_AREA1_1.txt"), sep='\t', comment='#', header=None)
        value1_ol = df[1].max()
        logger.log(f"now pos:{mid1_ol}, value of Si PL:{value1_ol}")

        objective_lens.move_to(mid2_ol)
        symphony.start_exposure()
        time.sleep(func.waittime4exposure(exposuretime))
        df = pd.read_csv(os.path.join(savedirpath, "IMAGE0001_0001_AREA1_1.txt"), sep='\t', comment='#', header=None)
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

def scan_ple(targetpower:float, minwavelength:int, maxwavelength:int, stepwavelength:int, integrationtime:int, path:str, startpos:tuple, endpos:tuple, numberofsteps:int, check_autofocus:bool, sweep:bool, logger:Logger) -> None:
    '''
    args:
        targetpower(float): 目標パワー[W]
        minwavelength(int): 最小励起中心波長[nm]
        maxwavelength(int): 最大励起中心波長[nm]
        stepwavelength(int): 中心励起波長のステップ[nm]
        wavelengthwidth(int): 励起波長の幅[nm]
        integrationtime(int): 露光時間[s]
        path(str): データを保存するディレクトリのパス
        startpos(tuple): 移動開始位置[x,y]
        endpos(tuple): 移動終了位置[x,y]
        numberofsteps(int): 移動ステップ数
    return:
        None
    '''
    poslist =[np.linspace(startpos[0], endpos[0], numberofsteps), np.linspace(startpos[1], endpos[1], numberofsteps)]
    poslist = list(poslist)
    poslist = [[int(x) for x in y] for y in poslist]

    slit_vector = np.array([endpos[0]-startpos[0], endpos[1]-startpos[1]])
    slit_orthogonal_vector = np.array([-slit_vector[1], slit_vector[0]])
    movepos_when_focus = slit_orthogonal_vector / np.linalg.norm(slit_orthogonal_vector) * 10000

    logger.log("Experiment started at " + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
    logger.log("Experiment Condition")
    logger.log(f"targetpower:{targetpower}")
    logger.log(f"minimum excite center wavelength:{minwavelength}")
    logger.log(f"maximum excite center wavelength:{maxwavelength}")
    logger.log(f"excite center wavelength step:{stepwavelength}")
    logger.log(f"integration time:{integrationtime}")
    logger.log(f"sweep is {sweep}")

    wavelengthlist = np.arange(minwavelength, maxwavelength + stepwavelength, stepwavelength)
    logger.log("")
    logger.log("wave length list")
    for wavelength in wavelengthlist:
        logger.log(str(wavelength))
    logger.log("")
    logger.log(f"start position:{startpos}")
    logger.log(f"end position:{endpos}")
    logger.log(f"number of steps:{numberofsteps}")
    logger.log("")
    for i in range(numberofsteps):
        logger.log(f"position {i}:{poslist[0][i], poslist[1][i]}")
    logger.log("")

    if not os.path.exists(path):
        os.makedirs(path)
        logger.log(f"make dir at {path}")

    flipshut = FlipMount()
    flipshut.close()
    logger.log("flipshut is closed")

    shut = shutter(config.SHUTTERCOMPORT)
    shut.close(2)
    logger.log("shutter is closed")

    mypowerdict = PowerDict()

    NDfilter = ThorlabStage(home=True)
    NDfilter.move_to(0, block=True)
    logger.log(f"stage is at {NDfilter.get_position()}")

    flipshut.open()
    logger.log("flipshut is opened")

    powermeter = juno()
    powermeter.open()
    powermeter.set_range(0)
    logger.log("powermeter is opened")

    symphony = Symphony()
    symphony.Initialize()
    symphony.set_exposuretime(integrationtime)
    symphony.set_config_savetofiles(path)
    logger.log("symphony is initialized")

    priorstage = Proscan(config.PRIORCOMPORT)
    logger.log("priorstage is initialized")

    tisp_linear_actuator = zaber_linear_actuator()
    logger.log("TiSap actuator is initialized")

    spectrometer = thorlabspectrometer()
    logger.log("spectrometer is initialized")

    if check_autofocus:
        logger.log("setting up for autofocus")
        logger.log("wave length is moving to 750nm")
        pid_control_wavelength(targetwavelength=750, TiSap_actuator=tisp_linear_actuator, spectrometer=spectrometer, logger=logger)
        logger.log("power is moving to 0.001W")
        pid_control_power(targetpower=0.001, powermeter=powermeter, NDfilter=NDfilter, eps=targetpower*config.EPSRATIO, logger=logger)
        mypowerdict.add(750, 0.001, NDfilter.get_position())

        objective_lens = Focus_adjuster(config.AUTOFOCUSCOMPORT)
        logger.log("arduino is initialized")
        diff_vec = slit_vector / np.linalg.norm(slit_vector) * 1000 #10um

        logger.log("start autofocus at start position")
        logger.log("stage is moving to {startpos[0]-diff_vec[0], startpos[1]-diff_vec[1]}")
        priorstage.move_to(startpos[0]-diff_vec[0], startpos[1]-diff_vec[1])
        shut.open(2)
        start_height = autofocus(objective_lens=objective_lens, symphony=symphony, savedirpath=path, exposuretime=5, logger=logger, range_dense_search=100, range_sparse_search=400)
        shut.close(2)

        logger.log("start autofocus at end position")
        logger.log(f"stage is moving to {endpos[0]+diff_vec[0], endpos[1]+diff_vec[1]}")
        priorstage.move_to(endpos[0]+diff_vec[0], endpos[1]+diff_vec[1])
        shut.open(2)
        end_height = autofocus(objective_lens=objective_lens, symphony=symphony, savedirpath=path, exposuretime=5, logger=logger, range_dense_search=100, range_sparse_search=400)
        shut.close(2)

        height_func = func.make_linear_from_two_points(0, start_height, numberofsteps-1, end_height)
        symphony.set_exposuretime(integrationtime)


    for posidx in range(numberofsteps):
        logger.log(f"stage is moving to {posidx}:{poslist[0][posidx], poslist[1][posidx]}")
        priorstage.move_to(poslist[0][posidx], poslist[1][posidx])

        savedirpath = path+"/"+ f"pos{posidx}_x{poslist[0][posidx]}_y{poslist[1][posidx]}"
        if not os.path.exists(savedirpath):
            os.makedirs(savedirpath)
            logger.log(f"make dir at {savedirpath}")
        symphony.set_config_savetofiles(savedirpath)

        if check_autofocus:
            logger.log(f"obejctive lens is moving to {height_func(posidx)}")
            objective_lens.move_to(height_func(posidx))

        for wavelength in wavelengthlist:
            logger.log(f"start wavelength control at {wavelength}")
            pid_control_wavelength(targetwavelength=wavelength, TiSap_actuator=tisp_linear_actuator, spectrometer=spectrometer, logger=logger)
            logger.log(f"start power control at {wavelength} for {targetpower}")
            pid_control_power(targetpower=targetpower, powermeter=powermeter, NDfilter=NDfilter, eps=targetpower*config.EPSRATIO, logger=logger, NDinitpos=mypowerdict.get_nearest(wavelength, targetpower))
            mypowerdict.add(wavelength, targetpower, NDfilter.get_position())
            logger.log(f"start to get PL spectra at {wavelength}")
            shut.open(2)
            symphony.start_exposure()
            if sweep:
                comeandgo(pos1=(poslist[0][posidx], poslist[1][posidx]), pos2=(poslist[0][posidx+1], poslist[1][posidx+1]), exposuretime=func.waittime4exposure(integrationtime), priorstage=priorstage)
            else:
                time.sleep(func.waittime4exposure(integrationtime))#sympnoyとの時刻ずれを考慮して，露光時間よりも長めに待つ
            shut.close(2)
            os.rename(os.path.join(savedirpath, "IMAGE0001_0001_AREA1_1.txt"), os.path.join(savedirpath, f"{wavelength}.txt"))
    shut.close(2)
    flipshut.close()

    logger.log("Experiment finished at " + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

def comeandgo(pos1:tuple, pos2:tuple, exposuretime:float, priorstage:Proscan)->None:
    '''
    2点間を往復しながら露光する関数
    '''
    starttime = time.time()
    while True:
        nowtime = time.time()
        if nowtime - starttime > exposuretime:
            break

        priorstage.move_to(pos1[0], pos1[1])

        nowtime = time.time()
        if nowtime - starttime > exposuretime:
            break

        priorstage.move_to(pos2[0], pos2[1])

def autofocus_test_Si(path):
    #autofocus test on Si
    exposuretime = 3
    logger = Logger(log_file_path=os.path.join(path, "log.txt"))

    shut = shutter(config.SHUTTERCOMPORT)
    shut.close(2)

    symphony = Symphony()
    symphony.Initialize()
    symphony.set_config_savetofiles(path)
    symphony.set_exposuretime(exposuretime)
    logger.log(f"exposuretime:{exposuretime}")

    stime = time.time()
    objective_lens = Focus_adjuster(config.AUTOFOCUSCOMPORT)
    shut.open(2)
    start_height = autofocus(objective_lens=objective_lens, symphony=symphony, savedirpath=path, exposuretime=exposuretime, logger=logger, range_dense_search=100, range_sparse_search=400)
    logger.log(f"autofocus at start position:{start_height}")
    logger.log(f"focus take {time.time()-stime}")

if __name__ == "__main__":
    autofocus_test_Si(input("path:"))