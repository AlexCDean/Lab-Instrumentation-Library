from drivers.utilities import list_devices, get_device
from drivers.psu.bk_precision.bk9130 import PSUInterface9130
from drivers.psu.rode_schwartz.hmp4030 import PSUInterfaceHMP4030

def main():
    all_devices = list_devices()
    print(all_devices)
    for dev in all_devices:
        dev = get_device(dev)
        dev.baud_rate = 4800  # set baud rate, can be whatever you want.
        if 'bk, 9130' in dev.query('*IDN?'):
            interface = PSUInterface9130(dev)
            interface.switch_on(1)
            print(interface.get_voltage(0))
        elif 'hmp4030' in dev.query('*IDN?'):
            interface = PSUInterfaceHMP4030(resource=dev)
            interface.get_voltage(0)

if __name__ == "__main__":
    main()