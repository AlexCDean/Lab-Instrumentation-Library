from .base_keithley import KeithleyInterface

MAX_K2701_BAUD = 115200

# Chan usage: Indexed from 1 to 40. 
class KeithleyInterfaceK2701(KeithleyInterface):
    _model = "KEITHLEY INSTRUMENTS INC.,MODEL 2701"
    max_slots = 2

    # Default values
    slot_channels = [20, 20]
    max_channels = 40
    channels = [i for i in range(1, max_channels+1)]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)