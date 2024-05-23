import tkinter
from superchrome import superchrome
from ophircom import ophircom
from thorlab import motor
from shutter import shutter
import time
import func




root = tkinter.Tk()
root.title(u"PL")
root.geometry("400x300")

#ボタン
Button1 = tkinter.Button(text=u'superchrome初期化')
Button1.pack()

root.mainloop()
