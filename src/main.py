from driver.fianium import superchrome
from driver.horiba import ihr320, Symphony
from driver.ophir import juno
from driver.prior import Proscan
from driver.sigmakoki import shutter
from driver.thorlab import ThorlabStage, FlipMount
from driver.focus_adjuster_driver import Focus_adjuster
import config
import time
import func
import numpy as np
import os
import sys
import pandas as pd


def pid_control_power(targetpower:float, wavelength:int, powermeter:juno, NDfilter:ThorlabStage, eps:float=0.001)->None:
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
        print("measured power: ", measuredpower)
        print("predicted current power: ", nowpower)
        print("now step: ", nowndstep)
        print("\n")

        if nowpower < targetpower - eps or targetpower + eps < nowpower:
            error = nowpower - targetpower
            acc += error * dt
            diff = (error - prev) / dt

            tostep = nowndstep + Kp * error + Ki * acc + Kd * diff
            print("move start")
            print("error: ", error)
            print("acc: ", acc)
            print("diff: ", diff)
            print("tostep: ", tostep)
            print("\n")
            NDfilter.move_to(tostep)
            prev = error
        else:
            print("Already at target power")
            return

def test():
    flipshut = FlipMount()
    flipshut.close()
    shut = shutter(config.SHUTTERCOMPORT)
    shut.close(2)

    laserchoone = superchrome()

    NDfilter = ThorlabStage(home=True)
    NDfilter.move_to(500000, block=True)
    print(f"stage is at {NDfilter.get_position()}")

    shut.open(2)
    flipshut.open()

    powermeter = juno()
    powermeter.open()
    powermeter.set_range(4)
    print(f"powermeter is at {powermeter.get_range()}")

    wavetar = 650
    powtar = 0.004
    print(f"changing wavelength to {wavetar}")
    laserchoone.change_lwbw(wavelength=wavetar, bandwidth=10)
    time.sleep(5)
    print("changed wavelength")
    print(f"powermeter is at {powermeter.get_latestdata()}")
    print("start controlling power")
    time.sleep(5)
    pid_control_power(powtar,wavetar, powermeter, NDfilter, eps=powtar*0.05)
    print("end controlling power")
    time.sleep(2)
    print(f"powermeter is at {powermeter.get_latestdata()}")
    print("waitng for 10s")
    time.sleep(10)

    wavetar = 810
    powtar = 0.004
    print(f"changing wavelength to {wavetar}")
    laserchoone.change_lwbw(wavelength=wavetar, bandwidth=10)
    time.sleep(5)
    print("changed wavelength")
    print(f"powermeter is at {powermeter.get_latestdata()}")
    print("start controlling power")
    time.sleep(5)
    pid_control_power(powtar,wavetar, powermeter, NDfilter, eps=powtar*0.05)
    print("end controlling power")
    time.sleep(2)
    print(f"powermeter is at {powermeter.get_latestdata()}")
    print("waitng for 10s")
    time.sleep(10)

