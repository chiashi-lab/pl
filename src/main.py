from superchrome import superchrome
from ophircom import ophircom
from thorlab import motor
import time
from pywinauto.application import Application

def pid(targetpower, measuredpower, kp, ki, kd, dt, integral, prev_error):
    error = targetpower - measuredpower
    integral = integral + error * dt
    derivative = (error - prev_error) / dt
    output = kp * error + ki * integral + kd * derivative
    prev_error = error
    return output, integral, prev_error


if __name__ == "__main__":
    app = Application(backend="win32").start(r"C:\Users\maruk\Desktop\Jobin Yvon\SDK\Examples\C++\FilterWheel\Release\FWExample.exe", timeout=10)
