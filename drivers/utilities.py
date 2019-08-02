import visa
import struct
from .common.visa.path import VISA_DLL_PATH_64, VISA_DLL_PATH_32


def list_devices(path=None):
    if path is None:
        path = _auto_choose_path()
        if path is None:
            print("Could not choose correct visa path!")
            return None
    rm = visa.ResourceManager(path)
    return rm.list_resources()


def get_device(resource, path=None):
    if path is None:
        path = _auto_choose_path()
        if path is None:
            print("Could not choose correct visa path!")
            return None
    rm = visa.ResourceManager(path)
    try:
        return rm.open_resource(resource)
    except visa.VisaIOError as err:
        raise IOError(err)  # Resource is busy or non-existent.


def _auto_choose_path():
    if (struct.calcsize("P") * 8) == 64:
        return VISA_DLL_PATH_64
    elif (struct.calcsize("P") * 8) == 32:
        return VISA_DLL_PATH_32
    else:
        return None