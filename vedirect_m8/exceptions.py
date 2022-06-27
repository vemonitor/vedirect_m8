"""
Vedirect Exceptions.

Contain Exception trowed in Vedirect package.

 .. seealso: Vedirect
"""
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


class InputReadException(Exception):
    """
    Input read fails

    .. seealso:: Settings
    """


class TimeoutException(Exception):
    """
    Serial Timeout Exception

    .. seealso:: Settings
    """


class VedirectException(Exception):
    """
    Serial Vedirect decoder Exception

    .. seealso:: Settings
    """
