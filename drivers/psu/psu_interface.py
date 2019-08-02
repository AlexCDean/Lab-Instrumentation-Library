from ...drivers.base_instrument_interface import BaseInterface


class PSUInterface(BaseInterface):
    _model = ""

    def __init__(self, **kwargs):
        self.resource = kwargs.pop('resource', None)
        self.serial = kwargs.pop('serial', None)
        if self.resource is None and self.serial is not None:
            if isinstance(self.serial, int):
                self.serial = str(self.serial)
            self.find_by_serial(self.serial)

    def set_local(self):
        raise NotImplementedError

    def query_set_current(self, chan=None):
        raise NotImplementedError

    def query_set_voltage(self, chan=None):
        raise NotImplementedError

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
