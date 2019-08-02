from ..drivers.utilities import list_devices, get_device
from ..drivers.common.scpi_commands import SCPI_IDENTIFY
from ..errors import VisaIOError


class BaseInterface():
    _model = ""

    def __init__(self, **kwargs):
        self.resource = kwargs.pop('resource', None)
        self.serial = kwargs.pop('serial', None)
        if self.resource is None and self.serial is not None:
            self.find_by_serial(self.serial)

    def _parse_string(self, string, _type):
        try:
            return _type(string)
        except ValueError:
            # TODO I am not sure if IO error is the correct exception to raise.
            # My reasoning is that we expect a pre-determined format from the inst
            # and if that predetermined value does not match the format then
            # something is wrong or has gone wrong.
            raise IOError(
                f"Error: {self._model}:{self.serial} Encountered an unknown value" +
                f"to parse: {string}"
            )

    def _query(self, _str):
        try:
            return self.resource.query(_str)
        except VisaIOError:
            raise IOError(
                f"Error: {self._model}:{self.serial} Query [{_str}] timed out"
            )

    def _write(self, _str):
        try:
            return self.resource.write(_str)
        except VisaIOError:
            raise IOError(
                f"Error: {self._model}:{self.serial} Write [{_str}] timed out"
            )

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
