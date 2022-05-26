#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import argparse
import sys

from vedirect_m8.vedirectsim import Vedirectsim
from vedirect_m8 import configure_logging

logging.basicConfig()
logger = logging.getLogger("vedirect")


def parse_args(args):
    """
    Parsing function
    :param args: arguments passed from the command line
    :return: return parser
    """
    # create arguments
    parser = argparse.ArgumentParser(description='A simple VE.Direct simulator')
    parser.add_argument('--port', help='Serial port')
    parser.add_argument('--device', help='Serial port')
    parser.add_argument('--debug', action='store_true', help='Show debug output')

    # parse arguments from script parameters
    return parser.parse_args(args)


if __name__ == '__main__':
    
    parser = parse_args(sys.argv[1:])

    configure_logging(parser.debug)
    
    ve = Vedirectsim(parser.port, parser.device)
    ve.run()
