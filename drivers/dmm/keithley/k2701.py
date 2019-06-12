from ..dmm_interface import DMMInterface
from ....errors import BadData
import visa
MAX_SLOT_CHANNELS = 20
MAX_SLOTS = 2
SLOT_ONE = 1
SLOT_TWO = 2


# Chan usage: Indexed from 1 to 40. should maybe consider 0 index.
class DMMInterfaceK2701(DMMInterface):
    _model = "KEITHLEY"
    overflow_number = 9.9E37

    def disable_all_channels(self):
        """
        Opens all relays in the keithley slots.
        """
        cmd = "ROUTe:OPEN:ALL"
        self.resource.write(cmd)
        # TODO error handling here - check number of open channels etc.
        # Return an error code or OK?

    def enable_channel(self, chan):
        """
        Closes the relay on that channel
        """
        slot, chan = self._get_slot_channel_value(chan)
        slot_chan_str = self._get_slot_channel_str(slot, chan)
        cmd = f"ROUTe:CLOSE {slot_chan_str}"
        self.resource.write(cmd)
        # TODO error handling.

    def _get_slot_channel_value(self, chan):
        if chan > MAX_SLOT_CHANNELS:
            return SLOT_TWO, abs(chan-MAX_SLOT_CHANNELS)
        else:
            return SLOT_ONE, chan

    def _get_slot_channel_str(self, slot, chan):
        return '(@%s%s)' % (str(slot).zfill(1), str(chan).zfill(2))

    def _parse_string_data(self, units, string, chan):
        try:
            value_str = string.split(',')[0]
            if units in value_str:
                value_str = value_str.split(units)[0]
            value = float(value_str)
            if value == self.overflow_number:
                raise BadData(f"Error: Overflow on {chan}")
            return value
        except (ValueError, IndexError):
            raise BadData

    def get_voltage_dc(self, chan=None):
        units = 'VDC'
        if chan is None:
            raise ValueError
        slot, chan = self._get_slot_channel_value(chan)
        cmd = 'MEASure:VOLTage:DC? %s' % self._get_slot_channel_str(slot, chan)
        raw = self.resource.query(cmd)
        if isinstance(raw, str):
            return self._parse_string_data(units, raw, chan)
        else:
            return raw

    def get_impedance(self, chan=None):
        units = 'OHM'
        if chan is None:
            raise ValueError
        slot, chan = self._get_slot_channel_value(chan)
        slot_chan_str = self._get_slot_channel_str(slot, chan)
        cmd = f'MEASure:RESistance? {slot_chan_str}'
        raw = self.resource.query(cmd)
        if isinstance(raw, str):
            return self._parse_string_data(units, raw, chan)
        else:
            return raw

    def get_voltage_ac(self, chan=None):
        units = 'VAC'
        if chan is None:
            raise ValueError
        slot, chan = self._get_slot_channel_value(chan)
        cmd = 'MEASure:VOLTage:AC? %s' % self._get_slot_channel_str(slot, chan)
        raw = self.resource.query(cmd)
        if isinstance(raw, str):
            return self._parse_string_data(units, raw, chan)
        else:
            return raw

    def get_temperature(self, chan=None):
        units = 'C'
        if chan is None:
            raise ValueError
        slot, chan = self._get_slot_channel_value(chan)
        cmd = 'MEAS:TEMP? %s' % self._get_slot_channel_str(slot, chan)
        raw = self.resource.query(cmd)
        if isinstance(raw, str):
            return self._parse_string_data(units, raw, chan)
        else:
            return raw

