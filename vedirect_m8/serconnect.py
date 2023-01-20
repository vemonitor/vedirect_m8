# -*- coding: utf-8 -*-
"""
Connect to serial port.

Contain method to scan all available ports.

 .. see also: Vedirect, VedirectController
 Raise:
  - SerialConfException,
  - OpenSerialVeException
  - SerialVeException
"""
import logging
import os
from serial import Serial, SerialException
import serial.tools.list_ports as serial_list_ports
from ve_utils.usys import USys
from vedirect_m8.serutils import SerialUtils as Ut
from vedirect_m8.exceptions import SerialConfException
from vedirect_m8.exceptions import OpenSerialVeException
from vedirect_m8.exceptions import SerialVeException

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "3.0.0"

logging.basicConfig()
logger = logging.getLogger("vedirect")


class SerialConnectionHelper:
    """
    SerialConnection class helper

    Available parameters:
          - serial_port = None: str or None: Serial port path to open
          - baudrate = 19600: int: Baud rate such as 9600 or 115200 etc.
          - timeout = 0: int or float or None: Set read timeout value in seconds
          - write_timeout = 0: int or float or None: Set write timeout value in seconds
          - exclusive = False: bool: Set exclusive access mode (POSIX only).
            A port cannot be opened in exclusive access mode
            if it is already open in exclusive access mode.
          - source_name: str: This is used in logger to identify the source of call
    """

    def __init__(self,
                 set_default: bool = True,
                 **kwargs
                 ):
        self.ser = None
        self._conf = None
        self._init_settings(conf=kwargs, set_default=set_default)

    def _is_serial_ready(self) -> bool:
        """
        Test if is serial connection is ready.

        :return: True if self._ser is an instance of Serial and if the serial connection is opened.
        """
        return isinstance(self.ser, Serial) and self.ser.isOpen()

    def has_conf(self) -> str or None:
        """Return source_name value from instance."""
        return Ut.is_dict(self._conf, not_null=True)

    def get_conf_key(self, key: str) -> any:
        """Return source_name value from instance."""
        result = None
        if self.has_conf() and Ut.is_str(key):
            result = self._conf.get(key)
        return result

    def get_source_name(self) -> str or None:
        """Return source_name value from instance."""
        return self.get_conf_key('source_name')

    def get_serial_port(self) -> str or None:
        """Return serial_port value from instance."""
        return self.get_conf_key('serial_port')

    def get_timeout(self) -> int or float:
        """Return timeout value from instance."""
        return self.get_conf_key('timeout')

    def is_settings(self) -> bool:
        """
        Test if class instance has valid configuration settings.

        :return: True if is valid configuration settings.
        """
        return SerialConnectionHelper.is_serial_conf(conf=self._conf)

    def _init_settings(self,
                       conf: dict or None,
                       set_default: bool = True,
                       ) -> bool:
        """
        Initialise configuration settings.
        :Example :
            >>> self._init_settings(conf={
            >>>     "serial_port": "/tmp/vmodem0",
            >>>     "baudrate": 19200,
            >>>     "timeout": 0,
            >>>     "write_timeout": 0,
            >>>     "exclusive": False,
            >>>     "source_name": "BMV700"
            >>> })
            >>> True
        Available parameters:
          - serial_port = None: str or None: Serial port path to open
          - baudrate = 19600: int: Baud rate such as 9600 or 115200 etc.
          - timeout = 0: int or float or None: Set read timeout value in seconds
          - write_timeout = 0: int or float or None: Set write timeout value in seconds
          - exclusive = False: bool: Set exclusive access mode (POSIX only).
            A port cannot be opened in exclusive access mode
            if it is already open in exclusive access mode.
          - source_name: str: This is used in logger to identify the source of call
        :return: True if configuration settings are valid.
        """
        logger.info(
            '[SerialConnectionHelper::init_settings] '
            'Start SerialConnectionHelper instance.'
        )
        if Ut.is_bool(conf.get('set_default')):
            set_default = conf.pop('set_default')

        self._conf = SerialConnectionHelper.set_serial_conf(
            conf=conf,
            set_default=set_default
        )
        return self.is_settings()

    def _set_serial_conf(self,
                         conf: dict or None = None,
                         set_default: bool = False
                         ) -> dict or None:
        """
        Set serial configuration settings to open serial connection.

        :Example :
            >>> self._set_serial_conf(
            >>>     serial_port="/tmp/vmodem0",
            >>>     baudrate=19200,
            >>>     timeout=0,
            >>>     write_timeout=0,
            >>>     exclusive=True
            >>> )
            >>> True
        :param serial_port: The serial port
        :param baudrate: The serial baud rate
        :param timeout: The serial timeout
        :param write_timeout: The serial write timeout
        :param exclusive: Set exclusive access mode (POSIX only).
            A port cannot be opened in exclusive access mode
            if it is already open in exclusive access mode.
        :return: a dictionary with the configuration to open a serial connection.
            Or None if a parameter is invalid.
        """
        result = None
        if conf is not None:
            result = SerialConnectionHelper.set_serial_conf(
                conf=conf,
                old_conf=self._conf,
                set_default=set_default
            )
        else:
            result = self._conf

        result = Ut.get_items_from_dict(
            result,
            ['serial_port', 'baudrate', 'timeout', 'write_timeout', 'exclusive']
        )
        return result

    def get_serial_ports_list(self) -> list:
        """
        Get all available ports on the machine.

        First get available virtual serial ports on /tmp/ directory.
        Then use serial.tools.list_ports.comports() to get available serial ports.

        :Example :
            >>> self.get_serial_ports_list()
            >>> ['/tmp/vmodem0', '/tmp/vmodem1', '/dev/ttyUSB1']
        :return: List of serial ports and virtual serial ports available.
        """
        result = []
        try:
            # scan unix virtual serial ports ports
            result = self.get_unix_virtual_serial_ports_list()
            ports = serial_list_ports.comports()
            for port, desc, hwid in sorted(ports):
                if hwid != 'n/a':
                    result.append(port)
                    logger.debug(
                        "Serial port found : "
                        "%s: %s [%s]",
                        port, desc, hwid
                    )
        except Exception as ex:
            logger.error(
                '[SerialConnectionHelper::get_serial_ports_list::%s] '
                'Unable to list serial ports. '
                'exception : %s',
                self.get_source_name(), ex
            )
        return result

    def get_unix_virtual_serial_ports_list(self) -> list:
        """
        Get all available virtual ports from /tmp/ directory.

        The port name must respect the syntax :
            - ttyUSB[0-999]
            - ttyACM[0-999]
            - vmodem[0-999]

        :Example :
            >>> self.get_unix_virtual_serial_ports_list()
            >>> ['/tmp/vmodem0', '/tmp/vmodem1']

        :return: List of virtual serial ports available.
        """
        result = []
        try:
            if USys.is_op_sys_type('unix'):
                for path in SerialConnectionHelper._get_virtual_ports_paths():
                    tmp = SerialConnectionHelper._scan_path(path)
                    if Ut.is_list(tmp, not_null=True):
                        result = result + tmp
        except Exception as ex:
            logger.error(
                '[SerialConnectionHelper::get_unix_virtual_serial_ports_list::%s] '
                'Unable to list serial ports. '
                'exception : %s',
                self.get_source_name(), ex
            )
        return result

    @staticmethod
    def _scan_path(path: str) -> list:
        """Scan path and get serial ports from it."""
        result = None
        if path != "/dev" and os.path.exists(path):
            # get list files from path
            result = []
            for entry in os.scandir(path):
                if not os.path.isdir(entry.path) \
                        and Ut.is_serial_port_name_pattern(entry.name):
                    if os.path.exists(entry.path):
                        result.append(entry.path)
        return result

    @staticmethod
    def set_serial_conf(conf: dict or None,
                        old_conf: dict or None = None,
                        set_default: bool = True
                        ) -> dict:
        """Get serial configuration data with default values."""
        result = None
        if Ut.is_dict(conf, not_null=True):
            result = {}
            if SerialConnectionHelper.is_serial_conf(old_conf):
                result = old_conf
            elif set_default is True:
                result = SerialConnectionHelper.get_default_serial_conf()

            if SerialConnectionHelper.is_serial_port(conf.get('serial_port')):
                result['serial_port'] = conf.get('serial_port')

            if SerialConnectionHelper.is_timeout(conf.get('timeout', -1)):
                result['timeout'] = conf.get('timeout')

            if SerialConnectionHelper.is_baud(conf.get('baudrate')):
                result['baudrate'] = conf.get('baudrate')

            if SerialConnectionHelper.is_timeout(conf.get('write_timeout', -1)):
                result['write_timeout'] = conf.get('write_timeout')

            if conf.get('exclusive') is not None:
                result['exclusive'] = Ut.str_to_bool(conf.get('exclusive'))

            if Ut.is_key_pattern(conf.get('source_name')):
                result['source_name'] = conf.get('source_name')
        return result

    @staticmethod
    def get_default_serial_conf() -> dict:
        """Get serial configuration data with default values."""
        return {
            "serial_port": None,
            "baudrate": 19200,
            "timeout": 0,
            "write_timeout": 0,
            # "exclusive": None,
            "source_name": "SerialConnectionHelper"
        }

    @staticmethod
    def is_serial_conf(conf: dict or None) -> bool:
        """
        Test if valid serial configuration settings.

        :Example :
            >>> SerialConnectionHelper.is_serial_conf({
            >>>     "serial_port": "/tmp/vmodem0",
            >>>     "baudrate": 19200,
            >>>     "timeout": 0,
            >>>     "write_timeout": 0,
            >>>     "exclusive": False,
            >>>     "source_name": "BMV700"
            >>> })
            >>> True
        :param conf: The Configuration data
        :return: True if configuration settings are valid
        """
        return Ut.is_dict(conf) \
            and SerialConnectionHelper.is_serial_port(
                conf.get('serial_port')) \
            and SerialConnectionHelper.is_baud(
                conf.get('baudrate')) \
            and SerialConnectionHelper.is_timeout(
                conf.get('timeout'))

    @staticmethod
    def _get_virtual_ports_paths() -> list:
        """
        Return valid virtual serial ports paths.

        :return: list of valid virtual serial ports paths
        """
        return [os.path.expanduser('~')]

    @staticmethod
    def get_virtual_home_serial_port(port: str) -> str or None:
        """
        Return the virtual serial port path from user home directory.

        :Example :
            >>> SerialConnectionHelper.get_virtual_home_serial_port(
            >>>     port="vmodem0"
            >>> )
            >>> "/home/${USER}/vmodem0"
        :param port: The port name to join at user home directory.
        :return: the virtual serial port path from user home directory.
                 Or None if port is invalid virtual port name.
        """
        path = None
        if Ut.is_virtual_serial_port_pattern(port):
            path = os.path.join(os.path.expanduser('~'), port)
        return path

    @staticmethod
    def _is_virtual_serial_port(serial_port: str) -> bool:
        """
        Test if is valid virtual serial port.

        First split the serial port in path and port name.
        Then test if serial port is a string, if path and port name are valid.
        :Example :
            >>> SerialConnectionHelper._is_virtual_serial_port(
            >>>     serial_port="/tmp/vmodem0"
            >>> )
            >>> True
            >>> SerialConnectionHelper._is_virtual_serial_port(
            >>>     serial_port="/run/vmodem0"
            >>> )
            >>> False
        :param serial_port: The serial port to test.
        :return: True if the virtual serial port is valid.
        """
        name, path = SerialConnectionHelper._split_serial_port(serial_port)
        return Ut.is_str(serial_port) \
            and path in SerialConnectionHelper._get_virtual_ports_paths() \
            and Ut.is_virtual_serial_port_pattern(name)

    @staticmethod
    def _split_serial_port(serial_port: str) -> tuple:
        """
        Return serial port split in name and path.

        :Example :
            >>> SerialConnectionHelper._split_serial_port(
            >>>     serial_port="/tmp/vmodem0"
            >>> )
            >>> ('vmodem0', '/tmp')
        :param serial_port: The serial port to split.
        :return: Tuple of name and path.
        """
        name, path = None, None
        if Ut.is_str(serial_port):
            path, name = os.path.split(serial_port)
        return name, path

    @staticmethod
    def is_serial_port_exists(serial_port: str) -> bool:
        """
        Test serial_port path exists.

        :Example :
            >>> SerialConnectionHelper.is_serial_port_exists(
            >>>     serial_port="/tmp/vmodem0"
            >>> )
            >>> True
        :param serial_port: The serial port to test.
        :return: True if the serial port path exists and is a string instance.
        """
        return Ut.is_str(serial_port) and os.path.exists(serial_port)

    @staticmethod
    def is_baud(baud: int) -> bool:
        """
        Test if is valid baud rate.

        :Example :
            >>> SerialConnectionHelper.is_baud(baud=1200)
            >>> True
        :param baud: The baudrate value to test.
        :return: True if the baudrate value is valid and is an integer instance.
        """
        return Ut.is_int(baud) \
            and baud in [
               110, 300, 600, 1200,
               2400, 4800, 9600, 14400,
               19200, 38400, 57600, 115200,
               128000, 256000
            ]

    @staticmethod
    def is_timeout(timeout: int or float or None) -> bool:
        """
        Test if is valid serial read timeout.

        Possible values for the parameter timeout which controls the behavior of read():
         - timeout = None: wait forever / until requested number of bytes are received.
         - timeout = 0: non-blocking mode, return immediately in any case,
           returning zero or more, up to the requested number of bytes
         - timeout = x: set timeout to x seconds (float allowed)
           returns immediately when the requested number of bytes are available,
           otherwise wait until the timeout expires
           and return all bytes that were received until then.

        :Example :
            >>> SerialConnectionHelper.is_timeout(timeout=0)
            >>> True
        :param timeout: The timeout value to test.
        :return: True if is valid read timeout value.
        """
        return (Ut.is_numeric(timeout) and timeout >= 0) or timeout is None

    @staticmethod
    def is_serial_port(serial_port: str or None) -> bool:
        """
        Test if is valid serial port.

        First split the serial port in path and port name.
        Then test if serial port is a string, if path and port name are valid.
        :Example :
            >>> SerialConnectionHelper.is_serial_port(
            >>>     serial_port="/tmp/vmodem0"
            >>> )
            >>> True
            >>> SerialConnectionHelper.is_serial_port(
            >>>     serial_port="/run/vmodem0"
            >>> )
            >>> False
        :param serial_port: The serial_port to test.
        :return: True if the serial port is valid or None.
        """
        name, path = SerialConnectionHelper._split_serial_port(serial_port)
        return (Ut.is_str(serial_port, not_null=True)
                and SerialConnectionHelper.is_serial_path(path)
                and Ut.is_serial_port_name_pattern(name)) \
            or serial_port is None

    @staticmethod
    def is_serial_path(path: str) -> bool:
        """
        Test if is valid serial path.

        For win32 systems path must be null (None or "").
        For unix systems path must be /dev or in get_virtual_ports_paths() method.
        :Example :
            >>> SerialConnectionHelper.is_serial_path(serial_port="/tmp")
            >>> True
            >>> SerialConnectionHelper.is_serial_path(serial_port="/run")
            >>> False
        :param path: The serial port path to test.
        :return: True if the serial port path is valid.
        """
        return (USys.is_op_sys_type('win32')
                and path is None or path == "") \
            or (USys.is_op_sys_type('unix')
                and Ut.is_str(path)
                and (path in SerialConnectionHelper._get_virtual_ports_paths()
                or path == "/dev"))


