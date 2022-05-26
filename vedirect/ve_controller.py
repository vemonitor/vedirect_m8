#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Used to decode the Victron Energy VE.Direct text protocol.

Extends Vedirect, and add ability to wait for serial connection,
at start, and or when reading serial data.

 .. seealso:: Vedirect
 .. raises:: InputReadException,
             serial.SerialException,
             serial.SerialTimeoutException,
             VedirectException
"""
import logging
import time
import serial

from ve_utils.utils import UType as Ut
from vedirect.sertest import SerialTestHelper
from vedirect.vedirect import Vedirect, VedirectException
from vedirect.serutils import InputReadException, TimeoutException

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vedirect")


class VedirectController(Vedirect):

    def __init__(self, **kwargs):
        Vedirect.__init__(self, **kwargs)
        self._ser_test = None
        self.init_serial_test(**kwargs)
    
    def has_serial_test(self) -> bool:
        """ Test if is valid serial test helper """
        return isinstance(self._ser_test, SerialTestHelper)\
            and self._ser_test.has_serial_tests()
    
    def init_serial_test(self, **kwargs) -> bool:
        """
        The init_serial_test function initialises the serial test helper.

        It takes a dictionary of arguments and passes it to SerialTestHelper.
        :param self: Refer to the object of the class
        :return: A boolean value
        :doc-author: Trelent
        """
        if Ut.is_dict_not_empty(kwargs.get("serialTest")):
            self._ser_test = SerialTestHelper(kwargs.get("serialTest"))
            return self._ser_test.has_serial_tests()
        return False

    def connect_to_serial(self):
        """ Test if is valid kwargs """
        if self.has_serial_com():
            if not self._com.is_ready() and self._com.connect():
                return True
            elif not self._com.is_ready():
                if self.wait_or_search_serial_connection():
                    return True
        return False

    def init_settings(self, **kwargs):
        """
        Initialise the settings for the class.

        It is called by __init__ and provides a convenient way
        to set default values of class attributes.
        These can be overwritten by passing them in
        as keyword arguments to __init__.
        :param self: Refer to the object itself.
        :return: A dictionary of the settings that were passed to it.
        :doc-author: Trelent
        """
        """ Initialise settings from kwargs """
        self.init_serial_test(**kwargs)
        try:
            return self.init_serial_connection(**kwargs)
        except Exception as ex:
            if self.wait_or_search_serial_connection(exception=ex):
                return True
        return False

    def read_data_to_test(self) -> dict:
        res = None
        if self.is_serial_ready():
            try:
                res = dict()
                # read data 4 times to ensure getting all vedirect blocks on result
                for i in range(4):
                    res.update(self.read_data_single(timeout=3))
            except Exception as ex:
                logger.debug(
                    '[VeDirect] Unable to read serial data to test'
                    'ex : %s' % ex
                )
        return res

    def test_serial_ports(self, ports: list) -> bool:
        """
        Test the serial connection to a VeDirect device.

        It takes in a list of ports and
        tests each port for the presence of a VeDirect device.
        If it finds one, it attempts to connect to that port
        and reads data from it. It then passes this data into 
        the SerialTestHelper class which runs some basic tests
        on the data returned by the serial connection.
        :param self: Reference the class instance
        :param ports:list: Specify the serial ports to test
        :return: True if the serial port is open and
                 connected to a device that returns valid data

        .. raises:: VedirectException,
        :doc-author: Trelent
        """
        if self.has_serial_com()\
                and self.has_serial_test():
            if Ut.is_list_not_empty(ports):
                for port in ports:
                    if self._com.is_serial_port(port):
                        if self._com.connect(**{"serialPort": port, 'timeout': 2}):
                            data = self.read_data_to_test()
                            if self._ser_test.run_serial_tests(data):
                                timeout = self._com._settings.get('timeout')
                                self._com._ser.timeout = timeout
                                logger.info(
                                    "[VeDirect::test_serial_ports] "
                                    "New connection established to serial port %s. " % 
                                    port
                                )
                                return True
                            else:
                                self._com._ser.close()
                return False
        else:
            raise VedirectException(
                "[VeDirect::test_serial_ports] "
                "Unable to test to any serial port. "
                "SerialConnection and/or SerialTestHelper, "
                "are not ready."
            )

    def wait_or_search_serial_connection(self,
                                         exception: Exception or None = None,
                                         timeout: int = 18400
                                         ) -> bool:
        """
        Wait or search for a new serial connection.

        It will first check if the VeDirect object has a SerialConnection,
        and SerialTestHelper with valid tests to run.
        If not, raise an VedirectException.
        Else if both of these are true, get a list of available serial ports,
        and call the test_serial_ports function on itself,
        to retrieve valid serial port, and connect to him.
        Return True or False depending on whether there is an active serial connection.
        Raise a TimeoutException in case there is no active serial connection,
        within the given timeout time.
        :param self: Reference the class instance
        :param exception: Pass an exception to the function.
        :param timeout: Set the timeout of the function.
        :return: True if the serial connection was successful

        .. raises:: TimeoutException, VedirectException
        :doc-author: Trelent
        """
        if self.has_serial_com() and self.has_serial_test():
            logger.info(
                "[VeDirect::wait_or_search_serial_connection] "
                "Lost serial connection, attempting to reconnect. "
                "reconnection timeout is set to %ss" % timeout
            )
            bc, now, tim = True, time.time(), 0
            while bc:
                tim = time.time()
                ports = self._com.get_serial_ports_list()
                if self.test_serial_ports(ports):
                    self.init_data_read()
                    return True

                if tim-now > timeout:
                    raise TimeoutException(
                        "[VeDirect::wait_or_search_serial_connection] "
                        "Unable to connect to any serial item. "
                        "Timeout error : %s. Exception : %s" % 
                        (timeout, exception)
                    )
                
                time.sleep(2)
        raise VedirectException(
            "[VeDirect::wait_or_search_serial_connection] "
            "Unable to connect to any serial item. "
            "Exception : %s" % exception
        )

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
                tim = time.time()
                    
                byte = self._com._ser.read(1)
                packet = self.input_read(byte)

                if packet is not None:
                    logger.debug(
                        "Serial reader success: dict: %s" % self.dict)
                    return self.dict
                
                # timeout serial read
                if tim-now > timeout:
                    logger.error(
                        '[VeDirect] Unable to read serial data. Timeout error - data : %s' % packet)
                    bc = False
        else:
            logger.error('[VeDirect] Unable to read serial data. Not connected to serial port...')
        
        return None

    def read_data_callback(self, 
                           callback_func,
                           timeout: int = 60,
                           connection_timeout: int = 18400,
                           max_loops: int or None = None
                           ) -> dict or None:
        """
        Read data from the serial port and returns it to a callback function.
        
        :param self: Reference the class instance
        :param callback_func:function: Pass a function to the read_data_callback function
        :param timeout:int=60: Set the timeout for the read_data_callback function
        :param connection_timeout:int=18400: Set the timeout for the connection
        :param max_loops:int or None=None: Limit the number of loops
        :return: A dictionary
        :doc-author: Trelent
        """
        bc, now, tim, i = True, time.time(), 0, 0
        packet = None
        if self.is_ready():
            byte = None
            while bc:
                tim = time.time()
                try:
                    byte = self._com._ser.read(1)
                    if byte == b'\x00':
                        byte = self._com._ser.read(1)
                    packet = self.input_read(byte)
                except (
                        InputReadException,
                        serial.SerialException,
                        serial.SerialTimeoutException
                        ) as ex:
                    if self.wait_or_search_serial_connection(ex, connection_timeout):
                        now = tim = time.time()

                if packet is not None:
                    logger.debug(
                        "Serial reader success: "
                        "byte: %s -- packet: %s -- "
                        "dict: %s -- state: %s -- "
                        "bytes_sum: %s " % 
                        (byte, packet, self.dict, self.state, self.bytes_sum)
                    )
                    callback_func(packet)
                    now = tim
                    i = i+1
                    packet = None
                # timeout serial read
                if tim-now > timeout:
                    logger.error(
                        '[VeDirect::read_data_callback] '
                        'Unable to read serial data. Timeout error. '
                        '- data : %s' % packet)
                    callback_func(False)
                    return False

                if Ut.is_int(max_loops) and i > max_loops:
                    return True
                time.sleep(0.95)
            else:
                logger.error(
                    '[VeDirect::read_data_callback] '
                    'Unable to read serial data. '
                    'Not connected to serial port...')
        
        callback_func(None)
