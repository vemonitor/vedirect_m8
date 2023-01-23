import pytest
import serial

from vedirect_m8.vedirectsim import Vedirectsim
from vedirect_m8.serconnect import SerialConnection


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

    def test_serial_connect(self):
        """"""
        assert self.obj.serial_connect()
        with pytest.raises((serial.SerialException, serial.SerialTimeoutException)):
            self.obj.serialport = "bad_port"
            self.obj.serial_connect()
            self.obj.serialport = 1
            self.obj.serial_connect()

    def test_set_device_and_device_path(self):
        """"""
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

    def control_dump_file(self, device: str):
        """"""
        result, nb, nb_blocks = False, 0, 0
        self.obj.set_device_settings(device)
        if self.obj.is_ready():
            result = True
            self.obj.dict = {}
            for key, value in self.obj.read_dump_file():
                if self.obj.process_data(key, value):
                    # checksum = self.obj.convert(self.obj.dict, get_checksum=True)
                    nb_blocks = len(self.obj.dict)
                    if nb_blocks > 18:
                        # or checksum != ord(value):
                        result = False
                    self.obj.dict = {}

                    nb = nb + 1
        return result, nb

    def test_dump_files(self):
        """"""
        result, nb = self.control_dump_file("bmv702")
        assert result is True and nb > 0
        result, nb = self.control_dump_file("bluesolar_1.23")
        assert result is True and nb > 0
        result, nb = self.control_dump_file("smartsolar_1.39")
        assert result is True and nb > 0

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
