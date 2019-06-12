from aardvark_py import *
from array import ArrayType


class Aardvark():
    # Abstract class. Should be inherited from only.
    is_open = False
    port = None

    def __init__(self, handle=None, serial=None, **kwargs):
        self.aardvark_handle = handle
        self.serial_id = serial
        self._auto_configure_handle_uid()

    def _auto_configure_handle_uid(self):
        # Common functionality to find aardvark if given either handle or uid.
        if self.aardvark_handle is not None:
            self._configure_handle_to_class()
        elif self.serial_id is not None:
            self.aardvark_handle = self.find_aardvark_handle_uid(self.serial_id)
            if self.aardvark_handle is not None and self.aardvark_handle > 0:
                self._configure_handle_to_class()

    def _configure_handle_to_class(self):
        # Inherited method - overridden in child class.
        raise NotImplementedError

    def find_aardvark_handle_uid(self, unique_id):
        if isinstance(unique_id, str):
            try:
                self.serial_id = int(unique_id)
                unique_id = int(unique_id)
            except ValueError:
                raise ValueError("Aardvark Serial ID is not a valid integer.")

        (num, ports, unique_ids) = self.find_free_aardvarks()

        for i, uid in enumerate(unique_ids):
            if self.serial_id == uid:
                port = ports[i]
                self.port = port
                self.is_open = True
                return aa_open(port)
        return None

    def find_free_aardvarks(self, max_aardvarks=16):
        free_port = None
        found_port = False
        handle = None
        (num, ports, unique_ids) = aa_find_devices_ext(max_aardvarks, max_aardvarks)
        ports_to_delete = []
        unique_ids_to_delete = []

        if num > 0:
            for i in range(num):
                port = ports[i]
                unique_id = unique_ids[i]
                if (port & AA_PORT_NOT_FREE):
                    ports_to_delete.append(port)
                    unique_ids_to_delete.append(unique_id)
        else:
            ports = []
            unique_ids = []
        for p in ports_to_delete:
            ports.remove(p)
        for u in unique_ids_to_delete:
            unique_ids.remove(u)
        num -= len(ports_to_delete)

        return (num, ports, unique_ids)

    def __del__(self):
        if self.aardvark_handle:
            aa_close(self.aardvark_handle)

    def open(self):
        if not self.is_open:
            if self.port:
                self.aardvark_handle = aa_open(self.port)
                self.is_open = True
            elif self.serial_id:
                self.aardvark_handle = self.find_aardvark_handle_uid(self.serial_id)
                self.is_open = True

    def close(self):
        if self.is_open:
            aa_close(self.aardvark_handle)
            self.is_open = False


class AardvarkI2CSPI(Aardvark):
    def __init__(self, aardvark_handle=None, serial=None, freq_spi=100, freq_i2c=100, **kwargs):
        self.aardvark_handle = aardvark_handle
        self.serial_id = serial
        self.freq_spi = freq_spi
        self.freq_i2c = freq_i2c
        self._auto_configure_handle_uid()

    def _configure_handle_to_class(self):
        if self.aardvark_handle:
            ret_val = aa_configure(self.aardvark_handle, AA_CONFIG_SPI_I2C)
            if ret_val == AA_OK:
                # success
                self.change_i2c_rate(self.freq_i2c)
                self.change_spi_rate(self.freq_spi)
            else:
                # if we're here then we most likely have an invalid handle.
                # Other potential errors: comm error.
                if ret_val == AA_INVALID_HANDLE:
                    raise ValueError("Aardvark: Invalid handle")
                if ret_val == AA_COMMUNICATION_ERROR:
                    pass

    def change_i2c_rate(self, bitrate_khz):
        self.freq_i2c = bitrate_khz
        return aa_i2c_bitrate(self.aardvark_handle, bitrate_khz)

    def change_spi_rate(self, bitrate_khz):
        self.freq_spi = bitrate_khz
        return aa_spi_bitrate(self.aardvark_handle, bitrate_khz)

    def i2c_write(self, slave_addr, data_out):
        return aa_i2c_write(self.aardvark_handle, slave_addr, AA_I2C_NO_FLAGS, data_out)

    def i2c_read(self, slave_addr, num_bytes):
        (bytes_read, data_in) = aa_i2c_read(self.aardvark_handle, slave_addr, AA_I2C_NO_FLAGS, num_bytes)
        return (bytes_read, data_in)

    def i2c_write_read(self, slave_addr, msg, num_bytes_read, delay_ms):
        if not isinstance(data_out, ArrayType):
            data_out = array('B', data_out)  # API needs this to be a 'B' arraytype.
        num_bytes_wrote = self.i2c_write(slave_addr, data_out)
        if num_bytes_wrote == len(data_out):
            aa_sleep_ms(delay_ms)
            return self.i2c_read(slave_addr, num_bytes_read)
        else:
            raise IOError(
                "Aardvark: Did not write expected bytes (wrote/len): " +
                f"{num_bytes_wrote}/{len(data_out)}"
            )

    def spi_write_read(self, data, num_bytes_to_read):
        if not isinstance(data, ArrayType):
            data = array('B', data)  # API needs this to be a 'B' arraytype.

        # TODO I think this function could be more useful - checking error codes etc.
        (num_bytes_read, bytes_read) = aa_spi_write(self.aardvark_handle, data, num_bytes_to_read)
        # Returns bytes_read as array, we want list.
        return (num_bytes_read, bytes_read.tolist())