def pl(targetpower:float, minwavelength:int, maxwavelength:int, stepwavelength:int, wavelengthwidth:int, integrationtime:int, path:str)->None:
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
    sys.stdout = open(os.path.join(path,'log.txt'), 'a')

    print("Experiment Condition")
    print(f"targetpower:{targetpower}")
    print(f"minimum excite center wavelength:{minwavelength}")
    print(f"maximum excite center wavelength:{maxwavelength}")
    print(f"excite center wavelength step:{stepwavelength}")
    print(f"excite wavelength width:{wavelengthwidth}")
    print(f"integration time:{integrationtime}")
    print(f"")

    if not os.path.exists(path):
        os.makedirs(path)
        print(f"make dir at {path}")

    flipshut = FlipMount()
    flipshut.close()
    shut = shutter(config.SHUTTERCOMPORT)
    shut.close(2)

    laserchoone = superchrome()

    NDfilter = ThorlabStage(home=True)
    NDfilter.move_to(0, block=True)
    print(f"stage is at {NDfilter.get_position()}")

    flipshut.open()

    powermeter = juno()
    powermeter.open()
    powermeter.set_range(3)

    symphony = Symphony()
    symphony.Initialize()
    symphony.set_exposuretime(integrationtime)
    symphony.set_config_savetofiles(path)

    for wavelength in np.arange(minwavelength, maxwavelength+stepwavelength, stepwavelength):
        laserchoone.change_lwbw(wavelength=wavelength, bandwidth=wavelengthwidth)
        time.sleep(5)
        print(f"start power control at {wavelength}nm")
        pid_control_power(targetpower=targetpower, wavelength=wavelength, powermeter=powermeter, NDfilter=NDfilter, eps=targetpower*config.EPSRATIO)
        print(f"start to get PL spectra at {wavelength}")
        shut.open(2)
        symphony.start_exposure()
        time.sleep(func.waittime4exposure(integrationtime))#sympnoyとの時刻ずれを考慮して，露光時間よりも長めに待つ
        shut.close(2)
        os.rename(os.path.join(path, "IMAGE0001_0001_AREA1_1.txt"), os.path.join(path, f"{wavelength}.txt"))
    
    shut.close(2)
    flipshut.close()

