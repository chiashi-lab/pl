from read_spe import SpeReference
import matplotlib.pyplot as plt
import cv2
import numpy as np
import time
# Import the .NET class library
import clr
# Import python sys module
import sys
# Import os module
import os
# Import System.IO for saving and opening files
from System.IO import *
# Import c compatible List and String
from System import String
from System.Collections.Generic import List
# Add needed dll references
sys.path.append(os.environ['LIGHTFIELD_ROOT'])
sys.path.append(os.environ['LIGHTFIELD_ROOT']+"\\AddInViews")
clr.AddReference('PrincetonInstruments.LightFieldViewV5')
clr.AddReference('PrincetonInstruments.LightField.AutomationV5')
clr.AddReference('PrincetonInstruments.LightFieldAddInSupportServices')
# PI imports
import PrincetonInstruments.LightField.AddIns as AddIns
from PrincetonInstruments.LightField.Automation import Automation
from PrincetonInstruments.LightField.AddIns import ExperimentSettings
from PrincetonInstruments.LightField.AddIns import CameraSettings
from PrincetonInstruments.LightField.AddIns import DeviceType
from PrincetonInstruments.LightField.AddIns import SensorTemperatureStatus

class PrincetonCamera():
    def __init__(self):

        self._exposure_time = None
        self._file_name = None
        self._folder_path = None

        self.auto = Automation(True, List[String]())
        self.experiment = self.auto.LightFieldApplication.Experiment
        print("Princeton camera initialized")
        print("Loaded experiment: " + self.experiment.Name)

    def __del__(self):
        self.auto.Dispose()

    def _set_value(self, setting, value: float) -> None:
        # Returns the value of the setting
        if self.experiment.Exists(setting):
            self.experiment.SetValue(setting, value)
        else:
            raise ValueError(f"Setting {setting} does not exist in the experiment.")

    def _get_value(self, setting) -> float|int:
        # Returns the value of the setting
        if self.experiment.Exists(setting):
            return self.experiment.GetValue(setting)
        else:
            raise ValueError(f"Setting {setting} does not exist in the experiment.")

    @property
    def exposure_time(self) -> int:
        # Returns the exposure time, in s
        if self._exposure_time is None:
            self._exposure_time = self._get_value(CameraSettings.ShutterTimingExposureTime)
        return self._exposure_time

    @exposure_time.setter
    def exposure_time(self, value: float):
        # Sets the exposure time, in s
        self._exposure_time = value
        self._set_value(CameraSettings.ShutterTimingExposureTime, value)

    @property
    def file_name(self) -> int:
        # Returns the file name
        if self._file_name is None:
            self._file_name = self._get_value(ExperimentSettings.FileNameGenerationBaseFileName)
        return self._file_name

    @file_name.setter
    def file_name(self, value: str):
        # Sets the file name
        self._file_name = value
        self._set_value(ExperimentSettings.FileNameGenerationBaseFileName, Path.GetFileName(value))

    @property
    def folder_path(self) -> str:
        if self._folder_path is None:
            self._folder_path = self._get_value(ExperimentSettings.FileNameGenerationDirectory)
        return self._folder_path

    @folder_path.setter
    def folder_path(self, value: str):
        # Sets the folder path
        self._folder_path = value
        self._set_value(ExperimentSettings.FileNameGenerationDirectory, value)

    @property
    def temperature(self):
        return self.experiment.GetValue(CameraSettings.SensorTemperatureReading)
    
    @property
    def temperature_status(self) -> None:
        current = self.experiment.GetValue(CameraSettings.SensorTemperatureStatus)
        return (current == SensorTemperatureStatus.Locked)

    def online_export(self):
        self._set_value(ExperimentSettings.OnlineExportEnabled, True)
        self._set_value(ExperimentSettings.OnlineExportFormat, AddIns.ExportFileType.Tiff)

    def acquire(self, block: bool = True, num_trials: int = 10) -> None:
        # Starts the acquisition
        for i in range(num_trials):
            if self.experiment.IsRunning:
                time.sleep(1)
                continue
            else:
                self.experiment.Acquire()
                if block:
                    time.sleep(self.exposure_time)
                    while self.experiment.IsRunning:
                        time.sleep(1)
                return

    def convert_spe2tiff(self, spe_filename: str, tiff_filename: str) -> None:
        # Converts the SPE file to TIFF format
        spe_file = SpeReference(spe_filename)
        data = spe_file.get_data()[0][0,:,:]
        data = data.astype(np.float32)
        data = cv2.medianBlur(data, 3)
        plt.imsave(tiff_filename, data, cmap='gray')


if __name__ == "__main__":
    camera = PrincetonCamera()
    camera.experiment.Load("Exp-5000ms")
    camera.exposure_time = 0.1  # Set exposure time to 100 ms
    camera.file_name = "test_image"  # Set file name for the image
    camera.online_export()  # Enable online export
    print(camera.file_name)  # Print the file name
    print("Exposure time: ", camera.exposure_time)  # Print the exposure time
    print("Folder path: ", camera.folder_path)  # Print the folder path
    print("Temperature: ", camera.temperature)  # Print the temperature
    print("Temperature status: ", camera.temperature_status)  # Print the temperature status
    camera.acquire()  # Acquire the image
    camera.convert_spe2tiff(os.path.join(camera.folder_path, (camera.file_name + ".spe")), "test_image_filtered.tiff")  # Convert SPE to TIFF
    print("Image acquired and converted to TIFF.")
