from ...loads.load_interface import LoadInterface
from ...common import scpi_commands as cmds


class LoadInterfaceHP605A(LoadInterface):
    _model = "HP605A"
    def get_identity(self):
        return self._query(cmds.SCPI_IDENTIFY)

    def _sel_chan(self, chan):
        if chan is None:
            print("No channel selected")
            raise ValueError
        self._write(f"CHAN {chan}")

    def input_on(self, chan=None):
        self._sel_chan(chan)
        self._write("INPUT ON")

    def input_off(self, chan=None):
        self._sel_chan(chan)
        self._write("INPUT OFF")

    def set_current_load(self, current, chan=None):
        self._sel_chan(chan)
        self._write('CURR %f' % current)

    def get_current_load(self, chan=None):
        self._sel_chan(chan)
        return self.response_to_float(self._query('MEAS:CURR?'))

    def set_voltage_load(self, voltage, chan=None):
        self._sel_chan(chan)
        self._write('VOLT:TRIG  %f' % voltage)

    def get_voltage_load(self, chan=None):
        self._sel_chan(chan)
        return self.response_to_float(self._query('MEAS:VOLT?'))

    def set_resistance_load(self, ohms, chan=None):
        self._sel_chan(chan)
        self._write('RES %i' % ohms)

    def set_mode_current(self, chan=None):
        self._sel_chan(chan)
        self._write('MODE:CURR')

    def set_mode_voltage(self, chan=None):
        self._sel_chan(chan)
        self._write('MODE:VOLT')

    def set_mode_resistance(self, chan=None):
        self._sel_chan(chan)
        self._write('MODE:RES')
