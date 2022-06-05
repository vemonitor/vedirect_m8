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
            'serialPort': "/tmp/vmodem1",
            'baud': 19200,
            'timeout': 2,
        }

        self.obj = SerialConnection(**conf)

    def teardown_method(self):
        """ teardown any state that was previously setup with a setup_function
        call.
        """
        pass

    def test_settings(self):
        """Test configuration settings from SerialConnection constructor"""
        assert self.obj._settings.get('serialPort') == "/tmp/vmodem1"
        assert self.obj._settings.get('baud') == 19200
        assert self.obj._settings.get('timeout') == 2
        assert self.obj.is_settings()
        bauds = [
                110, 300, 600, 1200,
                2400, 4800, 9600, 14400,
                19200, 38400, 57600, 115200,
                128000, 256000, 0, 1, 10, 302,
                2500, 4900, "300"
                ]
        tests = [x for x in bauds if self.obj.is_baud(x)]
        assert len(tests) == 14
        timeouts = [
                1, 5, 10,
                "2400", 0.1, 0
                ]
        tests = [x for x in timeouts if self.obj.is_timeout(x)]
        assert len(tests) == 3
        
    def test_connect(self):
        """"""
        assert self.obj.connect()
        assert self.obj.is_serial_ready()
        assert self.obj.is_ready()
        
    def test_get_serial_ports_list(self):
        """"""
        assert Ut.is_list_not_empty(self.obj.get_serial_ports_list())

