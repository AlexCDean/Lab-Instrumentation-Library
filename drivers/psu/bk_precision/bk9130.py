from ...psu.psu_interface import PSUInterface
from ...common import scpi_commands as cmds


class PSUInterface9130(PSUInterface):
    _model = "bk9130"
    channels = [1, 2, 3]
    def __init__(self, **kwargs):
        # TODO we do not use BK9130s and this was developed theoretically. 
        raise NotImplementedError("Not tested on BK9130s")
        super().__init__(**kwargs)
        if self.resource:
            self.resource.write_termination = '\n'
            self.resource.read_termination = '\n'

    def _sel_chan(self, chan):
        if chan not in self.channels:
            raise ValueError
        self._write(f'INST:NSEL {chan}')  # TODO try out.

    def get_current(self, chan=None):
        self._sel_chan(chan)
        return self.resource.query('MEAS:CURR?')

    def get_voltage(self, chan=None):
        self._sel_chan(chan)
        return self.resource.query('MEAS:VOLT?')

    def set_voltage(self, volts, chan=None):
        self._sel_chan(chan)
        volts *= 1000.0
        self._write('VOLT %imV' % volts)

    def set_current(self, amps, chan=None):
        self._sel_chan(chan)
        amps *= 1000.0
        self._write('CURR %imA')

    def switch_on(self, chan=None):
        self._sel_chan(chan)
        self._write('OUTP 1')

    def switch_off(self, chan=None):
        self._sel_chan(chan)
        self._write('OUTP 0')

    def get_identity(self):
        return self.resource.query(cmds.SCPI_IDENTIFY)

    def set_local(self):
        self._write('SYST:LOC')
