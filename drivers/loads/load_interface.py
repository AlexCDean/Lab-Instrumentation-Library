from ...drivers.utilities import list_devices, get_device
from ...drivers.common.scpi_commands import SCPI_IDENTIFY
from ...errors import VisaIOError


class LoadInterface():
    _model = ""

    def __init__(self, **kwargs):
        self.resource = kwargs.pop('resource', None)
        self.serial = kwargs.pop('serial', None)
        if self.resource is None and self.serial is not None:
            self.find_by_serial(self.serial)

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

    def set_level(self, value, chan=None):
        raise NotImplementedError

    def set_active_channel(self, chan=None):
        raise NotImplementedError

    def set_resistance_load(self, ohms, chan=None):
        raise NotImplementedError

    def get_resistance_load(self, chan=None):
        raise NotImplementedError

    def set_current_load(self, chan=None):
        raise NotImplementedError

    def get_current_load(self, chan=None):
        raise NotImplementedError

    def set_mode_resistance(self, chan=None):
        raise NotImplementedError

    def set_mode_conductance(self):
        raise NotImplementedError

    def set_mode_voltage(self):
        raise NotImplementedError

    def get_mode(self):
        raise NotImplementedError

    def set_range_high(self):
        raise NotImplementedError

    def set_range_low(self):
        raise NotImplementedError

    def get_range(self):
        raise NotImplementedError

    def get_voltage_load(self, chan=None):
        raise NotImplementedError

    def set_voltage_load(self, chan=None):
        raise NotImplementedError

    def switch_on(self, chan=None):
        raise NotImplementedError

    def switch_off(self, chan=None):
        raise NotImplementedError

    def get_identity(self):
        raise NotImplementedError
