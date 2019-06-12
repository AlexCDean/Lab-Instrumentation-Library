from ..psu_interface import PSUInterface
from ...common import scpi_commands as cmds


# This is 1 indexed not 0 index.
class PSUInterfaceMX100TP(PSUInterface):
    _model = "MX100TP"

    def get_current(self, chan=None):
        if chan is None:
            raise ValueError
        return self.resource.query('I%iO?' % chan)

    def get_voltage(self, chan=None):
        if chan is None:
            raise ValueError
        return self.resource.query('V%iO?' % chan)

    def set_voltage(self, volts, chan=None):
        if chan is None:
            raise ValueError
        self.resource.write("V%i %f" % (chan, volts))

    def set_current(self, amps, chan=None):
        if chan is None:
            raise ValueError
        self.resource.write("I%i %f" % (chan, amps))

    def get_identity(self):
        return self.resource.query(cmds.SCPI_IDENTIFY)

    def switch_on(self, chan=None):
        if chan is None:
            raise ValueError
        self.resource.write('OP%i 1' % chan)

    def switch_off(self, chan=None):
        if chan is None:
            raise ValueError
        self.resource.write('OP%i 0' % chan)

    def set_local(self):
        self.resource.write('LOCAL')
