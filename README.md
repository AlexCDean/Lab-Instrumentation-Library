Instantiate a ResourceManager from pyvisa, use to list resources, open resource and pass into appropriate interface class.

This library contains the appropiate dll required to function for both 32bit and 64 bit.

You do not need to specify which path as the library auto-detects the operating system size but it is still an optional
parameter in list_devices and get_device. This is done by passing in the path variables found in drivers/common/visa/path.py

See test.py for example usage.

NB: All channels are one-indexed not zero-indexed, i.e. pass in "1" (integer) to select channel 1.