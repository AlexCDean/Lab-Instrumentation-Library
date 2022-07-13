from ..base_instrument_interface import BaseInterface


class LoadInterface(BaseInterface):

    def set_level(self, value, chan=None):
        raise NotImplementedError

    def get_active_channel(self):
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
