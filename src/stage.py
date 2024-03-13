from pylablib.devices import Thorlabs

print(Thorlabs.list_kinesis_devices())
stage = Thorlabs.KinesisMotor("27502401")
print(stage.get_status())
stage.move_to(200000)
stage.wait_for_stop()
stage.move_to(0)
stage.wait_for_stop()