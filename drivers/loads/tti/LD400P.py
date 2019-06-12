from ..load_interface import LoadInterface
from ...common import scpi_commands as cmds
# from ...drivers.common import scpi_commands as cmds


class LoadLD400P(LoadInterface):
    _model = "LD400P"

    def get_identity(self):
        return self.resource.query(cmds.SCPI_IDENTIFY)

    def switch_on(self):
        self.resource.write('INP 1')

    def switch_off(self):
        self.resource.write('INP 0')

    def set_mode_current(self):
        self.resource.write('MODE C')

    def set_mode_power(self):
        self.resource.write('MODE P')

    def set_mode_resistance(self):
        self.resource.write('MODE R')

    def set_mode_conductance(self):
        self.resource.write('MODE G')

    def set_mode_voltage(self):
        self.resource.write('MODE V')

    def get_mode(self):
        return self.resource.query('MODE?')

    def set_range_high(self):
        self.resource.write('RANGE 0')

    def set_range_low(self):
        self.resource.write('RANGE 1')

    def get_range(self):
        return self.resource.query('RANGE?')

    def set_600W(self):
        self.resource.write('600W 1')

    def set_400W(self):
        self.resource.write('600W 0')

    def get_power_mode(self):
        self.resource.query('600W?')

    def _set_level_A(self, value):
        '''Sets the Level of A to value.
           Units are implied bu the present load mode'''
        self.resource.write('A %f' % value)

    def _set_level_B(self, value):
        '''Sets the Level of B to value.
           Units are implied bu the present load mode'''
        self.resource.write('B %f' % value)

    def get_level_A(self):
        return self.resource.query('A?')

    def get_level_B(self):
        return self.resource.query('B?')

    def _set_active_channel_A(self):
        self.resource.write('LVLSEL A')

    def _set_active_channel_B(self):
        self.resource.write('LVLSEL B')

    def get_current_load(self):
        return self.resource.query('I?')

    def get_voltage_load(self):
        return self.resource.query('V?')

    def set_level(self, chan, value):
        if chan == 0:
            self._set_level_A(value)
        elif chan == 1:
            self._set_level_B(value)
        else:
            raise ValueError

    def set_active_channel(self, chan):
        if chan == 0:
            self._set_active_channel_A()
        elif chan == 1:
            self._set_active_channel_B()
        else:
            raise ValueError
