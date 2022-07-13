from ..dmm_interface import DMMInterface
from ...common.errors import BadData
from ...common.scpi_commands import SCPI_IDENTIFY, SCPI_IDENTIFY_OPTIONS_QUERY

MODULES_CHAN_CAPABILITY = {
    "7700": 20,
    "7701": 32,
    "7702": 40,
    "7703": 32,
    "7708": 40,
    "NONE": 0
}

# Chan usage: Indexed from 1 to 40. 
class KeithleyInterface(DMMInterface):
    # Default values
    overflow_number = 9.9E37
    index_serial = 2
    identity_delimiter = ','

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.query_modules_slots()

    def query_modules_slots(self):
        reply = self._query(SCPI_IDENTIFY_OPTIONS_QUERY)
        # Clean and convert to list. Expected return is e.g "7702, 7700, NONE, etc."
        #TODO: make this also work with software control on/off if we see x13/x11
        modules = reply.replace(' ', '').split(',')

        # Iterate through each module to calculate max channels & a list of all modules' channels
        self.slot_channels = []
        max_channels = 0
        for module in modules:
            module_channels = MODULES_CHAN_CAPABILITY[module]
            self.slot_channels.append(module_channels)
            max_channels = max_channels + module_channels

        # Autoconfigure list of valid channels. 
        self.channels = [i for i in range(1, max_channels+1)]
        return reply


    def convert_chan(self, chan):        
        return self._get_slot_channel_str(*self._get_slot_channel_value(chan))

    def disable_all_channels(self):
        """
        Opens all relays in the keithley slots.
        """
        cmd = "ROUTe:OPEN:ALL"
        self._write(cmd)

    def enable_channel(self, chan):
        """
        Closes the relay on that channel
        """
        cmd = f"ROUTe:CLOSE {self.convert_chan(chan)}"
        self._write(cmd)

    def _get_slot_channel_value(self, chan):
        if chan not in self.channels:
            raise ValueError(f"Invalid {self._model} channel selected: {chan}")
        # Convert a raw channel number to a particular slot's channel
        n = 0
        slot = 1
        for slot_channel in self.slot_channels:
            n = n + slot_channel
            if chan <= n:
                break
            else:
                slot = slot + 1

        return slot, abs(chan - (n - slot_channel))

    def _get_slot_channel_str(self, slot, chan):
        if chan not in self.channels:
            raise ValueError(f"Invalid {self._model} channel selected: {chan}")
        return f'(@{slot}{chan:02d})'

    def _parse_string_data(self, units, string, chan):
        try:
            # TODO regex will simplify this massively. 
            value_str = string.split(',')[0]
            if units in value_str:
                value_str = value_str.split(units)[0]
            value = float(value_str)
            if value == self.overflow_number:
                raise BadData(f"Error: Overflow on {chan}")
            return value
        except (ValueError, IndexError):
            raise BadData

    def get_voltage_dc(self, chan):
        units = 'VDC'
        cmd = f'MEASure:VOLTage:DC? {self.convert_chan(chan)}'
        raw = self._query(cmd)
        if isinstance(raw, str):
            return self._parse_string_data(units, raw, chan)
        else:
            return raw

    def get_impedance(self, chan):
        units = 'OHM'
        cmd = f'MEASure:RESistance? {self.convert_chan(chan)}'

        raw = self._query(cmd)

        if isinstance(raw, str):
            return self._parse_string_data(units, raw, chan)
        else:
            return raw

    def get_voltage_ac(self, chan):
        units = 'VAC'        
        cmd = f'MEASure:VOLTage:AC? {self.convert_chan(chan)}'
        raw = self._query(cmd)
        if isinstance(raw, str):
            return self._parse_string_data(units, raw, chan)
        else:
            return raw

    def get_temperature(self, chan):
        units = 'C'        
        cmd = f'MEAS:TEMP? {self.convert_chan(chan)}'

        raw = self._query(cmd)
        if isinstance(raw, str):
            return self._parse_string_data(units, raw, chan)
        else:
            return raw

    def get_mac_address(self):
        cmd = 'SYST:COMM:ETH:MAC?'
        raw = self._query(cmd)
        return raw

    def get_serial_id(self):
        cmd = SCPI_IDENTIFY
        raw = self._query(cmd)
        ls_substrings = raw.split(self.identity_delimiter)

        try:
            return ls_substrings[self.index_serial]
        except IndexError:
            return IOError("Error: Could not get serial number")