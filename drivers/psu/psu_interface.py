from ...drivers.utilities import list_devices, get_device
from ...drivers.common.scpi_commands import SCPI_IDENTIFY
from ...errors import VisaIOError


class PSUInterface():
    _model = ""

    def __init__(self, **kwargs):
        self.resource = kwargs.pop('resource', None)
        self.serial = kwargs.pop('serial', None)
        if self.resource is None and self.serial is not None:
            self.find_by_serial(self.serial)

    def set_local(self):
        raise NotImplementedError

    def find_by_serial(self, serial):
        if not self._model:
            print(f"{self.__class__.__name__} interface does not have model defined yet")
            raise NotImplementedError
        for d in list_devices():
            dev = get_device(d)
            try:
                identity = dev.query(SCPI_IDENTIFY)
            except VisaIOError:
                continue
            if self._model in identity:
                if self.serial in identity:
                    self.resource = dev
                    return

    # Current return should be int amps.
    def get_current(self, chan=None):
        raise NotImplementedError

    # volt return should be int volts.
    def get_voltage(self, chan=None):
        raise NotImplementedError

    def set_voltage(self, volts, chan=None):
        raise NotImplementedError

    def set_current(self, amps, chan=None):
        raise NotImplementedError

    def get_identity(self):
        raise NotImplementedError

    def switch_on(self, chan=None):
        raise NotImplementedError

    def switch_off(self, chan=None):
        raise NotImplementedError
