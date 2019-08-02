from ..psu_interface import PSUInterface
from ...common import scpi_commands as cmds

CHAN_STRINGS = {
    1: "OUT1",
    2: "OUT2",
    3: "OUT3"
}


class PSUInterfaceHMP4030(PSUInterface):
    _model = "HMP4030"

    def _set_channel(self, chan):
        if chan is None:
            raise ValueError(f'Error: No channel specified on {self._model}:{self.serial}')
        self.resource.write(f"INST {CHAN_STRINGS[chan]}")
        # This command returns OUTP1 instead of OUT1
        ret_val = self.resource.query(f'INST?').replace('P', '').replace('\n', '')

        if ret_val != CHAN_STRINGS[chan]:
            raise IOError(f"Error: Setting channel on {self._model}:{self.serial} Failed")

    def get_current(self, chan=None):
        self._set_channel(chan)
        ret_val = self._query('MEAS:CURR?')
        return self._parse_string(ret_val, float)

    def get_voltage(self, chan=None):
        self._set_channel(chan)
        ret_val = self._query('MEAS:VOLT?')
        return self._parse_string(ret_val, float)

    def query_set_voltage(self, chan):
        self._set_channel(chan)
        ret_val = self._query('VOLT?')
        return self._parse_string(ret_val, float)

    def query_set_current(self, chan):
        self._set_channel(chan)
        ret_val = self._query('CURR?')
        return self._parse_string(ret_val, float)

    def set_voltage(self, volts, chan=None):
        self._set_channel(chan)
        self.resource.write(f"VOLT {volts}")

    def set_current(self, amps, chan=None):
        self._set_channel(chan)
        self.resource.write(f"CURR {amps}")

    def get_identity(self):
        return self._query(cmds.SCPI_IDENTIFY)

    def switch_on(self, chan=None):
        self._set_channel(chan)
        self.resource.write('OUTP 1')

    def switch_off(self, chan=None):
        self._set_channel(chan)
        self.resource.write('OUTP 0')

    def set_local(self):
        self.resource.write('SYST:LOC')
