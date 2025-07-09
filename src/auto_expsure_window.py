import os
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog, scrolledtext
from tkinterdnd2 import TkinterDnD, DND_FILES
import sys
sys.coinit_flags = 2
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.colors import Normalize
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pandas as pd
import threading
from logger import Logger
import config
import matplotlib.pyplot as plt
from driver.horiba import Symphony
import time
import pandas as pd


font_lg = ('Arial', 24)
font_md = ('Arial', 16)
font_sm = ('Arial', 12)

plt.rcParams['font.family'] = 'Arial'

plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.major.width'] = 1.0
plt.rcParams['ytick.major.width'] = 1.0
plt.rcParams['xtick.labelsize'] = 25
plt.rcParams['ytick.labelsize'] = 25

plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['axes.labelsize'] = 35         # 軸ラベルのフォントサイズ
plt.rcParams['axes.linewidth'] = 1.0        # グラフ囲う線の太さ

plt.rcParams['legend.loc'] = 'best'        # 凡例の位置、"best"でいい感じのところ
plt.rcParams['legend.frameon'] = True       # 凡例を囲うかどうか、Trueで囲う、Falseで囲わない
plt.rcParams['legend.framealpha'] = 1.0     # 透過度、0.0から1.0の値を入れる
plt.rcParams['legend.facecolor'] = 'white'  # 背景色
plt.rcParams['legend.edgecolor'] = 'black'  # 囲いの色
plt.rcParams['legend.fancybox'] = False     # Trueにすると囲いの四隅が丸くなる

plt.rcParams['lines.linewidth'] = 1.0
plt.rcParams['image.cmap'] = 'jet'
plt.rcParams['figure.subplot.top'] = 0.95
plt.rcParams['figure.subplot.bottom'] = 0.15
plt.rcParams['figure.subplot.left'] = 0.1
plt.rcParams['figure.subplot.right'] = 0.95

def update_spec_plot(func):
    def wrapper(*args, **kwargs):
        args[0].ax.clear()
        ret = func(*args, **kwargs)
        args[0].canvas.draw()
        return ret
    return wrapper

