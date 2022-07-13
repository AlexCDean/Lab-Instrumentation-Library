from .dmm.keithley.k2701 import KeithleyInterfaceK2701
from .dmm.keithley.k2750 import KeithleyInterfaceK2750
from .loads.agilent.hp605a import LoadInterfaceHP605A
from .loads.tti.ld400p import LoadInterfaceLD400P
from .psu.bk_precision.bk9130 import PSUInterface9130
from .psu.rode_schwartz.hmp4030 import PSUInterfaceHMP4030
from .psu.tti.mx100tp import PSUInterfaceMX100TP
from .psu.tti.ql355p import PSUInterfaceQL355P
import platform

from .virtual_instrument_interface import \
    VirtualPSUInterface, \
    VirtualLoadInterface, \
    VirtualDMMInterface, \
    VirtualScopeInterface, \
    VirtualI2CInterface, \
    VirtualSPIInterface, \
    VirtualGPIOInterface

_list_devices = [
    KeithleyInterfaceK2701,
    KeithleyInterfaceK2750,
    LoadInterfaceHP605A,
    LoadInterfaceLD400P,
    PSUInterface9130,
    PSUInterfaceMX100TP,
    PSUInterfaceQL355P,
    PSUInterfaceHMP4030,

    VirtualPSUInterface,
    VirtualLoadInterface,
    VirtualDMMInterface,
    VirtualScopeInterface,
    VirtualI2CInterface,
    VirtualSPIInterface,
    VirtualGPIOInterface
]

if platform.machine().endswith('64'):
    from .aardvark.aardvark_wrapper import AardvarkI2CSPI, AardvarkGPIO
    from .aardvark.aardvark_wrapper import Aardvark
    _list_devices.extend([AardvarkGPIO, AardvarkI2CSPI])


DICT_DEVICES_MODEL = {device._model: device for device in _list_devices}
DICT_DEVICES = {dev.__name__: dev for dev in _list_devices}