def moving_pl(targetpower:float, minwavelength:int, maxwavelength:int, stepwavelength:int, wavelengthwidth:int, integrationtime:int, path:str, startpos:tuple, endpos:tuple, numberofsteps:int, check_autofocus:bool)->None:
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
    sys.stdout = open(os.path.join(path,'log.txt'), 'a')

    poslist =[np.linspace(startpos[0], endpos[0], numberofsteps), np.linspace(startpos[1], endpos[1], numberofsteps)]
    poslist = list(poslist)
    poslist = [[int(x) for x in y] for y in poslist]

    slit_vector = np.array([endpos[0]-startpos[0], endpos[1]-startpos[1]])
    slit_orthogonal_vector = np.array([-slit_vector[1], slit_vector[0]])
    movepos_when_focus = slit_orthogonal_vector / np.linalg.norm(slit_orthogonal_vector) * 1000

    print("Experiment Condition")
    print(f"targetpower:{targetpower}")
    print(f"minimum excite center wavelength:{minwavelength}")
    print(f"maximum excite center wavelength:{maxwavelength}")
    print(f"excite center wavelength step:{stepwavelength}")
    print(f"excite wavelength width:{wavelengthwidth}")
    print(f"integration time:{integrationtime}")
    print(f"")
    print(f"start position:{startpos}")
    print(f"end position:{endpos}")
    print(f"number of steps:{numberofsteps}")
    print(f"")
    for i in range(numberofsteps):
        print(f"position {i}:{poslist[0][i], poslist[1][i]}")
    print(f"")

    if not os.path.exists(path):
        os.makedirs(path)
        print(f"make dir at {path}")

    flipshut = FlipMount()
    flipshut.close()
    shut = shutter(config.SHUTTERCOMPORT)
    shut.close(2)

    laserchoone = superchrome()

    NDfilter = ThorlabStage(home=True)
    NDfilter.move_to(0, block=True)
    print(f"stage is at {NDfilter.get_position()}")

    flipshut.open()

    powermeter = juno()
    powermeter.open()
    powermeter.set_range(3)

    symphony = Symphony()
    symphony.Initialize()
    symphony.set_exposuretime(integrationtime)
    symphony.set_config_savetofiles(path)

    priorstage = Proscan(config.PRIORCOMPORT)

    objective_lens = Focus_adjuster(config.AUTOFOCUSCOMPORT)

    for posidx in range(numberofsteps):
        priorstage.move_to(poslist[0][posidx], poslist[1][posidx])
        priorstage.wait_until_stop()

        savedirpath = path+"/"+ f"pos{posidx}_x{poslist[0][posidx]}_y{poslist[1][posidx]}"
        if not os.path.exists(savedirpath):
            os.makedirs(savedirpath)
            print(f"make dir at {savedirpath}")
        symphony.set_config_savetofiles(savedirpath)

        # autofocus
        if posidx % 10 == 0 and check_autofocus:
            symphony.set_exposuretime(1)

            priorstage.move_to(poslist[0][posidx] + movepos_when_focus[0], poslist[1][posidx] + movepos_when_focus[1])
            priorstage.wait_until_stop()

            shut.open(2)

            min_ol = -200
            max_ol = 200
            iter_ol = 0
            while max_ol - min_ol > 9:
                if iter_ol % 3 == 0:
                    objective_lens.set_rpm(objective_lens._clamp(int((max_ol - min_ol)/7), 2, 20))
                iter_ol += 1

                mid1_ol = min_ol + (max_ol - min_ol) / 3
                mid2_ol = max_ol - (max_ol - min_ol) / 3

                objective_lens.set_position(mid1_ol)
                symphony.start_exposure()
                time.sleep(func.waittime4exposure(1))
                df = pd.read_csv(os.path.join(savedirpath, "IMAGE0001_0001_AREA1_1.txt"), sep='\t', comment='#', header=None)
                value1_ol = df[1].max()

                objective_lens.set_position(mid2_ol)
                symphony.start_exposure()
                time.sleep(func.waittime4exposure(1))
                df = pd.read_csv(os.path.join(savedirpath, "IMAGE0001_0001_AREA1_1.txt"), sep='\t', comment='#', header=None)
                value2_ol = df[1].max()

                if value1_ol < value2_ol:
                    min_ol = mid1_ol
                else:
                    max_ol = mid2_ol
            objective_lens.set_position((min_ol + max_ol) / 2)
            shut.close(2)
            priorstage.move_to(poslist[0][posidx], poslist[1][posidx])
            priorstage.wait_until_stop()

        symphony.set_exposuretime(integrationtime)

        for wavelength in np.arange(minwavelength, maxwavelength+stepwavelength, stepwavelength):
            laserchoone.change_lwbw(wavelength=wavelength, bandwidth=wavelengthwidth)
            time.sleep(5)
            print(f"start power control at {wavelength}nm")
            pid_control_power(targetpower=targetpower, wavelength=wavelength, powermeter=powermeter, NDfilter=NDfilter, eps=targetpower*config.EPSRATIO)
            print(f"start to get PL spectra at {wavelength}")
            shut.open(2)
            symphony.start_exposure()
            time.sleep(func.waittime4exposure(integrationtime))#sympnoyとの時刻ずれを考慮して，露光時間よりも長めに待つ
            shut.close(2)
            time.sleep(3)
            os.rename(savedirpath+"/"+"IMAGE0001_0001_AREA1_1.txt", savedirpath+"/"+f"{wavelength}.txt")
    shut.close(2)
    flipshut.close()

