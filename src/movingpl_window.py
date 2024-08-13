import tkinter
import os
import sys
sys.coinit_flags = 2
from tkinter import filedialog
import threading
from concurrent.futures import ThreadPoolExecutor
from main import moving_pl
from proscan import PriorStage
import config

def get_path():
    iDir = os.path.abspath(os.path.dirname(__file__))
    file = filedialog.askdirectory(initialdir="C:\\Users\\optics\\individual")
    e9.delete(0,tkinter.END)
    e9.insert(tkinter.END, file)

def go_pl(event):
    Button1.pack_forget()
    thread1 = threading.Thread(target=moving_pl(targetpower=float(e5.get()), minwavelength=int(e1.get()), maxwavelength=int(e2.get()), stepwavelength=int(e3.get()), integrationtime=int(e4.get()), centerwavelength=int(e6.get()), grating=int(e7.get()), slit=float(e8.get()), path=e9.get(), startpos=[int(e10.get()), int(e11.get())], endpos=[int(e12.get()), int(e13.get())], numberofsteps=int(e14.get())))
    thread1.start()

def get_pos():
    stage = PriorStage(config.PRIORCOMPORT)
    return stage.get_pos()

def getpos_start(event):
    executer = ThreadPoolExecutor(max_workers=1)
    pos = executer.submit(get_pos)
    e10.delete(0, tkinter.END)
    e10.insert(tkinter.END, str(pos[0]))
    e11.delete(0, tkinter.END)
    e11.insert(tkinter.END, str(pos[1]))

def getpos_end(event):
    executer = ThreadPoolExecutor(max_workers=1)
    pos = executer.submit(get_pos)
    e12.delete(0, tkinter.END)
    e12.insert(tkinter.END, str(pos[0]))
    e13.delete(0, tkinter.END)
    e13.insert(tkinter.END, str(pos[1]))

root = tkinter.Tk()
root.title(u"ちくちくPL君")
root.geometry("600x700")

l1 = tkinter.Label(text=u'最小波長')
l1.place(x=10, y=10)
e1 = tkinter.Entry(width=7)
e1.insert(tkinter.END, '500')
e1.place(x=120, y=10)
l1l = tkinter.Label(text=u'nm')
l1l.place(x=180, y=10)

l2 = tkinter.Label(text=u'最大波長')
l2.place(x=10, y=50)
e2 = tkinter.Entry(width=7)
e2.insert(tkinter.END, '800')
e2.place(x=120, y=50)
l2l = tkinter.Label(text=u'nm')
l2l.place(x=180, y=50)

l3 = tkinter.Label(text=u'波長ステップ')
l3.place(x=10, y=90)
e3 = tkinter.Entry(width=7)
e3.insert(tkinter.END, '10')
e3.place(x=120, y=90)
l3l = tkinter.Label(text=u'nm')
l3l.place(x=180, y=90)

l4 = tkinter.Label(text=u'露光時間')
l4.place(x=10, y=130)
e4 = tkinter.Entry(width=7, text='120')
e4.insert(tkinter.END, '120')
e4.place(x=120, y=130)
l4l = tkinter.Label(text=u'秒')
l4l.place(x=180, y=130)

l5 = tkinter.Label(text=u'目標パワー')
l5.place(x=10, y=170)
e5 = tkinter.Entry(width=7)
e5.insert(tkinter.END, '0.002')
e5.place(x=120, y=170)
l5l = tkinter.Label(text=u'W')
l5l.place(x=180, y=170)

l6 = tkinter.Label(text=u'中心波長')
l6.place(x=10, y=210)
e6 = tkinter.Entry(width=7)
e6.insert(tkinter.END, '1200')
e6.place(x=120, y=210)
l6l = tkinter.Label(text=u'nm')
l6l.place(x=180, y=210)

l7 = tkinter.Label(text=u'グレーティング')
l7.place(x=10, y=250)
e7 = tkinter.Entry(width=7)
e7.insert(tkinter.END, '150')
e7.place(x=120, y=250)
l7l = tkinter.Label(text=u'/nm')
l7l.place(x=180, y=250)

l8 = tkinter.Label(text=u'フロントスリット')
l8.place(x=10, y=290)
e8 = tkinter.Entry(width=7)
e8.insert(tkinter.END, '0.5')
e8.place(x=120, y=290)
l8l = tkinter.Label(text=u'nm')
l8l.place(x=180, y=290)

l9 = tkinter.Label(text=u'保存先')
l9.place(x=10, y=330)
e9 = tkinter.Entry(width=40)
e9.insert(tkinter.END, 'C:\\Users\\optics\\individuall')
e9.place(x=120, y=330)
b9 = tkinter.Button(text=u'参照', width=10, command=get_path)
b9.place(x=410, y=330)

l10 = tkinter.Label(text=u'開始位置')
l10.place(x=10, y=400)
e10 = tkinter.Entry(width=8)
e10.insert(tkinter.END, '0')
e10.place(x=120, y=400)
e11 = tkinter.Entry(width=8)
e11.insert(tkinter.END, '0')
e11.place(x=250, y=400)
Button2 = tkinter.Button(text=u'位置取得', width=7)
Button2.bind("<1>", getpos_start)
Button2.place(x=400, y=400)

l12 = tkinter.Label(text=u'終了位置')
l12.place(x=10, y=470)
e12 = tkinter.Entry(width=8)
e12.insert(tkinter.END, '0')
e12.place(x=120, y=470)
e13 = tkinter.Entry(width=8)
e13.insert(tkinter.END, '0')
e13.place(x=250, y=470)
Button3 = tkinter.Button(text=u'位置取得', width=7)
Button3.bind("<1>", getpos_end)
Button3.place(x=400, y=470)

l14 = tkinter.Label(text=u'ステップ数')
l14.place(x=10, y=540)
e14 = tkinter.Entry(width=8)
e14.insert(tkinter.END, '1')
e14.place(x=120, y=540)


#ボタン
Button1 = tkinter.Button(text=u'スタート', width=30)#, command=lambda: go_pl())
Button1.bind("<1>", go_pl)
Button1.place(x=20, y=600)

root.mainloop()