class AardvarkGPIO(Aardvark):

    # Mapping the pinout to the actual GPIO bit masks.
    # This is to maintain a consistent interface api for the GPIO calls.
    _dict_pin_gpio = {
        1: AA_GPIO_SCL,
        3: AA_GPIO_SDA,
        5: AA_GPIO_MISO,
        7: AA_GPIO_SCK,
        8: AA_GPIO_MOSI,
        9: AA_GPIO_SS
    }

    current_direction_mask = 0x00  # default aardvark directions.
    current_pullup_mask = 0x00     # default aardvark pullups.
    current_output_state = 0x00    # default aardvark output values

    def _configure_handle_to_class(self):
        if self.aardvark_handle:
            ret_val = aa_configure(self.aardvark_handle, AA_CONFIG_GPIO_ONLY)
            if ret_val != AA_OK:
                # if we're here then we most likely have an invalid handle.
                # other error could be comms.
                raise ValueError("Aardvark: Invalid handle")

    def gpio_set_output(self, gpio, set_high):
        if self.aardvark_handle:
            gpio_bitmask = self._get_gpio_bitmask(gpio)

            # set gpio bit position as output whilst maintaining current mask
            new_mask = self.current_direction_mask | gpio_bitmask
            # Test the change worked...
            ret_val = aa_gpio_direction(self.aardvark_handle, new_mask)
            if ret_val == AA_OK:
                # Direction successfully changed, update the mask.
                self.current_direction_mask = new_mask
                if set_high:
                    new_output_state = self.current_output_state | gpio_bitmask
                else:
                    new_output_state = self.current_output_state & (~gpio_bitmask & 0xFF)
                ret_val = aa_gpio_set(self.aardvark_handle, new_output_state)
                if ret_val == AA_OK:
                    self.current_output_state = new_output_state
            else:
                pass  # todo raise error.

    def gpio_set_input(self, gpio, pullup_on):
        if self.aardvark_handle:

            gpio_bitmask = self._get_gpio_bitmask(gpio)
            # Change the bit position to input whilst maintaining current mask
            new_mask = self.current_direction_mask & (~gpio_bitmask & 0xFF)

            ret_val = aa_gpio_direction(self.aardvark_handle, new_mask)

            if ret_val == AA_OK:
                self.current_direction_mask = new_mask
                if pullup_on:
                    new_pullup = self.current_pullup_mask | gpio_bitmask
                else:
                    new_pullup = self.current_pullup_mask & (~gpio_bitmask & 0xFF)

                ret_val = aa_gpio_pullup(self.aardvark_handle, new_pullup)
                if ret_val == AA_OK:
                    self.current_pullup_mask = new_pullup

    def gpio_read_input(self, gpio):
        if self.aardvark_handle:
            gpio_bitmask = self._get_gpio_bitmask(gpio)
            ret_val = aa_gpio_get(self.aardvark_handle)
            # It can be negative for errors:
            if ret_val >= 0:
                state = ret_val & gpio_bitmask
                if state > 0:
                    return 1
                else:
                    return 0
            else:
                # Need to come up with error exceptions here.
                pass

    def _get_gpio_bitmask(self, gpio):
        try:
            return self._dict_pin_gpio[gpio]
        except KeyError:
            raise ValueError(f"Aardvark: Errror, pin {gpio} not supported")


if __name__ == "__main__":
    """
    Test code.
    Assuming pin:pin looped
    Pin 1: Pin 3
    Pin 5: Pin 7
    Pin 8: Pin 9

    Loop back and drive each other.
    """

    value_invalid = True
    # Find an aardvark. (2237928392)
    while value_invalid:
        serial = input("What is the serial number of the aardvark? ")
        aard = AardvarkGPIO(serial=serial)
        if aard.aardvark_handle is not None:
            value_invalid = False
        else:
            print(f"Serial number {serial} not found!")

    dict_pin_pairs = {
        1: 3,
        5: 7,
        8: 9
    }

    for key, value in dict_pin_pairs.items():
        for i in range(2):
            if i == 0:
                pin1 = key
                pin2 = value
            else:
                pin1 = value
                pin2 = key

            aard.gpio_set_input(pin2, True)
            aard.gpio_set_output(pin1, False)

            input2 = aard.gpio_read_input(pin2)
            if input2 != 0:  # We're not driving the pin at this point.
                print(f"Error! input pin {pin2} is not reading (low) output pin {pin1}!")
                break

            aard.gpio_set_output(pin1, True)
            input2 = aard.gpio_read_input(pin2)
            if input2 != 1:
                print(f"Error! input pin {pin2} is not reading (high) output pin {pin1}!")
                break
