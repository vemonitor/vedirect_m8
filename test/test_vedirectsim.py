import pytest
import serial

from vedirect_m8.vedirectsim import Vedirectsim
from vedirect_m8.serconnect import SerialConnection
from ve_utils.utime import PerfStats


class TestVeDirectSim:

    def setup_method(self):
        """
        Setup any state tied to the execution of the given function.

        Invoked for every test function in the module.
        """
        serial_port = SerialConnection.get_virtual_home_serial_port("vmodem0")
        device = "bmv702"

        self.obj = Vedirectsim(serial_port, device)

    def test_is_ready(self):
        """"""
        assert self.obj.is_ready()

    def test_has_serial_connection(self):
        """"""
        self.obj.serial_port = SerialConnection.get_virtual_home_serial_port("vmodem0")
        assert self.obj.serial_connect() is True
        assert self.obj.has_serial_connection() is True
        with pytest.raises(serial.SerialException):
            self.obj.ser = None
            self.obj.has_serial_connection()

    def test_serial_connect(self):
        """"""
        assert self.obj.serial_connect()
        with pytest.raises((serial.SerialException, serial.SerialTimeoutException)):
            self.obj.serialport = "bad_port"
            self.obj.serial_connect()

    def test_get_dump_file_path(self):
        """"""
        self.obj.serial_port = SerialConnection.get_virtual_home_serial_port("vmodem0")
        assert self.obj.serial_connect()
        with pytest.raises(ValueError):
            self.obj.device = "bad_device"
            self.obj.get_dump_file_path()

    def test_set_device_and_device_path(self):
        """"""
        self.obj.serial_port = SerialConnection.get_virtual_home_serial_port("vmodem0")
        assert self.obj.set_device("bmv702")
        assert self.obj.set_dump_file_path()
        assert self.obj.set_device("bluesolar_1.23")
        assert self.obj.set_dump_file_path()
        assert self.obj.set_device("smartsolar_1.39")
        assert self.obj.set_dump_file_path()
        assert not self.obj.set_device("hello")
        assert not self.obj.set_dump_file_path()

    def test_set_device_settings(self):
        """"""
        assert self.obj.set_device_settings("bmv702")
        assert self.obj.set_device_settings("bluesolar_1.23")
        assert self.obj.set_device_settings("smartsolar_1.39")

        with pytest.raises(ValueError):
            self.obj.set_device_settings("hello")
            self.obj.set_device_settings(SerialConnection.get_virtual_home_serial_port("world.bat"))

    def test_send_packet(self):
        """"""
        self.obj.perf = PerfStats()
        self.obj.perf.start_perf_key("writes")
        self.obj.dict = dict()
        self.obj.ser.write_timeout = 3
        for x in range(18):
            self.obj.dict.update({"%sKey" % x: "%sValue" % x})
        assert self.obj.send_packet() is True

        self.obj.dict = dict()
        self.obj.ser.write_timeout = 3
        for x in range(1):
            self.obj.dict.update({"%sKey" % x: "%sValue" % x})
        assert self.obj.send_packet() is True

        self.obj.dict = dict()
        for x in range(150):
            self.obj.dict.update({"%sKey" % x: "%sValue" % x})
        self.obj.ser.write_timeout = 0.00000002
        assert self.obj.send_packet() is False

        self.obj.ser.write_timeout = 3
        self.obj.ser.close()
        with pytest.raises(serial.serialutil.PortNotOpenError):
            self.obj.send_packet()

    def test_process_data(self):
        """"""
        self.obj.dict = {}
        for x in range(17):
            self.obj.dict.update({"%sKey" % x: "%sValue" % x})
        assert self.obj.process_data(key="ZKey", value="Ax125") is True

    def test_read_dump_file_line(self):
        """"""
        assert self.obj.read_dump_file_lines(max_writes=1)
        self.obj.set_device_settings("bluesolar_1.23")
        assert self.obj.read_dump_file_lines(max_writes=1)
        self.obj.set_device_settings("smartsolar_1.39")
        assert self.obj.read_dump_file_lines(max_writes=1)

    def test_run(self):
        """"""
        assert self.obj.run(max_writes=1)
        self.obj.set_device_settings("bluesolar_1.23")
        assert self.obj.run(max_writes=1)
        self.obj.set_device_settings("smartsolar_1.39")
        assert self.obj.run(max_writes=1)

        with pytest.raises(ValueError):
            self.obj.ser = None
            self.obj.run()
