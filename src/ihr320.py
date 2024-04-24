from pywinauto.application import Application
import time
import config

class ihr320:
    """
    Class to control the IHR320 software

    this class is indireclty controlling the IHR320 using IHR320 software with pywinauto.
    So, the IHR320 software should be installed in the computer.

    Attributes:
    app: pywinauto.application.Application object

    """
    def __init__(self):
        self.app = Application(backend="win32").start(config.CCDMONOPATH, timeout=10)
        self.app["IHR320"].wait(wait_for="enabled",timeout=20)
        print("IHR320 opened")
    
    def print(self):
        self.app["IHR320"].print_control_identifiers()

if __name__ == "__main__":
    ihr = ihr320()
    ihr.print()