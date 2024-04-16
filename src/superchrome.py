from pywinauto.application import Application
import time
class superchrome:
    """
    Class to control the SuperChrome software

    Attributes:
    app: pywinauto.application.Application object
    wavelength: current wavelength
    bandwidth: current bandwidth

    Methods:
    change_lw: change the wavelength and bandwidth of the SuperChrome

    """
    def __init__(self):
        self.app = Application(backend="win32").start("C:\Program Files (x86)\Fianium\SuperChrome\SuperChrome.exe", timeout=10)
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


    def change_lw(self, **kwargs):
        self.wavelength = kwargs.get("wavelength", self.wavelength)
        self.bandwidth = kwargs.get("bandwidth", self.bandwidth)
        self.app["SuperChrome"].Edit2.set_text(str(self.wavelength))
        self.app["SuperChrome"].Edit.set_text(str(self.bandwidth))
        self.app["SuperChrome"].Move.click()

if __name__ == "__main__":
    app = Application(backend="win32").start("C:\Program Files (x86)\Fianium\SuperChrome\SuperChrome.exe", timeout=10)
    print(app.windows())