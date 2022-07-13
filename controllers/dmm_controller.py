from controllers.base_controller import Controller
from controllers.actions import Actions
from drivers import DMMInterface
from clint.textui import puts, colored
from rich import print
from rich.prompt import Prompt
from drivers.common.errors import BadData

class DMMController(Controller):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options_dict = {            
            "Enable channel": (Actions.ENABLE_CHANNEL, self.enable_channel),
            "Disable channel": (Actions.DISABLE_CHANNEL, self.disable_channel),
            "Read Voltage": (Actions.READ_VOLTAGE, self.read_voltage),
            "Read Impedance": (Actions.READ_IMPEDANCE, self.read_impedance), 
            "Read Temperature": (Actions.READ_TEMPERATURE, self.read_temperature),
            "Read MAC Address": (Actions.READ_MAC_ADDRESS, self.read_mac_add),
            "Read Serial ID": (Actions.READ_SERIAL_ID, self.read_serial_id),
            "Write custom cmd": (Actions.WRITE_CUSTOM_CMD, self.write_custom_cmd),
            "Query Custom Cmd": (Actions.QUERY_CUSTOM_CMD, self.query_custom_cmd),
            "Back": (Actions.GO_BACK, None)
        }


    def enable_channel(self, device: DMMInterface):
        chan = self.get_chosen_chan(device)
        try:
            device.enable_channel(chan)
        except NotImplementedError:
            print(f"Error: device {device} does not support this action")

    def disable_channel(self, device: DMMInterface):
        chan = self.get_chosen_chan(device)
        try:
            device.disable_channel(chan)
        except NotImplementedError:
            print(f"Error: device {device} does not support this action")

    def read_voltage(self, device: DMMInterface):
        choice = Prompt.ask("DC or AC?", choices=["DC", "AC"])
        chan = self.get_chosen_chan(device)
        try:
            if choice == "AC":
                voltage = device.get_voltage_ac(chan)
            else:
                voltage = device.get_voltage_dc(chan)
            print(f"{choice} Voltage on {chan} is {voltage}")
        except (BadData, IOError):
            print(f"Chan [red]{chan}[/red] on DMM is invalid")
        pass

    def read_impedance(self, device: DMMInterface):
        chan = self.get_chosen_chan(device)
        try:
            impedance = device.get_impedance(chan)
            print(f"Chan Impedance is [cyan]{impedance}")
        except (BadData, IOError) as exc:
            print(f"Chan [red]{chan}[/red] on DMM is invalid")

    def read_temperature(self, device: DMMInterface):
        chan = self.get_chosen_chan(device)
        try:
            temp = device.get_temperature(chan)            
            print(f"Temperature on {chan} is: [red]{temp}[/red] C")            
        except (BadData, IOError):  # IO error can happen when the channel is not plugged in. 
            print(f"Chan [red]{chan}[/red] on DMM is invalid for temperature")
    
    def read_mac_add(self, device: DMMInterface):
        try:
            print(f"MAC Address is [yellow]{device.get_mac_address()}")
        except NotImplementedError:
            print(f"Device {device} does not have a mac address")

    def read_serial_id(self, device: DMMInterface):
        print(f"Serial ID is [yellow]{device.get_serial_id()}")