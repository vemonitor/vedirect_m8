"""
Used to decode the Victron Energy VE.Direct text protocol.

This is a forked version of script originally created by Janne Kario.
(https://github.com/karioja/vedirect).

 Raise:
        - SettingInvalidException
        - InputReadException
        - PacketReadException
        - ReadTimeoutException
        - SerialConnectionException
        - SerialConfException
        - SerialVeException
        - OpenSerialVeException
"""
import logging
import time
from ve_utils.utype import UType as Ut
from vedirect_m8.core.helpers import TimeoutHelper
from vedirect_m8.core.helpers import CountersHelper
from vedirect_m8.core.packet_stats import FlowPackets
from vedirect_m8.vedirect import Vedirect
from vedirect_m8.vedirect import VedirectReaderHelper
from vedirect_m8.core.exceptions import VeReadException
from vedirect_m8.core.exceptions import PacketReadException
from vedirect_m8.core.exceptions import SerialConnectionException

__author__ = "Janne Kario, Eli Serra"
__copyright__ = "Copyright 2015, Janne Kario"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vedirect")


class VedirectAppReaderHelper(VedirectReaderHelper):
    """Class helper used to read vedirect protocol from serial port."""

    def __init__(self, max_packet_blocks: int or None = 18):
        VedirectReaderHelper.__init__(
            self,
            max_packet_blocks=max_packet_blocks
        )


class VedirectApp(Vedirect):
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
                 options: dict or None = None
                 ):
        """
        Constructor of VedirectApp class.

        :Example:
            - > sc = VedirectController(serial_port = "/dev/ttyUSB1")
            - > sc.connect()
            - > True # if connection opened on serial port "/dev/tyyUSB1"
        :param self: Refer to the object instance itself,
        :param serial_conf: dict: The serial connection configuration,
        :param options: Options parameters as dict,
        :return: Nothing
        """
        Vedirect.__init__(
            self,
            serial_conf=serial_conf,
            options=options
        )
        self.packet_stats = FlowPackets(
            max_packet_errors=10
        )

    def read_all_packets(self,
                         nb_packets: int or None = None,
                         nb_blocks: int or None = None,
                         options: dict or None = None
                         ) -> dict or None:
        """Read all packets decoded from serial port and returns it as a dictionary."""
        run, timer = True, TimeoutHelper()

        params = Vedirect.get_read_data_params(options)
        self.packet_stats.set_nb_packets(nb_packets)
        self.packet_stats.set_nb_blocks(nb_blocks)
        timer.set_start()
        if self.is_ready():
            result = {}
            while run:
                try:
                    timer.set_now()
                    packet = self.read_data_single(params)

                    if Ut.is_dict(packet, not_null=True):
                        logger.debug(
                            "[VedirectApp::read_all_packets] "
                            "Serial reader success: packet: %s \n"
                            "-- state: %s -- bytes_sum: %s -- time to read: %s",
                            packet,
                            self.helper.state,
                            self.helper.bytes_sum,
                            timer.get_elapsed()
                        )
                        self.helper.reset_data_read()
                        if self.packet_stats.is_all_packets(packet):
                            run = False
                            break

                        time.sleep(params.get('sleep_time'))
                        timer.set_start()

                    # timeout serial read
                    timer.is_timeout_callback(
                        timeout=params.get('timeout'),
                        callback=Vedirect.raise_timeout
                    )

                    if self._counter.packet.is_max(params.get('max_loops')):
                        run = False

                except PacketReadException as ex:
                    if Vedirect.is_max_read_error(
                            params.get('max_packet_errors'),
                            self._counter.packet_errors.get_value()):
                        raise ex
                    self.helper.reset_data_read()
        else:
            raise SerialConnectionException(
                '[VedirectApp::read_all_packets] '
                'Unable to read serial data. '
                'Not connected to serial port...'
            )
        return False

    def scan_serial_packets(self) -> bool:
        """Scan serial port to retrieve packets structure"""
        try:
            # flush serial cache and sleep 1 second
            # to get fresh packets from 1 second interval
            self.flush_serial_cache()
            time.sleep(1)
            self.read_all_packets(nb_blocks=60,
                                  options={
                                      'timeout': 1,
                                      'sleep_time': 0.1,
                                      'max_loops': 8,
                                  })
        except VeReadException as ex:
            pass
