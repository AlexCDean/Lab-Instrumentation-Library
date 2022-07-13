from ...psu.psu_interface import PSUInterface
from ...common import scpi_commands as cmds




class PSUInterfaceHMP4030(PSUInterface):
    _model = "HMP4030"
    channels = [1, 2, 3]
    CHAN_STRINGS = {
        1: "OUT1",
        2: "OUT2",
        3: "OUT3"
    }
    
    def _set_channel(self, chan):
        if chan not in self.channels:
            raise ValueError(
                f'Error: No channel specified on {self._model}'
            )
        self._write(f"INST {self.CHAN_STRINGS[chan]}")
        # This command returns OUTP1 instead of OUT1
        ret_val = self._query(f'INST?').replace('P', '').replace('\n', '')

        if ret_val != self.CHAN_STRINGS[chan]:
            raise IOError(
                f"Error: Setting channel on {self._model} Failed"
            )

    def get_current(self, chan=None):
        self._set_channel(chan)        
        return self.response_to_float(self._query('MEAS:CURR?'))

    def get_voltage(self, chan=None):
        self._set_channel(chan)        
        return self.response_to_float(self._query('MEAS:VOLT?'))

    def query_set_voltage(self, chan):
        self._set_channel(chan)
        return self.response_to_float(self._query('VOLT?'))

    def query_set_current(self, chan):
        self._set_channel(chan)
        return self.response_to_float(self._query('CURR?'))

    def set_voltage(self, volts, chan):
        self._set_channel(chan)
        self._write(f"VOLT {volts}")

    def set_current(self, amps, chan):
        self._set_channel(chan)
        self._write(f"CURR {amps}")

    def get_identity(self):
        return self._query(cmds.SCPI_IDENTIFY)

    def switch_on(self, chan):
        self._set_channel(chan)
        self._write('OUTP 1')

    def switch_off(self, chan):
        self._set_channel(chan)
        self._write('OUTP 0')

    def set_local(self):
        self._write('SYST:LOC')
