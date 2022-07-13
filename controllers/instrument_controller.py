from controllers.base_controller import Controller
from controllers.dmm_controller import DMMController
from controllers.psu_controller import PSUController
from drivers.utilities import scan_devices
from controllers.actions import Actions
from drivers import PSUInterface, LoadInterface, DMMInterface
from clint.textui import puts, colored
from rich import print

# Basic CLI control of instruments.

# Should auto detect all instruments attached, then prompt user for choices. 
# Choices should be:
# 1. select instrument
# 2. Select action (including go back)

# Actions:
# - Read
# - Set
# - Enable/disable.
class InstrumentController(Controller):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.psu_controller = PSUController()
        self.dmm_controller = DMMController()
        #self.load_controller = LoadController()


    def handle_device(self, device):
        type_handlers = {
            PSUInterface: self.psu_controller.handle_actions,
            DMMInterface: self.dmm_controller.handle_actions
        }

        for interface, handler in type_handlers.items():
            if isinstance(device, interface):
                handler(device)

    def control(self):
        print("[magenta]Scanning for devices")
        supported_devs = scan_devices()
        if supported_devs:
            while True:
                device = self.prompt_options("Select Device", supported_devs)
                if device == Actions.GO_BACK:
                    print("[red]Terminating program")
                    break
                else:
                    print(f"Chosen [green]{device}")  #TODO serial ID?
                    self.handle_device(device)
        else:
            print("[red]No supported devices found. Exiting.")


if __name__ == "__main__":
    controller = Controller()
    controller.control()