import datetime
from tkinter import scrolledtext
import os
import time
import tkinter
import threading

class Logger:
    def __init__(self, log_file_path: str | None, timestamp_flag: bool = True, log_scroll: scrolledtext.ScrolledText | None = None) -> None:
        self._log_scroll = log_scroll

        if log_file_path is None: # if log file path is None, do not write log
            self._log_file_path = None
            return

        timestamp = ""
        if timestamp_flag:
            # タイムスタンプフラグがTrueの場合は，ログファイル名にタイムスタンプを追加する
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        # 拡張子がある場合は、拡張子の前にタイムスタンプを追加する．ない場合は，そのまま最後にタイムスタンプを追加してtxtファイルとする
        root, ext = os.path.splitext(log_file_path)
        if ext:
            self._log_file_path = root + timestamp + ext
        else:
            self._log_file_path = log_file_path + timestamp + ".txt"

    def _log_without_return(self, message: str) -> None:
        if self._log_file_path: # if log file path is None, do not write log
            with open(self._log_file_path, 'a') as log_file:
                log_file.write(message)
        if self._log_scroll:
            self._log_scroll.config(state="normal")
            self._log_scroll.insert("end", message)
            self._log_scroll.see("end")
            self._log_scroll.config(state="disabled")

    def log(self, message: str) -> None:
        self._log_without_return("\n" + datetime.datetime.now().strftime("%d %H:%M:%S") + " ; " + message)


if __name__ == "__main__":
    class Application(tkinter.Frame):
        def __init__(self, master=None):
            super().__init__(master)
            self.pack()
            self.master = master
            self.master.geometry("400x400")
            self.create_widgets()
        def create_widgets(self):
            self.scrolltxt = scrolledtext.ScrolledText(self.master, wrap=tkinter.WORD, width=50, height=10)
            self.scrolltxt.place(x=10, y=50)

            self.button = tkinter.Button(self.master, text="log")
            self.button.bind("<1>", self.call_log)
            self.button.place(x=10, y=10)
        def log(self):
            logger = Logger(log_file_path="log.txt", timestamp_flag=True, log_scroll=self.scrolltxt)
            for i in range(20):
                logger.log(f"test{i}")
                time.sleep(0.3)
        def call_log(self, event):
            thread1 = threading.Thread(target=self.log, args=())
            thread1.start()
    root = tkinter.Tk()
    app = Application(master=root)
    app.mainloop()
