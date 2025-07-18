SUPERCHROMEPATH = "C:\\Program Files (x86)\\Fianium\\SuperChrome\\SuperChrome.exe"

MFCCCDPATH = "C:\\Program Files (x86)\\Jobin Yvon\\SDK\\Examples\\C++\\CCD\\Release\\MFC_CCDExample.exe"

CCDMONOPATH = "C:\\Program Files (x86)\\Jobin Yvon\\SDK\\Examples\\C++\\Mono\\Release\\MonoExample.exe"

SPFIIIDIR = "C:\\SpfIII\\"

KINESISMFFID = 37856267

KINESISSTAGEMOTORID = 27502401
KINESISSTAGEMAXLIMIT = 1200000
KINESISSTAGEMINLIMIT = 0
NDINITPOS = 4.0e5
EPSRATIO = 0.02#レーザーパワーの許容誤差比率．(1.0±epsratio) * 目標パワー[W] = 許容パワー誤差[W] の範囲で許容する

EXCITEPOWERPIDNORMALIZATION = 2.0e7
EXCITEPOWERPIDKP = 4
EXCITEPOWERPIDKI = 0.01
EXCITEPOWERPIDKD = 0.005

SHUTTERCOMPORT = 'COM5'
PRIORCOMPORT = 'COM3'

AUTOFOCUSCOMPORT = 'COM8'
STEPS_PER_ROTATE_ST42BYH1004 = 400 #1回転に必要なステップ数　360deg/rotate / 0.9deg/step = 400step/rotate

#windows device manager -> NI-VISA USB Device -> Spectrometer -> Properties -> Details -> Device Instanceパス
#実際の表示はUSB\VID_1313&PID_8089\M00331284だった
CCS200SPECTROMETERID = "USB0::0x1313::0x8089::M00331284::RAW"
CCS200DLLPATH = "C:/Program Files/IVI Foundation/VISA/Win64/Bin/TLCCS_64.dll"

ZABERPORT = 'COM9'
ZABERMINLIMIT = 14.0
ZABERMAXLIMIT = 24.8#長すぎると複屈折フィルターのピストンクランク機構の可動範囲を超えてしまい機械的に壊れるのでリミットを設定している

EXCITEWAVELENGTHPIDKP = 0.035
EXCITEWAVELENGTHPIDKI = 0.0001
EXCITEWAVELENGTHPIDKD = 0.0001

VGC50X_PORT = 'COM4'  # Default port for VGC50X, can be overridden
