# -*- coding: utf-8 -*-
"""
Used to decode the Victron Energy VE.Direct text protocol.

This is a forked version of script originally created by Janne Kario.
(https://github.com/karioja/vedirect).

 Raise:
    - InputReadException,
    - serial.SerialException,
    - serial.SerialTimeoutException
"""
import logging
import time
from serial import SerialException
from ve_utils.utype import UType as Ut
from vedirect_m8.serconnect import SerialConnection
from vedirect_m8.exceptions import SettingInvalidException
from vedirect_m8.exceptions import InputReadException
from vedirect_m8.exceptions import TimeoutException, VedirectException

__author__ = "Janne Kario, Eli Serra"
__copyright__ = "Copyright 2015, Janne Kario"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vedirect")


class Vedirect:
    """
    Used to decode the Victron Energy VE.Direct text protocol.

    This is a forked version of script originally created by Janne Kario.
    (https://github.com/karioja/vedirect).

    :Example:
            >>> sc = Vedirect({"serial_port": "/dev/ttyUSB1"})
            >>> sc.read_data_single()
            >>> {"ser_key1": "ser_value1", ...}

    Raise:
        - InputReadException,
        - serial.SerialException,
        - serial.SerialTimeoutException
    """
    def __init__(self,
                 serial_conf: dict,
                 source_name: str = 'Vedirect',
                 auto_start: bool = True
                 ):
        """
        Constructor of Vedirect class.

        :Example:
            >>> sc = Vedirect({"serial_port": "/dev/ttyUSB1"})
            >>> sc.read_data_single()
            >>> {"ser_key1": "ser_value1", ...}
        :param self: Refer to the object instance itself,
        :param serial_conf: dict: The serial connection configuration,
        :param source_name: This is used in logger to identify the source of call,
        :param auto_start: bool: Define if serial connection must be established automatically.
        :return: Nothing
        """
        self._com = None
        self._delimiters = {
            "header1": ord('\r'),
            "header2": ord('\n'),
            "hexmarker": ord(':'),
            "delimiter": ord('\t')
        }
        self.key = ''
        self.value = ''
        self.bytes_sum = 0
        self.state = self.WAIT_HEADER
        self.dict = {}
        self.time_packet = 0
        self.init_settings(serial_conf=serial_conf,
                           source_name=source_name,
                           auto_start=auto_start
                           )

    (HEX, WAIT_HEADER, IN_KEY, IN_VALUE, IN_CHECKSUM) = range(5)

    def has_serial_com(self) -> bool:
        """Test if self._com is a valid SerialConnection instance."""
        return Vedirect.is_serial_com(self._com)

    def is_serial_ready(self) -> bool:
        """Test if is serial connection is ready"""
        return self.has_serial_com() and self._com.is_ready()

    def is_ready(self) -> bool:
        """Test if class Vedirect is ready"""
        return self.is_serial_ready()

    def get_serial_port(self) -> str or None:
        """Test if class Vedirect is ready"""
        return self._com.get_serial_port()

    def connect_to_serial(self) -> bool:
        """ Connect to serial port if not connected """
        if self.has_serial_com()\
                and ((not self._com.is_ready() and self._com.connect())
                     or self._com.is_ready()):
            result = True
        else:
            raise VedirectException(
                "[Vedirect::init_serial_connection] "
                "Connection to serial port fails."
            )
        return result

    def init_serial_connection_from_object(self,
                                           serial_connection: SerialConnection,
                                           auto_start: bool = True
                                           ) -> bool:
        """
        Initialise serial connection from SerialConnection object.

        Raise:
         - SettingInvalidException if serial_port, baud or timeout are not valid.
         - VedirectException if connection to serial port fails
        :Example :
            >>> self.init_serial_connection_from_object(serial_connection)
            >>> True
        :param self: Refer to the object itself,
        :param serial_connection: The SerialConnection object,
        :param auto_start: bool: Define if serial connection must be established automatically.
        :return: True if connection to serial port success.
        """
        result = False
        if Vedirect.is_serial_com(serial_connection) and serial_connection.is_settings():
            self._com = serial_connection
            if auto_start is False \
                    or (auto_start is True
                        and self.connect_to_serial()):
                result = True
        else:
            raise SettingInvalidException(
                "[Vedirect::init_serial_connection_from_object] "
                "Unable to init init_serial_connection_from_object, "
                "bad parameters : %s" %
                serial_connection
            )
        return result

    def init_serial_connection(self,
                               serial_conf: dict,
                               source_name: str = 'Vedirect',
                               auto_start: bool = True
                               ) -> bool:
        """
        Initialise serial connection from parameters.

        At least serial_port must be provided.
        Default :
         - baud rate = 19200,
         - timeout = 0 (non blocking mode)
         - source_name = 'Vedirect'
        Raise:
         - SettingInvalidException if serial_port, baud or timeout are not valid.
         - VedirectException if connection to serial port fails
        :Example :
            >>> self.init_serial_connection({"serial_port": "/dev/ttyUSB1"})
            >>> True
        :param self: Refer to the object itself,
        :param serial_conf: dict: dict: The serial connection configuration,
        :param source_name: str: This is used in logger to identify the source of call,
        :param auto_start: bool: Define if serial connection must be established automatically.
        :return: True if connection to serial port success.
        """
        result = False
        serial_conf = SerialConnection.get_default_serial_conf(serial_conf)
        if SerialConnection.is_serial_conf(**serial_conf):
            serial_conf.update({"source_name": source_name})
            auto_start = Ut.str_to_bool(auto_start)
            self._com = SerialConnection(**serial_conf)
            if auto_start is False\
                    or (auto_start is True
                        and self.connect_to_serial()):
                result = True
        else:
            raise SettingInvalidException(
                "[Vedirect::init_serial_connection] "
                "Unable to init SerialConnection, "
                "bad parameters. serial_conf : %s" %
                serial_conf
            )
        return result

    def init_settings(self,
                      serial_conf: dict,
                      source_name: str = 'Vedirect',
                      auto_start: bool = True
                      ) -> bool:
        """
        Initialise the settings for the class.

        At least serial_port must be provided.
        Default :
         - baud rate = 19200,
         - timeout = 0 (non blocking mode)
         - source_name = 'Vedirect'
        Raise:
         - SettingInvalidException if serial_port, baud or timeout are not valid.
         - VedirectException if connection to serial port fails
        :Example :
            >>> self.init_settings({"serial_port": "/dev/ttyUSB1"})
            >>> True
        :param self: Refer to the object itself,
        :param serial_conf: dict: The serial connection configuration,
        :param source_name: This is used in logger to identify the source of call,
        :param auto_start: bool: Define if serial connection must be established automatically.
        :return: True if connection to serial port success.
        """
        return self.init_serial_connection(serial_conf=serial_conf,
                                           source_name=source_name,
                                           auto_start=auto_start
                                           )

    def init_data_read(self):
        """ Initialise reader properties """
        self.key = ''
        self.value = ''
        self.bytes_sum = 0
        self.state = self.WAIT_HEADER
        self.dict = {}

    def input_read(self, byte) -> dict or None:
        """Input read from byte."""
        try:
            nbyte = ord(byte)
            if byte == self._delimiters.get("hexmarker")\
                    and self.state != self.IN_CHECKSUM:
                self.state = self.HEX
            if self.state == self.WAIT_HEADER:
                self.bytes_sum += nbyte
                if nbyte == self._delimiters.get("header1"):
                    self.state = self.WAIT_HEADER
                elif nbyte == self._delimiters.get("header2"):
                    self.state = self.IN_KEY
                return None
            elif self.state == self.IN_KEY:
                self.bytes_sum += nbyte
                if nbyte == self._delimiters.get("delimiter"):
                    if self.key == 'Checksum':
                        self.state = self.IN_CHECKSUM
                    else:
                        self.state = self.IN_VALUE
                else:
                    self.key += byte.decode('ascii')
                return None
            elif self.state == self.IN_VALUE:
                self.bytes_sum += nbyte
                if nbyte == self._delimiters.get("header1"):
                    self.state = self.WAIT_HEADER
                    self.dict[self.key] = self.value
                    self.key = ''
                    self.value = ''
                else:
                    self.value += byte.decode('ascii')
                return None
            elif self.state == self.IN_CHECKSUM:
                self.bytes_sum += nbyte
                self.key = ''
                self.value = ''
                self.state = self.WAIT_HEADER
                if self.bytes_sum % 256 == 0:
                    self.bytes_sum = 0
                    return self.dict
                else:
                    self.bytes_sum = 0
            elif self.state == self.HEX:
                self.bytes_sum = 0
                if nbyte == self._delimiters.get("header2"):
                    self.state = self.WAIT_HEADER
            else:
                raise AssertionError()
        except Exception as ex:
            raise InputReadException(
                "[Vedirect::input_read] "
                "Serial input read error"
            ) from ex

    def get_serial_packet(self) -> dict or None:
        """
        Return Ve Direct block packet from serial reader.

        Read a byte from serial and decode him with vedirect protocol.
        :return: A dictionary of vedirect block data or None if block not entirely decoded.
        """
        byte = self._com.ser.read(1)
        if byte == b'\x00':
            byte = self._com.ser.read(1)
        return self.input_read(byte)

    def read_data_single(self, timeout: int = 60) -> dict or None:
        """
        Read a single block decoded from serial port and returns it as a dictionary.

        :Example :
            >>> ve = Vedirect({"serial_port": "/dev/ttyUSB1"})
            >>> ve.read_data_single(timeout=3)
            >>> {'V': '12800', 'VS': '12800', 'VM': '1280', ...}

        :param self: Reference the class instance
        :param timeout: Set the timeout for the read_data_single function
        :return: A dictionary of the data
        """
        run, now, tim = True, time.time(), 0
        self.time_packet = 0
        if self.is_ready():
            try:
                while run:
                    packet, tim = None, time.time()

                    packet = self.get_serial_packet()

                    if packet is not None:
                        self.time_packet = tim
                        logger.debug(
                            "Serial reader success: dict: %s",
                            self.dict
                        )
                        return packet

                    # timeout serial read
                    Vedirect.is_timeout(tim-now, timeout)
            except SerialException as ex:
                raise VedirectException(
                    "[VeDirect:read_data_single] "
                    "Unable to read vedirect data : %s.",
                    ex
                ) from SerialException
        else:
            logger.error('[VeDirect] Unable to read serial data. Not connected to serial port...')

        return None

    def read_data_callback(self,
                           callback_function,
                           timeout: int = 60,
                           max_loops: int or None = None
                           ):
        """
        Read data from the serial port and returns it to a callback function.

        :param self: Reference the class instance
        :param callback_function:function: Pass a function to the read_data_callback function
        :param timeout:int=60: Set the timeout for the read_data_callback function
        :param max_loops:int or None=None: Limit the number of loops
        """
        run, now, tim, i = True, time.time(), 0, 0
        if self.is_ready():
            while run:
                tim = time.time()
                packet = self.get_serial_packet()

                if packet is not None:
                    logger.debug(
                        "Serial reader success: packet: %s "
                        "-- state: %s -- bytes_sum: %s ",
                        packet, self.state, self.bytes_sum
                    )
                    callback_function(packet)
                    now = tim
                    i = i + 1

                # timeout serial read
                Vedirect.is_timeout(tim-now, timeout)
                if isinstance(max_loops, int) and 0 < max_loops <= i:
                    return True
                time.sleep(0.1)
        else:
            raise VedirectException(
                '[VeDirect::read_data_callback] '
                'Unable to read serial data. '
                'Not connected to serial port...')

    @staticmethod
    def is_serial_com(obj: SerialConnection) -> bool:
        """
        Test if obj is valid SerialConnection instance.

        :Example :
            >>> Vedirect.is_serial_com(obj)
            >>> True
        :param obj: The object to test.
        :return: True if obj is valid SerialConnection instance.
        """
        return isinstance(obj, SerialConnection)

    @staticmethod
    def is_timeout(elapsed: float or int, timeout: float or int = 60) -> bool:
        """
        Test if elapsed time is greater than timeout.

        :Example :
            >>> Vedirect.is_timeout(elapsed=45, timeout=60)
            >>> True
        :param elapsed: The elapsed time to test,
        :param timeout: The timeout to evaluate.
        :return: True if elapsed time is upper than timeout.
        """
        if elapsed >= timeout:
            raise TimeoutException(
                '[VeDirect::is_timeout] '
                'Unable to read serial data. '
                'Timeout error.'
            )
        return True
