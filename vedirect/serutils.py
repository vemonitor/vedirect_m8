# -*- coding: utf-8 -*-
"""
Vedirect Utilities Helper.

Contain Exception trowed in Vedirect package.
And SerialUtils class, who extends ve_utils.utils.UType class,
adding some regexes test patterns.

 .. seealso: VedirectController
 .. raises: SettingInvalidException
"""
import re
from ve_utils.utils import UType

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "1.0.0"


class SettingInvalidException(Exception):
    """
    Some data must match the expected value/type

    .. seealso:: Settings
    """
    pass


class InputReadException(Exception):
    """
    Input read fails

    .. seealso:: Settings
    """
    pass


class TimeoutException(Exception):
    """
    Serial Timeout

    .. seealso:: Settings
    """
    pass


class SerialUtils (UType):

    @staticmethod
    def is_key_pattern(data: str) -> bool:
        """ Test if is valid key pattern """
        return SerialUtils.is_str(data)\
            and SerialUtils.is_list_not_empty(
            re.compile(
                r"(?=[a-zA-Z0-9_]{1,30}$)^([a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*)$"
                ).findall(data)
        )
    
    @staticmethod
    def is_serial_key_pattern(data: str) -> bool:
        """ Test if is valid key pattern """
        return SerialUtils.is_str(data)\
            and SerialUtils.is_list_not_empty(
            re.compile(
                r"(?=[a-zA-Z0-9_#]{1,30}$)^([a-zA-Z0-9#]+(?:_[a-zA-Z0-9#]+)*)$"
                ).findall(data)
        )
    
    @staticmethod
    def is_unix_serial_port_pattern(data: str) -> bool:
        """ Test if is valid unix serial port pattern """
        return SerialUtils.is_str(data) and SerialUtils.is_list_not_empty(
            re.compile(
                r'^((?:/dev/|/tmp/)((?:(?:tty(?:USB|ACM))|(?:vmodem))(?:\d{1,5})))$'
                ).findall(data)
        )
    
    @staticmethod
    def is_win_serial_port_pattern(data: str) -> bool:
        """ Test if is valid win serial port pattern """
        return SerialUtils.is_str(data) and SerialUtils.is_list_not_empty(
            re.compile(
                r'^(COM\d{1,3})$'
                ).findall(data)
        )
