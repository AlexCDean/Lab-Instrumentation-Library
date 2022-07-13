from enum import Enum
from multiprocessing import connection
import time
from statistics import mean

# TODO: make this configurable, maybe env variable?
ADDRESS = '/tmp/ATE.socket'


class VirtualInstrumetType(Enum):
    PSU = 1
    LOAD = 2
    DMM = 3
    SCOPE = 4

    GPIO = 20

    I2C_BUS = 30
    SPI_BUS = 31


class VirtualPSUCommands(Enum):
    ENABLE = 1
    SET_VOLTAGE = 2
    SET_CURRENT = 3
    GET_VOLTAGE = 4
    GET_CURRENT = 5
    QUERY_SET_VOLTAGE = 6
    QUERY_SET_CURRENT = 7


class VirtualDMMCommands(Enum):
    GET_VOLTAGE_DC = 1
    GET_VOLTAGE_AC = 2
    GET_IMPEDANCE = 3


class VirtualLoadCommands(Enum):
    ENABLE = 1
    SET_MODE = 2
    SET_VALUE = 3
    GET_VOLTAGE = 4
    GET_CURRENT = 5
    QUERY_SET_MODE = 6
    QUERY_SET_VALUE = 7


class VirtualLoadModes(Enum):
    CURRENT = 1
    RESISTANCE = 2
    VOLTAGE = 3
    CONDUCTANCE = 4


class VirtualGPIOCommands(Enum):
    SET_OUTPUT = 1
    SET_INPUT = 2
    GET_VALUE = 3


class VirtualScopeCommands(Enum):
    ENABLE = 1      # channel, state
    SET_TRIGGER = 2 # channel, direction. level
    ARM = 3         # dt, pretrig_samples, posttrig_samples
    STOP = 4
    IS_READY = 5
    GET_DATA = 6    # channel


def _chan_to_int(chan):
    return int(chan) if chan is not None else None


class VirtualInterface:
    _model = "NotSet"
    _type = 0
    _connection = None

    def __init__(self, *args, serial=None, **kwargs):
        self._serial = serial
        if self._type:
            self._connect(self._type, serial)

    def _connect(self, _type, serial=None):
        if self._connection:
            self._connection.close()
            self._connection = None
        self._connection = connection.Client(ADDRESS)
        # TODO: handle exceptions here?
        try:
            t = _type.value
        except AttributeError:
            t = int(_type)
        self._query([0, t, serial])

    def _query(self, cmd, min_reply_length=0, timeout=1.0):
        result = None
        if self._connection:
            self._connection.send(cmd)
            if self._connection.poll(timeout):
                try:
                    result = self._connection.recv()
                except EOFError:
                    self._connection.close()
                    self._connection = None
        if result is None or not result[0]:
            raise IOError
        if len(result[1:]) < min_reply_length:
            raise IOError
        return result[1:]


class VirtualPSUInterface(VirtualInterface):
    _type = VirtualInstrumetType.PSU

    def get_current(self, chan=None):
        return self._query([VirtualPSUCommands.GET_CURRENT.value, _chan_to_int(chan)], 1)[0]

    def get_voltage(self, chan=None):
        return self._query([VirtualPSUCommands.GET_VOLTAGE.value, _chan_to_int(chan)], 1)[0]

    def query_set_current(self, chan):
        return self._query([VirtualPSUCommands.QUERY_SET_CURRENT.value, _chan_to_int(chan)], 1)[0]

    def query_set_voltage(self, chan):
        return self._query([VirtualPSUCommands.QUERY_SET_VOLTAGE.value, _chan_to_int(chan)], 1)[0]

    def set_voltage(self, volts, chan=None):
        self._query([VirtualPSUCommands.SET_VOLTAGE.value, _chan_to_int(chan), volts])

    def set_current(self, amps, chan=None):
        self._query([VirtualPSUCommands.SET_CURRENT.value, _chan_to_int(chan), amps])

    def switch_on(self, chan=None):
        self._query([VirtualPSUCommands.ENABLE.value, _chan_to_int(chan), True])

    def switch_off(self, chan=None):
        self._query([VirtualPSUCommands.ENABLE.value, _chan_to_int(chan), False])


