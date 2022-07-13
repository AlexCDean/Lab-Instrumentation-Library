import ctypes
import ctypes.util
import sys
import math
import time
import numpy

from .pico_status import PicoStatus
from . import ps2000a_api, ps3000a_api


class PicoScopeException(Exception):
    pass


class PicoScopeNotFound(PicoScopeException):
    pass


def _to_pico_status(result, func, arguments):
    try:
        return PicoStatus(result)
    except ValueError:
        # TODO: something else what provides .value attribute etc?
        return result


def get_call(fapi, lib):
    restype, name, arg_info = fapi
    obj = getattr(lib, name)
    if restype is PicoStatus:
        # actual return value is c_type.c_uint32, but convert it to PicoStatus for Python code purposes
        obj.restype = ctypes.c_uint32
        obj.errcheck = _to_pico_status
    else:
        obj.restype = restype
    obj.argtypes = tuple(t for t, n in arg_info)
    return obj


class ChannelInfo():
    # For some strange (and undocumented as far as I see) reason passing too short buffer to he set_data_buffer()
    # leads to subsequent get_values() to fail with PICO_BUFFERS_NOT_SET error under some circumstances despite
    # set_data_buffer() returned PICO_OK and number of requested samples in get_values() is not higher than buffer
    # length.
    # Using the minimal buffer length limit does seem to help here.
    # Experimentally determined minimal value for number of samples is 7 with 3206MSO scope. No idea about other
    # scopes, using semi-random guess of 32 now, can be adjusted freely if necessary.
    MIN_BUFFER_LENGTH = 32

    def __init__(self, channel_idx, default_coupling, ranges, adc_max, adc_min):
        self.idx = channel_idx
        self._default_coupling = default_coupling
        self._ranges = ranges
        self._adc_max = adc_max
        self._adc_min = adc_min
        self.reset()
        self._data_buffer = None
        self.overflow = False
        self._max_buffer = (ctypes.c_int16 * self.MIN_BUFFER_LENGTH)()
        self._min_buffer = (ctypes.c_int16 * self.MIN_BUFFER_LENGTH)()

    def reset(self):
        self.active = False
        self.coupling = self._default_coupling
        self.rng, self.rng_volt = max(self._ranges, key=lambda itm: itm[1])
        self.offset = 0.0

    def set_range(self, min_voltage):
        # TODO: This can throw a ValueError if min_range is too high, is it OK to left it like this?
        self.rng, self.rng_volt = min(((i, v) for i, v in self._ranges if v >= min_voltage), key=lambda itm: itm[1])

    def to_adc_value(self, volts):
        return int(round((volts + self.offset) / self.rng_volt * self._adc_max))

    def set_buffer(self, samples):
        self._max_buffer[0] = 0
        self._min_buffer[0] = 0
        samples = max(samples, self.MIN_BUFFER_LENGTH)
        self._data_buffer = (ctypes.c_int16 * samples)()
        return self._data_buffer, samples

    def min_max_buffers(self):
        return self._max_buffer, self._min_buffer, self.MIN_BUFFER_LENGTH

    def decode_overflow(self, overflow_bitfield):
        self.overflow = bool(overflow_bitfield & (1 << self.idx))
        if not self.overflow:
            # if any sample was fullscale value, set overflow flag too
            self.overflow = (self._max_buffer[0] >= self._adc_max) or (self._max_buffer[0] <= self._adc_min)

    def get_data(self, capture_length):
        return (numpy.array(self._data_buffer[:capture_length],
                            dtype='float_') * self.rng_volt / self._adc_max - self.offset,
                self.overflow)

    def __str__(self):
        return '{}, {}, range: {} V, offset: {} V'.format(
            'ON' if self.active else 'OFF',
            self.coupling.name,
            self.rng_volt,
            self.offset)


class TriggerInfo:
    def __init__(self, channel, direction, level, pretrig):
        self.channel = channel
        self.direction = direction
        self.level = level
        self.pretrig = pretrig