class MainWindow(tk.Frame):
    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self.master = master

        self.x0, self.y0, self.x1, self.y1 = 0, 0, 0, 0
        self.rectangles = []
        self.texts = []
        self.ranges = []
        self.drawing = False
        self.rect_drawing = None

        self.new_window = None
        self.widgets_assign = {}

        self.back_df = None
        self.df = None

        self.stop_flag = False

        self.symphony = None

        self.create_widgets()

    def create_widgets(self) -> None:
        # スタイル設定
        style = ttk.Style()
        style.theme_use('winnative')
        style.configure('TButton', font=font_md, width=14, padding=[0, 4, 0, 4], foreground='black')
        style.configure('R.TButton', font=font_md, width=14, padding=[0, 4, 0, 4], foreground='red')
        style.configure('TLabel', font=font_sm, padding=[0, 4, 0, 4], foreground='black')
        style.configure('Color.TLabel', font=font_lg, padding=[0, 0, 0, 0], width=4, background='black')
        style.configure('TEntry', font=font_md, width=14, padding=[0, 4, 0, 4], foreground='black')
        style.configure('TCheckbutton', font=font_md, padding=[0, 4, 0, 4], foreground='black')
        style.configure('TMenubutton', font=font_md, padding=[20, 4, 0, 4], foreground='black')
        style.configure('TCombobox', font=font_md, padding=[20, 4, 0, 4], foreground='black')
        style.configure('TTreeview', font=font_md, foreground='black')

        self.width_canvas = 900
        self.height_canvas = 600
        dpi = 50
        if os.name == 'posix':
            fig = plt.figure(figsize=(self.width_canvas / 2 / dpi, self.height_canvas / 2 / dpi), dpi=dpi)
        else:
            fig = plt.figure(figsize=(self.width_canvas / dpi, self.height_canvas / dpi), dpi=dpi)

        self.ax = fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(fig, self.master)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=3)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.master, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.grid(row=3, column=0)

        frame_download = ttk.LabelFrame(self.master, text='download')
        frame_map = ttk.LabelFrame(self.master, text='settings')
        frame_download.grid(row=0, column=1)
        frame_map.grid(row=1, column=1)

        self.label_path = ttk.Label(frame_map, text=u'保存先', font=font_md)
        self.entry_path = tk.Entry(width=40)
        self.entry_path = tk.Entry(frame_map, width=30, font=font_md)
        self.entry_path.insert(tk.END, 'C:\\Users\\optics\\individual')
        self.button_path = ttk.Button(frame_map, text=u'参照', width=10, state=tk.NORMAL)
        self.button_path.bind("<1>", self.get_path)

        self.label_path.grid(row=0, column=0)
        self.entry_path.grid(row=0, column=1, columnspan=2)
        self.button_path.grid(row=0, column=3)

        self.pb = ttk.Progressbar(frame_map, orient="horizontal", length=200, mode="indeterminate")
        self.pb.grid(row=5, column=0, columnspan=4)

        self.pb_exposure = ttk.Progressbar(frame_map, orient="horizontal", length=200, mode="determinate")
        self.pb_exposure.grid(row=7, column=0, columnspan=4)

        self.button_start = ttk.Button(frame_map, text=u'開始', width=7, state=tk.NORMAL)
        self.button_start.bind("<1>", self.call_start_measurement)
        self.button_start.grid(row=3, column=0)
        self.button_stop = ttk.Button(frame_map, text=u'停止', width=7, state=tk.DISABLED)
        self.button_stop.bind("<1>", self.stop_measurement)
        self.button_stop.grid(row=3, column=1)

        self.center_wavelength = tk.IntVar(value=1300)
        self.entry_center_wavelength = ttk.Entry(frame_map, textvariable=self.center_wavelength, justify=tk.CENTER, font=font_md, width=6)
        self.label_center_wavelength = ttk.Label(frame_map, text=u'中心波長', font=font_md)
        self.label_center_wavelength.grid(row=2, column=0)
        self.entry_center_wavelength.grid(row=2, column=1)

        self.exposure_time = tk.IntVar(value=2)
        self.entry_exposure_time = ttk.Entry(frame_map, textvariable=self.exposure_time, justify=tk.CENTER, font=font_md, width=6)
        self.label_exposure_time = ttk.Label(frame_map, text=u'露光時間', font=font_md)
        self.label_exposure_time.grid(row=1, column=0)
        self.entry_exposure_time.grid(row=1, column=1)

        self.log_scrolltext = scrolledtext.ScrolledText(self.master, width=60, height=10, font=font_sm)
        self.log_scrolltext.grid(row=2, column=1)

        self.logger = Logger(log_file_path=None, log_scroll=self.log_scrolltext)

        # canvas_drop
        self.canvas_drop = tk.Canvas(self.master, width=self.width_canvas, height=self.height_canvas)
        self.canvas_drop.create_rectangle(0, 0, self.width_canvas, self.height_canvas, fill='lightgray')
        self.canvas_drop.create_text(self.width_canvas / 2, self.height_canvas * 1 / 2, text='Data Drop Here',
                                     font=('Arial', 30))

    def get_path(self, event):
        if self.button_path["state"] == tk.DISABLED:
            return
        self.button_path["state"] = tk.DISABLED

        file = filedialog.askdirectory(initialdir="C:\\Users\\optics\\individual")
        self.entry_path.delete(0, tk.END)
        self.entry_path.insert(tk.END, file)

        self.button_path["state"] = tk.NORMAL
        return

    def drop(self, event=None) -> None:
        self.canvas_drop.place_forget()
        if event.data[0] == '{':
            filenames = list(map(lambda x: x.strip('{').strip('}'), event.data.split('} {')))
        else:
            filenames = event.data.split()
        self.back_df = pd.read_csv(filenames[0], comment='#', header=None, engine='python', encoding='cp932', sep=None)

    def drop_enter(self, event: TkinterDnD.DnDEvent) -> None:
        self.canvas_drop.place(anchor='nw', x=0, y=0)

    def drop_leave(self, event: TkinterDnD.DnDEvent) -> None:
        self.canvas_drop.place_forget()

    @update_spec_plot
    def show_spectrum(self) -> None:
        if self.back_df is not None:
            self.df[1] = self.df[1] - self.back_df[1]

        self.df = self.df.iloc[::-1]
            #x軸にラフな値を代入する処理
        list_wl = []
        start_wl = self.center_wavelength.get() - 246
        delta_wl = 509.5 / 511
        for j in range(512):
            list_wl.append(start_wl + delta_wl * j)
        self.df[0] = list_wl

        self.ax.plot(self.df[0], self.df[1], color='black', linewidth=1.0)

    def call_start_measurement(self, event=None) -> None:
        if self.button_start["state"] == tk.DISABLED:
            return
        self.button_start["state"] = tk.DISABLED
        self.button_stop["state"] = tk.NORMAL
        self.thread1 = threading.Thread(target=self.start_measurement)
        self.thread1.start()

    def stop_measurement(self, event=None) -> None:
        if self.button_stop["state"] == tk.DISABLED:
            return
        self.button_stop["state"] = tk.DISABLED
        self.button_start["state"] = tk.NORMAL
        self.stop_flag = True

    def start_measurement(self, event=None) -> None:
        self.pb.start(10)
        if self.symphony is None:
            self.symphony = Symphony()
        self.symphony.Initialize()
        self.symphony.set_exposuretime(self.exposure_time.get())
        self.symphony.set_config_savetofiles(self.entry_path.get())
        time.sleep(2)
        self.logger.log("Symphony initialized and configured.")

        while True:
            if self.stop_flag:
                self.pb.stop()
                self.pb_exposure.stop()
                self.logger.log("Measurement stopped by user.")
                self.stop_flag = False
                break

            try:
                self.pb_exposure["value"] = 0
                self.pb_exposure.start(interval=int(int(self.exposure_time.get()) / 100 * 1000)) #exp_time[s] / 100[step] * 1000[ms/s] = exp_time_per_step[ms/step]
                self.symphony.start_exposure(block=True)
                self.pb_exposure.stop()
                self.df = pd.read_csv(os.path.join(self.entry_path.get(), "IMAGE0001_0001_AREA1_1.txt"), comment='#', header=None, engine='python', encoding='cp932', sep=None)
                self.show_spectrum()
            except Exception as e:
                self.logger.log(f"Error during measurement: {e}")
                messagebox.showerror("Error", f"Measurement failed: {e}")
                self.pb_exposure.stop()
                self.pb.stop()
                break


def main():
    root = TkinterDnD.Tk()
    app = MainWindow(master=root)
    root.protocol('WM_DELETE_WINDOW', app.quit)
    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<DropEnter>>', app.drop_enter)
    root.dnd_bind('<<DropLeave>>', app.drop_leave)
    root.dnd_bind('<<Drop>>', app.drop)
    app.mainloop()


if __name__ == '__main__':
    main()