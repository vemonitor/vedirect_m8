"""VedirectController unittest class."""
import time
import pytest
from vedirect_m8.ve_controller import VedirectController
from vedirect_m8.serconnect import SerialConnection
from ve_utils.utype import UType as Ut
from vedirect_m8.exceptions import SettingInvalidException, InputReadException, TimeoutException, VedirectException


class TestVedirectController:

    def setup_method(self):
        """
        Setup any state tied to the execution of the given function.

        Invoked for every test function in the module.
        """
        conf = {
            'serial_port': SerialConnection.get_virtual_home_serial_port("vmodem1"),
            'baud': 19200,
            'timeout': 0
        }
        serial_test = {
            'PID_test': {
                "typeTest": "value",
                "key": "PID",
                "value": "0x203"
            }
        }

        self.obj = VedirectController(
            serial_conf=conf,
            serial_test=serial_test
        )

    def test_settings(self):
        """Test configuration settings from Vedirect constructor."""
        assert self.obj.is_serial_ready()
        assert self.obj.is_ready()
        assert self.obj.has_serial_com()
        assert self.obj.connect_to_serial()
        assert self.obj.has_serial_test()

    def test_is_serial_com(self):
        """Test is_serial_com method."""
        assert VedirectController.is_serial_com(self.obj._com)
        assert not VedirectController.is_serial_com(dict())
        assert not VedirectController.is_serial_com(None)

    @staticmethod
    def test_is_timeout():
        """Test is_timeout method."""
        assert VedirectController.is_timeout(elapsed=59, timeout=60)
        with pytest.raises(TimeoutException):
            VedirectController.is_timeout(elapsed=60, timeout=60)
            VedirectController.is_timeout(elapsed=102, timeout=60)

    def test_init_serial_test(self):
        """Test init_serial_test method."""
        assert self.obj.init_serial_test({
            'PID_test': {
                "typeTest": "value",
                "key": "PID",
                "value": "0x203"
            }
        })

        with pytest.raises(SettingInvalidException):
            self.obj.init_serial_test(serial_test=None)

        with pytest.raises(SettingInvalidException):
            self.obj.init_serial_test(serial_test=list())

        with pytest.raises(SettingInvalidException):
            self.obj.init_serial_test(serial_test=dict())

        with pytest.raises(SettingInvalidException):
            self.obj.init_serial_test(serial_test={
                'PID_test': {
                    "typeTest": "value",
                    "key": "PID"
                }
            })

    def test_init_serial_connection_from_object(self):
        """Test init_serial_connection_from_object method."""
        obj = self.obj._com
        assert self.obj.init_serial_connection_from_object(obj)

        # test with bad serial port format
        obj = SerialConnection(
            serial_port="/etc/bad_port",
            source_name="TestVedirect"
        )
        with pytest.raises(SettingInvalidException):
            self.obj.init_serial_connection_from_object(obj)

        # test with bad serial port connection
        obj = SerialConnection(
            serial_port=SerialConnection.get_virtual_home_serial_port("vmodem255"),
            source_name="TestVedirect"
        )
        with pytest.raises(VedirectException):
            self.obj.init_serial_connection_from_object(obj)

    def test_init_serial_connection(self):
        """Test init_serial_connection method."""
        assert self.obj.init_serial_connection({'serial_port': self.obj._com._serial_port},
                                               source_name="TestVedirectController"
                                               )

        # test with bad serial port format
        with pytest.raises(SettingInvalidException):
            self.obj.init_serial_connection({'serial_port': "/etc/bad_port"},
                                            source_name="TestVedirectController"
                                            )

        # test with bad serial port connection
        with pytest.raises(VedirectException):
            self.obj.init_serial_connection(
                {'serial_port': SerialConnection.get_virtual_home_serial_port("vmodem255")},
                source_name="TestVedirectController"
            )

    def test_init_settings(self):
        """Test init_settings method."""
        good_serial_port = self.obj._com._serial_port
        assert self.obj.init_settings({'serial_port': good_serial_port},
                                      source_name="TestVedirectController"
                                      )

        # test with bad serial port format
        with pytest.raises(SettingInvalidException):
            self.obj.init_settings({'serial_port': "/etc/bad_port"},
                                   source_name="TestVedirectController"
                                   )

        # test with bad serial port connection
        # the serial port vmodem255 is not defined
        # the method search a valid serial port with serial test data
        # and return True when reached a valid serial port
        self.obj.set_wait_timeout(30)
        assert self.obj.init_settings({'serial_port': SerialConnection.get_virtual_home_serial_port("vmodem255")},
                                      source_name="TestVedirectController"
                                      )
        # now serial port is same as start
        assert good_serial_port == self.obj._com._serial_port

        with pytest.raises(VedirectException):
            self.obj._ser_test = None
            self.obj.set_wait_timeout(0.5)
            self.obj.init_settings(
                {'serial_port': SerialConnection.get_virtual_home_serial_port("vmodem255")},
                source_name="TestVedirectController"
            )

    def test_read_data_to_test(self):
        """Test read_data_to_test method."""
        data = self.obj.read_data_to_test()
        assert Ut.is_dict(data, not_null=True)

    def test_search_serial_port(self):
        """Test search_serial_port method."""
        try:
            self.obj.init_serial_connection(
                {'serial_port': SerialConnection.get_virtual_home_serial_port("vmodem255")},
                source_name="TestVedirectController"
            )
        except VedirectException:
            tst = False
            for i in range(20):
                if self.obj.search_serial_port():
                    tst = True
                    print("serial port retrieved at %s" % i)
                    break
                time.sleep(0.8)
            assert tst

    def test_init_data_read(self):
        """Test init_data_read method."""
        self.obj.read_data_single()
        assert Ut.is_dict(self.obj.dict, not_null=True)
        self.obj.init_data_read()
        assert not Ut.is_dict(self.obj.dict, not_null=True) and Ut.is_dict(self.obj.dict)

    def test_input_read(self):
        """Test input_read method."""
        datas = [
            b'\r', b'\n', b'P', b'I', b'D', b'\t',
            b'O', b'x', b'0', b'3', b'\r',
        ]
        for x in datas:
            self.obj.input_read(x)
        assert Ut.is_dict(self.obj.dict, not_null=True) and self.obj.dict.get('PID') == "Ox03"
        self.obj.init_data_read()
        datas = [
            b'\r', b'\n', b'C', b'h', b'e', b'c', b'k', b's', b'u', b'm', b'\t',
            b'O', b'\r', b'\n', b'\t', 'helloWorld'
        ]
        with pytest.raises(InputReadException):
            for x in datas:
                self.obj.input_read(x)

    def test_read_data_single(self):
        """Test read_data_single method."""
        data = self.obj.read_data_single()
        assert Ut.is_dict(data, not_null=True)

    def test_read_data_callback(self):
        """Test read_data_callback method."""

        def func_callback(data: dict or None):
            """Callback function."""
            assert Ut.is_dict(data, not_null=True)

        self.obj.set_wait_timeout(3600)
        self.obj.read_data_callback(callback_function=func_callback,
                                    timeout=20,
                                    max_loops=1
                                    )

        with pytest.raises(TimeoutException):
            self.obj.set_wait_timeout(3600)
            self.obj.read_data_callback(callback_function=func_callback,
                                        timeout=0.1,
                                        max_loops=1
                                        )
