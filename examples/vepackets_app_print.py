"""Example for vepackets module example."""
import logging
import argparse
import sys
import time
from ve_utils.utype import UType as Ut
from vedirect_m8.vepackets_app import VePacketsApp
from vedirect_m8 import configure_logging

logging.basicConfig()
logger = logging.getLogger("vedirect")


def get_device_serial_tests(device):
    """Return the serial test corresponding of the device."""
    result = None
    if Ut.is_str(device)\
            and device in ["bmv702", "bluesolar_1.23", "smartsolar_1.39"]:
        if device == "bmv702":
            result = {
                'PID_test': {
                    "typeTest": "value",
                    "key": "PID",
                    "value": "0x203"
                },
            }
        elif device == "bluesolar_1.23":
            result = {
                'PID_test': {
                    "typeTest": "value",
                    "key": "PID",
                    "value": "0xA042"
                },
            }
        elif device == "smartsolar_1.39":
            result = {
                'PID_test': {
                    "typeTest": "value",
                    "key": "PID",
                    "value": "0xA05F"
                },
            }
    return result


def parse_args(args):
    """
    Parsing function.

    Parse arguments used in example
    :param args: arguments passed from the command line
    :return: return parser
    """
    # create arguments
    arg_parser = argparse.ArgumentParser(
        description='Process VE.Direct protocol'
    )
    arg_parser.add_argument(
        '--device',
        help='[bmv702, bluesolar_1.23, smartsolar_1.39]'
    )
    arg_parser.add_argument(
        '--port',
        help='Serial port'
    )
    arg_parser.add_argument(
        '--timeout',
        help='Serial port read timeout',
        type=int,
        default='60'
        )
    arg_parser.add_argument(
        '--debug',
        action='store_true',
        help='Show debug output'
    )

    # parse arguments from script parameters
    return arg_parser.parse_args(args)


if __name__ == '__main__':

    parser = parse_args(sys.argv[1:])

    configure_logging(parser.debug)

    conf = {
        "serial_port": parser.port,
        "timeout": parser.timeout
    }

    ve = VePacketsApp(
        serial_conf=conf,
        serial_test=get_device_serial_tests(parser.device),
        source_name="VeExample",
        wait_timeout=5,
        nb_packets=2,
        min_interval=1,
        max_read_error=5
    )

    logger.info(
            "Start Reading 10 items on serial"
        )
    for i in range(10):
        # On i == 0 we read serial data
        # Then on i == 1 we read cache data
        # because interval is less than 1s
        if i > 1:
            time.sleep(1)

        data = ve.read_data(
            caller_name="VeExample",
            timeout=2
        )
        logger.info(
            "Read data at %s",
            time.time()
        )
        logger.info(
            "Packets Data: %s",
            data
        )
        logger.info(
            "Packets Stats: %s",
            ve.packets_stats
        )
        