class Picoscope():
    API = [
        ('2000a', ps2000a_api),
        ('3000a', ps3000a_api),
    ]

    def _open_unit(self, serial, use_api=None):
        if use_api is not None and use_api not in {n for n, a in self.API}:
            raise PicoScopeNotFound('Requested API library "{}" is not supported.'.format(use_api))

        for api_name, api in self.API:
            if use_api is not None and api_name != use_api:
                continue

            # FIXME: do we want find_library on windows?
            library_path = ctypes.util.find_library(api.LIBRARY)
            # TODO: should we handle exceptions here?
            try:
                if sys.platform == 'win32':
                    lib = ctypes.WinDLL(library_path)
                else:
                    lib = ctypes.cdll.LoadLibrary(library_path)
            except OSError as e:
                # TODO: what is the best way to report an issue?
                print('PicoSDK library not compatible (check 32 vs 64-bit): {}'.format(e), file=sys.stderr)
                # TODO: is it better to raise an exception here or continue
                continue

            c_handle = ctypes.c_int16()
            result = get_call(
                api.FUNCTION['open_unit'],
                lib
            )(c_handle, bytes(serial, 'ascii') if not isinstance(serial, bytes) else serial)

            if result == PicoStatus.PICO_NOT_FOUND:
                # try another library
                continue

            if result == PicoStatus.PICO_OK:
                # unit found
                self._handle = c_handle.value
                return api, lib

            # TODO: handle some special status cases like power supply issues ...
            # TODO: what is the best way to report an issue?
            print('Opening PicoScope #{} with {} library failed: {}'.format(serial, api_name, result.name),
                  file=sys.stderr)

        # nothing found
        raise PicoScopeNotFound('PicoScope unit #{} not found.'.format(serial))

    def _init_channels(self):
        # get the ADC value which represents full-range voltage
        c_max_value = ctypes.c_int16()
        c_min_value = ctypes.c_int16()
        r = self._api.maximum_value(self._handle, c_max_value)
        if r != PicoStatus.PICO_OK:
            raise PicoScopeException('Can not read maximum ADC value: {}'.format(r.name))
        r = self._api.minimum_value(self._handle, c_min_value)
        if r != PicoStatus.PICO_OK:
            raise PicoScopeException('Can not read minimum ADC value: {}'.format(r.name))
        max_value = c_max_value.value
        min_value = c_min_value.value

        self.channel = {}
        for idx, name in enumerate(self.CHANNELS):
            length = ctypes.c_int32(len(self.RANGES) + 1)
            ranges = (ctypes.c_int32 * length.value)()
            r = self._api.get_channel_information(self._handle, 0, 0, ranges, length, idx)
            if r == PicoStatus.PICO_OK and length.value > 0:
                ch = ChannelInfo(idx,
                                 self.ChannelCoupling.DC,
                                 [(i, v) for i, v in enumerate(self.RANGES) if i in set(ranges[:length.value])],
                                 max_value,
                                 min_value)
                # PicoScope seems to start with all channels enabled(?), disable them to bring device into known
                # well-defined state.
                self._set_channel(ch)
                self.channel[name] = ch

                r = self._api.set_data_buffers(self._handle,
                                               idx,
                                               *ch.min_max_buffers(),  # buffers, bufferLth
                                               0,  # segmentIndex
                                               self.RatioMode.AGGREGATE.value)
                if r != PicoStatus.PICO_OK:
                    raise PicoScopeException('Setting bmin/max buffers for channel {} failed: {}'.format(name, r.name))

    def __init__(self, *, hw_config=None, serial, model=None, **kwargs):
        api, lib = self._open_unit(serial, use_api=model)

        # generate API class
        api_dict = {fname: get_call(fapi, lib) for fname, fapi in api.FUNCTION.items()}
        self._api = type('PicoScopeApi', (object, ), api_dict)

        for itm in 'ChannelCoupling', 'TriggerDirection', 'RatioMode', 'CHANNELS', 'RANGES':
            setattr(self, itm, getattr(api, itm))

        self._init_channels()
        # TODO: disable (or handle somehow) digital ports?

        self._capture_length = None

        # mapping for the set_trigger() param
        self._api.TRIGGER_DIRECTION = [
            None,
            api.TriggerDirection.RISING,
            api.TriggerDirection.FALLING,
            api.TriggerDirection.BOTH
        ]
        self.trigger = None
        self._set_trigger()

    def _set_channel(self, ch_info):
        r = self._api.set_channel(self._handle,
                                  ch_info.idx,
                                  ch_info.active,
                                  ch_info.coupling.value,
                                  ch_info.rng,
                                  ch_info.offset)
        if r != PicoStatus.PICO_OK:
            raise PicoScopeException('Can not set channel {} to {}: {}'.format(self.CHANNELS[ch_info.idx],
                                                                               str(ch_info),
                                                                               r.name))

    def _set_trigger(self):
        if self.trigger is None:
            r = self._api.set_simple_trigger(self._handle, False, 0, 0, 0, 0, 0)
        else:
            r = self._api.set_simple_trigger(self._handle,
                                             True,
                                             self.trigger.channel.idx,
                                             self.trigger.channel.to_adc_value(self.trigger.level),
                                             self.trigger.direction.value,
                                             -int(self.trigger.pretrig // self._dt) if self.trigger.pretrig < 0 else 0,
                                             0)
        if r != PicoStatus.PICO_OK:
            raise PicoScopeException('Can not set trigger {}: {}'.format(self.trigger, r.name))

    def close(self):
        if self._api is not None and self._handle is not None:
            self._api.close_unit(self._handle)
            self._handle = None
            self._api = None

    def activate_channel(self, chan=None):
        ch = self.channel[chan]
        ch.active = True
        self._set_channel(ch)

    def deactivate_channel(self, chan=None):
        if chan in self.channel:
            ch = self.channel[chan]
            ch.reset()
            self._set_channel(ch)

    def set_channel_range(self, peak_voltage, chan):
        ch = self.channel[chan]
        ch.set_range(peak_voltage)
        if ch.active:
            self._set_channel(ch)

    def set_channel_coupling(self, ac, chan):
        ch = self.channel[chan]
        if ac:
            ch.coupling = self.ChannelCoupling.AC
        else:
            ch.coupling = self.ChannelCoupling.DC
        if ch.active:
            self._set_channel(ch)

    def set_channel_offset(self, offset, chan):
        ch = self.channel[chan]
        ch.offset = offset
        if ch.active:
            self._set_channel(ch)

    def clear_trigger(self):
        self.trigger = None
        self._set_trigger()

    def set_trigger(self, *, chan, direction, level, pretrig):
        self.trigger = TriggerInfo(self.channel[chan], self._api.TRIGGER_DIRECTION[direction], level, pretrig)

    def set_timebase(self, *, duration=None, samples=None, sample_time=None):
        if len([1 for x in [duration, samples, sample_time] if x]) != 2:
            raise ValueError('set_timebase() needs exactly two arguments set')
        self._timebase_id, self._samples, self._oversample, self._dt = self._find_timebase(duration=duration,
                                                                                           samples=samples,
                                                                                           sample_time=sample_time)
        self._downsampled_dt = self._dt * self._oversample

    def stop(self):
        r = self._api.stop(self._handle)
        if r != PicoStatus.PICO_OK:
            raise PicoScopeException('Could not stop scope: {}'.format(r.name))

    def is_ready(self):
        c_ready = ctypes.c_int16()
        r = self._api.is_ready(self._handle, c_ready)
        if r != PicoStatus.PICO_OK:
            raise PicoScopeException('Could not check readiness of the PicoScope: {}'.format(r.name))
        # TODO: can we get return value other than PICO_OK as a valid status?
        return bool(c_ready.value)

    def arm(self):
        # _capture_length works as a flag too, when not None the get_data() was called after arming the scope
        # and waveforms can be retrieved from buffers in ChannelInfo instances
        self._capture_length = None
        self._set_trigger()
        if self.trigger is not None and self.trigger.pretrig > 0:
            pre_trig_samples = int(self.trigger.pretrig // self._dt)
        else:
            pre_trig_samples = 0
        post_trig_samples = self._samples - pre_trig_samples
        c_time_indisposed_ms = ctypes.c_int32()
        # Note: It seems that A-API library does not like non-zero oversample parameter passed to the RunBlock
        # call (PICO_INVALID_PARAMETER is retuned) despite it is documented as "not used".
        r = self._api.run_block(self._handle,
                                pre_trig_samples,  # noOfPreTriggerSamples
                                post_trig_samples,  # noOfPostTriggerSamples
                                self._timebase_id,
                                0,  # oversample (not used)
                                c_time_indisposed_ms,
                                0,  # segment_index
                                None,  # lpReady (callback)
                                None)  # pparameter
        if r != PicoStatus.PICO_OK:
            raise PicoScopeException('Could not arm the PicoScope: {}'.format(r.name))

    def _do_fetch(self, max_wait=None):
        delay = 0.2
        if max_wait is not None:
            timeout = time.monotonic() + max_wait
            if delay > max_wait / 10:
                delay = max_wait / 10

        if self._oversample > 1:
            ratio_mode = self.RatioMode.AVERAGE.value
        else:
            ratio_mode = self.RatioMode.NONE.value

        # It is not completely clear from API documentation, but it seems that we need to prepare buffers for all
        # active channels before calling get_data, otherwise strange things happens (there is no channel selector
        # in get_data call and neither "remove_data_buffer() kind of API, so it probably makes sense, kind of).
        for ch in self.channel.values():
            if not ch.active:
                continue

            c_no_of_samples = ctypes.c_uint32(self._samples // self._oversample)

            r = self._api.set_data_buffer(self._handle,
                                          ch.idx,  # channel
                                          *ch.set_buffer(c_no_of_samples.value),  # buffer, bufferLth
                                          0,  # segmentIndex
                                          ratio_mode)
            if r != PicoStatus.PICO_OK:
                raise PicoScopeException('set_data_buffer() failed: {}'.format(r.name))

        while True:
            if self.is_ready():
                c_overflow = ctypes.c_int16()
                r = self._api.get_values(self._handle,
                                         0,  # startIndex
                                         c_no_of_samples,
                                         self._oversample,
                                         ratio_mode,
                                         0,  # segmentIndex
                                         c_overflow)
                if r == PicoStatus.PICO_OK:
                    # Note: the overflow flag reported by Pico library seems to be set only when voltag eexceeds limit
                    # by some non-negligible margin, not at any arbitrary small overflow.
                    # Get the minimum and maximum of the measured data to detect overflow by presence of full scale
                    # reading.
                    # TODO: do we want to do this, or is it better to use the overflow flag from the Pico library only?
                    c_single_sample = ctypes.c_uint32(1)
                    self._api.get_values(self._handle,
                                         0,  # startIndex
                                         c_single_sample,
                                         self._samples,
                                         self.RatioMode.AGGREGATE.value,
                                         0,  # segmentIndex
                                         None)
                    for ch in self.channel.values():
                        ch.decode_overflow(c_overflow.value)
                    self._capture_length = c_no_of_samples.value
                    # we are done, capture data retrieved
                    return True
                if r != PicoStatus.PICO_NO_SAMPLES_AVAILABLE:
                    raise PicoScopeException('get_values() failed: {}'.format(r.name))

            # wait a moment and try again
            if max_wait is not None and time.monotonic() > timeout:
                return False
            time.sleep(delay)

    def fetch(self, max_wait=None, chan=None):
        ch = self.channel[chan]
        if not ch.active:
            raise ValueError('Can not fetch data for inactive channel {}.'.format(chan))

        if self._capture_length is None:
            # we have not called get_values() yet, so do it now
            if not self._do_fetch(max_wait=max_wait):
                # TODO: handle no data situation somehow better ....?
                return None, False

        return ch.get_data(self._capture_length)

    def _check_timebase(self, timebase_id, sample_time=None, duration=None, samples=None):
        """Check if given timebase id can fulfill requested sample time and record duration.

        Returned value is tuple: (status, timebase id, number of samples to record, oversample factor, timestep).
          Number of samples is before downsampling, i.e. the value to pass into RunBlock() call, timestep is
          for downsampled data (that is data returned from GetValues with right oversampling factor passed in).
        Status value:
           2: sampling rate with this timebase is slower than requested even without oversampling
           1: requested params are fulfilled, lower the timebase_id more oversampling applied
           0: it is not possible to apply enough oversampling to reach requested samplerate, whole duration can be
              returned, but sampling rate will be (much) higher than requested
          -1: timebase is not available at all, or is too fast to even fit whole duration into the buffer.
        """
        # TODO: should we consider staying with ns time units here to avoid floating point rounding errors?
        # PicoScope API documentation recommends using GetTimebase2 with float argument, but is it really the best
        # idea?
        if sample_time is None:
            sample_time = duration / samples

        c_interval_ns = ctypes.c_float()
        c_max_samples = ctypes.c_int32()
        r = self._api.get_timebase2(self._handle,
                                    timebase_id,
                                    1,  # noSamples
                                    c_interval_ns,
                                    1,  # oversample (not used)
                                    c_max_samples,
                                    0)  # segmentIndex
        if r == PicoStatus.PICO_INVALID_TIMEBASE:
            # Depending on the channel settings, low timebase_id can fail with this exception if scope does not
            # support such combination of channels and rate.
            return (-1, timebase_id, None, None, None)
        elif r != PicoStatus.PICO_OK:
            raise PicoScopeException('get_timebase() failed with: {}'.format(r.name))
        # TODO: PicoStatus.PICO_INVALID_CHANNEL if no channel is enabled

        dt = c_interval_ns.value * 1e-9
        max_samples = c_max_samples.value

        if samples is None:
            # always record integer multiple of oversampling factor number of samples
            oversample_factor = int(sample_time / dt)
            if oversample_factor >= 1:
                need_samples = int(math.ceil(duration / (dt * oversample_factor))) * oversample_factor
            else:
                need_samples = int(math.ceil(duration / dt))
        else:
            oversample_factor = int(math.ceil(sample_time / dt))
            if oversample_factor >= 1:
                need_samples = samples * oversample_factor
            else:
                need_samples = samples

        if need_samples > max_samples:
            # Too fast sampling rate, requested duration does not fit into the buffer
            return (-1, timebase_id, None, None, None)
        if oversample_factor < 1:
            # too slow for requested sample_time
            return (2, timebase_id, need_samples, 1, dt)

        c_max_factor = ctypes.c_uint32(0)
        r = self._api.get_max_down_sample_ratio(self._handle,
                                                need_samples,
                                                c_max_factor,
                                                self.RatioMode.AVERAGE.value,
                                                0)  # segmentIndex
        max_factor = c_max_factor.value

        if r == PicoStatus.PICO_TOO_MANY_SAMPLES:
            # Too fast sampling rate, requested duration does not fit into the buffer
            return (-1, timebase_id, None, None, None)
        elif r != PicoStatus.PICO_OK or max_factor < 1:
            raise PicoScopeException('get_max_downsample_ratio() failed: {}'.format(r.name))

        if max_factor < oversample_factor:
            # Scope does not support so high oversampling factor, so we have to return more datapoints to caller,
            # nevertheless, minimal sampling rate and total duration are fulfilled, so consider it OK too.
            # TODO: Do we want different behaviour for fixed number of samples specified in call parameters?
            return (0,
                    timebase_id,
                    int(math.ceil(duration / sample_time)) * max_factor if samples is None else samples,
                    max_factor,
                    dt)
        return (1, timebase_id, need_samples, oversample_factor, dt)

    def _find_timebase(self, sample_time=None, duration=None, samples=None):
        """Run binary search to find the best suitable (including oversampling) timebase ID."""
        # TODO: should we allow request specifying oversampling explicitely or requiring no oversampling at all?

        # two initial points
        check_a = self._check_timebase(0, sample_time, duration, samples)
        check_b = self._check_timebase(0xffffffff, sample_time, duration, samples)
        # theoretically, check results should look like this:
        #
        # tbase_id: 0.................................................................0xffffffff
        # check:    ------------0000000011111112222222222222222222222222222222222222222
        # the point we want: ...........^
        #
        # If there is no "1" range, get the highest "0" as the best possible result, if there are neither "0"s,
        # take the lowest "2". So ...:
        #   - if we start with negative 'b' the requested block is likely unreasonably long and there is no good
        #     solution
        #   - if we start with 'a' >= 1, return it directly.
        #   - keep 'a' < 1 (and 'b' >= 1) until 'b' ends up just next id point above the 'a'
        #   - return b if b == 1, elif a if a == 0, else b
        if check_a[0] >= 1:
            return check_a[1:]
        if check_b[0] < 0:
            # give up, requested duration is waaay too long ...
            raise PicoScopeException('Acquisition with requested timebase {} is not possible for the PicoScope.'.\
                                     format((sample_time, duration, samples)))
            return None  # maybe exception?
        while check_b[1] - check_a[1] > 1:
            midpoint = self._check_timebase(int((check_b[1] + check_a[1]) / 2), sample_time, duration, samples)
            if midpoint[0] < 1:
                check_a = midpoint
            else:
                check_b = midpoint
        if check_b[0] != 1 and check_a[0] == 0:
            return check_a[1:]
        else:
            return check_b[1:]

    def get_time_axis(self):
        if self._capture_length is None:
            return None
        # TODO: we should add an offset retrieved from get_trigger_time_offset64() API call
        pretrig = self.trigger.pretrig if self.trigger is not None else 0
        return numpy.linspace(-pretrig + self._downsampled_dt / 2,
                              self._capture_length * self._downsampled_dt - pretrig + self._downsampled_dt / 2,
                              self._capture_length,
                              endpoint=False,
                              dtype=numpy.dtype('float_'))


def main():
    scope = None
    try:
        scope = Picoscope(serial='CT266/137')

        scope.set_channel_range(chan='B', peak_voltage=0.01)
        scope.set_channel_range(chan='A', peak_voltage=5)

        #scope.set_channel_coupling(chan='A', ac=True)
        scope.set_channel_offset(chan='A', offset=-5.5)

        scope.activate_channel('A')
        scope.activate_channel('B')

        for k, v in scope.channel.items():
            print('{}: {} {} {}'.format(k, v, v._ranges, v._adc_max))

        scope.set_timebase(sample_time=5e-7, samples=500)
        scope.set_trigger(chan='A', direction=1, level=0.5, pretrig=10e-5)
        # def set_timebase(self, *, duration=None, samples=None, sample_time=None):
        print('[T] #{}, Raw smpls: {}, dt: {}, oversample: {}'.\
              format(scope._timebase_id, scope._samples, scope._dt, scope._oversample))

        scope.arm()

        data, overflow = scope.fetch(max_wait=5, chan='B')
        print(data)
        print(overflow)

        data, overflow = scope.fetch(max_wait=5, chan='A')
        print(data)
        print(overflow)

        # print(scope.get_time_axis())

    finally:
        if scope is not None:
            scope.close()


if __name__ == "__main__":
    main()