class VirtualDMMInterface(VirtualInterface):
    _type = VirtualInstrumetType.DMM

    def get_voltage_dc(self, chan):
        return self._query([VirtualDMMCommands.GET_VOLTAGE_DC.value, _chan_to_int(chan)], 1)[0]

    def get_voltage_ac(self, chan):
        return self._query([VirtualDMMCommands.GET_VOLTAGE_AC.value, _chan_to_int(chan)], 1)[0]

    def get_impedance(self, chan):
        return self._query([VirtualDMMCommands.GET_IMPEDANCE.value, _chan_to_int(chan)], 1)[0]

    def enable_channel(self, chan):
        # no-op for now, probably ok like this in emulated system
        pass

    def disable_all_channels(self):
        # no-op for now, probably ok like this in emulated system
        pass


class VirtualLoadInterface(VirtualInterface):
    _type = VirtualInstrumetType.LOAD

    def set_mode_current(self):
        self._query([VirtualLoadCommands.SET_MODE.value, None, VirtualLoadModes.CURRENT.value])

    def set_mode_resistance(self):
        self._query([VirtualLoadCommands.SET_MODE.value, None, VirtualLoadModes.RESISTANCE.value])

    def set_mode_voltage(self):
        self._query([VirtualLoadCommands.SET_MODE.value, None, VirtualLoadModes.VOLTAGE.value])

    def set_mode_conductance(self):
        self._query([VirtualLoadCommands.SET_MODE.value, None, VirtualLoadModes.CONDUCTANCE.value])

    def set_level(self, chan, value):
        self._query([VirtualLoadCommands.SET_VALUE.value, chan, value])

    def set_active_channel(self, chan):
        # no-op
        pass

    def switch_on(self):
        self._query([VirtualLoadCommands.ENABLE.value, None, True])

    def switch_off(self):
        self._query([VirtualLoadCommands.ENABLE.value, None, False])

    def get_current_load(self):
        return self._query([VirtualLoadCommands.GET_CURRENT.value, None], 1)[0]

    def get_voltage_load(self):
        return self._query([VirtualLoadCommands.GET_VOLTAGE.value, None], 1)[0]

    def query_set_level(self, chan):
        # FIXME: quite unclear with chan param (used in HWInterface)
        return self._query([VirtualLoadCommands.QUERY_SET_VALUE.value, chan], 1)[0]


class VirtualScopeInterface(VirtualInterface):
    _type = VirtualInstrumetType.SCOPE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._channel_ac_coupling = set()
        self._channel_offest = {}
        self._dt = 1.0
        self._samples = 0
        self._pretrig_time = 0
        self._pretrig_samples = 0
        self._posttrig_samples = 0

    def set_channel_range(self, peak_voltage, chan=None):
        return

    def set_channel_coupling(self, ac_coupling, chan=None):
        if ac_coupling:
            self._channel_ac_coupling.add(chan)
        else:
            self._channel_ac_coupling.discard(chan)

    def set_channel_offset(self, offset, chan=None):
        self._channel_offest[chan] = offset

    def activate_channel(self, chan):
        self._query([VirtualScopeCommands.ENABLE.value, chan, True])

    def deactivate_channel(self, chan):
        self._query([VirtualScopeCommands.ENABLE.value, chan, False])

    def is_ready(self):
        return self._query([VirtualScopeCommands.IS_READY.value])[0]

    def set_timebase(self, duration=None, samples=None, sample_time=None):
        if len([1 for x in [duration, samples, sample_time] if x]) != 2:
            raise ValueError('set_timebase() needs exactly two arguments set')
        self._dt = sample_time if sample_time else duration / samples
        self._samples = samples if samples else duration // sample_time
        # TODO: should we somehow implement emulated oversampling here too?

    def clear_trigger(self, chan=None):
        self._posttrig_samples = self._samples
        self._pretrig_samples = 0
        self._query([VirtualScopeCommands.SET_TRIGGER.value, None, None, None])

    def set_trigger(self, chan, direction, level=0, pretrig=0):
        self._pretrig_time = pretrig
        level = level - self._channel_offest.get(chan, 0)
        # Note AC trigger does not work correctly because of postprocessed AC conversion!!
        self._query([VirtualScopeCommands.SET_TRIGGER.value, chan, direction, level])

    def arm(self):
        self._pretrig_samples = self._pretrig_time // self._dt
        self._posttrig_samples = self._samples - self._pretrig_samples
        self._query([VirtualScopeCommands.ARM.value, self._dt, int(self._pretrig_samples), int(self._posttrig_samples)])

    def fetch(self, chan, max_wait=None):
        delay = 0.1
        if max_wait is not None:
            timeout = time.monotonic() + max_wait
            if delay > max_wait / 10:
                delay = max_wait / 10
        while not self.is_ready():
            if max_wait is not None and time.monotonic() > timeout:
                return (None, [])
            time.sleep(delay)

        data = self._query([VirtualScopeCommands.GET_DATA.value, chan])[0]
        if data is None:
            return (data, False)
        if chan in self._channel_ac_coupling:
            # Quick&dirty implementation: this is a bit of cheating, real AC coupling should follow the test point
            # voltage through some lowpass, but subtracting the mean should be enough for now.
            m = mean(data)
        else:
            m = -self._channel_offest.get(chan, 0)
        data = [x - m for x in data]
        return (data, False)

    def get_time_axis(self, chan=None):
        if not self.is_ready():
            return None
        return [x * self._dt for x in range(int(self._pretrig_samples), int(self._posttrig_samples))]

    def stop(self):
        self._query([VirtualScopeCommands.STOP.value])


