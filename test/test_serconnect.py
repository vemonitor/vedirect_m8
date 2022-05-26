import pytest
from vedirect_m8.serconnect import SerialConnection
from ve_utils.utils import USys as USys
from vedirect_m8.serutils import SerialUtils as Ut


class TestSerialConnection:

    def setup_method(self):
        """ setup any state tied to the execution of the given function.
        Invoked for every test function in the module.
        """
        conf = {
            'serialPort': "COM1"
        }

        if USys.is_op_sys_type("unix"):
            conf['serialPort'] = "/tmp/vmodem1"
            conf['serialPath'] = "/tmp/"

        self.obj = SerialConnection(**conf)

    def teardown_method(self):
        """ teardown any state that was previously setup with a setup_function
        call.
        """
        pass

    def test_properties(self):
        """"""
        assert self.obj.is_settings()

    def test_get_serial_ports_list(self):
        """"""
        assert Ut.is_list_not_empty(self.obj.get_serial_ports_list())

    def test_connect(self):
        """"""
        assert self.obj.connect()

    def test_is_key_pattern(self):
        """"""
        assert not Ut.is_key_pattern('_hello')
        assert not Ut.is_key_pattern('hel lo')
        assert Ut.is_key_pattern("hj_58Hyui")

    def test_is_unix_serial_port_pattern(self):
        """"""
        assert not Ut.is_unix_serial_port_pattern('/etc/ttyUSB1')
        assert not Ut.is_unix_serial_port_pattern("/dev/tty")
        assert not Ut.is_unix_serial_port_pattern("/dev/tty1")
        assert Ut.is_unix_serial_port_pattern("/tmp/vmodem1")
        assert Ut.is_unix_serial_port_pattern("/dev/ttyUSB3")

    def test_is_win_serial_port_pattern(self):
        """"""
        assert not Ut.is_win_serial_port_pattern('/etc/ttyUSB1')
        assert not Ut.is_win_serial_port_pattern('/dev/COM3')
        assert not Ut.is_win_serial_port_pattern('/COM3')
        assert not Ut.is_win_serial_port_pattern('COM')
        assert Ut.is_win_serial_port_pattern("COM255")
        assert Ut.is_win_serial_port_pattern("COM3")
        assert Ut.is_win_serial_port_pattern("COM3")
