from ...psu.psu_interface import PSUInterface
from ...common import scpi_commands as cmds


# This is 1 indexed not 0 index.
class PSUInterfaceQL355P(PSUInterface):
    _model = "QL355P"
    channels = [1]

    def get_current(self):
        return self.response_to_float(self._query('I1O?'))

    def get_voltage(self):
        return self.response_to_float(self._query('V1O?'))

    def query_set_current(self):
        return self.response_to_float(self._query('I1?'))

    def query_set_voltage(self):
        return self.response_to_float(self._query('V1?'))

    def set_voltage(self, volts):
        self.resource.write("V1 {:f}".format(volts))

    def set_current(self, amps):
        self.resource.write("I1 {:f}".format(amps))

    def get_identity(self):
        return self._query(cmds.SCPI_IDENTIFY)

    def switch_on(self):
        self.resource.write('OP1 1')

    def switch_off(self):
        self.resource.write('OP1 0')

    def set_local(self):
        self.resource.write('LOCAL')
