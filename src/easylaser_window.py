import tkinter
import sys
sys.coinit_flags = 2
import threading
from main import pid_control_power
from superchrome import superchrome
from ophircom import ophircom
from thorlab import ThorlabStage, FlipMount
from shutter import shutter
import config
import sys


def choonepower(targetpower, centerwavelength, wavelenghwidth):
    laserchoone.change_lwbw(wavelength=centerwavelength, bandwidth=wavelenghwidth)
    pid_control_power(targetpower=targetpower, wavelength=centerwavelength, powermeter=powermeter, NDfilter=NDfilter, eps=targetpower*config.EPSRATIO)

def thredchoonepower(event):
    thread1 = threading.Thread(target=choonepower(0.001*float(e3.get()), int(e1.get()), int(e2.get())))
    thread1.start()


if __name__ == "__main__":
    flipshut = FlipMount()
    flipshut.close()
    shut = shutter(config.SHUTTERCOMPORT)
    shut.close(2)

    laserchoone = superchrome()


    NDfilter = ThorlabStage(home=True)
    NDfilter.move_to(0, block=True)
    print(f"stage is at {NDfilter.get_position()}")

    flipshut.open()
    shut.open(2)

    powermeter = ophircom()
    powermeter.open()
    powermeter.set_range(4)


    root = tkinter.Tk()
    root.title(u"レーザー狙い撃ち君")
    root.geometry("400x300")

    l1 = tkinter.Label(text=u'波長')
    l1.place(x=30, y=10)
    e1 = tkinter.Entry(width=7)
    e1.insert(tkinter.END, '500')
    e1.place(x=140, y=10)
    l1l = tkinter.Label(text=u'nm')
    l1l.place(x=200, y=10)

    l2 = tkinter.Label(text=u'波長幅')
    l2.place(x=30, y=60)
    e2 = tkinter.Entry(width=7)
    e2.insert(tkinter.END, '10')
    e2.place(x=140, y=60)
    l2l = tkinter.Label(text=u'nm')
    l2l.place(x=200, y=60)

    l3 = tkinter.Label(text=u'目標パワー')
    l3.place(x=30, y=110)
    e3 = tkinter.Entry(width=7)
    e3.insert(tkinter.END, '2')
    e3.place(x=140, y=110)
    l3l = tkinter.Label(text=u'mW')
    l3l.place(x=200, y=110)

    #ボタン
    Button1 = tkinter.Button(text=u'セット', width=20)#, command=lambda: go_pl())
    Button1.bind("<1>", thredchoonepower)
    Button1.place(x=20, y=200)

    root.mainloop()