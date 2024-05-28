import tkinter
import os
import sys
sys.coinit_flags = 2
from tkinter import filedialog
import threading
from main import pl, pid_control_power, test

def get_path():
    iDir = os.path.abspath(os.path.dirname(__file__))
    file = filedialog.askdirectory(initialdir=iDir)
    e9.delete(0,tkinter.END)
    e9.insert(tkinter.END, file)

def go_pl():
    Button1.pack_forget()

    thread1 = threading.Thread(target=pl(targetpower=float(e5.get()), minwavelength=int(e1.get()), maxwavelength=int(e2.get()), stepwavelength=int(e3.get()), integrationtime=int(e4.get()), centerwavelength=int(e6.get()), grating=int(e7.get()), slit=float(e8.get()), path=e9.get()))
    thread1.start()


root = tkinter.Tk()
root.title(u"簡単PL君")
root.geometry("600x500")

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
e9.insert(tkinter.END, 'C:\\Users\\optical group\\Documents\\individual')
e9.place(x=120, y=330)
b9 = tkinter.Button(text=u'参照', width=10, command=get_path)
b9.place(x=410, y=330)


#ボタン
Button1 = tkinter.Button(text=u'スタート', width=30, command=lambda: go_pl())
Button1.place(x=20, y=450)

root.mainloop()