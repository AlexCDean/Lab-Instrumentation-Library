from ..load_interface import LoadInterface
from ....drivers.common import scpi_commands as cmds
import visa


class LoadHP605A(LoadInterface):
    def get_identity(self):
        return self.resource.query(cmds.SCPI_IDENTIFY)

    def _sel_chan(self, chan):
        if chan is None:
            print("No channel selected")
            raise ValueError
        self.resource.write("CHAN %i" % chan)

    def input_on(self, chan=None):
        self._sel_chan(chan)
        self.resource.write("INPUT ON")

    def input_off(self, chan=None):
        self._sel_chan(chan)
        self.resource.write("INPUT OFF")

    def set_current_load(self, current, chan=None):
        self._sel_chan(chan)
        self.resource.write('CURR %f' % current)

    def get_current_load(self, chan=None):
        self._sel_chan(chan)
        return self.resource.query('MEAS:CURR?')

    def set_voltage_load(self, voltage, chan=None):
        self._sel_chan(chan)
        self.resource.write('VOLT:TRIG  %f' % voltage)

    def get_voltage_load(self, chan=None):
        self._sel_chan(chan)
        return self.resource.query('MEAS:VOLT?')

    def set_resistance_load(self, ohms, chan=None):
        self._sel_chan(chan)
        self.resource.write('RES %i' % ohms)

    def set_mode_current(self, chan=None):
        self._sel_chan(chan)
        self.resource.write('MODE:CURR')

    def set_mode_voltage(self, chan=None):
        self._sel_chan(chan)
        self.resource.write('MODE:VOLT')

    def set_mode_resistance(self, chan=None):
        self._sel_chan(chan)
        self.resource.write('MODE:RES')
