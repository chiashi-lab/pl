from pywinauto.application import Application
import os
import warnings
import sys
sys.path.append('../')
import config
import time

class Aotf:
    def __init__(self, check_amplitude: bool = True)->None:
        if check_amplitude:
            if not self._check_amplitude():
                return
        self.app = Application(backend="win32").start(os.path.join(config.SPFIIIDIR, "SpfIII.exe"), timeout=10, work_dir=config.SPFIIIDIR)

    def _read_amplitude_from_cfg(self)->int:
        flag = False
        with open(os.path.join(config.SPFIIIDIR, "SpfIII.cfg")) as f:
            for s_line in f:
                if "[Amplitude]" in s_line.rstrip():
                    flag = True
                    continue
                if flag:
                    return int(s_line.rstrip().split(' ')[2])

    def _check_amplitude(self)->bool:
        """
        amplitudeが100に設定されているか確認する
        return:
            True: amplitudeが100に設定されている場合
            False: amplitudeが100に設定されていない場合
        """
        amplitude = self._read_amplitude_from_cfg()
        if amplitude == 100:
            return True
        else:
            warnings.warn("SpfIIIGを手動起動してAmplitudeを100に設定した後にSpfIIIを閉じてださい")
            return False

    def _print(self)->None:
        print(self.app["Spf III Driver 2.0.0"].print_control_identifiers())
        
    def set_wavelength(self, wavelength: int)->None:
        """
        wavelengthを設定する
        args:
            wavelength: int wavelength
        """
        self.app["Spf III Driver 2.0.0"]["Edit7"].set_text(str(wavelength))
        self.app["Spf III Driver 2.0.0"]["Edit7"].type_keys("{ENTER}")

if __name__ == "__main__":
    test = Aotf(check_amplitude=True)
    for _ in range(5):
        test.set_wavelength(1053)
        time.sleep(2)
        test.set_wavelength(1200)
        time.sleep(2)
