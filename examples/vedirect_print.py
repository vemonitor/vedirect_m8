#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
from vedirect.vedirect import Vedirect


def print_data_callback(packet):
    print(packet)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process VE.Direct protocol')
    parser.add_argument('--port', help='Serial port')
    parser.add_argument('--timeout', help='Serial port read timeout', type=int, default='60')
    args = parser.parse_args()
    conf = {
        "serialPort": args.port,
        "timeout": args.timeout
    }
    ve = Vedirect(**conf)
    print(ve.read_data_callback(print_data_callback))
