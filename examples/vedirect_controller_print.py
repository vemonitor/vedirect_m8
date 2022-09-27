# -*- coding: utf-8 -*-
"""VedirectController class Example."""
import logging
import argparse
import sys
from vedirect_m8.ve_controller import VedirectController
from vedirect_m8 import configure_logging
from ve_utils.utype import UType as Ut

logging.basicConfig()
logger = logging.getLogger("vedirect")


def get_device_serial_tests(device):
    """Return the serial test corresponding of the device."""
    if Ut.is_str(device) and device in ["bmv702", "bluesolar_1.23", "smartsolar_1.39"]:
        if device == "bmv702":
            return {
                'PID_test': {
                    "typeTest": "value",
                    "key": "PID",
                    "value": "0x203"
                },
            }
        elif device == "bluesolar_1.23":
            return {
                'PID_test': {
                    "typeTest": "value",
                    "key": "PID",
                    "value": "0xA042"
                },
            }
        elif device == "smartsolar_1.39":
            return {
                'PID_test': {
                    "typeTest": "value",
                    "key": "PID",
                    "value": "0xA05F"
                },
            }


def parse_args(args):
    """
    Parsing function.

    Parse arguments used in example
    :param args: arguments passed from the command line
    :return: return parser
    """
    # create arguments
    arg_parser = argparse.ArgumentParser(description='Process VE.Direct protocol')
    arg_parser.add_argument('--device', help='[bmv702, bluesolar_1.23, smartsolar_1.39]')
    arg_parser.add_argument('--port', help='Serial port')
    arg_parser.add_argument('--timeout', help='Serial port read timeout', type=int, default='60')
    arg_parser.add_argument('--debug', action='store_true', help='Show debug output')

    # parse arguments from script parameters
    return arg_parser.parse_args(args)


def print_data_callback(packet):
    """Print received packet."""
    logger.info("%s\n" % packet)


if __name__ == '__main__':

    parser = parse_args(sys.argv[1:])

    configure_logging(parser.debug)

    conf = {
        "serial_port": parser.port,
        "timeout": parser.timeout
    }

    ve = VedirectController(
        serial_conf=conf,
        serial_test=get_device_serial_tests(parser.device)
    )
    ve.read_data_callback(print_data_callback)
