from driver.fianium import superchrome
from driver.horiba import ihr320, Symphony
from driver.ophir import juno
from driver.prior import Proscan
from driver.sigmakoki import shutter
from driver.thorlab import ThorlabStage, FlipMount
from driver.focus_adjuster_driver import Focus_adjuster
from logger import Logger
import config
import time
import func
import numpy as np
import os
import pandas as pd


def pid_control_power(targetpower:float, wavelength:int, powermeter:juno, NDfilter:ThorlabStage, eps:float = 0.001, logger:Logger = None) -> None:
    '''
    PID制御を用いて目標パワーに制御する関数
    args:
        targetpower(float): 目標パワー[W]
        wavelength(int): 現在の波長[nm]
        powermeter(juno): パワーメーターの自作ドライバークラス
        NDfilter(ThorlabStage): NDフィルターがついているthorlabステージの自作ドライバークラス
        eps(float): 目標パワーの許容誤差割合[無次元]
    return:
        None
    '''
    r = config.PIDNORMALIZATION / targetpower #正規化項
    Kp = config.PIDKP * r
    Ki = config.PIDKI * r
    Kd = config.PIDKD * r
    dt = 1.0
    acc = 0.0
    diff = 0.0
    prev = 0.0
    if NDfilter.get_position() < config.NDINITPOS:##ポジションが0に近いときは，透過率が高すぎてPID制御に時間がかかりすぎるので，透過率を下げる
        NDfilter.move_to(config.NDINITPOS, block=True)
    while (True):
        time.sleep(10)
        nowndstep = NDfilter.get_position()
        ratio = func.wavelength2ratio(wavelength)
        measuredpower = powermeter.get_latestdata()
        nowpower = ratio * measuredpower
        logger.log(f"measured power: {measuredpower}")
        logger.log(f"predicted current power: {nowpower}")
        logger.log(f"now step: {nowndstep}")

        if nowpower < targetpower - eps or targetpower + eps < nowpower:
            error = nowpower - targetpower
            acc += error * dt
            diff = (error - prev) / dt

            tostep = nowndstep + Kp * error + Ki * acc + Kd * diff
            logger.log("move start")
            logger.log(f"error: {error}")
            logger.log(f"acc: {acc}")
            logger.log(f"diff: {diff}")
            logger.log(f"tostep: {tostep}")
            NDfilter.move_to(tostep)
            prev = error
        else:
            logger.log("Already at target power")
            return

def pl(targetpower:float, minwavelength:int, maxwavelength:int, stepwavelength:int, wavelengthwidth:int, integrationtime:int, path:str, logger:Logger) -> None:
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
    logger.log("Experiment Condition")
    logger.log(f"targetpower:{targetpower}")
    logger.log(f"minimum excite center wavelength:{minwavelength}")
    logger.log(f"maximum excite center wavelength:{maxwavelength}")
    logger.log(f"excite center wavelength step:{stepwavelength}")
    logger.log(f"excite wavelength width:{wavelengthwidth}")
    logger.log(f"integration time:{integrationtime}")
    logger.log(f"")

    if not os.path.exists(path):
        os.makedirs(path)
        logger.log(f"make dir at {path}")

    flipshut = FlipMount()
    flipshut.close()
    shut = shutter(config.SHUTTERCOMPORT)
    shut.close(2)

    #laserchoone = superchrome()

    NDfilter = ThorlabStage(home=True)
    NDfilter.move_to(0, block=True)
    logger.log(f"stage is at {NDfilter.get_position()}")

    flipshut.open()

    powermeter = juno()
    powermeter.open()
    powermeter.set_range(3)

    symphony = Symphony()
    symphony.Initialize()
    symphony.set_exposuretime(integrationtime)
    symphony.set_config_savetofiles(path)

    for wavelength in np.arange(minwavelength, maxwavelength+stepwavelength, stepwavelength):
        #laserchoone.change_lwbw(wavelength=wavelength, bandwidth=wavelengthwidth)
        time.sleep(5)
        logger.log(f"start power control at {wavelength}nm")
        pid_control_power(targetpower=targetpower, wavelength=wavelength, powermeter=powermeter, NDfilter=NDfilter, eps=targetpower*config.EPSRATIO, logger=logger)
        logger.log(f"start to get PL spectra at {wavelength}nm")
        shut.open(2)
        symphony.start_exposure()
        time.sleep(func.waittime4exposure(integrationtime))#sympnoyとの時刻ずれを考慮して，露光時間よりも長めに待つ
        shut.close(2)
        os.rename(os.path.join(path, "IMAGE0001_0001_AREA1_1.txt"), os.path.join(path, f"{wavelength}.txt"))
    
    shut.close(2)
    flipshut.close()

