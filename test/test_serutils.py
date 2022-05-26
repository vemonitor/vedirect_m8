import pytest
from vedirect.serutils import SerialUtils


class TestSerialUtils:

    def setup_method(self):
        """ setup any state tied to the execution of the given function.
        Invoked for every test function in the module.
        """
        self.obj = SerialUtils()

    def teardown_method(self):
        """ teardown any state that was previously setup with a setup_function
        call.
        """
        pass

    def test_is_key_pattern(self):
        """"""
        assert not self.obj.is_key_pattern('_hello')
        assert not self.obj.is_key_pattern('hel lo')
        assert self.obj.is_key_pattern("hj_58Hyui")

    def test_is_serial_key_pattern(self):
        """"""
        assert not self.obj.is_serial_key_pattern('_hello')
        assert not self.obj.is_serial_key_pattern('hel lo')
        assert self.obj.is_serial_key_pattern("hj_58Hyui")
        assert self.obj.is_serial_key_pattern("#hj_58Hyui#")

    def test_is_unix_serial_port_pattern(self):
        """"""
        assert not self.obj.is_unix_serial_port_pattern('/etc/ttyUSB1')
        assert not self.obj.is_unix_serial_port_pattern("/dev/tty")
        assert not self.obj.is_unix_serial_port_pattern("/dev/tty1")
        assert self.obj.is_unix_serial_port_pattern("/tmp/vmodem1")
        assert self.obj.is_unix_serial_port_pattern("/dev/ttyUSB3")

    def test_is_win_serial_port_pattern(self):
        """"""
        assert not self.obj.is_win_serial_port_pattern('/etc/ttyUSB1')
        assert not self.obj.is_win_serial_port_pattern('/dev/COM3')
        assert not self.obj.is_win_serial_port_pattern('/COM3')
        assert not self.obj.is_win_serial_port_pattern('COM')
        assert self.obj.is_win_serial_port_pattern("COM255")
        assert self.obj.is_win_serial_port_pattern("COM3")
        assert self.obj.is_win_serial_port_pattern("COM3")
