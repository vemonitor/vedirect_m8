# -*- coding: utf-8 -*-
"""
Connect to serial port.

Contain method to scan all available ports.

 .. seealso: Vedirect, VedirectController
 .. raises: serial.SerialException,
             serial.SerialTimeoutException
"""
import logging
import serial
import os
from ve_utils.utils import USys as USys
from vedirect_m8.serutils import SerialUtils as Ut

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vedirect")


class SerialConnection:
    """ 
        Serial connection tool. Set up connection to serial port.

        Able to scan serial ports available on system.

        If you are working with VeDirect protol,
        remember the configuration :
            - Baud rate : 19200
            - Data bits : 8
            - Parity: None
            - Stop bits: 1
            - Flow Control None
    """
    def __init__(self, **kwargs):
        """
        Constructor of SerialConnection class.
        
        :Example:
            - > sc = SerialConnection(**{"serialPort": "/dev/ttyUSB1"})  
            - > sc.connect() 
            - > True # if connection opened on serial port "/dev/tyyUSB1" 

        :param self: Refer to the object instance itself.
        :return: Nothing
        """
        self._source_name = "void"
        self._settings = dict()
        self._ser = None
        self._op_sys = USys.get_operating_system_type()
        self._dev_paths = {
            'unix': ['/dev/', '/tmp/']
            }
        
        self.init_settings(**kwargs)

    def is_ready(self) -> bool:
        """Test if is settings and serial connection is open."""
        return self.is_settings() and self.is_serial_ready()

    def is_serial_ready(self) -> bool:
        """Test if is serial connection is ready."""
        return isinstance(self._ser, serial.Serial) and self._ser.isOpen()

    def is_serial_conf(self, data: dict) -> bool:
        """Test if data is valid serial configuration settings."""
        return Ut.is_dict(data)\
            and self.is_serial_port(data.get('serialPort'))\
            and self.is_baud(data.get('baud'))\
            and self.is_timeout(data.get('timeout'))

    def is_settings(self) -> bool:
        """Test if class instance has valid configuration settings."""
        return self.is_serial_conf(self._settings)

    def is_serial_port(self, data: str) -> bool:
        """Test if is valid serial port."""
        return Ut.is_str(data)\
            and (self._op_sys[0] == "win32"
                 and Ut.is_win_serial_port_pattern(data))\
            or (self._op_sys[0] == "unix"
                and Ut.is_unix_serial_port_pattern(data))
    
    def is_serial_tty(self, data: str) -> bool:
        """Test if is valid serial port device."""
        return Ut.is_str(data)

    def is_serial_path(self, data: str) -> bool:
        """Test if is valid serial path"""
        return (self._op_sys[0] == "win32"
                and data is None or data == "")\
            or (self._op_sys[0] == "unix"
                and Ut.is_str(data)
                and data in self._dev_paths.get("unix"))
    
    def is_baud(self, data: int) -> bool:
        """Test if is valid baud rate"""
        return Ut.is_int(data)\
            and data in [
                        110, 300, 600, 1200,
                        2400, 4800, 9600, 14400,
                        19200, 38400, 57600, 115200,
                        128000, 256000
                        ]
    
    def is_timeout(self, data: int) -> bool:
        """Test if is valid serial connection timeout"""
        return Ut.is_int(data) and data > 0
    
    def _get_absolute_serial_path(self, conf: dict) -> str:
        """Get serial port from serialPath and serialTty."""
        if Ut.is_dict(conf)\
                and not self.is_serial_port(conf.get('serialPort'))\
                and Ut.is_str(conf.get('serialPath'))\
                and Ut.is_str(conf.get('serialTty')):
            port = "%s%s" % (
                conf.get('serialPath'),
                conf.get('serialTty')
            )
            if self.is_serial_port(port):
                return port
    
    def default_serial(self) -> dict:
        """ Initialise default settings """
        return {
                'serialPort': None,
                'serialPath': None,
                'baud': 19200,
                'timeout': 10,
                'sourceName': 'void',
            }

    def init_serial_port(self, conf: dict) -> None:
        """Initialise serial port from conf dictionary."""
        if Ut.is_dict_not_empty(conf):
            if not self.is_serial_port(conf.get('serialPort')):
                if self._op_sys[0] == "win32"\
                        and self.is_serial_port(conf.get('serialTty')):
                    conf['serialPort'] = conf.get('serialTty')
                elif self._op_sys[0] == "unix":
                    conf['serialPort'] = self._get_absolute_serial_path(conf)
                    
    def init_settings(self, **kwargs) -> bool:
        """Initialise settings from kwargs."""
        self._settings = self.get_serial_conf(**kwargs)
        return self.is_serial_conf(self._settings)
    
    def _get_settings_keys(self) -> list:
        """Get configuration settings valid keys list."""
        return ['serialPort', 'serialTty', 'serialPath', 'baud', 'timeout', 'sourceName']
    
    def is_valid_setting_key(self, key: str, value: int or str) -> bool:
        """Evaluate settings key value."""
        if key == 'serialPort':
            return self.is_serial_port(value)
        elif key == 'serialTty':
            return self.is_serial_tty(value)
        elif key == 'serialPath':
            return self.is_serial_path(value)
        elif key == 'baud':
            return self.is_baud(value)
        elif key == 'timeout':
            return self.is_timeout(value)
        elif key == 'sourceName':
            return Ut.is_key_pattern(value)
        return False
    
    def get_serial_conf(self, **kwargs) -> dict:
        """Get combined serial configuration from kwargs, self._settings or default."""
        defaults = self.default_serial()
        res = dict()
        for key in self._get_settings_keys():
            if self.is_valid_setting_key(key, kwargs.get(key)):
                res[key] = kwargs.get(key)
            elif Ut.is_dict_not_empty(self._settings)\
                    and self.is_valid_setting_key(key, self._settings.get(key)):
                res[key] = self._settings.get(key)
            elif self.is_valid_setting_key(key, defaults.get(key)):
                res[key] = defaults.get(key)
        self.init_serial_port(res)
        return res

    def connect(self, **kwargs) -> bool:
        """Start serial connection from kwargs parameters or from settings."""
        logger.debug('[SerialConnection::%s] settings : %s' % (self._source_name, self._settings))
        conf = self.get_serial_conf(**kwargs)

        if self.is_serial_conf(conf):
            d = Ut.get_keys_from_dict(conf, ['serialPort', 'baud', 'timeout'])
            serial_port, baud, timeout = d.get('serialPort'), d.get('baud'), d.get('timeout')
            try:
                self._ser = serial.Serial(serial_port, baud, timeout=timeout)
                if self._ser.isOpen():
                    logger.info(
                        '[SerialConnection::connect::%s] New Serial connection established. '
                        'args : %s.' % 
                        (self._source_name, d)
                    )
                    return True
                else:
                    logger.error(
                        '[SerialConnection::connect::%s] '
                        'Unable to open serial connection. args: %s' % 
                        (self._source_name, d)
                    )
            except (serial.SerialException, serial.SerialTimeoutException) as ex:
                logger.error(
                    '[SerialConnection::connect::%s] '
                    'Exception when attempting to open serial connection. '
                    ' args: %s - ex : %s' % 
                    (self._source_name, d, ex)
                )    
        else:
            logger.error(
                '[SerialConnection::connect::%s] '
                'Unable to open serial connection. '
                'Invalid settings : %s' % 
                (self._source_name, conf)
            )
        
        return False

    def get_serial_ports_list(self, exclude: str or None = None) -> list:
        """Get available serial ports list."""
        ttys = None
        if USys.is_op_sys_type('unix'):
            ttys = list()
            
            if Ut.is_dict(self._dev_paths) and Ut.is_list(self._dev_paths.get('unix')):
                for path in self._dev_paths.get('unix'):
                    if Ut.is_str(path)\
                            and os.path.exists(path):
                        tmp = self._get_unix_tty_ports_from_path(path, exclude)
                        if Ut.is_list_not_empty(tmp):
                            ttys = ttys + tmp
                if Ut.is_str(self._settings.get('serialPath'))\
                        and os.path.exists(self._settings.get('serialPath')):
                    tmp = self._get_unix_tty_ports_from_path(
                        self._settings.get('serialPath'),
                        exclude
                    )
                    if Ut.is_list_not_empty(tmp):
                        ttys = ttys + tmp
                ttys = list(set(ttys))
            else:
                logger.error(
                    "[SerialConnection::get_serial_ports_list::%s] "
                    "Fatal Error : Unable to get serial port list, "
                    "serialPath '%s' parameter and defaults dev paths '%s' "
                    "invalid/unavailable from object properties." %
                    (
                        self._source_name, 
                        self._settings.get('serialPath'), 
                        self._dev_paths.get('unix')
                    )
                )
        elif USys.is_op_sys_type('win32'):
            return ["COM1", "COM2", "COM3", "COM4", "COM5", "COM6"]
        else:
            logger.error(
                "[SerialConnection::get_serial_ports_list::%s] "
                "Fatal Error : Sorry you are running unrecognized system '%s', "
                "only unix and win32 are compatibles." % 
                (self._source_name, self._op_sys)
            )
        return ttys

    def _get_unix_tty_ports_from_path(self,
                                      path: str,
                                      exclude: str or None = None
                                      ) -> list or None:
        """ 
        Get list of serial ports from path on linux operating system.

        :param path: absolute path to search serial ports
        :param exclude: serial port to exclude from search
        :return: list of available serial ports

        :Example:
            tty_ports = self._get_unix_tty_ports_from_path(
                path="/dev",
                exclude="ttyUSB0"
            )
        """
        ttys = None
        if not USys.is_op_sys_type('unix'):
            logger.error(
                "[SerialConnection::get_unix_tty_ports_from_path::%s] "
                "Only unix systems can run this function. "
                "Your system is '%s'" % 
                (self._source_name, self._op_sys)
            )
            return ttys
        try:
            if Ut.is_str(path)\
                    and path in self._dev_paths.get('unix')\
                    and os.path.exists(path):
                ttys = list()
                # get list files from path
                content_path = os.listdir(path)
                if Ut.is_list_not_empty(content_path):
                    for f in content_path:
                        port = "%s%s" % \
                               (path, f)
                        if exclude != f \
                                and self.is_serial_port(port):
                            ttys.append(port)
                else:
                    logger.error(
                        "[SerialConnection::get_unix_tty_ports_from_path::%s] "
                        "Error, no serial port retrieved in dev path. "
                        "Be sure your material is connected "
                        "and/or path is correct %s" % 
                        (self._source_name, path)
                    )
            else:
                logger.error(
                    "[SerialConnection::get_unix_tty_ports_from_path::%s] "
                    "Error unable to scan path '%s'. "
                    "The path don't exist, not readable, "
                    "or nor registered on available dev paths : "
                    "%s" % 
                    (self._source_name, path, self._dev_paths.get('unix')))

        except OSError as ex:
            logger.error(
                "[SerialConnection::get_unix_tty_ports_from_path::%s] "
                "Error on get list tty on path '%s' - err : '%s'" % 
                (self._source_name, path, ex)
            )
        return ttys