def moving_pl(targetpower:float, minwavelength:int, maxwavelength:int, stepwavelength:int, wavelengthwidth:int, integrationtime:int, path:str, startpos:tuple, endpos:tuple, numberofsteps:int, check_autofocus:bool, logger:Logger) -> None:
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
    movepos_when_focus = slit_orthogonal_vector / np.linalg.norm(slit_orthogonal_vector) * 1000

    logger.log("Experiment Condition")
    logger.log(f"targetpower:{targetpower}")
    logger.log(f"minimum excite center wavelength:{minwavelength}")
    logger.log(f"maximum excite center wavelength:{maxwavelength}")
    logger.log(f"excite center wavelength step:{stepwavelength}")
    logger.log(f"excite wavelength width:{wavelengthwidth}")
    logger.log(f"integration time:{integrationtime}")
    logger.log(f"")
    logger.log(f"start position:{startpos}")
    logger.log(f"end position:{endpos}")
    logger.log(f"number of steps:{numberofsteps}")
    logger.log(f"")
    for i in range(numberofsteps):
        logger.log(f"position {i}:{poslist[0][i], poslist[1][i]}")
    logger.log(f"")

    if not os.path.exists(path):
        os.makedirs(path)
        logger.log(f"make dir at {path}")

    flipshut = FlipMount()
    flipshut.close()
    shut = shutter(config.SHUTTERCOMPORT)
    shut.close(2)

    #laserchoone = superchrome()

    NDfilter = ThorlabStage(home=True)
    NDfilter.move_to(0, block=True)
    logger.log(f"stage is at {NDfilter.get_position()}")

    flipshut.open()

    powermeter = juno()
    powermeter.open()
    powermeter.set_range(3)

    symphony = Symphony()
    symphony.Initialize()
    symphony.set_exposuretime(integrationtime)
    symphony.set_config_savetofiles(path)

    priorstage = Proscan(config.PRIORCOMPORT)

    if check_autofocus:
        objective_lens = Focus_adjuster(config.AUTOFOCUSCOMPORT)

    for posidx in range(numberofsteps):
        priorstage.move_to(poslist[0][posidx], poslist[1][posidx])
        priorstage.wait_until_stop()

        savedirpath = path+"/"+ f"pos{posidx}_x{poslist[0][posidx]}_y{poslist[1][posidx]}"
        if not os.path.exists(savedirpath):
            os.makedirs(savedirpath)
            logger.log(f"make dir at {savedirpath}")
        symphony.set_config_savetofiles(savedirpath)

        # autofocus
        if posidx % 10 == 0 and check_autofocus:
            logger.log(f"start autofocus at {poslist[0][posidx], poslist[1][posidx]}")
            symphony.set_exposuretime(1)

            priorstage.move_to(poslist[0][posidx] + movepos_when_focus[0], poslist[1][posidx] + movepos_when_focus[1])
            priorstage.wait_until_stop()

            shut.open(2)

            min_ol = -200 + objective_lens.position
            max_ol = 200 + objective_lens.position
            iter_ol = 0
            while max_ol - min_ol > 9:
                if iter_ol % 3 == 0:
                    objective_lens.set_rpm(objective_lens._clamp(int((max_ol - min_ol)/7), 2, 20))
                iter_ol += 1

                mid1_ol = min_ol + (max_ol - min_ol) / 3
                mid2_ol = max_ol - (max_ol - min_ol) / 3

                objective_lens.move_to(mid1_ol)
                symphony.start_exposure()
                time.sleep(func.waittime4exposure(1))
                df = pd.read_csv(os.path.join(savedirpath, "IMAGE0001_0001_AREA1_1.txt"), sep='\t', comment='#', header=None)
                value1_ol = df[1].max()

                objective_lens.move_to(mid2_ol)
                symphony.start_exposure()
                time.sleep(func.waittime4exposure(1))
                df = pd.read_csv(os.path.join(savedirpath, "IMAGE0001_0001_AREA1_1.txt"), sep='\t', comment='#', header=None)
                value2_ol = df[1].max()

                if value1_ol < value2_ol:
                    min_ol = mid1_ol
                else:
                    max_ol = mid2_ol
            objective_lens.move_to((min_ol + max_ol) / 2)
            logger.log(f"autofocus at {poslist[0][posidx], poslist[1][posidx]}")
            logger.log(f"autofocus at {objective_lens.position}")
            shut.close(2)
            priorstage.move_to(poslist[0][posidx], poslist[1][posidx])
            priorstage.wait_until_stop()

        symphony.set_exposuretime(integrationtime)

        for wavelength in np.arange(minwavelength, maxwavelength+stepwavelength, stepwavelength):
            #laserchoone.change_lwbw(wavelength=wavelength, bandwidth=wavelengthwidth)
            time.sleep(5)
            logger.log(f"start power control at {wavelength}")
            pid_control_power(targetpower=targetpower, wavelength=wavelength, powermeter=powermeter, NDfilter=NDfilter, eps=targetpower*config.EPSRATIO, logger=logger)
            logger.log(f"start to get PL spectra at {wavelength}")
            shut.open(2)
            symphony.start_exposure()
            time.sleep(func.waittime4exposure(integrationtime))#sympnoyとの時刻ずれを考慮して，露光時間よりも長めに待つ
            shut.close(2)
            time.sleep(3)
            os.rename(savedirpath+"/"+"IMAGE0001_0001_AREA1_1.txt", savedirpath+"/"+f"{wavelength}.txt")
    shut.close(2)
    flipshut.close()

