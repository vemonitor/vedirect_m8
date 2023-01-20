#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Used to decode the Victron Energy VE.Direct text protocol.

Extends Vedirect, and add ability to wait for serial connection,
at start, and or when reading serial data.

 .. see also:: Vedirect
 .. raises:: InputReadException,
             serial.SerialException,
             serial.SerialTimeoutException,
             VedirectException
"""
import logging
import time

from ve_utils.utype import UType as Ut
from vedirect_m8.sertest import SerialTestHelper
from vedirect_m8.helpers import TimeoutHelper
from vedirect_m8.vedirect import Vedirect
from vedirect_m8.serconnect import SerialConnection
from vedirect_m8.exceptions import VedirectException
from vedirect_m8.exceptions import SettingInvalidException
from vedirect_m8.exceptions import InputReadException
from vedirect_m8.exceptions import ReadTimeoutException
from vedirect_m8.exceptions import SerialConnectionException
from vedirect_m8.exceptions import PacketReadException

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vedirect")


class VedirectController(Vedirect):
    """
    Used to decode the Victron Energy VE.Direct text protocol.

    Extends Vedirect, and add ability to wait for serial connection,
    at start, and or when reading serial data.

     .. see also:: Vedirect
     .. raises:: InputReadException,
                 serial.SerialException,
                 serial.SerialTimeoutException,
                 VedirectException
    """
    def __init__(self,
                 serial_conf: dict,
                 serial_test: dict,
                 options: dict or None = None
                 ):
        """
        Constructor of VedirectController class.

        :Example:
            - > sc = VedirectController(serial_port = "/dev/ttyUSB1")
            - > sc.connect()
            - > True # if connection opened on serial port "/dev/tyyUSB1"
        :param serial_conf: dict: The serial connection configuration,
        :param serial_test: The serial_test to execute to retrieve the serial port,
        :param options: Options parameters as dict,
        :return: Nothing
        """
        self._wait_connection = True
        self._wait_timeout = 30
        self._ser_test = None
        self.init_serial_test(serial_test)

        Vedirect.__init__(
            self,
            serial_conf=serial_conf,
            options=options
        )

    def has_serial_test(self) -> bool:
        """Test if is valid serial test helper."""
        return isinstance(self._ser_test, SerialTestHelper)\
            and self._ser_test.has_serial_tests()

    def is_ready(self) -> bool:
        """Test if class Vedirect is ready."""
        return self.is_serial_ready() and self.has_serial_test()

    def is_ready_to_search_ports(self) -> bool:
        """Test if class Vedirect is ready."""
        return self.has_serial_com() and self.has_serial_test()

    def set_wait_timeout(self, wait_timeout: int or float):
        """Test if class Vedirect is ready."""
        self._wait_timeout = Ut.get_float(wait_timeout, 3600)

    def get_wait_timeout(self) -> float or int:
        """Test if class Vedirect is ready."""
        return self._wait_timeout

    def init_serial_test(self, serial_test: dict) -> bool:
        """
        Initialises the serial test helper.

        It takes a dictionary of arguments and passes it to SerialTestHelper,
        Raise SettingInvalidException
        :param self: Refer to the object of the class
        :param serial_test: The serial_test to execute to retrieve the serial port,
        :return: True if SerialTestHelper initialisation success.
        """
        if Ut.is_dict(serial_test, not_null=True):
            self._ser_test = SerialTestHelper(serial_test)
            if not self._ser_test.has_serial_tests():
                raise SettingInvalidException(
                    "[Vedirect::init_serial_test] "
                    "Unable to init SerialTestHelper, "
                    f"bad parameters : {serial_test}."

                )
            return True
        raise SettingInvalidException(
            "[Vedirect::init_serial_test] "
            "Unable to init SerialTestHelper, "
            f"bad parameters : {serial_test}."
        )

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
        Raise:
         - SettingInvalidException if serial_port, baud or timeout are not valid.
         - VedirectException if connection to serial port fails
        :Example :
            >>> self.init_settings({"serial_port": "/dev/ttyUSB1"})
            >>> True
        :param self: Refer to the object itself
        :param serial_conf: dict: The serial connection configuration,
        :param options: Options parameters as dict,
        :return: True if connection to serial port success.
        """
        try:
            if Ut.is_dict(options, not_null=True):
                self._wait_connection = Ut.str_to_bool(options.get('wait_connection'))
                self._wait_timeout = Ut.get_float(options.get('wait_timeout'))

            result = Vedirect.init_settings(
                self,
                serial_conf=serial_conf,
                options=options
            )
        except SerialConnectionException as ex:
            if self._wait_connection is True\
                    and self.wait_or_search_serial_connection(
                        timeout=self._wait_timeout,
                        exception=ex
                    ):
                result = True
            else:
                raise SerialConnectionException(
                    "[VedirectController::init_settings] "
                    "Unable to retrieve valid serial port to read. "
                    f"waiting: {self._wait_timeout}s."
                ) from ex
        return result

    def read_data_to_test(self) -> dict:
        """Return decoded Vedirect blocks from serial to identify the right serial port."""
        result = None
        if self.is_ready():
            try:
                result = {}
                for i in range(4):
                    try:
                        data = self.read_data_single(timeout=2)
                        if Ut.is_dict(data, not_null=True):
                            result.update(data)
                        time.sleep(0.1)
                    except InputReadException:
                        time.sleep(0.5)
            except VedirectException as ex:
                logger.debug(
                    '[VeDirect] Unable to read serial data to test'
                    'ex : %s',
                    ex
                )
        return result

    def test_serial_port(self, port: str) -> bool:
        """
        Attempt serial connection on specified port.
        """
        result = False
        if SerialConnection.is_serial_port(port):
            timeout, serial_port = self._com.get_timeout(), self._com.get_serial_port()
            if self._com.connect(conf={"serial_port": port, 'timeout': 0}):
                data = self.read_data_to_test()
                if self._ser_test.run_serial_tests(data):
                    self._com.ser.timeout = timeout
                    logger.info(
                        "[VeDirect::_test_serial_port] "
                        "New connection established to serial port %s. ",
                        port
                    )
                    self._com.init_serial_conf(
                        conf={"serial_port": port},
                        set_default=False
                    )
                    result = True
                else:
                    logger.debug(
                        "[VeDirect::_test_serial_port] Test serial port %s fails."
                        "\n data: %s",
                        port,
                        data
                    )
                    self._com.init_serial_conf(
                        conf={"serial_port": serial_port, "timeout": timeout},
                        set_default=False
                    )
                    self._com.ser.close()
            else:
                logger.info(
                    "[VeDirect::_test_serial_port] Unable to test serial port %s, connexion fails.",
                    port
                )
        return result

    def test_serial_ports(self, ports: list) -> bool:
        """
        Test the serial connection to a VeDirect device.

        It takes in a list of ports and
        tests each port for the presence of a VeDirect device.
        If it finds one, it attempts to connect to that port
        and reads data from it. It then passes this data into
        the SerialTestHelper class which runs some basic tests
        on the data returned by the serial connection.

        Raise:
            - SerialConnectionException
        :param self: Reference the class instance
        :param ports: list: Specify the serial ports to test
        :return: True if the serial port is open and
                 connected to a device that returns valid data
        """
        result = False
        if self.is_ready_to_search_ports():
            if Ut.is_list(ports, not_null=True):
                for port in ports:
                    if self.test_serial_port(port):
                        result = True
                        break
        else:
            raise SerialConnectionException(
                "[VeDirect::test_serial_ports] "
                "Unable to test to any serial port. "
            )
        return result

    def search_serial_port(self) -> bool:
        """Search the serial port from serial tests."""
        if self.is_ready_to_search_ports():
            ports = self._com.get_serial_ports_list()
            if self.test_serial_ports(ports):
                self.helper.init_data_read()
                return True
        return False

    def wait_or_search_serial_connection(self,
                                         exception: Exception or None = None,
                                         timeout: int or float = 18400,
                                         sleep_time: int or float = 5
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
        within the given timeout time
        :param self: Reference the class instance
        :param exception: Pass an exception to the function
        :param timeout: Set the timeout of the function
        :param sleep_time: Time to sleep between two connection test
        :return: True if the serial connection was successful

        .. raises:: TimeoutException, VedirectException
        :doc-author: Trelent
        """
        if self.is_ready_to_search_ports():
            logger.info(
                "[VeDirect::wait_or_search_serial_connection] "
                "Lost serial connection, attempting to reconnect. "
                "reconnection timeout is set to %ss",
                timeout
            )
            run, timer = True, TimeoutHelper()
            timer.set_start()
            sleep_time = Vedirect.set_sleep_time(value=sleep_time, default=5)

            while run:
                timer.set_now()
                if self.search_serial_port():
                    return True

                if timer.is_timeout(timeout):
                    raise ReadTimeoutException(
                        "[VeDirect::wait_or_search_serial_connection] "
                        "Unable to connect to any serial item. "
                        f"Timeout error : {timeout}. Exception : {exception}"
                    )
                time.sleep(sleep_time)
        raise SerialConnectionException(
            "[VeDirect::wait_or_search_serial_connection] "
            "Unable to connect to any serial item. "
            f"Exception : {exception}"
        )

    def read_data_callback(self,
                           callback_function,
                           options: dict or None = None
                           ) -> dict or None:
        """
        Read data from the serial port and returns it to a callback function

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
        run = True
        if self.is_ready():
            while run:
                try:
                    return Vedirect.read_data_callback(
                        self,
                        callback_function=callback_function,
                        options=options
                    )
                except (
                        InputReadException,
                        PacketReadException,
                        SerialConnectionException
                        ) as ex:
                    if self._wait_connection is True\
                            and self.wait_or_search_serial_connection(
                                exception=ex,
                                timeout=self._wait_timeout
                            ):
                        pass
        else:
            logger.error(
                '[VeDirect::read_data_callback] '
                'Unable to read serial data. '
                'Not connected to serial port...')

        callback_function(None)
        return None
