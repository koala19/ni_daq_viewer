import nidaqmx

system = nidaqmx.system.System.local()
device_list = []

for device in system.devices:
    device_list.append(device.name)
print(device_list[1:])
