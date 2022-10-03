# -*- coding: utf-8 -*-
"""
Used to simulate encoded Victron Energy VE.Direct text protocol.

This is a forked version of script originally created by Janne Kario.
(https://github.com/karioja/vedirect).
 .. raises:: InputReadException,
             serial.SerialException,
             serial.SerialTimeoutException,
             VedirectException
"""
import logging
import inspect
import os
import time
import serial
from ve_utils.utype import UType as Ut
from ve_utils.utime import PerfStats

__author__ = "Janne Kario, Eli Serra"
__copyright__ = "Copyright 2015, Janne Kario"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vedirect")


class Vedirectsim:
    """Vedirect simulator class."""
    def __init__(self, serialport: str, device: str = "bmv702"):
        """Vedirectsim init instance."""
        self.serialport = serialport
        self.ser = None
        self.perf = PerfStats()
        self.device = None
        self.dump_file_path = None
        self.block_counter = 0
        self.dict = {'V': '12800', 'VS': '12800', 'VM': '1280', 'DM': '120',
                     'VPV': '3350', 'PPV': '130', 'I': '15000', 'IL': '1500',
                     'LOAD': 'ON', 'T': '25', 'P': '130', 'CE': '13500',
                     'SOC': '876', 'TTG': '45', 'Alarm': 'OFF', 'Relay': 'OFF',
                     'AR': '1', 'H1': '55000', 'H2': '15000', 'H3': '13000',
                     'H4': '230', 'H5': '12', 'H6': '234000', 'H7': '11000',
                     'H8': '14800', 'H9': '7200', 'H10': '45', 'H11': '5',
                     'H12': '0', 'H13': '0', 'H14': '0', 'H15': '11500',
                     'H16': '14800', 'H17': '34', 'H18': '45', 'H19': '456',
                     'H20': '45', 'H21': '300', 'H22': '45', 'H23': '350',
                     'ERR': '0', 'CS': '5', 'BMV': '702', 'FW': '1.19',
                     'PID': '0x204', 'SER#': 'HQ141112345', 'HSDS': '0'}
        logger.info(
            "Starting vedirect simulator."
            )
        self.set_device_settings(device)
        self.serial_connect()

    def is_ready(self) -> bool:
        """Test if is all ready to run."""
        return Ut.is_str(self.device)\
            and os.path.isfile(self.dump_file_path)\
            and self.is_serial_ready()

    def is_serial_ready(self) -> bool:
        """Test if is serial ready and connection opened."""
        return isinstance(self.ser, serial.Serial) and self.ser.is_open

    def serial_connect(self) -> bool:
        """Connect to serial port."""
        self.ser = serial.Serial(
            port=self.serialport,
            baudrate=19200,
            timeout=0,
            rtscts=False,
            dsrdtr=False
        )
        self.ser.write_timeout = 0
        if self.is_serial_ready():
            logger.info(
                "Connected to serial port %s",
                self.serialport
            )
            return True
        raise serial.SerialException(
            "Fatal error, unable to connect on serial port %s." %
            self.serialport
        )

    def set_device(self, device: str):
        """Set the vedirect device to simulate."""
        self.device = None
        if Ut.is_str(device) and device in Vedirectsim.get_valid_devices():
            self.device = device
            return True
        return False

    def set_dump_file_path(self):
        """Set the dump file path to read."""
        if Ut.is_str(self.device) and self.device in Vedirectsim.get_valid_devices():
            file = "%s.dump" % self.device
            current_path = os.path.dirname(
                os.path.abspath(
                    inspect.getfile(inspect.currentframe())
                    )
                )
            self.dump_file_path = os.path.join(current_path, "sim_data", file)
            return os.path.isfile(self.dump_file_path)
        return False

    def set_device_settings(self, device: str) -> bool:
        """Set the device settings."""
        if self.set_device(device)\
                and self.set_dump_file_path():
            logger.info(
                "Device %s fully configured.",
                device
            )
            return True
        raise ValueError(
            "Fatal error, unable to set device settings on %s."
            "Valid devices are : (bmv702, bluesolar_1.23, smartsolar_1.39) " %
            device
        )

    def convert(self, data: dict) -> list:
        """Convert data to vedirect protocol."""
        result = list()
        for key in self.dict:
            result.append(ord('\r'))
            result.append(ord('\n'))
            result.extend([ord(i) for i in key])
            result.append(ord('\t'))
            result.extend([ord(i) for i in data[key]])
        # checksum
        result.append(ord('\r'))
        result.append(ord('\n'))
        result.extend([ord(i) for i in 'Checksum'])
        result.append(ord('\t'))
        result.append((256 - (sum(result) % 256)) % 256)
        return result

    def send_packet(self):
        """Send the packet to serial port."""
        packet_write = False
        packet = self.convert(self.dict)
        try:
            self.ser.write(bytes(packet))
            self.block_counter += 1
            packet_write = True
        except serial.SerialTimeoutException as ex:
            logger.error(
                "Error : SerialTimeoutException on writing on serial :"
                "packet nb : %s - packet %s - ex %s. \n",
                self.block_counter, self.dict, ex
            )
            self.ser.cancel_write()
            self.ser.reset_output_buffer()

        write_time = self.perf.get_elapsed(
            self.perf.get_perf_key_stat("writes", "start")
        )
        sleep_time = 0
        if 0 < write_time < 0.5:
            sleep_time = round(0.5 - round(write_time, 3) - 0.0025, 3)
            time.sleep(sleep_time)

        if logger.level <= 10:
            write_time = self.perf.get_elapsed(
                self.perf.get_perf_key_stat("writes", "start")
            )

            logger.debug(
                "Sending packet %s %s on serial in %s s."
                "Sleep before next: %s.\n"
                "Write Stats: %s.\n %s\n",
                self.block_counter,
                packet_write,
                write_time,
                sleep_time,
                self.perf.serialize_perf_key("writes"),
                self.dict
            )

        self.dict = dict()

    def process_data(self, key: str, value: str):
        """Process read data."""
        result = False
        if Ut.is_str(key, not_null=True):
            if key != 'Checksum':
                self.dict.update({key: value})
                if len(self.dict) == 18:
                    result = True
            elif Ut.is_dict(self.dict, not_null=True):
                result = True
        return result

    def is_max_writes(self, max_writes: int or None = None):
        """Test if max serial writes."""
        return Ut.is_int(max_writes) and self.block_counter >= max_writes

    def read_dump_file(self):
        """Read dump file."""
        if self.is_ready():
            with open(self.dump_file_path) as lines:
                for line in lines:
                    values = Vedirectsim.get_key_value_from_line(line)
                    if Ut.is_tuple(values, eq=2):
                        yield values

    def read_dump_file_lines(self, max_writes: int or None = None) -> bool:
        """Read file lines."""
        result = False
        if self.is_ready():
            self.perf.start_perf_key("writes")
            result = True
            for key, value in self.read_dump_file():
                time.sleep(0.01)
                if self.is_max_writes(max_writes):
                    logger.info(
                        "End read dump file lines on max serial writes : %s/%s",
                        self.block_counter, max_writes
                    )
                    result = True
                    break

                if self.process_data(key, value):
                    self.send_packet()
                    self.perf.end_perf_key("writes")
                    self.perf.start_perf_key("writes")

        return result

    def run(self, max_writes: int or None = None) -> bool:
        """Run the simulator."""
        if self.is_ready():
            running = True
            while running:
                self.dict = dict()
                self.perf.start_perf_key("dump")

                start_writes = self.block_counter
                logger.info(
                    "Starting to read dump file lines on device %s. "
                    "Max serial writes : %s",
                    self.device, max_writes
                )
                running = self.read_dump_file_lines(max_writes)
                time_dump = self.perf.end_perf_key("dump")
                logger.info(
                    "End read dump file lines. Write %s/%s packets in % s.\n"
                    "Write Stats : %s.\n"
                    "Stats dump: %s\n",
                    self.block_counter - start_writes,
                    self.block_counter,
                    time_dump,
                    self.perf.serialize_perf_key("writes"),
                    self.perf.serialize_perf_key("dump")
                )
                self.perf.init_perf_key("writes", reset=True)
                if Ut.is_int(max_writes) and self.block_counter >= max_writes:
                    break
            return running
        raise ValueError(
            "Fatal error, unable to set device settings on %s."
            "Valid devices are : (bmv702, bluesolar_1.23, smartsolar_1.39). "
            "Or can be path file error: %s" %
            (self.device, self.dump_file_path)
        )

    @staticmethod
    def get_valid_devices() -> list:
        """Get valid devices to simulate vedirect data."""
        return ["bmv702", "bluesolar_1.23", "smartsolar_1.39"]

    @staticmethod
    def get_key_value_from_line(line):
        """Get key value from dump file line."""
        result = None
        if Ut.is_str(line):
            value = line.replace('\n', "").replace('\r', "")
            values = value.split('\t')
            if Ut.is_list(values, eq=2):
                result = tuple(values)
        return result