def detect_pl(targetpower:float, wavelength:int, wavelengthwidth:int, integrationtime:int, path:str, startpos:tuple, endpos:tuple, numberofsteps:int, check_autofocus:bool)->None:
    sys.stdout = open(os.path.join(path,'log.txt'), 'a')

    poslist =[np.linspace(startpos[0], endpos[0], numberofsteps), np.linspace(startpos[1], endpos[1], numberofsteps)]
    poslist = list(poslist)
    poslist = [[int(x) for x in y] for y in poslist]

    slit_vector = np.array([endpos[0]-startpos[0], endpos[1]-startpos[1]])
    slit_orthogonal_vector = np.array([-slit_vector[1], slit_vector[0]])
    movepos_when_focus = slit_orthogonal_vector / np.linalg.norm(slit_orthogonal_vector) * 1000

    print("Experiment Condition")
    print(f"targetpower:{targetpower}")
    print(f"excite center wavelength:{wavelength}")
    print(f"excite wavelength width:{wavelengthwidth}")
    print(f"integration time:{integrationtime}")
    print(f"")
    print(f"start position:{startpos}")
    print(f"end position:{endpos}")
    print(f"number of steps:{numberofsteps}")
    print(f"")
    for i in range(numberofsteps):
        print(f"position {i}:{poslist[0][i], poslist[1][i]}")
    print(f"")

    if not os.path.exists(path):
        os.makedirs(path)
        print(f"make dir at {path}")

    flipshut = FlipMount()
    flipshut.close()
    shut = shutter(config.SHUTTERCOMPORT)
    shut.close(2)

    laserchoone = superchrome()

    NDfilter = ThorlabStage(home=True)
    NDfilter.move_to(0, block=True)
    print(f"stage is at {NDfilter.get_position()}")

    flipshut.open()

    powermeter = juno()
    powermeter.open()
    powermeter.set_range(3)

    symphony = Symphony()
    symphony.Initialize()
    symphony.set_exposuretime(integrationtime)
    symphony.set_config_savetofiles(path)

    priorstage = Proscan(config.PRIORCOMPORT)

    objective_lens = Focus_adjuster(config.AUTOFOCUSCOMPORT)

    for posidx in range(numberofsteps-1):
        priorstage.move_to(poslist[0][posidx], poslist[1][posidx])
        priorstage.wait_until_stop()

        savedirpath = path+"/"+ f"pos{posidx}_x{poslist[0][posidx]}_y{poslist[1][posidx]}"
        if not os.path.exists(savedirpath):
            os.makedirs(savedirpath)
            print(f"make dir at {savedirpath}")
        symphony.set_config_savetofiles(savedirpath)

        # autofocus
        if posidx % 10 == 0 and check_autofocus:
            symphony.set_exposuretime(1)

            priorstage.move_to(poslist[0][posidx] + movepos_when_focus[0], poslist[1][posidx] + movepos_when_focus[1])
            priorstage.wait_until_stop()

            shut.open(2)
            min_ol = -200
            max_ol = 200
            iter_ol = 0
            while max_ol - min_ol > 9:
                if iter_ol % 3 == 0:
                    objective_lens.set_rpm(objective_lens._clamp(int((max_ol - min_ol)/7), 2, 20))
                iter_ol += 1

                mid1_ol = min_ol + (max_ol - min_ol) / 3
                mid2_ol = max_ol - (max_ol - min_ol) / 3

                objective_lens.set_position(mid1_ol)
                symphony.start_exposure()
                time.sleep(func.waittime4exposure(1))
                df = pd.read_csv(os.path.join(savedirpath, "IMAGE0001_0001_AREA1_1.txt"), sep='\t', comment='#', header=None)
                value1_ol = df[1].max()

                objective_lens.set_position(mid2_ol)
                symphony.start_exposure()
                time.sleep(func.waittime4exposure(1))
                df = pd.read_csv(os.path.join(savedirpath, "IMAGE0001_0001_AREA1_1.txt"), sep='\t', comment='#', header=None)
                value2_ol = df[1].max()

                if value1_ol < value2_ol:
                    min_ol = mid1_ol
                else:
                    max_ol = mid2_ol
            objective_lens.set_position((min_ol + max_ol) / 2)
            shut.close(2)
            priorstage.move_to(poslist[0][posidx], poslist[1][posidx])
            priorstage.wait_until_stop()

        symphony.set_exposuretime(integrationtime)

        laserchoone.change_lwbw(wavelength=wavelength, bandwidth=wavelengthwidth)
        time.sleep(5)
        print(f"start power control at {wavelength}nm")
        pid_control_power(targetpower=targetpower, wavelength=wavelength, powermeter=powermeter, NDfilter=NDfilter, eps=targetpower*config.EPSRATIO)
        print(f"start to get PL spectra at {wavelength}")
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
    test()