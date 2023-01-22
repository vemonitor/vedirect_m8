# -*- coding: utf-8 -*-
"""
Used to decode the Victron Energy VE.Direct text protocol.

This is a forked version of script originally created by Janne Kario.
    - original: https://github.com/karioja/vedirect.
    - repo: https://github.com/mano8/vedirect_m8.
 Raise:
    - VedirectException: when any exception is raised.
      All extends from it.
    - SettingInvalidException: when invalid setting is set.
    - VeReadException: when any exception occurs on reading data.
      All read exception extends from it.
    - InputReadException: when error on reading serial byte
    - PacketReadException: when error on reading serial packet (Invalid packet).
    - ReadTimeoutException: when serial read timeout exceeded.
    - SerialConnectionException: when any exception occurs on connecting serial port.
      All connection exception extends from it.
    - SerialConfException: When serial connection settings is bad
    - SerialVeException: In case the device can not be found or can not be configured.
      From serial.SerialException
    - OpenSerialVeException: Will be raised when the device is configured but port is not opened.
"""
import logging
import time
from serial import SerialException
from ve_utils.utype import UType as Ut
from vedirect_m8.helpers import TimeoutHelper
from vedirect_m8.helpers import CountersHelper
from vedirect_m8.serconnect import SerialConnection
from vedirect_m8.exceptions import SettingInvalidException
from vedirect_m8.exceptions import InputReadException
from vedirect_m8.exceptions import PacketReadException
from vedirect_m8.exceptions import ReadTimeoutException
from vedirect_m8.exceptions import SerialConnectionException
from vedirect_m8.exceptions import SerialConfException
from vedirect_m8.exceptions import SerialVeException

__author__ = "Janne Kario, Eli Serra"
__copyright__ = "Copyright 2015, Janne Kario"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vedirect")


class VedirectReaderHelper:
    """Class helper used to read vedirect protocol from serial port."""

    def __init__(self, max_packet_blocks: int or None = 18):
        self._delimiters = {
            "header1": ord('\r'),
            "header2": ord('\n'),
            "hexmarker": ord(':'),
            "delimiter": ord('\t')
        }
        self.max_blocks = 18
        self.key = ''
        self.value = ''
        self.bytes_sum = 0
        self.state = self.WAIT_HEADER
        self.dict = {}
        self.set_max_packet_blocks(max_packet_blocks)

    (HEX, WAIT_HEADER, IN_KEY, IN_VALUE, IN_CHECKSUM) = range(5)

    def has_free_block(self) -> bool:
        """Test if block of key value can be added to dict packet."""
        return self.max_blocks is None\
            or len(self.dict) <= self.max_blocks

    def set_max_packet_blocks(self, value: int or None) -> bool:
        """
        Set max blocks by packet value.

        If input packet in dict has more key that max_blocks,
        raise a PacketReadException on reading serial.
        To disable this limitation, set the value to None.
        By default, the value is 18 blocks per packet.
        (See VeDirect protocol)

        Example :
            >>> self.set_max_packet_blocks(22)
            >>> True
        :param value: max blocks by packet value
        :return: True if max blocks by packet value is updated.

        Raise:
         - SettingInvalidException: if the value is invalid.
        """
        result = True
        self.max_blocks = 18
        if Ut.is_int(value, positive=True):
            self.max_blocks = value
        elif value is None:
            self.max_blocks = None
        else:
            raise SettingInvalidException(
                "[Vedirect:set_max_packet_blocks] "
                "Max blocks by packet value is not valid. "
                "Value must be integer or null. "
            )
        return result

    def reset_data_read(self):
        """ Reset reader cache properties """
        self.key = ''
        self.value = ''
        self.bytes_sum = 0
        self.state = self.WAIT_HEADER
        self.dict = {}

    def is_state(self, value: int) -> bool:
        """ Initialise reader properties """
        return self.state == value

    def is_delimiter(self, key: str, value: int) -> bool:
        """ Test if value is equal to delimiter key value"""
        return self._delimiters.get(key) == value

    def is_unexpected_header(self, data: int) -> bool:
        """ Test if byte is unexpected block header."""
        return (self.is_state(self.IN_KEY)
                and (self.is_delimiter("header1", data)
                     or self.is_delimiter("header2", data)))\
            or (self.is_state(self.IN_VALUE)
                and self.is_delimiter("header2", data))

    def run_wait_header(self, data: int) -> None:
        """ Wait block header."""
        self.bytes_sum += data
        if self.is_delimiter("header1", data):
            self.state = self.WAIT_HEADER
        elif self.is_delimiter("header2", data):
            self.state = self.IN_KEY

    def run_in_key(self, data: int, byte: bytes) -> None:
        """ Get block key. """
        self.bytes_sum += data
        if self.is_delimiter("delimiter", data):
            if self.key == 'Checksum':
                self.state = self.IN_CHECKSUM
            else:
                self.state = self.IN_VALUE
        else:
            self.key += byte.decode('ascii')

    def run_in_value(self, data: int, byte: bytes) -> None:
        """ Get block value. """
        self.bytes_sum += data
        if self.is_delimiter("header1", data):
            if not self.has_free_block():
                raise PacketReadException(
                    "[Vedirect::input_read] "
                    "Serial input read error: "
                    f"Packet read limit: {len(self.dict)} / {self.max_blocks} blocks"
                    f"packet: {self.dict}"
                )
            self.state = self.WAIT_HEADER
            self.dict[self.key] = self.value
            self.key = ''
            self.value = ''
        else:
            self.value += byte.decode('ascii')

    def run_in_checksum(self, data: int) -> dict or None:
        """ Control checksum and return read packet. """
        self.bytes_sum += data
        self.key = ''
        self.value = ''
        self.state = self.WAIT_HEADER
        if not self.bytes_sum % 256 == 0:
            raise PacketReadException(
                "[Vedirect::input_read] "
                f"Checksum Packet error (!=0): {self.bytes_sum % 256} -- "
                f"Packet Blocks : {len(self.dict)} / {self.max_blocks} -- "
                f"packet: {self.dict}"
            )
        else:
            self.bytes_sum = 0
            return self.dict

    def run_in_hex(self, data: int) -> None:
        """ Read a hex value, aboard and wait header. """
        self.bytes_sum = 0
        if self.is_delimiter("header1", data):
            self.state = self.WAIT_HEADER