class SerialConnection(SerialConnectionHelper):
    """
        Serial connection tool. Set up connection to serial port.

        Able to scan serial ports available on system.

        If you are working with VeDirect protocol,
        remember the configuration :
            - Baud rate : 19200
            - Data bits : 8
            - Parity: None
            - Stop bits: 1
            - Flow Control None
    """
    def __init__(self,
                 set_default: bool = True,
                 **kwargs):
        """
        Constructor of SerialConnection class.

        Initialise configuration and open serial port

        :Example :
            >>> sc = SerialConnection(serial_port = "/dev/ttyUSB1")
            >>> sc.connect()
            >>> True

        Available parameters:
          - serial_port = None: str or None: Serial port path to open
          - baudrate = 19600: int: Baud rate such as 9600 or 115200 etc.
          - timeout = 0: int or float or None: Set read timeout value in seconds
          - write_timeout = 0: int or float or None: Set write timeout value in seconds
          - exclusive = False: bool: Set exclusive access mode (POSIX only).
            A port cannot be opened in exclusive access mode
            if it is already open in exclusive access mode.
          - source_name: str: This is used in logger to identify the source of call
        """
        SerialConnectionHelper.__init__(
            self,
            set_default=set_default,
            **kwargs
        )

    def is_ready(self) -> bool:
        """
        Test if the object is ready.

        :return: True if configuration settings are valid and if the serial connection is opened.
        """
        return self.is_settings() and self._is_serial_ready()

    def connect(self,
                conf: dict or None = None,
                set_default: bool = False
                ) -> bool:
        """
        Start serial connection from parameters.

        :Example :
            >>> self.connect({
            >>>     "serial_port": "/tmp/vmodem0",
            >>>     "baudrate": 19200,
            >>>     "timeout": 0,
            >>>     "write_timeout": 0,
            >>>     "exclusive": False,
            >>>     "source_name": "BMV700"
            >>> })
            >>> True
        Available parameters:
          - serial_port = None: str or None: Serial port path to open
          - baudrate = 19600: int: Baud rate such as 9600 or 115200 etc.
          - timeout = 0: int or float or None: Set read timeout value in seconds
          - write_timeout = 0: int or float or None: Set write timeout value in seconds
          - exclusive = False: bool: Set exclusive access mode (POSIX only).
            A port cannot be opened in exclusive access mode
            if it is already open in exclusive access mode.
          - source_name: str: This is used in logger to identify the source of call
        :param conf: The serial configuration to open port
        :return: True if success to open a serial connection.
        Raise:
         - SerialConfException:
           Will be raised when parameter
           are out of range or invalid,
           e.g. serial_port, baudrate, data bits
         - SerialVeException:
           In case the device can not be found or can not be configured.
         - OpenSerialVeException:
           Will be raised when the device is configured but port is not opened.
        """
        serial_conf = self._set_serial_conf(
            conf=conf,
            set_default=set_default
        )
        logger.debug(
            '[SerialConnection::connect::%s] '
            'settings : %s',
            self.get_source_name(), serial_conf
        )

        if SerialConnection.is_serial_conf(serial_conf):
            try:
                serial_conf['port'] = serial_conf.pop('serial_port')
                self.ser = Serial(
                    **serial_conf
                )
                if self.ser.isOpen():
                    logger.info(
                        '[SerialConnection::connect::%s]'
                        'New Serial connection established: %s.',
                        self.get_source_name(), serial_conf
                    )
                    result = True
                else:
                    raise OpenSerialVeException(
                        '[SerialConnection::connect::%s] '
                        'Unable to open serial connection. args: %s' %
                        (self.get_source_name(), serial_conf)
                    )

            except SerialException as ex:
                raise SerialVeException(
                    '[SerialConnection::connect::%s] '
                    'Exception when attempting to open serial connection. '
                    ' args: %s - ex : %s' %
                    (self.get_source_name(), serial_conf, ex)
                ) from SerialException
            except ValueError as ex:
                raise SerialConfException(
                    '[SerialConnection::connect::%s] '
                    'Parameter are out of range, e.g. baud rate, data bits. '
                    ' args: %s - ex : %s' %
                    (self.get_source_name(), serial_conf, ex)
                ) from ValueError

        else:
            raise SerialConfException(
                '[SerialConnection::connect::%s] '
                'Unable to open serial connection. '
                'Invalid configuration : %s' %
                (self.get_source_name(), serial_conf)
            )

        return result

    def flush_serial_cache(self) -> bool:
        """
        Flush serial cache data from serial port.

        :return: True if ready and flushed data cache
        """
        result = False
        if self.is_ready():
            self.ser.flush()
            result = True
        return result

    def serialize(self):
        """
        This method allows to serialize in a proper way this object

        :return: A dict of order
        :rtype: Dict
        """

        return self._conf
