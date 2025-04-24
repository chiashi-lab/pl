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
from PrincetonInstruments.LightField.Automation import Automation
from PrincetonInstruments.LightField.AddIns import ExperimentSettings
from PrincetonInstruments.LightField.AddIns import CameraSettings
from PrincetonInstruments.LightField.AddIns import DeviceType

class PrincetonCamera():
    def __init__(self, camera_name):
        self.auto = Automation(True, List[String]())
        self.experiment = self.auto.LightFieldApplication.Experiment
        print("Princeton camera initialized")
        print("Loaded experiment: " + self.experiment.Name)

    @property
    def exposure_time(self) -> int:
        # Returns the exposure time, in s
        value = self.get(CameraSettings.ShutterTimingExposureTime)
        return value

    @exposure_time.setter
    def exposure_time(self, value: float):
        # Sets the exposure time, in s
        self.set(CameraSettings.ShutterTimingExposureTime, value)

    @property
    def file_name(self) -> int:
        # Returns the file name
        value = self.get(ExperimentSettings.FileNameGenerationBaseFileName)
        return value

    @file_name.setter
    def file_name(self, value: float):
        # Sets the file name
        self.set(ExperimentSettings.FileNameGenerationBaseFileName, Path.GetFileName(value))
