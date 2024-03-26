from ctypes import *
import ctypes
import time
dll = windll.LoadLibrary("C:\Program Files (x86)\Fianium\SuperChrome\SuperChromeSDK.dll")

class SuperChrome(Instrument):
    """ A class for controlling the fianium superchrome filter
    """
    def __init__(self):
#        self.dll = cdll.LoadLibrary(os.path.dirname(__file__) + "\\SuperChromeSDK")
#        self.dll.InitialiseDll(windll.kernel32._handle)
#        self.dll = windll

        self.dll = cdll.LoadLibrary(r'C:\Program Files (x86)\Fianium\SuperChrome' + "\\SuperChromeSDK.dll")
        self.init();
    def init(self):
        self.dll.InitialiseDll(windll.kernel32._handle)
        self.dll.Initialise();
        self.MoveSyncWaveAndBw(633, 10)
        self.wvl = 633;
        self.bw = 10;
    def MoveWvl(self, centWvl, bwWvl):
        """ centWvl and bwWvl are in nm
        """
        print("Moving")
        self.MoveSyncWaveAndBw(centWvl, bwWvl)
        self.wvl = centWvl;
        self.bw = bwWvl;
