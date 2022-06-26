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
    parser_args = argparse.ArgumentParser(description='A simple VE.Direct simulator')
    parser_args.add_argument('--port', help='Serial port')
    parser_args.add_argument('--device', help='Serial port')
    parser_args.add_argument('--debug', action='store_true', help='Show debug output')

    # parse arguments from script parameters
    return parser_args.parse_args(args)


if __name__ == '__main__':
    
    parser_args = parse_args(sys.argv[1:])

    configure_logging(parser_args.debug)
    
    ve = Vedirectsim(parser_args.port, parser_args.device)
    ve.run()
