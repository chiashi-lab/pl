import datetime
import os
import time

class Logger:
    def __init__(self, log_file_path: str, no_timestamp_flag: bool = False) -> None:
        timestamp = ""
        if not no_timestamp_flag:
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        # 拡張子がある場合は、拡張子の前にタイムスタンプを追加する．ない場合は，そのまま最後にタイムスタンプを追加してtxtファイルとする
        root, ext = os.path.splitext(log_file_path)
        if ext:
            self._log_file_path = root + timestamp + ext
        else:
            self._log_file_path = log_file_path + timestamp + ".txt"

    def _log_without_return(self, message: str) -> None:
        with open(self._log_file_path, 'a') as log_file:
            log_file.write(message)

    def log(self, message: str) -> None:
        self._log_without_return("\n" + message)


if __name__ == "__main__":
    logger = Logger("log")
    logger.log("Hello, World!")
    time.sleep(10)
    logger.log("Goodbye, World!")
