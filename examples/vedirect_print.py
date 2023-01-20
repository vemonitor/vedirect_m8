#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Vedirect example.
"""
import logging
import argparse
import time

from vedirect_m8.serutils import SerialUtils as Ut
from vedirect_m8.vedirect import Vedirect
from vedirect_m8 import configure_logging
from vedirect_m8.exceptions import PacketReadException

logging.basicConfig()
logger = logging.getLogger("vedirect")


def print_data_callback(packet_callback: dict):
    """
    Callback function who receive the decoded data from serial port.

    See above on read_data_callback method.
    """
    logger.info(
        '[print_data_callback] '
        'New packet received in callback function: '
    )
    if Ut.is_dict(packet, not_null=True):
        logger.info(
            '[print_data_callback] -> Packet '
            '(%s Blocks): %s.',
            len(packet_callback),
            packet_callback
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process VE.Direct protocol')
    parser.add_argument('--port', help='Serial port')
    parser.add_argument('--timeout', help='Serial port read timeout', type=int, default='60')
    parser.add_argument('--debug', action='store_true', help='Show debug output')
    args = parser.parse_args()

    configure_logging(args.debug)

    # serial configuration settings used to open serial port (Required)
    serial_conf = {
        "serial_port": args.port,
        # baudrate can be one of the standard values:
        # 50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200.
        # These are well-supported on all platforms.
        'baud': 19200,
        # serial read timeout
        #   - timeout = None: wait forever / until requested number of bytes are received
        #   - timeout = 0: non-blocking mode, return immediately in any case,
        #                  returning zero or more, up to the requested number of bytes
        #   - timeout = x: set timeout to x seconds (float allowed)
        #                  returns immediately when the requested number of bytes are available,
        #                  otherwise wait until the timeout expires
        #                  and return all bytes that were received until then.
        "timeout": args.timeout,
        # Caller function name used only in logs
        # In case you have many serial ports connections
        'source_name': 'PrintCallbackExample'
    }
    # The Vedirect options settings(Optional can be None or Omitted)
    options = {
        # Max blocks per packet
        'max_packet_blocks': 18,
        # Define if serial port must be open on initialise object instance.
        # or if you need to open it later
        'auto_start': True
    }
    # Initialise the Vedirect Module
    # Victron devices send packets with maximum of 18 blocks of key/value pairs.
    # That mean you can receive many packets/second on serial port depending on your device type.
    # e.g. BMV702 from vedirect simulator sends 2 packets and 26 Blocks of key/value pairs.
    ve = Vedirect(serial_conf=serial_conf, options=options)

    # flush the serial cache data and wait for new data
    ve.flush_serial_cache()
    time.sleep(1)

    # decode one packet from serial port
    packet = ve.read_data_single(
        # time max to read one packet
        timeout=1,
        # Define nb errors permitted on read blocks before exit (InputReadException):
        #   - -1: never exit
        #   - 0: exit on first error
        #   - x: exit after x errors
        max_block_errors=0,
        # Define nb errors permitted on read blocks before exit (PacketReadException):
        #   - -1: never exit
        #   - 0: exit on first error
        #   - x: exit after x errors
        max_packet_errors=-1
    )
    logger.info(
        '[vedirect_print] '
        'Decode single packet from serial port: '
    )
    if Ut.is_dict(packet, not_null=True):
        logger.info(
            '[vedirect_print] -> Packet '
            '(%s Blocks): %s.',
            len(packet),
            packet
        )
    logger.info(
        '[vedirect_print] '
        'Decode packets and send them to callback function: '
    )
    run = True
    nb_packet_errors = 0
    while run:
        try:
            # decode packets and send them to callback function
            # here get 2 packet for second with disabled InputReadException
            # And catching PacketReadException here without exiting.
            ve.read_data_callback(
                # callback function who receive the decoded data
                callback_function=print_data_callback,
                # time max to read one packet
                timeout=1,
                # time to sleep between read two packets from serial
                # sleep 0.5 seem ~ 2 packets/second
                sleep_time=0.5,
                # Define max packets to read before exit :
                #   - None: never stop until no error occurs
                #   - x: exit after read and decode x packets if no error occurs.
                max_loops=None,
                # Define nb errors permitted on read blocks before exit (InputReadException):
                #   - -1: never exit
                #   - 0: exit on first error
                #   - x: exit after x errors
                max_block_errors=0,
                # Define nb errors permitted on read blocks before exit (PacketReadException):
                #   - -1: never exit
                #   - 0: exit on first error
                #   - x: exit after x errors
                max_packet_errors=0
            )
        except PacketReadException as ex:
            # catch PacketReadException errors and count them
            logger.info(
                '[vedirect_print] '
                'Invalid packet detected (%s): %s',
                nb_packet_errors,
                ex
            )
            nb_packet_errors = nb_packet_errors + 1
