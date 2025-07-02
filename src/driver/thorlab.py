from pylablib.devices import Thorlabs
import sys
sys.path.append('../')
import config
from ctypes import *
import numpy as np

#thorlabsのデバイスを操作するクラス定義
#pylablibというライブラリを使っている
#StageクラスはThorlabs.KinesisMotorを使ってNDフィルターが設置されているステージを操作する
#FlipMountクラスはThorlabs.MFFを使ってターミネーターへのミラーが設置されているフリップマウントを操作する
class ThorlabStage:
    """
    class to control the Thorlabs stage

    Attributes:
    stage: Thorlabs.KinesisMotor object
    maxlimit: maximum limit of the stage
    minlimit: minimum limit of the stage
    position: current position of the stage

    Methods:
    get_status: get the status of the stage
    get_scale: get the scale of the stage
    get_scale_units: get the scale units of the stage
    get_position: get the position of the stage
    wait_for_stop: wait for the stage to stop
    move_to: move the stage to a position
    move_to_home: move the stage to the home position
    gethome: get the home parameters of the stage
    getparam: get the parameters of the stage
    setparam: set the parameters of the stage
    """
    def __init__(self, home: bool = False) -> None:
        """
        connect to the Thorlabs stage

        args:
        home: if True, the stage will be moved to the home position

        return:
        None
        """
        self.stage = Thorlabs.KinesisMotor(str(config.KINESISSTAGEMOTORID))
        if home:
            self.move_to_home(block=True)
        self.position = self.get_position()
        self.maxlimit = config.KINESISSTAGEMAXLIMIT
        self.minlimit =  config.KINESISSTAGEMINLIMIT
    
    def get_status(self):
        return self.stage.get_status()
    
    def get_scale(self):
        return self.stage.get_scale()
    
    def get_scale_units(self):
        return self.stage.get_scale_units()
    
    def get_position(self) -> int:
        """
        get the position of the stage

        args:
        None

        return:
        position(int): current position of the stage
        """
        return self.stage.get_position()
    
    def wait_for_stop(self) -> None:
        """
        wait for the stage to stop

        args:
        None

        return:
        None
        """
        self.stage.wait_for_stop()
    
    def move_to(self, position: int, block: bool = True) -> None:
        """
        move the stage to a position
        
        args:
        position(int): position to move
        block(bool): if True, the function will wait for the stage to stop
        """
        if position > self.maxlimit:
            position = self.maxlimit
        elif position < self.minlimit:
            position = self.minlimit
        self.stage.move_to(position)
        if block:
            self.wait_for_stop()
    
    def move_to_home(self,block) -> None:
        """
        move the stage to the home position

        args:
        block(bool): if True, the function will wait for the stage to stop

        return:
        None
        """
        self.stage.home(sync=block, force=True)

    def _gethome(self):
        return self.stage.get_homing_parameters()
    
    def _getparam(self, scale=False):
        return self.stage.get_polctl_parameters()
    
    def _setparam(self, velocity=None, home_position=None, jog1=None, jog2=None, jog3=None, scale=False):
        self.stage.setup_polctl(velocity=velocity, home_position=home_position, jog1=jog1, jog2=jog2, jog3=jog3, scale=scale)


class FlipMount:
    def __init__(self) -> None:
        self.flip = Thorlabs.MFF(str(config.KINESISMFFID))
        self.state = self.flip.get_state()
    
    def open(self) -> None:
        self.flip.move_to_state(1)
        self.state = self.flip.get_state()

    def close(self) -> None:
        self.flip.move_to_state(0)
        self.state = self.flip.get_state()


