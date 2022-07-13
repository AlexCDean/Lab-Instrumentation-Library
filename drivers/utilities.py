import pyvisa
from pyvisa.errors import VisaIOError
from serial import SerialException
from .common import scpi_commands as cmds
from .devices import DICT_DEVICES_MODEL


def list_devices():
    rm = pyvisa.ResourceManager()
    devices = []
    for resource in rm.list_resources():
        try:
            devices.append(open_resource(resource))
        except (VisaIOError, SerialException, IOError):
            pass
    
    return devices

def open_resource(resource):
    rm = pyvisa.ResourceManager()
    try:
        return rm.open_resource(resource)
    except pyvisa.VisaIOError as err:
        raise IOError(err)  # Resource is busy or non-existent.

def scan_devices(scan_aardvarks=False, aardvark_in_gpio_mode=False):
    devices = list_devices()
    supported_devices = {}    
    supported_devices.update(find_device_interface(devices))
    if scan_aardvarks:
        supported_devices.update(scan_aardvarks(aardvark_in_gpio_mode))
    print(f"Supported devices: {supported_devices}")
    return supported_devices

def scan_aardvarks(is_gpio_mode=False):
    from .devices import AardvarkGPIO, AardvarkI2CSPI, Aardvark
    supported_devices = {}
    num_aardvarks, ports, uids = Aardvark.find_free_aardvarks()
    for i in range(num_aardvarks):
        if is_gpio_mode:
            supported_devices[uids[i]] = AardvarkGPIO(serial=uids[i])
        else:
            supported_devices[uids[i]] = AardvarkI2CSPI(serial=uids[i])
    return supported_devices

def get_interface_by_identity(identity):
    for model, interface in DICT_DEVICES_MODEL.items():
        if model in identity:
            print(f"Found supported device: {identity}")
            return interface
    return None

# PyVisa searches using baud 9600. some devices could be any baud and any line endings. 
def find_device_interface(devices):
    print(f"Scanning through {devices} via various bauds and terminators")
    # in order of most to least likely. 
    baud_to_try = [9600, 115200, 19200, 57600, 38400, 4800, 2400, 1200, 600, 300]
    read_term_to_try = ['\n', '\r', '\r\n']  
    supported_devices = {}
    for device in devices:
        device.timeout = 200  # Reduce timeout to reduce time this takes (ms)
        interface = None
        for baud in baud_to_try:    
            if interface is not None:
                break  # No clean way of moving to next loop. 
            for term in read_term_to_try:
                try:
                    device.baud_rate = baud
                    device.read_termination = term                
                    identity = device.query(cmds.SCPI_IDENTIFY)                    
                    interface = get_interface_by_identity(identity)                    
                    if interface:
                        device.timeout = 2000 # Default
                        supported_devices[identity] = interface(resource=device)
                        break
                    device.flush(pyvisa.constants.VI_READ_BUF)
                    device.flush(pyvisa.constants.VI_WRITE_BUF)
                except VisaIOError:
                    device.flush(pyvisa.constants.VI_READ_BUF)
                    device.flush(pyvisa.constants.VI_WRITE_BUF)

    return supported_devices


