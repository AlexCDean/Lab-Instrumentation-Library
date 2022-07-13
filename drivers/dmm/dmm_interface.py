from ..base_instrument_interface import BaseInterface


class DMMInterface(BaseInterface):
    def enable_channel(self, chan):
        raise NotImplementedError

    def disable_channel(self, chan):
        raise NotImplementedError
        
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

    def get_mac_address(self):
        raise NotImplementedError

    def get_serial_id(self):
        raise NotImplementedError