# class for CCS200 spectrometer
# https://github.com/Thorlabs/Light_Analysis_Examples/blob/main/Python/Thorlabs%20CCS%20Spectrometers/CCS%20using%20ctypes%20-%20Python%203.py
class thorlabspectrometer:
    def __init__(self) -> None:

        self._lib = cdll.LoadLibrary(config.CCS200DLLPATH)
        self._ccs_handle = c_int(0)
        self._lib.tlccs_init(config.CCS200SPECTROMETERID.encode(), 1, 1, byref(self._ccs_handle))
        self.set_integration_time(0.001)
        self._wavelengths = self._get_wavelengths()
        #以下の波長校正式はnotebook/002ccs200.ipynbにて算出したもの
        #ArHgランプの輝度スペクトルを基準としている
        self.wavelengths_corrected = [x + 6.333 for x in self._wavelengths]

    def __del__(self) -> None:
        self._lib.tlccs_close (self._ccs_handle)

    def set_integration_time(self, integration_time: float) -> None:
        """
        set the integration time of the spectrometer
        args:
            time(float): integration time in seconds not milliseconds
        return:
            None
        
        """
        self._integration_time = integration_time
        self._lib.tlccs_setIntegrationTime(self._ccs_handle, c_double(integration_time))

    def get_integration_time(self) -> float:
        """
        get the integration time of the spectrometer
        args:
            None
        return:
            integration_time(float): integration time in seconds not milliseconds
        """
        return self._integration_time

    def _get_wavelengths(self) -> list:
        """
        get the wavelengths from the spectrometer
        args:
            None
        return:
            wavelengths(list): wavelengths from the spectrometer
        """
        wavelengths = (c_double * 3648)()
        self._lib.tlccs_getWavelengthData(self._ccs_handle, 0, byref(wavelengths), c_void_p(None), c_void_p(None))
        return list(wavelengths)

    def get_wavelengths(self) -> list:
        """
        get the corrected wavelengths from the spectrometer
        args:
            None
        return:
            wavelengths(list): corrected wavelengths from the spectrometer
        """
        return self._wavelengths_corrected

    def get_spectrum(self) -> list:
        """
        get the spectrum from the spectrometer
        args:
            None
        return:
            spectrum(list): spectrum from the spectrometer
        """
        self._lib.tlccs_startScan(self._ccs_handle)
        status = c_int(0)
        
        while (status.value & 0x0010) == 0:
            self._lib.tlccs_getDeviceStatus(self._ccs_handle, byref(status))

        spectrum = (c_double * 3648)()
        self._lib.tlccs_getScanData(self._ccs_handle, byref(spectrum))
        return list(spectrum)

    def get_peak(self) -> float:
        """
        get the peak of the spectrum
        args:
            None
        return:
            peak(float): peak of the spectrum

        #最もナイーブな実装は以下
        spectrum = self.get_spectrum()
        peakindex = np.argmax(spectrum)
        return self.wavelengths_corrected[peakindex]
        #この実装だとサチって最大値が複数ある場合に正しく動作しない
        """
        for _ in range(10):#露光時間の調整は10回まで行う
            spectrum = np.array(self.get_spectrum())
            n_maxvalue = np.count_nonzero(spectrum == np.max(spectrum))
            if n_maxvalue <= 1:#最大値が一つだけならサチっていない
                peakindex = np.argmax(spectrum)
                peakwavelength = self.wavelengths_corrected[peakindex]
                if peakwavelength < 650 or 950 < peakwavelength: #ピーク波長がチタンサファイアレーザーの利得帯域外なら上手く露光出来ていないので露光時間を延ばす
                    self.set_integration_time(self.get_integration_time() * 2)
                else:
                    return peakwavelength
            else: #最大値が複数あるならサチっているので露光時間を短くする
                self.set_integration_time(self.get_integration_time() / 2)



if __name__ == "__main__":
    print(Thorlabs.list_kinesis_devices())
    
    stage = ThorlabStage(home=True)
    stage.move_to(0,block=True)
    print(f"moved{stage.get_position()}")

    #flip = FlipMount()
    #print(flip.state)
    """
    import matplotlib.pyplot as plt
    ccs200 = thorlabspectrometer()
    plt.plot(ccs200.wavelengths_corrected, ccs200.get_spectrum())
    print(ccs200.get_peak())
    plt.show()
    """