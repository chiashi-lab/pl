import tkinter
import os
import sys
sys.coinit_flags = 2
from tkinter import filedialog
from main import pl, pid_control_power, test

def get_path():
    iDir = os.path.abspath(os.path.dirname(__file__))
    file = filedialog.askdirectory(initialdir=iDir)
    e6.insert(tkinter.END, file)


root = tkinter.Tk()
root.title(u"PL")
root.geometry("500x300")

l1 = tkinter.Label(text=u'最小波長')
l1.place(x=20, y=10)
e1 = tkinter.Entry(width=7)
e1.insert(tkinter.END, '500')
e1.place(x=100, y=10)
l1l = tkinter.Label(text=u'nm')
l1l.place(x=160, y=10)

l2 = tkinter.Label(text=u'最大波長')
l2.place(x=20, y=50)
e2 = tkinter.Entry(width=7)
e2.insert(tkinter.END, '800')
e2.place(x=100, y=50)
l2l = tkinter.Label(text=u'nm')
l2l.place(x=160, y=50)

l3 = tkinter.Label(text=u'波長ステップ')
l3.place(x=20, y=90)
e3 = tkinter.Entry(width=7)
e3.insert(tkinter.END, '10')
e3.place(x=100, y=90)
l3l = tkinter.Label(text=u'nm')
l3l.place(x=160, y=90)

l4 = tkinter.Label(text=u'露光時間')
l4.place(x=20, y=130)
e4 = tkinter.Entry(width=7, text='120')
e4.insert(tkinter.END, '120')
e4.place(x=100, y=130)
l4l = tkinter.Label(text=u'秒')
l4l.place(x=160, y=130)

l5 = tkinter.Label(text=u'目標パワー')
l5.place(x=20, y=170)
e5 = tkinter.Entry(width=7)
e5.insert(tkinter.END, '0.002')
e5.place(x=100, y=170)
l5l = tkinter.Label(text=u'W')
l5l.place(x=160, y=170)

l6 = tkinter.Label(text=u'保存先')
l6.place(x=20, y=210)
e6 = tkinter.Entry(width=40)
e6.place(x=100, y=210)
b6 = tkinter.Button(text=u'参照', width=10, command=get_path)
b6.place(x=410, y=210)


#ボタン
Button1 = tkinter.Button(text=u'スタート', width=30, command=lambda: pl(targetpower=float(e5.get()), minwavelength=int(e1.get()), maxwavelength=int(e2.get()), stepwavelength=int(e3.get()), integrationtime=int(e4.get()), path=e6.get()))
Button1.place(x=20, y=250)

root.mainloop()