class VirtualAardvarkInterface(VirtualInterface):
    _type_list = {
        "i2c": VirtualInstrumetType.I2C_BUS,
        "spi": VirtualInstrumetType.SPI_BUS,
        "gpio": VirtualInstrumetType.GPIO
    }
    _active_type = 0

    def _configure(self, t):
        if self._active_type != self._type_list[t]:
            self._connect(self._type_list[t], self._serial)
            self._active_type = self._type_list[t]

    def i2c_write_read(self, slave_addr, data_out, num_bytes_read, delay_ms):
        self._configure("i2c")
        # Command number sent is "1", not sure if there is any use for more commands, but keep it there for possible
        # extension in future.
        # Status is returned as a first item (TBD), but the instrumentation library and protocol library are obviously
        # fine with returning zero-length data. We can eventually raise IOError in case of I2C failure, but likely not
        # too important anyway.
        status, reply = self._query([1, None,
                                     int(slave_addr), data_out, int(num_bytes_read)], 2)[0:2]
        return (len(reply), reply)

    def gpio_set_output(self, chan, value):
        self._configure("gpio")
        self._query([VirtualGPIOCommands.SET_OUTPUT.value, _chan_to_int(chan), bool(value)])

    def gpio_set_input(self, chan, pull_up):
        self._configure("gpio")
        self._query([VirtualGPIOCommands.SET_INPUT.value, _chan_to_int(chan), bool(pull_up)])

    def gpio_read_input(self, chan):
        self._configure("gpio")
        return self._query([VirtualGPIOCommands.GET_VALUE.value, _chan_to_int(chan)], 1)[0]


class VirtualI2CInterface(VirtualInterface):
    _type = VirtualInstrumetType.I2C_BUS

    def i2c_write_read(self, slave_addr, data_out, num_bytes_read, delay_ms):
        # Command number sent is "1", not sure if there is any use for more commands, but keep it there for possible
        # extension in future.
        # Status is returned as a first item (TBD), but the instrumentation library and protocol library are obviously
        # fine with returning zero-length data. We can eventually raise IOError in case of I2C failure, but likely not
        # too important anyway.
        status, reply = self._query([1, None, int(slave_addr), data_out, int(num_bytes_read)], 2)[0:2]
        return (len(reply), reply)


class VirtualSPIInterface(VirtualInterface):
    _type = VirtualInstrumetType.SPI_BUS


class VirtualGPIOInterface(VirtualInterface):
    _type = VirtualInstrumetType.GPIO

    def gpio_set_output(self, chan, value):
        self._query([VirtualGPIOCommands.SET_OUTPUT.value, _chan_to_int(chan), bool(value)])

    def gpio_set_input(self, chan, pull_up):
        self._query([VirtualGPIOCommands.SET_INPUT.value, _chan_to_int(chan), bool(pull_up)])

    def gpio_read_input(self, chan):
        return self._query([VirtualGPIOCommands.GET_VALUE.value, _chan_to_int(chan)], 1)[0]

