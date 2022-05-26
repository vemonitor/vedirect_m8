import pytest
import serial

from vedirect.vedirectsim import Vedirectsim
from ve_utils.utils import USys as USys


class TestVeDirectSim:

    def setup_method(self):
        """ setup any state tied to the execution of the given function.
        Invoked for every test function in the module.
        """
        serialport = "COM1"
        device = "bmv702"
        if USys.is_op_sys_type("unix"):
            serialport = "/tmp/vmodem0"

        self.obj = Vedirectsim(serialport, device)

    def teardown_method(self):
        """ teardown any state that was previously setup with a setup_function
        call.
        """
        pass

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
            self.obj.set_device_settings("/tmp/world.bat")

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
