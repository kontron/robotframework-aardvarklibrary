# Copyright 2014 Kontron Europe GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import array
import pyaardvark

from . import __version__
from .utils import int_any_base, list_any_input

from robot.utils.connectioncache import ConnectionCache
from robot.api import logger

class AardvarkLibrary:
    """Robot Framework test library for the Totalphase Aardvark host adapter.
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__

    def __init__(self, i2c_bitrate=100, spi_bitrate=100):
        self._cache = ConnectionCache()
        self._i2c_bitrate = i2c_bitrate
        self._spi_bitrate = spi_bitrate
        self._device = None

    def open_aardvark_adapter(self, port_or_serial=0, alias=None):
        """Opens a new Aardvark host adapter.

        The adapter to be used is identified by the port or by a serial number.
        By default the port 0 is used, which is sufficient if there is only one
        host adapter. If there are multiple adapters connected, you have to
        provide either the port or a serial number. The serial number must be
        given in the form NNNN-NNNNNN, otherwise the argument is interpreted as
        the port number.

        Possible already opened adapters are cached and it is possible to
        switch back to them using the `Switch Aardvark Adapter` keyword. It is
        possible to switch either using explicitly given `alias` or using the
        index returned by this keyword. Indexing start from 1 and is reset back
        to it by the `Close All Connections` keyword.
        """

        port = None
        serial = None
        if isinstance(port_or_serial, basestring) and '-' in port_or_serial:
            logger.info('Opening Aardvark adapter with serial %s' %
                    (port_or_serial,))
            serial = port_or_serial
        else:
            port = int(port_or_serial)
            logger.info('Opening Aardvark adapter on port %d' % (port,))

        device = pyaardvark.open(port=port, serial_number=serial)

        device.i2c_bitrate = self._i2c_bitrate
        device.spi_bitrate = self._spi_bitrate
        device.enable_i2c = True
        device.enable_spi = True
        device.spi_configure_mode(pyaardvark.SPI_MODE_3)
        self._device = device
        return self._cache.register(self._device, alias)

    def switch_aardvark_adapter(self, index_or_alias):
        """Switches between active Aardvark host adapters using an index or
        alias.

        Aliases can be given to `Open Aardvark Adapter` keyword wich also
        always returns the connection index.

        This keyword retruns the index of previous active connection.
        """
        old_index = self._cache_current_index
        self._device = self._cache.switch(index_or_alias)
        return old_index

    def close_all_aardvark_adapters(self):
        """Closes all open Aardvark host adapters and empties the open adapters
        cache.

        If multiple adapters are opened, this keyword should be used in a test
        or suite teardown to make sure that all adapters are closed.

        After this keyword, new indexes returned by the `Open Conection`
        keyword are reset to 1.
        """
        self._device = self._cache.close_all()

    def close_adapter(self):
        """Closes the current Aardvark host adapter.

        Use `Close All Aardvark Adapters` if you want to make sure all opened
        host adapters are closed.
        """
        self._device.close()

    def set_i2c_bitrate(self, bitrate):
        """Sets the bitrate used during I2C transfers.

        The `bitrate` is given in kHz. This changes only the bitrate for the
        current adapter. The default value can be set when importing the
        library.
        """
        self._device.i2c_bitrate(bitrate)

    def set_spi_bitrate(self, bitrate):
        """Sets the bitrate used during SPI transfers.

        The `bitrate` is given in kHz. This changes only the bitrate for the
        current adapter. The default value can be set when importing the
        library.
        """
        self._device.spi_bitrate(bitrate)

    def enable_i2c_pullups(self, enable=True):
        """Enable (or disable) the I2C pullup resistors."""

        if enable:
            logger.info('Enabling I2C pullup resistors.')
        else:
            logger.info('Disabling I2C pullup resistors.')
        self._device.i2c_pullups = enable

    def enable_traget_power(self, enable=True):
        """Enable (or disable) the target power."""

        if enable:
            logger.info('Enabling target power.')
        else:
            logger.info('Disabling target power.')
        self._device.target_power = enable

    def i2c_master_read(self, address, length=1):
        """Perform an I2C master read access.

        Read `length` bytes from a slave device with the address given in the
        `address` argument.
        """

        address = int_any_base(address)
        length = int_any_base(length)
        data = self._device.i2c_master_read(address, length)
        data = array.array('B', data)
        logger.info('Read %d bytes from %02xh: %s',
                length, address, ' '.join('%02x' % d for d in data))
        return data

    def i2c_master_write(self, address, *data):
        """Perform an I2C master write access.

        Writes the given `data` to a slave device with address given in the
        `address` argument. The `data` argument can either be list of bytes, a
        whitespace separated list of bytes or a single byte. See the examples
        below.

        Both the `address` and `data` can be given either as strings or
        integers.  Strings are parsed accoding to their prefix. Eg. `0x`
        denotes a hexadecimal number.

        Examples:
        | I2C Master Write | 0xa4 | 0x10           |
        | I2C Master Write | 0xa4 | 0x10 0x12 0x13 |
        | I2C Master Write | 0xa4 | 0x10 | 0x12 | 0x13 |
        """

        address = int_any_base(address)
        if len(data) == 1:
            data = list_any_input(data[0])
        else:
            data = [int_any_base(c) for c in data]
        logger.info('Writing %d bytes to %02xh: %s' %
                (len(data), address, ' '.join('%02x' % d for d in data)))
        data = ''.join('%c' % chr(c) for c in data)
        self._device.i2c_master_write(address, data)

    def i2c_master_write_read(self, address, length, *data):
        """Perform an I2C master write read access.

        First write the given `data` to a slave device, then read `length`
        bytes from it. For more information see the `I2C Master Read` and `I2C
        Master Write` keywords.

        Examples:
        | I2C Master Write Read | 0xa4 | 1 | 0x10           |
        | I2C Master Write Read | 0xa4 | 1 | 0x10 0x12 0x13 |
        | I2C Master Write Read | 0xa4 | 1 | 0x10 | 0x12 | 0x13 |
        """

        address = int_any_base(address)
        length = int_any_base(length)
        if len(data) == 1:
            data = list_any_input(data[0])
        else:
            data = [int_any_base(c) for c in data]
        logger.info('Writing %d bytes to %02xh: %s' %
                (len(data), address, ' '.join('%02x' % d for d in data)))
        data = ''.join('%c' % chr(c) for c in data)
        data = self._device.i2c_master_write_read(address, data, length)
        data = array.array('B', data)
        logger.info('Read %d bytes from %02xh: %s' %
                (length, address, ' '.join('%02x' % d for d in data)))
        return data

    def spi_transfer(self, *data):
        """Performs a SPI access.

        Writes a stream of bytes (given in `data`) on the SPI interface while
        reading back the same amount of bytes. The read back has the same
        length as the input data. If you want to read more data than writing on
        the bus you have to send dummy bytes.

        Examples:
        | SPI Write | 0x10           |
        | SPI Write | 0x10 0x12 0x13 |
        | SPI Write | 0x10 | 0x12 | 0x13 |
        | ${ret}=  | SPI Write | 0x10 | 0x12 | 0x13 | # ${ret} is an array of 3 bytes |
        """

        if len(data) == 1:
            data = list_any_input(data[0])
        else:
            data = [int_any_base(c) for c in data]
        logger.info('Writing %d bytes: %s' %
                (len(data), ' '.join('%02x' % d for d in data)))
        data = ''.join('%c' % chr(c) for c in data)
        data = self._device.spi_write(data)
        data = array.array('B', data)
        logger.info('Read %d bytes: %s' %
                (len(data), ' '.join('%02x' % d for d in data)))
        return data
