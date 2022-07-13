from typing import IO
from ..base_instrument_interface import BaseInterface


class PSUInterface(BaseInterface):

    def set_local(self):
        raise NotImplementedError

    def query_set_current(self, chan=None):
        raise NotImplementedError

    def query_set_voltage(self, chan=None):
        raise NotImplementedError

    # Current return should be float amps.
    def get_current(self, chan=None):
        raise NotImplementedError

    # volt return should be float volts.
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

    def is_switched_on(self, chan=None):
        raise NotImplementedError