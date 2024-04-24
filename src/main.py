from superchrome import superchrome
from ophircom import ophircom
from thorlab import motor
import time
from pywinauto.application import Application


if __name__ == "__main__":
    app = Application(backend="win32").start("C:\Users\maruk\Desktop\Jobin Yvon\SDK\Examples\C++\FilterWheel\Release\FilterWheel.exe", timeout=10)
