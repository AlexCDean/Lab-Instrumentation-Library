from ...psu.psu_interface import PSUInterface
from ...common import scpi_commands as cmds


# This is 1 indexed not 0 index.
class PSUInterfaceMX100TP(PSUInterface):
    _model = "MX100TP"
    channels = [1, 2, 3]
    
    def get_current(self, chan):
        if chan not in self.channels:
            raise ValueError
        return self.response_to_float(self._query(f'I{chan}O?'))

    def get_voltage(self, chan):
        if chan not in self.channels:
            raise ValueError
        return self.response_to_float(self._query(f'V{chan}O?'))

    def query_set_current(self, chan):
        if chan not in self.channels:
            raise ValueError
        return self.response_to_float(self._query(f"I{chan}?"))

    def query_set_voltage(self, chan):
        if chan not in self.channels:
            raise ValueError
        return self.response_to_float(self._query(f"V{chan}?"))

    def set_voltage(self, volts, chan):
        if chan not in self.channels:
            raise ValueError
        self._write(f"V{chan} {volts}")

    def set_current(self, amps, chan):
        if chan not in self.channels:
            raise ValueError
        self._write(f"I{chan} {amps}")

    def get_identity(self):
        return self._query(cmds.SCPI_IDENTIFY)

    def switch_on(self, chan):
        if chan not in self.channels:
            raise ValueError
        self._write(f'OP{chan} 1')

    def switch_off(self, chan):
        if chan not in self.channels:
            raise ValueError
        self._write(f'OP{chan} 0')

    def is_switched_on(self, chan):
        if chan not in self.channels:
            raise ValueError                
        return int(self._query(f"OP{chan}?")) == 1


    def set_local(self):
        self._write('LOCAL')
