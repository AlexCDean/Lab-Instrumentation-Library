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
            raise ValueError
        self.resource.write(f"INST {CHAN_STRINGS[chan]}")
        ret_val = self.resource.query(f'INST?')
        if ret_val != CHAN_STRINGS[chan]:
            pass
            # TODO error handling here.

    def get_current(self, chan=None):
        self._set_channel(chan)
        return self.resource.query('CURR?')

    def get_voltage(self, chan=None):
        self._set_channel(chan)
        # TODO return as string or number?
        return self.resource.query('VOLT?')

    def set_voltage(self, volts, chan=None):
        self._set_channel(chan)
        self.resource.write(f"VOLT {volts}")

    def set_current(self, amps, chan=None):
        self._set_channel(chan)
        self.resource.write(f"CURR {amps}")

    def get_identity(self):
        return self.resource.query(cmds.SCPI_IDENTIFY)

    def switch_on(self, chan=None):
        self._set_channel(chan)
        self.resource.write('OUTP 1')

    def switch_off(self, chan=None):
        self._set_channel(chan)
        self.resource.write('OUTP 0')

    def set_local(self):
        self.resource.write('LOCAL')
