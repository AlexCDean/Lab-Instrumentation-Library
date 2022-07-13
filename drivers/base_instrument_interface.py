
from .common.scpi_commands import SCPI_IDENTIFY
from .common.errors import VisaIOError
import re

class BaseInterface:
    _model = "NOTSET"
    channels = []
    def __str__(self):
        return f"{self._model} Interface"

    def __init__(self, **kwargs):
        self.resource = kwargs.pop('resource', None)
        self.serial_id = kwargs.pop('serial_id', None)
    
    def response_to_float(self, response):
        value = re.findall("\d+\.\d+", response)
        if len(value) > 1:
            raise ValueError("More than one float found")
        try:
            return float(value[0])
        except ValueError:            
            # With a regex this is probably unnecessary. 
            raise IOError(
                f"Error: {self.__name__} encountered an unknown value" +
                f"to parse: {value}"
            )


    def _query(self, _str):        
        try:
            return self.resource.query(_str)
        except VisaIOError:
            raise IOError(
                f"Error: {self._model}:{self.serial_id} Query [{_str}] timed out"
            )

    def _write(self, _str):
        try:
            return self.resource.write(_str)
        except VisaIOError:
            raise IOError(
                f"Error: {self._model}:{self.serial_id} Write [{_str}] timed out"
            )