class Vedirect:
    """
    Used to decode the Victron Energy VE.Direct text protocol.

    This is a forked version of script originally created by Janne Kario.
    (https://github.com/karioja/vedirect).

    :Example:
        >>> sc = Vedirect(
        >>>     serial_conf={"serial_port": "/dev/ttyUSB1"}
        >>> )
        >>> sc.read_data_single()
        >>> {"ser_key1": "ser_value1", ...}

    Raise:
        - SettingInvalidException
        - InputReadException
        - PacketReadException
        - ReadTimeoutException
        - SerialConnectionException
        - SerialConfException
        - SerialVeException
        - OpenSerialVeException
    """
    def __init__(self,
                 serial_conf: dict,
                 options: dict or None = None
                 ):
        """
        Constructor of Vedirect class.

        :Example:
            >>> sc = Vedirect(
            >>>     serial_conf={"serial_port": "/dev/ttyUSB1"}
            >>> )
            >>> sc.read_data_single()
            >>> {"ser_key1": "ser_value1", ...}
        :param self: Refer to the object instance itself,
        :param serial_conf: dict: The serial connection configuration,
        :param options: Options parameters as dict,
        :return: Nothing
        """
        self._com = None
        self.helper = None
        self._counter = CountersHelper()
        self.init_settings(serial_conf=serial_conf,
                           options=options
                           )

    def has_serial_com(self) -> bool:
        """Test if _com is a valid SerialConnection instance."""
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
        """
        Connect to serial port if not connected.

        Raise:
         - SerialConfException: when invalid parameter is set.
         - OpenSerialVeException: when serial device configured,
           but connection not opened.
         - SerialVeException: on raise serial.SerialException
         - SerialConnectionException: on connection fails
        """
        if self.has_serial_com()\
                and ((not self._com.is_ready() and self._com.connect())
                     or self._com.is_ready()):
            result = True
            time.sleep(0.5)
        else:
            raise SerialConnectionException(
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
         - SerialConfException: if serial_port, baud or timeout are not valid.
         - OpenSerialVeException: when serial device configured,
           but connection not opened.
         - SerialVeException: on raise serial.SerialException
         - SerialConnectionException: on connection fails
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
            raise SerialConfException(
                "[Vedirect::init_serial_connection_from_object] "
                "Unable to init init_serial_connection_from_object, "
                f"bad parameters: {serial_connection}"
            )
        return result

    def init_serial_connection(self,
                               serial_conf: dict,
                               auto_start: bool = True,
                               ) -> bool:
        """
        Initialise serial connection from parameters.

        At least serial_port must be provided.
        serial_conf default :
         - baud rate = 19200,
         - timeout = 0 (non blocking mode)
         - source_name = 'Vedirect'
        Raise:
         - SerialConfException: if serial_port, baud or timeout are not valid.
         - OpenSerialVeException: when serial device configured,
           but connection not opened.
         - SerialVeException: on raise serial.SerialException
         - SerialConnectionException: on connection fails
        :Example :
            >>> self.init_serial_connection({"serial_port": "/dev/ttyUSB1"})
            >>> True
        :param self: Refer to the object itself,
        :param serial_conf: dict: dict: The serial connection configuration,
        :param auto_start: bool: Define if serial connection must be established automatically.
        :return: True if connection to serial port success.
        """
        result = False
        self._com = SerialConnection(**serial_conf)
        if self._com.is_settings():
            auto_start = Ut.str_to_bool(auto_start)
            if auto_start is False\
                    or (auto_start is True
                        and self.connect_to_serial()):
                result = True
        else:
            raise SerialConfException(
                "[Vedirect::init_serial_connection] "
                "Unable to init SerialConnection, "
                f"bad parameters. serial_conf : {serial_conf}"
            )
        return result

    def init_settings(self,
                      serial_conf: dict,
                      options: dict or None = None
                      ) -> bool:
        """
        Initialise the settings for the class.

        At least serial_port must be provided.

        serial_conf default :
         - baud rate = 19200,
         - timeout = 0 (non blocking mode)

        options default :
         - source_name: "VeDirect"
         - max_packet_blocks: 18
         - auto_start: True

        :Example :
            >>> self.init_settings({"serial_port": "/dev/ttyUSB1"})
            >>> True
        :param self: Refer to the object itself,
        :param serial_conf: dict: The serial connection configuration,
        :param options: Options parameters as dict,
        :return: True if connection to serial port success.

        Raise:
         - SerialConfException: if serial_port, baud or timeout are not valid.
         - OpenSerialVeException: when serial device configured,
           but connection not opened.
         - SerialVeException: on raise serial.SerialException
         - SerialConnectionException: on connection fails
        """
        logger.info(
            '[Vedirect::init_settings] '
            'Start Vedirect instance.'
        )
        max_packet_blocks = 18
        auto_start = True
        if Ut.is_dict(options, not_null=True):
            max_packet_blocks = options.get('max_packet_blocks') or 18
            if options.get('auto_start') is not None:
                auto_start = Ut.str_to_bool(options.get('auto_start'))

        self.helper = VedirectReaderHelper(max_packet_blocks)
        return self.init_serial_connection(serial_conf=serial_conf,
                                           auto_start=auto_start
                                           )

    def flush_serial_cache(self) -> bool:
        """Flush serial cache data from serial port."""
        result = False
        if self.is_ready():
            self._com.flush_serial_cache()
            result = True
        return result

    def get_bitrate_duration(self) -> float:
        """Get serial bite rate time in s."""
        result = 0.0
        if self.has_serial_com()\
                and Ut.is_dict(self._com.bit_rates)\
                and Ut.is_float(self._com.bit_rates.get('real_byte_duration_ms')):
            result = Ut.get_rounded_float(
                self._com.bit_rates.get('real_byte_duration_ms') / 1000,
                9,
                default=0.0
            )
        return result

    def get_counter_key_value(self, key: str) -> int:
        """Get serial bite rate time in s."""
        result = -1
        if isinstance(self._counter, CountersHelper):
            if key == "packet":
                if self._counter.has_counter_key('callback_packets'):
                    result = self._counter.get_key_value('callback_packets')
                elif self._counter.has_counter_key('simple_packets'):
                    result = self._counter.get_key_value('simple_packets')
            elif key == "packet_errors":
                if self._counter.has_counter_key('callback_packet_errors'):
                    result = self._counter.get_key_value('callback_packet_errors')
                elif self._counter.has_counter_key('single_packet_errors'):
                    result = self._counter.get_key_value('single_packet_errors')
            elif key == "block_errors":
                if self._counter.has_counter_key('callback_block_errors'):
                    result = self._counter.get_key_value('callback_block_errors')
                elif self._counter.has_counter_key('single_block_errors'):
                    result = self._counter.get_key_value('single_block_errors')
            elif key == "byte":
                if self._counter.has_counter_key('single_byte'):
                    result = self._counter.get_key_value('single_byte')
        return result

    def input_read(self, byte: bytes) -> dict or None:
        """
        Input flow read from byte.

        Raise:
         - PacketReadException:
           - when malformed packet, with unexpected header (\r or \n).
           - when malformed packet, with checksum error.
           - when malformed packet, with max blocks per packet limit.
         - InputReadException: when any other error occurs.

        """
        result = None
        try:
            ord_byte = ord(byte)
            if self.helper.is_unexpected_header(ord_byte):
                raise PacketReadException(
                    "[Vedirect::input_read] "
                    f"Unexpected byte header in packet: {byte} --> next byte: {self._com.ser.read(1)}\n"
                    f"Packet read limit: {len(self.helper.dict)} / {self.helper.max_blocks} blocks"
                    f"packet: {self.helper.dict}"
                )
            if self.helper.is_delimiter("hexmarker", ord_byte)\
                    and self.helper.state != self.helper.IN_CHECKSUM:
                self.helper.state = self.helper.HEX
            #
            if self.helper.is_state(self.helper.WAIT_HEADER):
                self.helper.run_wait_header(ord_byte)
            #
            elif self.helper.is_state(self.helper.IN_KEY):
                self.helper.run_in_key(ord_byte, byte)
            #
            elif self.helper.is_state(self.helper.IN_VALUE):
                self.helper.run_in_value(ord_byte, byte)
            #
            elif self.helper.is_state(self.helper.IN_CHECKSUM):
                result = self.helper.run_in_checksum(ord_byte)
            #
            elif self.helper.is_state(self.helper.HEX):
                self.helper.run_in_hex(ord_byte)
            else:
                raise AssertionError()
        except PacketReadException as ex:
            raise ex
        except Exception as ex:
            raise InputReadException(
                "[Vedirect::input_read] "
                f"Serial input read error on byte : {byte}"
            ) from ex

        return result

    def get_serial_packet(self) -> dict or None:
        """
        Return Ve Direct block packet from serial reader.

        Read a byte from serial and decode him with vedirect protocol.
        :return: A dictionary of vedirect block data or None if block not entirely decoded.
        """
        byte = self._com.ser.read(1)
        return self.input_read(byte)

    def read_data_single(self,
                         timeout: int = 60,
                         max_block_errors: int = 0,
                         max_packet_errors: int = 0
                         ) -> dict or None:
        """
        Read a single packet decoded from serial port and returns it as a dictionary.

        :Example :
            >>> ve = Vedirect({"serial_port": "/dev/ttyUSB1"})
            >>> ve.read_data_single(timeout=3)
            >>> {'V': '12800', 'VS': '12800', 'VM': '1280', ...}

        :param self: Reference the class instance
        :param timeout: Set the timeout for the read_data_single function
        :param max_block_errors:int=0: Define nb errors permitted on read blocks
          before exit (InputReadException)
        :param max_packet_errors:int=0: Define nb errors permitted on read packets
          before exit (PacketReadException)
        :return: A dictionary of the data
        - SerialConfException:
           Will be raised when parameter
           are out of range or invalid,
           e.g. serial_port, baud rate, data bits
         - SerialVeException:
           In case the device can not be found or can not be configured.
         - OpenSerialVeException:
           Will be raised when the device is configured but port is not openned.
        """
        run, timer = True, TimeoutHelper()
        timer.set_start()
        self._counter.add_counter_key('single_byte', reset=True)
        self._counter.add_counter_key('single_packet')
        self._counter.add_counter_key('single_packet_errors')
        self._counter.add_counter_key('single_block_errors', reset=True)
        max_block_errors = Ut.get_int(max_block_errors, 0)
        max_packet_errors = Ut.get_int(max_packet_errors, 0)
        sleep_time = self.get_bitrate_duration()
        if self.is_ready():
            while run:
                try:
                    timer.set_now()
                    packet = self.get_serial_packet()
                    self._counter.add_to_key('single_byte')
                    if packet is not None:
                        logger.debug(
                            "Serial reader success: dict: %s",
                            packet
                        )
                        self.helper.reset_data_read()
                        self._counter.add_to_key('single_packet')
                        return packet
                    # timeout serial read
                    timer.is_timeout_callback(
                        timeout=timeout,
                        callback=Vedirect.raise_timeout
                    )
                except InputReadException as ex:
                    self.helper.reset_data_read()
                    if Vedirect.is_max_read_error(
                            max_block_errors,
                            self._counter.get_key_value('single_block_errors')):
                        raise InputReadException(ex) from InputReadException
                    self._counter.add_to_key('single_block_errors')
                except PacketReadException as ex:
                    self.helper.reset_data_read()
                    if Vedirect.is_max_read_error(
                            max_packet_errors,
                            self._counter.get_key_value('single_packet_errors')):
                        raise ex
                    self._counter.add_to_key('single_packet_errors')
                except SerialException as ex:
                    self.helper.reset_data_read()
                    raise SerialVeException(
                        "[VeDirect:read_data_single] "
                        "Unable to read vedirect data."
                    ) from ex

                # sleep to ensure reading speed not exceed serial bitrate
                Vedirect.sleep_on_demand(sleep_time)

        else:
            raise SerialConnectionException(
                "[VeDirect:read_data_single] "
                "Unable to read vedirect data, serial port is closed."
            )

    def sleep_on_read_single_loop(self,
                                  sleep_time: int or float,
                                  execution_timer: TimeoutHelper or None = None
                                  ) -> bool or None:
        """
        Used to compensate sleep duration on read single loops.

        In read_data_single method for every byte read,
        sleep time is defined by serial bitrate duration.

        To compensate sleep duration on main loop, we rest:
            - byte_counter value * bitrate_duration
              (total sleep time in read_data_single method)
            - Optional execution time value

        :return: None if no sleep executed,
            False if sleep not compensate time (sleep_time value),
            or True if sleep compensate time

        """
        result = None

        is_sleep_time = Ut.is_numeric(sleep_time, positive=True)
        execution_time = 0
        if isinstance(execution_timer, TimeoutHelper):
            execution_timer.set_now()
            execution_time = execution_timer.get_elapsed()
        if Ut.is_numeric(execution_time, positive=True)\
                and is_sleep_time\
                and 0 < execution_time < sleep_time:
            sleep_total = sleep_time - execution_time

            if Vedirect.sleep_on_demand(sleep_total):
                execution_timer.set_start()
                result = True

        if result is None\
                and is_sleep_time:
            bitrate_duration = self.get_bitrate_duration()
            byte_counter = self._counter.get_key_value('single_byte')
            if Ut.is_numeric(bitrate_duration, positive=True)\
                    and Ut.is_int(byte_counter, positive=True):

                sleep_p = sleep_time - (byte_counter * bitrate_duration)
                if Vedirect.sleep_on_demand(sleep_p):
                    result = True

        if result is None\
                and is_sleep_time\
                and Vedirect.sleep_on_demand(sleep_time):
            result = False
        return result

    def read_data_callback(self,
                           callback_function,
                           options: dict or None = None
                           ):
        """
        Read data from the serial port and returns it to a callback function.

        max_block_errors and max_packet_errors possible values:
            - -1: never exit
            - 0: exit on first error
            - x: exit after x errors

        Method options available:
          - timeout:int=60: Set the timeout for the read_data_callback function
          - sleep_time:int=1: Define time to sleep between 2 packet read
          - max_loops:int or None=None: Limit the number of loops
          - max_block_errors:int=0: Define nb errors permitted on read blocks
          before exit (InputReadException)
          - max_packet_errors:int=1: Define nb errors permitted on read packets
          before exit (PacketReadException)

        :param self: Reference the class instance
        :param callback_function:function: Pass a function to the read_data_callback function
        :param options:dict: Method options see on description
        """
        run, timer = True, TimeoutHelper()
        execution_time = TimeoutHelper()
        params = Vedirect.get_read_data_params(options)

        self._counter.add_counter_key('callback_packets', True)
        self._counter.add_counter_key('callback_packet_errors', True)

        logger.debug(
            '[Vedirect::read_data_callback] '
            'Start to decode Vedirect data from serial port . '
            'options: %s',
            options
        )
        timer.set_start()
        if self.is_ready():

            while run:
                try:
                    timer.set_now()
                    packet = self.read_data_single(
                        timeout=params.get('timeout'),
                        max_block_errors=params.get('max_block_errors'),
                        max_packet_errors=params.get('max_packet_errors')
                    )

                    if packet is not None:
                        logger.debug(
                            "Serial reader success: packet: %s \n"
                            "-- state: %s -- bytes_sum: %s -- time to read: %s",
                            packet,
                            self.helper.state,
                            self.helper.bytes_sum,
                            timer.get_elapsed()
                        )
                        self._counter.add_to_key('callback_packets')
                        self.helper.reset_data_read()
                        callback_function(packet)
                        timer.set_start()

                    # timeout serial read
                    timer.is_timeout_callback(
                        timeout=params.get('timeout'),
                        callback=Vedirect.raise_timeout
                    )

                    if self._counter.is_max_key(
                            'callback_packets',
                            params.get('max_loops')):
                        return True
                except PacketReadException as ex:
                    self.helper.reset_data_read()
                    if Vedirect.is_max_read_error(
                            params.get('max_packet_errors'),
                            self._counter.get_key_value('callback_packet_errors')):
                        raise ex
                    self._counter.add_to_key('callback_packet_errors')

                self.sleep_on_read_single_loop(
                    params.get('sleep_time'),
                    execution_time
                )

        else:
            raise SerialConnectionException(
                '[VeDirect::read_data_callback] '
                'Unable to read serial data. '
                'Not connected to serial port...'
            )

    @staticmethod
    def sleep_on_demand(sleep_time: int or float) -> bool:
        """Used to Sleep only if is valid sleep_time."""
        result = False
        if sleep_time > 0:
            time.sleep(sleep_time)
            result = True
        return result

    @staticmethod
    def get_default_read_data_params(options: dict or None = None):
        """Get default read_data parameters"""
        return {
            'timeout': 2,
            'sleep_time': 1,
            'max_loops': None,
            'max_block_errors': 0,
            'max_packet_errors': 0
        }

    @staticmethod
    def get_read_data_params(options: dict or None = None):
        """Get formatted read_data parameters"""
        result = Vedirect.get_default_read_data_params()

        if Ut.is_dict(options, not_null=True):

            timeout = options.get('timeout')
            if Ut.is_numeric(timeout, positive=True):
                result['timeout'] = timeout
            elif timeout is not None:
                raise SettingInvalidException(
                    "[Vedirect:get_read_data_callback_params] "
                    "Invalid timeout parameter, "
                    "Must be positive int or float type."
                )

            sleep_time = options.get('sleep_time')
            if Ut.is_numeric(sleep_time, positive=True):
                result['sleep_time'] = sleep_time
            elif sleep_time is not None:
                raise SettingInvalidException(
                    "[Vedirect:get_read_data_callback_params] "
                    "Invalid sleep_time parameter, "
                    "Must be positive int or float type."
                )

            max_loops = options.get('max_loops')
            if Ut.is_int(max_loops, positive=True):
                result['max_loops'] = max_loops
            elif max_loops is not None:
                raise SettingInvalidException(
                    "[Vedirect:get_read_data_callback_params] "
                    "Invalid max_loops parameter, "
                    "Must be positive int type."
                )

            max_block_errors = options.get('max_block_errors')
            if Ut.is_int(max_block_errors):
                result['max_block_errors'] = max_block_errors
            elif max_block_errors is not None:
                raise SettingInvalidException(
                    "[Vedirect:get_read_data_callback_params] "
                    "Invalid max_block_errors parameter, "
                    "Must be int type."
                )

            max_packet_errors = options.get('max_packet_errors')
            if Ut.is_int(max_packet_errors):
                result['max_packet_errors'] = max_packet_errors
            elif max_packet_errors is not None:
                raise SettingInvalidException(
                    "[Vedirect:get_read_data_callback_params] "
                    "Invalid max_packet_errors parameter, "
                    "Must be int type."
                )
        return result

    @staticmethod
    def is_max_read_error(max_value: int, counter: int) -> bool:
        """Get sleep time value or default if invalid type or value."""
        result = False
        if max_value == 0:
            result = True
        elif max_value > 0 and 0 <= counter <= max_value:
            result = True
        return result

    @staticmethod
    def set_sleep_time(value: int or float, default: int or float = 0) -> int or float:
        """Get sleep time value or default if invalid type or value."""
        value = Ut.get_float(value, default)
        if value <= 0:
            value = default
        return value

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
        return isinstance(obj, SerialConnection)\
            and obj.get_serial_port() is not None

    @staticmethod
    def is_timeout(elapsed: float or int, timeout: float or int = 60) -> bool:
        """
        Test if elapsed time is greater than timeout.

        :Example :
            >>> Vedirect.is_timeout(elapsed=45, timeout=60)
            >>> True
        :param elapsed: The elapsed time to test,
        :param timeout: The timeout to evaluate.
        :return: True if elapsed time is uppermore than timeout.
        """
        if elapsed >= timeout:
            Vedirect.raise_timeout(elapsed, timeout)
        return True

    @staticmethod
    def raise_timeout(elapsed: float or int, timeout: float or int = 60) -> bool:
        """Raise timeout exception"""
        raise ReadTimeoutException(
            '[VeDirect::is_timeout] '
            'Unable to read serial data. '
            f'Timeout error: {elapsed}s of {timeout}s '
        )
