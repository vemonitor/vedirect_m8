"""vepackets module"""
import logging
import time
from typing import Optional, Union
from ve_utils.utype import UType as Ut
from vedirect_m8.exceptions import VeReadException
from vedirect_m8.exceptions import SerialConnectionException
from vedirect_m8.exceptions import VedirectException
from vedirect_m8.ve_controller import VedirectController
from vedirect_m8.packet_stats import PacketStats

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__license__ = "MIT"

logging.basicConfig()
logger = logging.getLogger("vedirect")


class VePacketsApp(VedirectController):
    """
        Extends VedirectController and minitor reading packets from Vedirect
        Some vedirect devices send many packets of data
        composed by between 0 and 18 blocks.
        Here we get all packets frome same timestamp and set stats
        of reading stability on VeDirect Serial port.
    """
    def __init__(self,
                 serial_conf: dict,
                 serial_test: dict,
                 source_name: str = 'VePackets',
                 auto_start: bool = True,
                 wait_connection: bool = True,
                 wait_timeout: Union[int, float] = 3600,
                 max_packet_blocks: Optional[int] = 18,
                 nb_packets: int = 10,
                 accepted_keys: Optional[list] = None,
                 min_interval: int = 1,
                 max_read_error: int = 0
                 ):
        """
        Constructor of VedirectController class.

        :Example:
            - > sc = VedirectController(serial_port = "/dev/ttyUSB1")
            - > sc.connect()
            - > True # if connection opened on serial port "/dev/tyyUSB1"
        :param self: Refer to the object instance itself,
        :param serial_conf: dict: The serial connection configuration,
        :param serial_test:
            The serial_test to execute to retrieve the serial port,
        :param source_name:
            This is used in logger to identify the source of call,
        :param auto_start: bool:
            Define if serial connection must be established automatically,
        :param wait_connection: bool:
            Used to wait for connection on new serial port at start,
        :param wait_timeout:
            Timeout value to search valid serial port,
            in case of connection fails
        :param max_packet_blocks:
            Max blocks per packet value
        :param packet_keys:
            List of accepted packet keys
        :return: Nothing
        """
        VedirectController.__init__(
            self,
            serial_conf=serial_conf,
            serial_test=serial_test,
            source_name=source_name,
            auto_start=auto_start,
            wait_connection=wait_connection,
            wait_timeout=wait_timeout,
            max_packet_blocks=max_packet_blocks
        )
        self._data_cache = None
        self._min_interval = 1
        self.packets_stats = PacketStats(
            nb_packets=nb_packets,
            accepted_keys=accepted_keys,
            max_read_error=max_read_error
        )
        self.set_min_interval(min_interval)

    def has_data_cache(self) -> bool:
        """Test if instance has data_cache"""
        return Ut.is_tuple(self._data_cache)\
            and Ut.is_numeric(
                self._data_cache[0],  # type: ignore
                not_null=True)\
            and Ut.is_dict(
                self._data_cache[1],  # type: ignore
                not_null=True)

    def get_time_cache(self) -> Optional[float]:
        """Get data_cache time value"""
        result = None
        if self.has_data_cache():
            result = self._data_cache[0]  # type: ignore
        return result

    def get_data_cache(self) -> Optional[dict]:
        """Get data_cache value"""
        result = None
        if self.has_data_cache():
            result = self._data_cache[1]  # type: ignore
        return result

    def set_min_interval(self, value: int):
        """Set min_interval"""
        min_interval = Ut.get_int(value, 1)
        if min_interval >= 1:
            self._min_interval = min_interval
        return self._min_interval

    def reset_data_cache(self):
        """Reset data_cache"""
        self._data_cache = None

    def set_data_cache(self,
                       data: Optional[dict]
                       ) -> bool:
        """Init cache tuple values."""
        result = False
        self._data_cache = None
        if Ut.is_dict(data, not_null=True):
            self._data_cache = (time.time(), data)
            result = True
        return result

    def update_data_cache(self,
                          data: Optional[dict]
                          ) -> bool:
        """Add data to cache."""
        result = False
        if self.has_data_cache():
            if Ut.is_dict(data, not_null=True):
                self._data_cache[1].update(data)  # type: ignore
                result = True
        else:
            result = self.set_data_cache(data)
        return result

    def search_available_serial_port(self,
                                     caller_name: str,
                                     raise_exception: bool = True
                                     ) -> bool:
        """
        Search and connect to new valid Serial Port if it's available
        """
        result = False
        if self.search_serial_port():
            logger.warning(
                "%s: Connected to serial port %s.",
                caller_name,
                self.get_serial_port()
            )
            result = True
        elif raise_exception is True:
            raise VedirectException(
                "Fatal Error: "
                "Unable to connect to any serial port. "
                f"caller: {caller_name}"
            )
        return result

    def try_serial_connection(self, caller_name: str) -> bool:
        """
        Try to connect to serial port, and run a serial test on it.
        """
        result = False
        try:
            if self.connect_to_serial()\
                    and self.get_serial_port() is not None\
                    and self.test_serial_port(
                        port=self.get_serial_port()  # type: ignore
                    ):
                logger.info(
                    "Serial port %s is ready. ",
                    self.get_serial_port()
                )
                result = True
        except VedirectException as ex:
            logger.debug(
                "[VePacketsApp::try_serial_connection] "
                "Unable to connect to serial port %s.\n"
                "ex: %s",
                self.get_serial_port(),
                ex
            )
        if result is False:
            logger.info(
                "Disconnected from Serial Port. "
                "Searching for valid and available serial port."
            )
            self.packets_stats.add_serial_reconnection()
            if self.search_available_serial_port(
                    caller_name=caller_name,
                    raise_exception=False
                    ):
                result = True
        return result

    def try_to_reconnect(self,
                         caller_name: str,
                         from_exception: Optional[Exception] = None
                         ) -> bool:
        """
        Try to connect to serial port, and run a serial test on it.
        """
        if not self.try_serial_connection(caller_name):
            logger.error(
                "[VePacketsApp::try_to_reconnect] "
                "Unable to get valid Serial port."
            )
            msg = "[VePacketsApp::try_to_reconnect] "\
                "Fatal error on reading serial port "\
                f"{self.get_serial_port()}"
            if isinstance(from_exception, Exception):
                raise VedirectException(msg) from from_exception

            raise VedirectException(msg)
        return True

    def read_serial_data(self,
                         caller_name: str,
                         timeout: int = 2
                         ) -> Optional[dict]:
        """
        Get single packet from VeDirect controller.
        """
        result = None
        if self.is_ready():
            try:
                timeout = Ut.get_int(timeout, default=2)
                result = self.read_data_single(timeout=timeout)
            except (SerialConnectionException) as ex:
                # Here we try the actual serial connexion
                # And if fails try to search and connect to new serial port
                self.try_to_reconnect(
                    caller_name=caller_name,
                    from_exception=ex
                )
        else:
            self.try_to_reconnect(
                caller_name=caller_name
            )
        return result

    def get_all_packets(self,
                        caller_name: str,
                        timeout: int = 2
                        ) -> bool:
        """
        Get All packets from from VeDirect controller.
        Most VeDirect Devices has many packets to read.
        Every packet contain 0-18 blocks.
        """
        result = False
        read_errors, blocks = 0, []
        nb_packets = self.packets_stats.get_nb_packets()
        self.reset_data_cache()

        for i in range(nb_packets):
            read_errors = self.packets_stats.get_serial_read_errors()
            try:
                tmp = self.read_serial_data(caller_name, timeout)
                if self.update_data_cache(tmp):
                    self.packets_stats.set_loop_packet_stats(
                        index=i,
                        packet=tmp  # type: ignore
                    )
                    blocks.append(len(tmp))  # type: ignore
                    time.sleep(0.005)
                else:
                    self.packets_stats.add_serial_read_errors()
                    logger.debug(
                        "[VePacketsApp::read_data] "
                        "Serial read Error n° %s",
                        read_errors
                    )

            except VeReadException as ex:
                logger.debug(
                    "[VePacketsApp::get_all_packets] "
                    "Serial read Error n° %s ex : %s",
                    read_errors,
                    ex
                )
                self.packets_stats.add_serial_read_errors()

        if self.has_data_cache():
            self.packets_stats.init_nb_packets()
            result = True
            logger.debug(
                "[VePacketsApp::get_all_packets] "
                "Read %s blocks from serial. "
                "len: %s - blocks: %s - "
                "errors: %s - time ref: %s \n"
                "result: %s",
                i+1,
                len(self.get_data_cache()),  # type: ignore
                blocks,
                read_errors,
                self.get_time_cache(),
                self.get_data_cache()
            )
        return result

    def is_time_to_read_serial(self,
                               now: float
                               ) -> bool:
        """Test if is time to read from serial"""
        result = True
        time_cache = Ut.get_int(self.get_time_cache(), default=-1)
        now = Ut.get_int(now, default=-1)
        min_interval = Ut.get_int(self._min_interval, default=-1)
        if Ut.is_int(time_cache, positive=True)\
                and Ut.is_int(now, positive=True)\
                and Ut.is_int(min_interval, positive=True):
            diff = abs(time_cache - now)
            result = diff >= min_interval
            logger.debug(
                "[VePacketsApp::is_time_to_read_serial] "
                "Evaluate cache validity: %s.\n"
                "Diff %s > %s",
                result,
                diff,
                min_interval
            )

        return result

    def read_serial_packets(self,
                            caller_name: str,
                            now: int,
                            timeout: int = 2
                            ) -> Optional[dict]:
        """Read serial packets from serial."""
        result = None
        self.init_data_read()
        # reset cache
        self.reset_data_cache()
        if self.get_all_packets(caller_name, timeout):
            result = self.get_data_cache()
            if not Ut.is_dict(result, not_null=True):
                logger.debug(
                    "[VePacketsApp::read_data] "
                    "Error: Unable read packets from serial. "
                    "Time packet: %s \n"
                    "Time diff: %s \n",
                    self.get_time_cache(),
                    self.get_time_cache_diff(
                        time_cache=self.get_time_cache(),
                        now=now
                    )  # type: ignore
                )
                self.packets_stats.add_serial_read_errors()
                result = None

            logger.debug(
                "[VePacketsApp::read_data] Read data from serial. "
                "worker: %s - time: %s  \n"
                "Time packet: %s \n"
                "Time diff: %s \n"
                "Data Dict: %s \n",
                caller_name,
                now,
                self.get_time_cache(),
                self.get_time_cache_diff(
                    time_cache=self.get_time_cache(),
                    now=now
                ),  # type: ignore
                result
            )
        else:
            self.packets_stats.add_serial_read_errors()
        # Control if has reached max serial read errors
        # raise InputReadException if reached max value.
        self.packets_stats.has_reached_max_errors()
        return result

    def read_data(self,
                  caller_name: str,
                  timeout: int = 2
                  ) -> tuple:
        """Read data"""
        result, is_cache = None, False
        now = time.time()
        logger.debug(
            "[VePacketsApp::read_data] Read vedirect data."
            "worker: %s - time: %s",
            caller_name,
            now
        )
        if self.is_time_to_read_serial(now):
            result = self.read_serial_packets(
                caller_name=caller_name,
                now=now,
                timeout=timeout
            )

        else:
            result = self.get_data_cache()
            is_cache = True
            logger.debug(
                "[VePacketsApp::read_data] Read data from cache."
                "worker: %s - time: %s  \n"
                "Time packet: %s \n"
                "Time diff: %s \n",
                caller_name,
                now,
                self.get_time_cache(),
                self.get_time_cache_diff(
                    time_cache=self.get_time_cache(),
                    now=now
                )  # type: ignore
            )
        return result, is_cache

    @staticmethod
    def get_time_cache_diff(time_cache: Union[int, float],
                            now: Union[int, float]
                            ) -> Union[int, float]:
        """Test if actual index is equal to last index."""
        result = -1
        time_cache = Ut.get_int(time_cache, -1)
        now = Ut.get_int(now, -1)
        if Ut.is_int(time_cache, positive=True)\
                and Ut.is_int(now, positive=True):
            result = abs(time_cache - now)
        return result
