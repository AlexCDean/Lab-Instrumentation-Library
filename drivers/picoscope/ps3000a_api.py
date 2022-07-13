from ctypes import POINTER, c_uint32, c_int16, c_int32, c_void_p, c_char_p, c_float
from enum import Enum, unique
from .pico_status import PicoStatus

LIBRARY = 'ps3000a'

CHANNELS = [
    'A', 'B', 'C', 'D'
]

RANGES = [
    0.01, 0.02, 0.05, 0.10, 0.20, 0.50, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0
]


@unique
class ChannelCoupling(Enum):
    AC = 0
    DC = 1


class TriggerDirection(Enum):
    ABOVE = 0
    BELOW = 1
    RISING = 2
    FALLING = 3
    BOTH = 4
    ABOVE_LOWER = 5
    BELOW_LOWER = 6
    RISING_LOWER = 7
    FALLING_LOWER = 8


@unique
class RatioMode(Enum):
    NONE = 0
    AGGREGATE = 1
    DECIMATE = 2
    AVERAGE = 4


# Function definitions:
#  - keyword is python call name
#  - data tuple:
#     - return value (ctype, description)
#     - C library name
#     - call parameters (list op tuples): ctype, name, type description
FUNCTION = {
    'open_unit': (PicoStatus, 'ps3000aOpenUnit', [(POINTER(c_int16), 'handle'), (c_char_p, 'serial')]),
    'close_unit': (PicoStatus, 'ps3000aCloseUnit', [(c_int16, 'handle')]),
    'maximum_value': (PicoStatus, 'ps3000aMaximumValue', [(c_int16, 'handle'), (POINTER(c_int16), 'value')]),
    'minimum_value': (PicoStatus, 'ps3000aMinimumValue', [(c_int16, 'handle'), (POINTER(c_int16), 'value')]),
    'get_channel_information': (PicoStatus, 'ps3000aGetChannelInformation', [
        (c_int16, 'handle'),
        (c_int32, 'info'),
        (c_int32, 'probe'),
        (POINTER(c_int32), 'ranges'),
        (POINTER(c_int32), 'length'),
        (c_int32, 'channel')]),
    'set_channel': (PicoStatus, 'ps3000aSetChannel', [
        (c_int16, 'handle'),
        (c_int32, 'channel'),
        (c_int16, 'enabled'),
        (c_int32, 'type'),
        (c_int32, 'range'),
        (c_float, 'analogueOffset')]),
    'set_simple_trigger': (PicoStatus, 'ps3000aSetSimpleTrigger', [
        (c_int16, 'handle'),
        (c_int16, 'enable'),
        (c_int32, 'source'),
        (c_int16, 'threshold'),
        (c_int32, 'direction'),
        (c_uint32, 'delay'),
        (c_int16, 'autoTrigger_ms')]),
    'stop': (PicoStatus, 'ps3000aStop', [(c_int16, 'handle')]),
    'is_ready': (PicoStatus, 'ps3000aIsReady', [(c_int16, 'handle'), (POINTER(c_int16), 'ready')]),
    'get_timebase2': (PicoStatus, 'ps3000aGetTimebase2', [
        (c_int16, 'handle'),
        (c_uint32, 'timebase'),
        (c_int32, 'noSamples'),
        (POINTER(c_float), 'timeIntervalNanoseconds'),
        (c_int16, 'oversample'),
        (POINTER(c_int32), 'maxSamples'),
        (c_uint32, 'segmentIndex')]),
    'get_max_down_sample_ratio': (PicoStatus, 'ps3000aGetMaxDownSampleRatio', [
        (c_int16, 'handle'),
        (c_uint32, 'noOfUnaggregatedSamples'),
        (POINTER(c_uint32), 'maxDownSampleRatio'),
        (c_int32, 'downSampleRatioMode'),
        (c_uint32, 'segmentIndex')]),
    'run_block': (PicoStatus, 'ps3000aRunBlock', [
        (c_int16, 'handle'),
        (c_int32, 'noOfPreTriggerSamples'),
        (c_int32, 'noOfPostTriggerSamples'),
        (c_uint32, 'timebase'),
        (c_int16, 'oversample'),
        (POINTER(c_int32), 'timeIndisposedMs'),
        (c_uint32, 'segmentIndex'),
        (c_void_p, 'lpReady'),  # TODO?
        (c_void_p, 'pParameter')]),
    'set_data_buffer': (PicoStatus, 'ps3000aSetDataBuffer', [
        (c_int16, 'handle'),
        (c_int32, 'channel'),
        (POINTER(c_int16), 'buffer'),
        (c_int32, 'bufferLth'),
        (c_uint32, 'segmentIndex'),
        (c_int32, 'mode')]),
    'set_data_buffers': (PicoStatus, 'ps3000aSetDataBuffers', [
        (c_int16, 'handle'),
        (c_int32, 'channel'),
        (POINTER(c_int16), 'bufferMax'),
        (POINTER(c_int16), 'bufferMin'),
        (c_int32, 'bufferLth'),
        (c_uint32, 'segmentIndex'),
        (c_int32, 'mode')]),
    'get_values': (PicoStatus, 'ps3000aGetValues', [
        (c_int16, 'handle'),
        (c_uint32, 'startIndex'),
        (POINTER(c_uint32), 'noOfSamples'),
        (c_uint32, 'downSampleRatio'),
        (c_int32, 'downSampleRatioMode'),
        (c_uint32, 'segmentIndex'),
        (POINTER(c_int16), 'overflow')]),
}
