from .base_keithley import KeithleyInterface

MAX_K2750_BAUD = 19200

# Chan usage: Indexed from 1 to 40. 
class KeithleyInterfaceK2750(KeithleyInterface):
    _model = "KEITHLEY INSTRUMENTS INC.,MODEL 2750"
    max_slots = 5

    # Default values
    slot_channels = [20, 20, 20, 20, 20]
    max_channels = 100
    channels = [i for i in range(1, max_channels+1)]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)