from .dmm.keithley.k2701 import DMMInterfaceK2701
from .loads.agilent.HP605A import LoadHP605A
from .aardvark.aardvark_wrapper import AardvarkI2CSPI, AardvarkGPIO
from .loads.tti.LD400P import LoadLD400P  # TODO sort out the inconsistent name for laods.
from .psu.bk_precision.bk9130 import PSUInterface9130
from .psu.tti.mx100tp import PSUInterfaceMX100TP

_list_devices = [
    DMMInterfaceK2701,
    LoadHP605A,
    LoadLD400P,
    PSUInterface9130,
    PSUInterfaceMX100TP,
    AardvarkI2CSPI,
    AardvarkGPIO
]

DICT_DEVICES = {
    dev.__name__: dev for dev in _list_devices
}
