import time
from pylablib.devices import Andor

def connection_test():
    print("cam number: ", Andor.get_cameras_number_SDK2())

    cam = Andor.AndorSDK2Camera(temperature=-70, fan_mode="on")

    for i in range(10):
        time.sleep(3)
        print("temp",cam.get_temperature())
        print("temp status",cam.get_temperature_status())

    cam.close()


def spec_test():
    inttime = 3
    cam = Andor.AndorSDK2Camera()
    cam.set_exposure(inttime)
    cam.set_acquisition_mode("single scan")
    cam.set_trigger_mode("internal")
    cam.setup_shutter("auto")
    cam.set_read_mode("fvb")
    cam.set_acquisition_mode("single")
    cam.start_acquisition()
    for i in range(inttime + 2):
        print(i)
        print(cam.get_acquisition_progress())
        time.sleep(1)
    #cam.wait_for_frame()
    frame = cam.read_newest_image()
    print("frame shape: ", frame.shape)
    print(frame)
    cam.close()

if __name__ == "__main__":
    connection_test()
