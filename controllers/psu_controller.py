from controllers.base_controller import Controller
from controllers.actions import Actions
from drivers.psu.psu_interface import PSUInterface
from clint.textui import puts, colored
from time import sleep



class PSUController(Controller):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options_dict = {
            "Set Voltage": (Actions.SET_VOLTAGE, self.set_voltage),
            "Set Current": (Actions.SET_CURRENT, self.set_current),
            "Read Set Voltage": (Actions.READ_SET_VOLTAGE, self.read_set_voltage),
            "Read Set Current": (Actions.READ_SET_CURRENT, self.read_set_current),
            "Read Voltage": (Actions.READ_VOLTAGE, self.read_voltage),
            "Read Current": (Actions.READ_CURRENT, self.read_current),
            "Enable Channel": (Actions.ENABLE_CHANNEL, self.enable_channel),
            "Disable Channel": (Actions.DISABLE_CHANNEL, self.disable_channel),
            "Channel status": (Actions.GET_CHANNEL_STATUS, self.get_channel_status),
            "Continous status": (Actions.CONTINOUSLY_PRINT_STATUS, self.continous_print_status),
            "Back": (Actions.GO_BACK, None)
        }

    def get_channel_status(self, device: PSUInterface):
        chan = self.get_chosen_chan(device)
        if chan != Actions.GO_BACK:
            self._print_channel_status(chan, device.is_switched_on(chan))

    def read_set_current(self, device: PSUInterface):
        chan = self.get_chosen_chan(device)
        if chan != Actions.GO_BACK:
            current = device.query_set_current(chan)
            puts(colored.yellow(f"Set current for chan {chan} is {current}"))

    def read_set_voltage(self, device: PSUInterface):
        chan = self.get_chosen_chan(device)
        if chan != Actions.GO_BACK:
            voltage = device.query_set_voltage(chan)
            puts(colored.cyan(f"Set Voltage for chan {chan} is: {voltage}"))

    def read_voltage(self, device: PSUInterface):
        chan = self.get_chosen_chan(device)
        if chan != Actions.GO_BACK:
            voltage = device.get_voltage(chan=chan)
            puts(colored.cyan(f"Current Voltage for chan {chan} is: {voltage}"))

    def set_voltage(self, device: PSUInterface):
        chan = self.get_chosen_chan(device)
        if chan != Actions.GO_BACK:
            voltage = self.query_float("Enter desired voltage in float format: ")
            puts(colored.cyan(f"Setting Chan {chan} voltage to {voltage} V"))
            device.set_voltage(voltage, chan)

    def read_current(self, device: PSUInterface):
        chan = self.get_chosen_chan(device)
        if chan != Actions.GO_BACK:
            current = device.get_current(chan)
            puts(colored.yellow(f"Current draw for chan {chan} is {current}"))

    def set_current(self, device: PSUInterface):
        chan = self.get_chosen_chan(device)
        if chan != Actions.GO_BACK:
            current = self.query_float("Enter desired current in float format: ")
            puts(colored.yellow(f"Setting Chan {chan} current limit to {current} A"))
            device.set_current(current, chan)

    def enable_channel(self, device: PSUInterface):
        chan = self.get_chosen_chan(device)
        if chan != Actions.GO_BACK:
            device.switch_on(chan)
            self._print_channel_status(chan, device.is_switched_on(chan))

    def _print_channel_status(self, chan, chan_status):
            string = f"Channel {chan} is "
            string += colored.green("ON") if chan_status else colored.red("OFF")
            puts(string)

    def disable_channel(self, device: PSUInterface):
        chan = self.get_chosen_chan(device)
        if chan != Actions.GO_BACK:
            device.switch_off(chan)
            self._print_channel_status(chan, device.is_switched_on(chan))

    def continous_print_status(self, device: PSUInterface):
        # Print voltage and current draw for each channel
        # Channel indicator GREEN for on and RED for off. 
        # e.g. chan 1 2V 1A chan 2 2V 0A etc.... in one line. 
        try:
            puts(f"Printing every channel status for {device._model}. Press ctrl-c to stop")
            chan_dict = {
                chan: { 
                    "volage": 0, 
                    "current": 0, 
                    "enabled": False
                } for chan in device.channels
            }

            while True:
                # Update info
                for chan, status_dict in chan_dict.items():
                    status_dict["voltage"] = device.get_voltage(chan)
                    status_dict["current"] = device.get_current(chan)
                    status_dict["enabled"] = device.is_switched_on(chan)
                # Print info
                for chan, status_dict in chan_dict.items():
                    chan_str = colored.green(f"Chan {chan}\t") if status_dict["enabled"] else colored.red(f"Chan {chan}\t")
                    voltage_str = colored.cyan(f"{status_dict['voltage']}V\t")
                    current_str = colored.yellow(f"{status_dict['current']}A\t")
                    puts(chan_str + voltage_str + current_str, newline=False)
                puts("\r", newline=False)
                sleep(1)
        except KeyboardInterrupt:
            return