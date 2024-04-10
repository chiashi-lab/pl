from pywinauto.application import Application

app = Application(backend="win32").start("C:\Program Files (x86)\Fianium\SuperChrome\SuperChrome.exe", timeout=10)
print(app.windows())