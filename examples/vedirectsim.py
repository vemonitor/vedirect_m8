# -*- coding: utf-8 -*-
"""Vedirectsim example."""
import logging
import argparse
import sys

from vedirect_m8.vedirectsim import Vedirectsim
from vedirect_m8 import configure_logging

logging.basicConfig()
logger = logging.getLogger("vedirect")


def parse_args(args):
    """
    Parsing arguments.

    :param args: arguments passed from the command line
    :return: return parser
    """
    parser_arguments = argparse.ArgumentParser(description='A simple VE.Direct simulator')
    parser_arguments.add_argument('--port', help='Serial port')
    parser_arguments.add_argument('--device', help='Serial port')
    parser_arguments.add_argument('--debug', action='store_true', help='Show debug output')

    # parse arguments from script parameters
    return parser_arguments.parse_args(args)


if __name__ == '__main__':

    parser_args = parse_args(sys.argv[1:])

    configure_logging(parser_args.debug)

    ve = Vedirectsim(parser_args.port, parser_args.device)
    ve.run()
