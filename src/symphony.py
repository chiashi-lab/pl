from pywinauto.application import Application
import time
import config

class symphony:
    """
    Class to control the Symphony software

    this class is indireclty controlling the Symphony using Symphony software with pywinauto.
    So, the Symphony software should be installed in the computer.

    Attributes:
    app: pywinauto.application.Application object

    """
    def __init__(self):
        self.app = Application(backend="win32").start(config.SYMPHONYPATH, timeout=10)
        self.app["Symphony"].wait(wait_for="enabled",timeout=20)
        print("Symphony opened")
    
    def print(self):
        self.app["Symphony"].print_control_identifiers()


if __name__ == "__main__":
    sym = symphony()
    sym.print()