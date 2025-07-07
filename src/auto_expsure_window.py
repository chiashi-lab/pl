import os
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
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

def is_num(s):
    try:
        float(s)
    except ValueError:
        if s == "-":
            return True
        return False
    else:
        return True

def update_spec_plot(func):
    def wrapper(*args, **kwargs):
        args[0].ax.clear()
        ret = func(*args, **kwargs)
        args[0].canvas.draw()
        return ret
    return wrapper

def check_map_loaded(func):
    # マッピングデータが読み込まれているか確認するデコレータ
    # 読み込まれていない場合，エラーメッセージを表示する
    def wrapper(*args, **kwargs):
        if len(args[0].dl_raw.spec_dict) == 0:
            messagebox.showerror('Error', 'Choose map data.')
            return
        return func(*args, **kwargs)

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

        self.dl_raw = DataLoader()

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

        # frame_listbox
        self.treeview = ttk.Treeview(frame_download, height=6, selectmode=tk.EXTENDED)
        self.treeview['columns'] = ['filename']
        self.treeview.column('#0', width=40, stretch=tk.NO)
        self.treeview.column('filename', width=300, anchor=tk.CENTER)
        self.treeview.heading('#0', text='#')
        self.treeview.heading('filename', text='filename')
        self.treeview.bind('<<TreeviewSelect>>', self.select_data)
        self.treeview.bind('<Button-2>', self.delete_data)
        self.treeview.bind('<Button-3>', self.delete_data)

        self.button_download = ttk.Button(frame_download, text='DOWNLOAD', command=self.download, state=tk.DISABLED)
        self.treeview.pack()
        self.button_download.pack()

                # frame_map
        vmr1 = (self.register(self.validate_emission_range_1), '%P')
        vmr2 = (self.register(self.validate_emission_range_2), '%P')

        self.emission_range_1 = tk.DoubleVar(value=0)
        self.emission_range_2 = tk.DoubleVar(value=1610)
        self.entry_emission_range_1 = ttk.Entry(frame_map, textvariable=self.emission_range_1, validate="key", validatecommand=vmr1, justify=tk.CENTER, font=font_md, width=6)
        self.entry_emission_range_2 = ttk.Entry(frame_map, textvariable=self.emission_range_2, validate="key", validatecommand=vmr2, justify=tk.CENTER, font=font_md, width=6)
        self.entry_emission_range_1.config(state=tk.DISABLED)
        self.entry_emission_range_2.config(state=tk.DISABLED)
       
        self.entry_emission_range_1.grid(row=2, column=1)
        self.entry_emission_range_2.grid(row=2, column=2)
        # canvas_drop
        self.canvas_drop = tk.Canvas(self.master, width=self.width_canvas, height=self.height_canvas)
        self.canvas_drop.create_rectangle(0, 0, self.width_canvas, self.height_canvas, fill='lightgray')
        self.canvas_drop.create_text(self.width_canvas / 2, self.height_canvas * 1 / 2, text='Data Drop Here',
                                     font=('Arial', 30))
        
        self.map_ax.set_aspect(self.aspect_ratio.get())

    @check_map_loaded
    def validate_emission_range_1(self, after):
        if self.dl_raw.spec_dict is None:
            return False
        if is_num(after):
            if after == '-':
                after = 0
            if float(after) < self.emission_range_2.get():
                self.update_plemap(emission_range=(float(after), self.emission_range_2.get()),
                                    cmap_range_auto=self.map_autoscale.get())
                self.canvas.draw()
            return True
        elif after == '':
            return True
        else:
            return False

    @check_map_loaded
    def validate_emission_range_2(self, after):
        if self.dl_raw.spec_dict is None:
            return False
        if is_num(after):
            if after == '-':
                after = 0
            if self.emission_range_1.get() < float(after):
                self.update_plemap(emission_range=(self.emission_range_1.get(), float(after)),
                                    cmap_range_auto= self.map_autoscale.get())
                self.canvas.draw()
            return True
        elif after == '':
            return True
        else:
            return False

 

    def download(self) -> None:
        pass # TODO download PLEmap

    @update_spec_plot
    def select_data(self, event) -> None:
        if self.treeview.focus() == '':
            return
        key = self.treeview.item(self.treeview.focus())['values'][0]
        self.show_spectrum(self.dl_raw.spec_dict[key])

    @update_spec_plot
    def delete_data(self, event) -> None:
        if self.treeview.focus() == '':
            return
        key = self.treeview.item(self.treeview.focus())['values'][0]
        ok = messagebox.askyesno('確認', f'Delete {key}?')
        if not ok:
            return
        self.dl_raw.delete_file(key)

        self.update_treeview()
        self.msg.set(f'Deleted {key}.')

    @update_spec_plot
    def drop(self, event=None) -> None:
        self.canvas_drop.place_forget()
        if event.data[0] == '{':
            filenames = list(map(lambda x: x.strip('{').strip('}'), event.data.split('} {')))
        else:
            filenames = event.data.split()
        filenames = sorted(filenames, key=lambda x: os.path.basename(x).split(".")[0].split("_")[0])#filename先頭に波長が入っていることを前提にfilenameでソートしている
        self.excite_wl_list = [int(os.path.basename(filename).split(".")[0].split("_")[0]) for filename in filenames]
        self.dl_raw.load_files(filenames)
        self.show_spectrum(self.dl_raw.spec_dict[filenames[0]])
        self.update_treeview()
        self.show_plemap()

    def drop_enter(self, event: TkinterDnD.DnDEvent) -> None:
        self.canvas_drop.place(anchor='nw', x=0, y=0)

    def drop_leave(self, event: TkinterDnD.DnDEvent) -> None:
        self.canvas_drop.place_forget()

    def show_spectrum(self, spectrum) -> None:
        self.ax.plot(spectrum.xdata, spectrum.ydata, color='black', linewidth=1.0)

    def update_treeview(self) -> None:
        self.treeview.delete(*self.treeview.get_children())
        for i, filename in enumerate(self.dl_raw.spec_dict.keys()):
            self.treeview.insert(
                '',
                tk.END,
                iid=str(i),
                text=str(os.path.basename(filename).split(".")[0].split("_")[0]),
                values=[filename],
                open=True,
                )

    def show_plemap(self) -> None:
        #ple mapの表示
        self.ple_df = {}
        for i, spectrum in enumerate(self.dl_raw.spec_dict.values()):
            temp_df = {}
            for j, wl in enumerate(spectrum.xdata):
                temp_df[wl] = spectrum.ydata[j]
            self.ple_df[self.excite_wl_list[i]] = temp_df
        self.ple_df = pd.DataFrame(self.ple_df).T

        self.ple_x = self.ple_df.columns#emission wavelength
        self.ple_y = self.ple_df.index#excitation wavelength
        yticks = np.linspace(self.excite_wl_list[0], self.excite_wl_list[-1], 5)
        X, Y = np.meshgrid(self.ple_x, self.ple_y)
        Z = self.ple_df.values

        self.emission_range_1.set(round(min(self.ple_x)))
        self.emission_range_2.set(round(max(self.ple_x)))

        if self.map_autoscale.get():
            self.cmap_range_1.set(round(np.min(Z)))
            self.cmap_range_2.set(round(np.max(Z)))
        else:
            if self.cmap_range_1.get() > self.cmap_range_2.get():
                messagebox.showerror('Error', 'Color range is invalid.')
                return
        self.contour = self.map_ax.pcolormesh(X, Y, Z, cmap=self.map_color.get(), shading='auto', norm=Normalize(vmin=self.cmap_range_1.get(), vmax=self.cmap_range_2.get()))

        divider = make_axes_locatable(self.map_ax)
        cax = divider.append_axes('right', size='5%', pad=0.1)
        pp = self.map_ax.figure.colorbar(self.contour, cax=cax, orientation='vertical')

        # 既知のPLEmapデータを表示
        ple_tick_fontsize = 40
        ple_label_fontsize = 30
        lefebvre_df = pd.read_csv(r"data/data#530.txt", comment='#', header=None, engine='python', encoding='cp932', sep=None)
        lefebvre_df.columns = ["n", "m", "dt", "mod", "theta", "E11_eV", "E22_eV", "E12_eV", "EL1_eV", "EL1*_eV", "E22+G_eV", "E22+2G_eV", "ET1_eV", "ET2_eV"]
        lefebvre_df["E11_nm"] = 1240 / lefebvre_df["E11_eV"]
        lefebvre_df["E22_nm"] = 1240 / lefebvre_df["E22_eV"]
        lefebvre_df_filtered = lefebvre_df[(min(self.ple_y) <= lefebvre_df["E22_nm"]) & (lefebvre_df["E22_nm"] <= max(self.ple_y)) & (min(self.ple_x) <= lefebvre_df["E11_nm"]) & (lefebvre_df["E11_nm"] <= max(self.ple_x))]
        self.lefebvre_scatter = self.map_ax.scatter(lefebvre_df_filtered["E11_nm"], lefebvre_df_filtered["E22_nm"], color='black', s=70, label='lefebvre 2007', marker='x')
        self.lefebvre_txt =[]
        for i in range(len(lefebvre_df_filtered)):
            self.lefebvre_txt.append(self.map_ax.text(lefebvre_df_filtered["E11_nm"].iloc[i], lefebvre_df_filtered["E22_nm"].iloc[i], f"({str(int(lefebvre_df_filtered['n'].iloc[i]))}, {str(int(lefebvre_df_filtered['m'].iloc[i]))})", fontsize=30, color='black', ha='left', va='bottom'))
        self.legend = self.map_ax.legend(loc='upper right', fontsize=20)
        self.on_change_show_ref_settings()

        #raman lineの表示
        raman_df = pd.read_csv(r"data/PL_RamanLine.txt", comment='#', header=None, engine='python', encoding='cp932', sep=None)
        raman_df.columns = ["excite_wavelength_nm", "Rayleigh_eV", "D_nm", "D_eV", "G_nm", "2D_nm", "2G_nm", "G+2D_nm", "4D_nm", "2G+2D_nm", "G+4D_nm", "6D_nm"]
        excitefiltered_raman_df = raman_df[(min(self.ple_y) <= raman_df["excite_wavelength_nm"]) & (raman_df["excite_wavelength_nm"] <= max(self.ple_y))]
        self.raman_lines = []
        self.raman_txts = []
        #self.raman_lines.append(self._filter_plot(excitefiltered_raman_df, "D_nm")
        self._filter_plot(excitefiltered_raman_df, "G_nm")
        self._filter_plot(excitefiltered_raman_df, "2D_nm")
        self._filter_plot(excitefiltered_raman_df, "2G_nm")
        self._filter_plot(excitefiltered_raman_df, "G+2D_nm")
        self._filter_plot(excitefiltered_raman_df, "4D_nm")
        self._filter_plot(excitefiltered_raman_df, "2G+2D_nm")
        self._filter_plot(excitefiltered_raman_df, "G+4D_nm")
        self._filter_plot(excitefiltered_raman_df, "6D_nm")
        self.on_change_show_ramanline_settings()

        self.map_ax.tick_params(labelsize=ple_tick_fontsize)
        self.map_ax.set_xlabel('Emission Wavelength [nm]', fontsize=ple_label_fontsize)
        self.map_ax.set_ylabel('Excitation Wavelength [nm]', fontsize=ple_label_fontsize)
        self.map_ax.grid()

    def _filter_plot(self, df:pd.DataFrame, col: str) -> None:
        filtered_df = df[(min(self.map_ax.get_xlim()) <= df[col]) & (df[col] <= max(self.map_ax.get_xlim()))]
        filtered_df = filtered_df.reset_index(drop=True)
        if len(filtered_df) == 0:
            return
        self.raman_lines.append(self.map_ax.plot(filtered_df[col], filtered_df["excite_wavelength_nm"], color='black', linestyle='--')[0])
        self.raman_txts.append(self.map_ax.text(filtered_df[col][0], filtered_df["excite_wavelength_nm"][0], col.split("_")[0], fontsize=20, color='black', ha='left', va='bottom', alpha=0.8))

    def update_plemap(self, cmap: str = None, cmap_range: tuple = None, cmap_range_auto: bool = None, emission_range: tuple = None, emission_range_auto: bool = None) -> [float, float]:
        # emission rangeの設定
        emission_range = emission_range if emission_range is not None else [self.emission_range_1.get(), self.emission_range_2.get()]
        self.map_ax.set_xlim(emission_range[0], emission_range[1])
        # カラーマップ関連の設定
        cmap = cmap if cmap is not None else self.map_color.get()
        cmap_range = cmap_range if cmap_range is not None else [self.cmap_range_1.get(), self.cmap_range_2.get()]
        if cmap_range_auto is not None and cmap_range_auto:
            emission_ranged_mask = ((emission_range[0] < self.ple_x) & (self.ple_x < emission_range[1]))
            emission_ranged_values = np.array(self.ple_df.values)[:, emission_ranged_mask]
            cmap_range = [np.min(emission_ranged_values), np.max(emission_ranged_values)]
            self.cmap_range_1.set(round(cmap_range[0]))
            self.cmap_range_2.set(round(cmap_range[1]))
        self.contour.set(cmap=cmap, norm=Normalize(vmin=cmap_range[0], vmax=cmap_range[1]))

        # 既存refデータの削除
        self.lefebvre_scatter.remove()
        for txt in self.lefebvre_txt:
            txt.remove()

        # refデータの再表示
        lefebvre_df = pd.read_csv(r"data/data#530.txt", comment='#', header=None, engine='python', encoding='cp932', sep=None)
        lefebvre_df.columns = ["n", "m", "dt", "mod", "theta", "E11_eV", "E22_eV", "E12_eV", "EL1_eV", "EL1*_eV", "E22+G_eV", "E22+2G_eV", "ET1_eV", "ET2_eV"]
        lefebvre_df["E11_nm"] = 1240 / lefebvre_df["E11_eV"]
        lefebvre_df["E22_nm"] = 1240 / lefebvre_df["E22_eV"]
        lefebvre_df_filtered = lefebvre_df[(min(self.map_ax.get_ylim()) <= lefebvre_df["E22_nm"]) & (lefebvre_df["E22_nm"] <= max(self.map_ax.get_ylim())) & (min(self.map_ax.get_xlim()) <= lefebvre_df["E11_nm"]) & (lefebvre_df["E11_nm"] <= max(self.map_ax.get_xlim()))]
        self.lefebvre_scatter = self.map_ax.scatter(lefebvre_df_filtered["E11_nm"], lefebvre_df_filtered["E22_nm"], color='black', s=70, label='lefebvre 2007', marker='x')
        self.lefebvre_txt =[]
        for i in range(len(lefebvre_df_filtered)):
            self.lefebvre_txt.append(self.map_ax.text(lefebvre_df_filtered["E11_nm"].iloc[i], lefebvre_df_filtered["E22_nm"].iloc[i], f"({str(int(lefebvre_df_filtered['n'].iloc[i]))}, {str(int(lefebvre_df_filtered['m'].iloc[i]))})", fontsize=30, color='black', ha='left', va='bottom'))
        self.legend = self.map_ax.legend(loc='upper right', fontsize=20)
        self.on_change_show_ref_settings()

        # 既存raman lineの削除
        for raman_line in self.raman_lines:
            raman_line.remove()
        for raman_txt in self.raman_txts:
            raman_txt.remove()

        #raman lineの表示
        raman_df = pd.read_csv(r"data/PL_RamanLine.txt", comment='#', header=None, engine='python', encoding='cp932', sep=None)
        raman_df.columns = ["excite_wavelength_nm", "Rayleigh_eV", "D_nm", "D_eV", "G_nm", "2D_nm", "2G_nm", "G+2D_nm", "4D_nm", "2G+2D_nm", "G+4D_nm", "6D_nm"]
        excitefiltered_raman_df = raman_df[(min(self.map_ax.get_ylim()) <= raman_df["excite_wavelength_nm"]) & (raman_df["excite_wavelength_nm"] <= max(self.map_ax.get_ylim()))]
        self.raman_lines = []
        self.raman_txts = []
        #self.raman_lines.append(self._filter_plot(excitefiltered_raman_df, "D_nm")
        self._filter_plot(excitefiltered_raman_df, "G_nm")
        self._filter_plot(excitefiltered_raman_df, "2D_nm")
        self._filter_plot(excitefiltered_raman_df, "2G_nm")
        self._filter_plot(excitefiltered_raman_df, "G+2D_nm")
        self._filter_plot(excitefiltered_raman_df, "4D_nm")
        self._filter_plot(excitefiltered_raman_df, "2G+2D_nm")
        self._filter_plot(excitefiltered_raman_df, "G+4D_nm")
        self._filter_plot(excitefiltered_raman_df, "6D_nm")
        self.on_change_show_ramanline_settings()
        return cmap_range



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