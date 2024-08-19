import tkinter
import os
import sys
sys.coinit_flags = 2
from tkinter import filedialog
import threading
from main import pl, pid_control_power, test

def get_path():
    iDir = os.path.abspath(os.path.dirname(__file__))
    file = filedialog.askdirectory(initialdir="C:\\Users\\optics\\individual")
    e9.delete(0,tkinter.END)
    e9.insert(tkinter.END, file)

def go_pl(event):
    Button1.pack_forget()
    thread1 = threading.Thread(target=pl(targetpower=float(e6.get())*0.001, minwavelength=int(e1.get()), maxwavelength=int(e2.get()), stepwavelength=int(e3.get()), wavelengthwidth=int(e4.get()), integrationtime=int(e5.get()), path=e9.get()))
    thread1.start()


root = tkinter.Tk()
root.title(u"簡単PL君")
root.geometry("600x500")

l1 = tkinter.Label(text=u'励起光最短中心波長')
l1.place(x=10, y=10)
e1 = tkinter.Entry(width=7)
e1.insert(tkinter.END, '500')
e1.place(x=150, y=10)
l1l = tkinter.Label(text=u'nm')
l1l.place(x=210, y=10)

l2 = tkinter.Label(text=u'励起光最長中心波長')
l2.place(x=10, y=50)
e2 = tkinter.Entry(width=7)
e2.insert(tkinter.END, '800')
e2.place(x=150, y=50)
l2l = tkinter.Label(text=u'nm')
l2l.place(x=210, y=50)

l3 = tkinter.Label(text=u'励起光中心波長間隔')
l3.place(x=10, y=90)
e3 = tkinter.Entry(width=7)
e3.insert(tkinter.END, '10')
e3.place(x=150, y=90)
l3l = tkinter.Label(text=u'nm')
l3l.place(x=210, y=90)

l4 = tkinter.Label(text=u'励起光波長幅')
l4.place(x=10, y=130)
e4 = tkinter.Entry(width=7)
e4.insert(tkinter.END, '10')
e4.place(x=150, y=130)
l4l = tkinter.Label(text=u'nm')
l4l.place(x=210, y=130)

l5 = tkinter.Label(text=u'露光時間')
l5.place(x=10, y=170)
e5 = tkinter.Entry(width=7, text='120')
e5.insert(tkinter.END, '120')
e5.place(x=150, y=170)
l5l = tkinter.Label(text=u'秒')
l5l.place(x=210, y=170)

l6 = tkinter.Label(text=u'サンプル照射パワー')
l6.place(x=10, y=210)
e6 = tkinter.Entry(width=7)
e6.insert(tkinter.END, '2')
e6.place(x=150, y=210)
l6l = tkinter.Label(text=u'mW')
l6l.place(x=210, y=210)

l9 = tkinter.Label(text=u'保存先')
l9.place(x=10, y=330)
e9 = tkinter.Entry(width=40)
e9.insert(tkinter.END, 'C:\\Users\\optics\\individuall')
e9.place(x=120, y=330)
b9 = tkinter.Button(text=u'参照', width=10, command=get_path)
b9.place(x=410, y=330)


#ボタン
Button1 = tkinter.Button(text=u'スタート', width=30)#, command=lambda: go_pl())
Button1.bind("<1>", go_pl)
Button1.place(x=20, y=450)

root.mainloop()