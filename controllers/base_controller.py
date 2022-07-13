from typing import Type
from drivers.base_instrument_interface import BaseInterface
from drivers import DMMInterface
from drivers.utilities import list_devices
from drivers.devices import DICT_DEVICES_MODEL
from drivers.common.errors import *
from drivers.common import scpi_commands as cmds
import logging
from clint.textui.prompt import options, query
from clint.textui import validators
from controllers.actions import Actions
from rich.prompt import Prompt
log = logging.getLogger(__name__)

class FloatValidator:
    message = "Enter a valid float"

    def __init__(self, message=None):
        if message is not None:
            self.message = message
    
    def __call__(self, value):
        """Validates input is a float"""
        try:
            return float(value)
        except (TypeError, ValueError):
            raise validators.ValidationError(self.message)

class RangeValidator:
    def __init__(self, min, max):
        self.message = f"Choose between {min} and {max} (inclusive)"
        self.min = min
        self.max = max

    def __call__(self, value):
        try:
            val = int(value)
            if val >= self.min and val <= self.max:
                return val
            else:
                raise ValueError
        except (TypeError, ValueError):
            raise validators.ValidationError(self.message)

class Controller:
    options_dict = {}

    def query_custom_cmd(self, device: DMMInterface):
        cmd = Prompt.ask("What do you want to query?")
        try:
            print(device._query(cmd))
        except (IOError, OSError):
            print(f"{cmd} timed out")

    def write_custom_cmd(self, device: BaseInterface):
        custom_cmd = Prompt.ask("What command do you want to send?")
        device._write(custom_cmd)
    
    def get_chosen_chan(self, device: BaseInterface):
        value = query(
            f"Choose channel between 1 and {len(device.channels)}\n",
            validators=[RangeValidator(1, len(device.channels))]
        )
        return value

    def query_float(self, prompt_str="What value do you want to set?\n"):
        value = query(prompt_str, validators=[FloatValidator()])
        return value

    def handle_actions(self, device):
        while True:
            option, handler = self.prompt_options(
                f"\nSelect Action for {device._model}", 
                self.options_dict, 
                add_go_back=False
            )
            
            if option == Actions.GO_BACK:
                break
            else:
                handler(device)

    def prompt_options(self, string, options_dict, add_go_back=True):
        prompt_options = []
        if add_go_back:
            options_dict["Back"] = Actions.GO_BACK
        for i, key in enumerate(options_dict):
            prompt_options.append(
                {"selector": str(i+1), "prompt": key, "return": options_dict[key]}
            )
        return options(
            string, 
            prompt_options, 
            default=f"{len(prompt_options)}"
        )