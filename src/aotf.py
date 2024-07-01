from pywinauto.application import Application
import os
import warnings
import config

class Aotf:
    def __init__(self, check_amplitude=True):
        if check_amplitude:
            if not self._check_amplitude():
                return
        self.app = Application(backend="uia").start(os.path.join(config.SPFIIIDIR, "SpfIII.exe"), timeout=10, work_dir=config.SPFIIIDIR)

    def _read_amplitude_from_cfg(self):
        flag = False
        with open(os.path.join(config.SPFIIIDIR, "SpfIII.cfg")) as f:
            for s_line in f:
                if "[Amplitude]" in s_line.rstrip():
                    flag = True
                    continue
                if flag:
                    return int(s_line.rstrip().split(' ')[2])

    def _check_amplitude(self):
        amplitude = self._read_amplitude_from_cfg()
        if amplitude == 100:
            return True
        else:
            warnings.warn("SpfIIIを手動起動してAmplitudeを100に設定した後にSpfIIIを閉じてださい")
            return False

    def print(self):
        print(self.app["Spf III Driver 2.0.0"].print_control_identifiers())
        
    def set_wavelength(self, wavelength):
        self.app["Spf III Driver 2.0.0"]["Edit7"].set_text(str(wavelength))
        self.app["Spf III Driver 2.0.0"]["Edit7"].TypeKeys("{ENTER}")

if __name__ == "__main__":
    test = Aotf(check_amplitude=True)