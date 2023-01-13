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


class VedirectException(Exception):
    """
    Serial Vedirect core exception.
    """


class SettingInvalidException(VedirectException):
    """
    Some data must match the expected value/type
    """


class VeReadException(VedirectException):
    """
    VeDirect Read Exception.
    Extends: VeCoreException
    """


class InputReadException(VeReadException):
    """
    Input read fails.
    Extends: VeCoreException, VeReadException
    """


class PacketReadException(VeReadException):
    """
    Packet read fails.
    Extends: VeCoreException, VeReadException
    """


class ReadTimeoutException(VeReadException):
    """
    Serial Read Timeout Exception.
    Extends: VeCoreException, VeReadException
    """


class SerialConnectionException(VedirectException):
    """
    Serial Vedirect Exception.
    Extends: VeCoreException
    """


class SerialConfException(SerialConnectionException):
    """
    Serial Configuration Exception.
    """


class SerialVeTimeoutException(SerialConnectionException):
    """
    Serial Timeout Exception.
    Extends: VeCoreException, SerialConnexionException
    """


class SerialVeException(SerialConnectionException):
    """
    Serial Vedirect device can not be found or can not be configured.
    Extends: VeCoreException, SerialConnexionException
    """


class OpenSerialVeException(SerialConnectionException):
    """
    Serial Vedirect device configured but connection not opened.
    Extends: VeCoreException, SerialConnexionException
    """

