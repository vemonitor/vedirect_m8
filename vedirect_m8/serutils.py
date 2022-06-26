# -*- coding: utf-8 -*-
"""
Vedirect Utilities Helper.

Extends ve_utils.utils.UType class,
adding some regexes test patterns.

 .. seealso: SerialConnection
"""
import re
from ve_utils.utype import UType

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "1.0.0"


class SerialUtils (UType):
    """
    Vedirect Utilities Helper.

    Extends ve_utils.utils.UType class,
    adding some regexes test patterns.

     .. seealso: SerialConnection
    """
    @staticmethod
    def is_key_pattern(data: str) -> bool:
        """Test if is valid key pattern."""
        return SerialUtils.is_str(data)\
            and SerialUtils.is_list(
            re.compile(
                r"(?=\w{1,30}$)^([a-zA-Z\d]+(?:_[a-zA-Z\d]+)*)$"
                ).findall(data),
            not_null=True
        )

    @staticmethod
    def is_serial_key_pattern(data: str) -> bool:
        """Test if is valid key pattern."""
        return SerialUtils.is_str(data)\
            and SerialUtils.is_list(
            re.compile(
                r"(?=[a-zA-Z\d_#]{1,30}$)^([a-zA-Z\d#]+(?:_[a-zA-Z\d#]+)*)$"
                ).findall(data),
            not_null=True
        )

    @staticmethod
    def is_virtual_serial_port_pattern(data: str) -> bool:
        """Test if is valid unix virtual serial port pattern."""
        return SerialUtils.is_str(data) and SerialUtils.is_list(
            re.compile(
                r'^(vmodem\d{1,3})$'
            ).findall(data),
            not_null=True
        )

    @staticmethod
    def is_serial_port_name_pattern(data: str) -> bool:
        """Test if is valid serial port name pattern."""
        return SerialUtils.is_str(data) and SerialUtils.is_list(
            re.compile(
                r'^((?:tty(?:USB|ACM)|vmodem|COM)\d{1,3})$'
            ).findall(data),
            not_null=True
        )

    @staticmethod
    def is_unix_serial_port_pattern(data: str) -> bool:
        """Test if is valid unix serial port pattern."""
        return SerialUtils.is_str(data) and SerialUtils.is_list(
            re.compile(
                r'^(/dev/(tty(?:USB|ACM)\d{1,3}))$'
                ).findall(data),
            not_null=True
        )

    @staticmethod
    def is_win_serial_port_pattern(data: str) -> bool:
        """Test if is valid win serial port pattern."""
        return SerialUtils.is_str(data) and SerialUtils.is_list(
            re.compile(
                r'^(COM\d{1,3})$'
                ).findall(data),
            not_null=True
        )
