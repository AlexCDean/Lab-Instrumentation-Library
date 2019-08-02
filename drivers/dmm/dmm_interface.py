from ...drivers.base_instrument_interface import BaseInterface


class DMMInterface(BaseInterface):
    _model = ""

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
