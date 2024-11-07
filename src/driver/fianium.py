from pywinauto.application import Application
import time
import sys
sys.path.append('../')
import config

#pywinautoを使って波長可変チューナブルフィルタSuperChromeを操作するクラス
#SuperChromeのソフトウェア"SuperChrome"がインストールされている必要がある

class superchrome:
    """
    Class to control the SuperChrome software

    this class is indireclty controlling the SuperChrome using SuperChrome software with pywinauto.
    So, the SuperChrome software should be installed in the computer.

    Attributes:
    app: pywinauto.application.Application object
    wavelength: current wavelength
    bandwidth: current bandwidth

    Methods:
    change_lw(wavelength=,bandwidth=): change the wavelength and bandwidth of the SuperChrome

    """
    def __init__(self):
        """
        initialize the SuperChrome software

        args:
        None

        return:
        None
        """
        self.app = Application(backend="win32").start(config.SUPERCHROMEPATH, timeout=10)
        time.sleep(1)
        self.app["SuperChrome Initialisation"].wait(wait_for="exists",timeout=20)
        self.app["SuperChrome Initialisation"].OK.click()
        print("SuperChrome opening")
        self.app["SuperChrome"].wait(wait_for="enabled",timeout=20)
        time.sleep(3)
        self.wavelength = int(self.app["SuperChrome"].Edit2.texts()[0])
        self.bandwidth = int(self.app["SuperChrome"].Edit.texts()[0])
        print("SuperChrome opened")
    
    def print(self):
        self.app["SuperChrome"].print_control_identifiers()


    def change_lwbw(self, **kwargs):
        """
        change the wavelength and bandwidth of the SuperChrome

        args:
        wavelength: wavelength to change
        bandwidth: bandwidth to change

        return:
        None
        """
        self.wavelength = kwargs.get("wavelength", self.wavelength)
        self.bandwidth = kwargs.get("bandwidth", self.bandwidth)
        self.app["SuperChrome"].Edit2.set_text(str(self.wavelength))
        self.app["SuperChrome"].Edit.set_text(str(self.bandwidth))
        self.app["SuperChrome"].Move.click()

if __name__ == "__main__":
    superchrome = superchrome()