def detect_pl(targetpower:float, wavelength:int, wavelengthwidth:int, integrationtime:int, path:str, startpos:tuple, endpos:tuple, numberofsteps:int, check_autofocus:bool, logger:Logger) -> None:
    poslist =[np.linspace(startpos[0], endpos[0], numberofsteps), np.linspace(startpos[1], endpos[1], numberofsteps)]
    poslist = list(poslist)
    poslist = [[int(x) for x in y] for y in poslist]

    slit_vector = np.array([endpos[0]-startpos[0], endpos[1]-startpos[1]])
    slit_orthogonal_vector = np.array([-slit_vector[1], slit_vector[0]])
    movepos_when_focus = slit_orthogonal_vector / np.linalg.norm(slit_orthogonal_vector) * 1000

    logger.log("Experiment Condition")
    logger.log(f"targetpower:{targetpower}")
    logger.log(f"excite center wavelength:{wavelength}")
    logger.log(f"excite wavelength width:{wavelengthwidth}")
    logger.log(f"integration time:{integrationtime}")
    logger.log(f"")
    logger.log(f"start position:{startpos}")
    logger.log(f"end position:{endpos}")
    logger.log(f"number of steps:{numberofsteps}")
    logger.log(f"")
    for i in range(numberofsteps):
        logger.log(f"position {i}:{poslist[0][i], poslist[1][i]}")
    logger.log(f"")

    if not os.path.exists(path):
        os.makedirs(path)
        logger.log(f"make dir at {path}")

    flipshut = FlipMount()
    flipshut.close()
    shut = shutter(config.SHUTTERCOMPORT)
    shut.close(2)

    #laserchoone = superchrome()

    NDfilter = ThorlabStage(home=True)
    NDfilter.move_to(0, block=True)
    logger.log(f"stage is at {NDfilter.get_position()}")

    flipshut.open()

    powermeter = juno()
    powermeter.open()
    powermeter.set_range(3)

    symphony = Symphony()
    symphony.Initialize()
    symphony.set_exposuretime(integrationtime)
    symphony.set_config_savetofiles(path)

    priorstage = Proscan(config.PRIORCOMPORT)

    if check_autofocus:
        objective_lens = Focus_adjuster(config.AUTOFOCUSCOMPORT)

    for posidx in range(numberofsteps-1):
        priorstage.move_to(poslist[0][posidx], poslist[1][posidx])
        priorstage.wait_until_stop()

        savedirpath = path+"/"+ f"pos{posidx}_x{poslist[0][posidx]}_y{poslist[1][posidx]}"
        if not os.path.exists(savedirpath):
            os.makedirs(savedirpath)
            logger.log(f"make dir at {savedirpath}")
        symphony.set_config_savetofiles(savedirpath)

        # autofocus
        if posidx % 10 == 0 and check_autofocus:
            logger.log(f"start autofocus at {poslist[0][posidx], poslist[1][posidx]}")
            symphony.set_exposuretime(1)

            priorstage.move_to(poslist[0][posidx] + movepos_when_focus[0], poslist[1][posidx] + movepos_when_focus[1])
            priorstage.wait_until_stop()

            shut.open(2)
            min_ol = -200 + objective_lens.position
            max_ol = 200 + objective_lens.position
            iter_ol = 0
            while max_ol - min_ol > 9:
                if iter_ol % 3 == 0:
                    objective_lens.set_rpm(objective_lens._clamp(int((max_ol - min_ol)/7), 2, 20))
                iter_ol += 1

                mid1_ol = min_ol + (max_ol - min_ol) / 3
                mid2_ol = max_ol - (max_ol - min_ol) / 3

                objective_lens.move_to(mid1_ol)
                symphony.start_exposure()
                time.sleep(func.waittime4exposure(1))
                df = pd.read_csv(os.path.join(savedirpath, "IMAGE0001_0001_AREA1_1.txt"), sep='\t', comment='#', header=None)
                value1_ol = df[1].max()

                objective_lens.move_to(mid2_ol)
                symphony.start_exposure()
                time.sleep(func.waittime4exposure(1))
                df = pd.read_csv(os.path.join(savedirpath, "IMAGE0001_0001_AREA1_1.txt"), sep='\t', comment='#', header=None)
                value2_ol = df[1].max()

                if value1_ol < value2_ol:
                    min_ol = mid1_ol
                else:
                    max_ol = mid2_ol
            objective_lens.move_to((min_ol + max_ol) / 2)
            logger.log(f"autofocus at {poslist[0][posidx], poslist[1][posidx]}")
            logger.log(f"autofocus at {objective_lens.position}")
            shut.close(2)
            priorstage.move_to(poslist[0][posidx], poslist[1][posidx])
            priorstage.wait_until_stop()

        symphony.set_exposuretime(integrationtime)

        #laserchoone.change_lwbw(wavelength=wavelength, bandwidth=wavelengthwidth)
        time.sleep(5)
        logger.log(f"start power control at {wavelength}")
        pid_control_power(targetpower=targetpower, wavelength=wavelength, powermeter=powermeter, NDfilter=NDfilter, eps=targetpower*config.EPSRATIO, logger=logger)
        logger.log(f"start to get PL spectra at {wavelength}")
        shut.open(2)
        symphony.start_exposure()
        #time.sleep(func.waittime4exposure(integrationtime))#sympnoyとの時刻ずれを考慮して，露光時間よりも長めに待つ
        comeandgo(pos1=(poslist[0][posidx], poslist[1][posidx]), pos2=(poslist[0][posidx+1], poslist[1][posidx+1]), exposuretime=func.waittime4exposure(integrationtime), priorstage=priorstage)
        shut.close(2)
        time.sleep(3)
        os.rename(savedirpath+"/"+"IMAGE0001_0001_AREA1_1.txt", savedirpath+"/"+f"{wavelength}.txt")

    shut.close(2)
    flipshut.close()

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
        priorstage.wait_until_stop()

        nowtime = time.time()
        if nowtime - starttime > exposuretime:
            break

        priorstage.move_to(pos2[0], pos2[1])
        priorstage.wait_until_stop()

if __name__ == "__main__":
    #path = r"c:\Users\optical group\Documents\individual\kanai"
    #pl(targetpower=0.002, minwavelength=500, maxwavelength=800, stepwavelength=10, integrationtime=120, path=path)
    pass