from ...drivers.utilities import list_devices, get_device
from ...drivers.common.scpi_commands import SCPI_IDENTIFY
from ...errors import VisaIOError


class DMMInterface():
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

    def get_voltage_dc(self, chan):
        raise NotImplementedError

    def get_voltage_ac(self, chan):
        raise NotImplementedError

    def get_temperature(self, chan):
        raise NotImplementedError

    def get_impedance(self, chan):
        raise NotImplementedError

    def get_current(self, chan):
        raise NotImplementedError

    def get_identity(self):
        raise NotImplementedError
