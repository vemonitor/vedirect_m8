# -*- coding: utf-8 -*-
"""
Used to decode the Victron Energy VE.Direct text protocol.

This is a forked version of script originally created by Janne Kario.
(https://github.com/karioja/vedirect).
 .. raises:: InputReadException,
             serial.SerialException,
             serial.SerialTimeoutException,
             VedirectException
"""
import logging
import time
import serial
from ve_utils.utils import UType as Ut, USys as USys
from vedirect_m8.serconnect import SerialConnection
from vedirect_m8.serutils import SettingInvalidException, InputReadException, TimeoutException

__author__ = "Janne Kario, Eli Serra"
__copyright__ = "Copyright 2015, Janne Kario"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vedirect")


class VedirectException(Exception):
    """
    Some data must match the expected value/type

    .. seealso:: Settings
    """
    pass


class Vedirect:

    def __init__(self, **kwargs):
        self._debug = False
        self._com = None
        self.header1 = ord('\r')
        self.header2 = ord('\n')
        self.hexmarker = ord(':')
        self.delimiter = ord('\t')
        self.key = ''
        self.value = ''
        self.bytes_sum = 0
        self.state = self.WAIT_HEADER
        self.dict = {}
        self.init_settings(**kwargs)

    (HEX, WAIT_HEADER, IN_KEY, IN_VALUE, IN_CHECKSUM) = range(5)

    def is_ready(self):
        """ Test if is ready """
        return self.is_serial_ready()

    def is_serial_ready(self):
        return self.has_serial_com() and self._com.is_ready()

    def is_serial_com(self, data):
        """ Test if is valid kwargs """
        return isinstance(data, SerialConnection)
    
    def has_serial_com(self):
        """ Test if is valid kwargs """
        return self.is_serial_com(self._com)
    
    def connect_to_serial(self):
        """ Connect to serial port if not connected """
        if self.has_serial_com():
            if not self._com.is_ready() and self._com.connect():
                return True
        return False

    def init_serial_connection_from_object(self, serial_connection: SerialConnection) -> bool:
        """ Initialise serial connection from SerialConnection object """
        if self.is_serial_com(serial_connection):
            self._com = serial_connection
            return self.connect_to_serial()
        else:
            raise SettingInvalidException(
                "[Vedirect::init_data] "
                "Unable to init SerialConnection, "
                "bad parameters type."
            )

    def init_serial_connection(self, **kwargs):
        """Initialise serial connection from dictionary"""
        if Ut.is_dict_not_empty(kwargs):
            self._com = SerialConnection(**kwargs)
            return self.connect_to_serial()
        else:
            raise SettingInvalidException(
                "[Vedirect::init_data] "
                "Unable to init SerialConnection, "
                "bad parameters type."
            )

    def init_settings(self, **kwargs):
        """ Initialise settings from kwargs """
        return self.init_serial_connection(**kwargs)
    
    def init_data_read(self):
        """ Initialise settings from kwargs """
        self.key = ''
        self.value = ''
        self.bytes_sum = 0
        self.state = self.WAIT_HEADER
        self.dict = {}

    def input_read(self, byte):
        try:
            nbyte = ord(byte)
            if byte == self.hexmarker and self.state != self.IN_CHECKSUM:
                self.state = self.HEX
            if self.state == self.WAIT_HEADER:
                self.bytes_sum += nbyte
                if nbyte == self.header1:
                    self.state = self.WAIT_HEADER
                elif nbyte == self.header2:
                    self.state = self.IN_KEY
                return None
            elif self.state == self.IN_KEY:
                self.bytes_sum += nbyte
                if nbyte == self.delimiter:
                    if self.key == 'Checksum':
                        self.state = self.IN_CHECKSUM
                    else:
                        self.state = self.IN_VALUE
                else:
                    self.key += byte.decode('ascii')
                return None
            elif self.state == self.IN_VALUE:
                self.bytes_sum += nbyte
                if nbyte == self.header1:
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
                if nbyte == self.header2:
                    self.state = self.WAIT_HEADER
            else:
                raise AssertionError()
        except Exception as ex:
            raise InputReadException(
                "[Vedirect::input_read] "
                "Serial input read error %s " % ex
            )

    def get_serial_packet(self):
        """Get Ve Direct block packet from serial reader."""
        byte = self._com._ser.read(1)
        if byte == b'\x00':
            byte = self._com._ser.read(1)
        return self.input_read(byte)
    
    def is_timeout(self, elapsed: float, timeout:float = 60):
        """Test if elapsed time is greater than timeout."""
        if elapsed > timeout:
            raise TimeoutException(
                '[VeDirect] Unable to read serial data. '
                'Timeout error.')
        return True
        
    def read_data_single(self, timeout: int = 60):
        """
        Read a single block from the serial port and returns it as a dictionary.
        
        :param self: Reference the class instance
        :param timeout: Set the timeout for the read_data_single function
        :return: A dictionary of the data
        :doc-author: Trelent
        """
        bc, now, tim = True, time.time(), 0

        if self.is_ready():
            while bc:
                packet, tim = None, time.time()
                    
                packet = self.get_serial_packet()
                    
                if packet is not None:
                    logger.debug("Serial reader success: dict: %s" % self.dict)
                    return packet
                
                # timeout serial read
                self.is_timeout(tim-now, timeout)
        else:
            logger.error('[VeDirect] Unable to read serial data. Not connected to serial port...')
        
        return None

    def read_data_callback(self, callback_function, timeout: int = 60):
        """ Read on serial and return vedirect data on callback function """
        bc, now, tim = True, time.time(), 0
        if self.is_ready():
            while bc:
                tim = time.time()
                
                packet = self.get_serial_packet()
                
                if packet is not None:
                    logger.debug(
                        "Serial reader success: packet: %s "
                        "-- dict: %s -- state: %s -- bytes_sum: %s " %
                        (packet, self.dict, self.state, self.bytes_sum))
                    callback_function(packet)
                    now = tim
                
                # timeout serial read
                self.is_timeout(tim-now, timeout)
        else:
            logger.error('[VeDirect] Unable to read serial data. Not connected to serial port...')
            callback_function(None)
