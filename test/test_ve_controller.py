"""VedirectController unittest class."""
import time
import pytest
from vedirect_m8.ve_controller import VedirectController
from vedirect_m8.serconnect import SerialConnection
from ve_utils.utype import UType as Ut
from vedirect_m8.exceptions import SettingInvalidException
from vedirect_m8.exceptions import InputReadException
from vedirect_m8.exceptions import PacketReadException
from vedirect_m8.exceptions import ReadTimeoutException
from vedirect_m8.exceptions import SerialConnectionException
from vedirect_m8.exceptions import SerialConfException
from vedirect_m8.exceptions import SerialVeException
from vedirect_m8.exceptions import VedirectException


class TestVedirectController:

    def setup_method(self):
        """
        Setup any state tied to the execution of the given function.

        Invoked for every test function in the module.
        """
        conf = {
            'serial_port': SerialConnection.get_virtual_home_serial_port("vmodem1"),
            'baud': 19200,
            'timeout': 2
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
        assert self.obj.get_wait_timeout()
        self.obj._com = None
        with pytest.raises(SerialConnectionException):
            self.obj.connect_to_serial()

    def test_set_max_packet_blocks(self):
        """Test set_max_packet_blocks method."""
        assert self.obj.has_free_block()
        assert self.obj.set_max_packet_blocks(2)
        assert self.obj.set_max_packet_blocks(None)
        with pytest.raises(SettingInvalidException):
            self.obj.set_max_packet_blocks("error")

    def test_is_serial_com(self):
        """Test is_serial_com method."""
        assert VedirectController.is_serial_com(self.obj._com)
        assert not VedirectController.is_serial_com(dict())
        assert not VedirectController.is_serial_com(None)

    @staticmethod
    def test_is_timeout():
        """Test is_timeout method."""
        assert VedirectController.is_timeout(elapsed=59, timeout=60)
        with pytest.raises(ReadTimeoutException):
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

    def test_init_settings(self):
        """Test init_settings method."""
        good_serial_port = self.obj._com._serial_port
        assert self.obj.init_settings({'serial_port': good_serial_port},
                                      source_name="TestVedirectController"
                                      )

        # test with bad serial port format
        # now on bad serial port scan, test and connect valid port.
        # Don't raise exception if valid port available.
        self.obj.init_settings({"serial_port": "/etc/bad_port"},
                               source_name="TestVedirect"
                               )

        # test with bad serial port type
        # now on bad serial port scan, test and connect valid port.
        # Don't raise exception if valid port available.
        self.obj.init_settings(
            {"serial_port": 32},
            source_name="TestVedirect"
        )

        # test with bad serial port connection
        # now on bad serial port scan, test and connect valid port.
        # Don't raise exception if valid port available.
        self.obj.init_settings(
            {"serial_port": SerialConnection.get_virtual_home_serial_port("vmodem255")},
            source_name="TestVedirect"
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

    def test_test_serial_port(self):
        """Test test_serial_port method."""
        assert self.obj.test_serial_port(
            port=self.obj.get_serial_port()
        )

        bad_serial_test = {
            'PID_test': {
                "typeTest": "value",
                "key": "PID",
                "value": "0x800"
            }
        }
        assert self.obj.init_serial_test(bad_serial_test)
        assert not self.obj.test_serial_port(
            port=self.obj.get_serial_port()
        )
        with pytest.raises(SerialVeException):
            self.obj.test_serial_port(
                port=SerialConnection.get_virtual_home_serial_port("vmodem255")
            )

    def test_test_serial_ports(self):
        """Test test_serial_ports method."""
        ports = self.obj._com.get_serial_ports_list()
        assert self.obj.test_serial_ports(ports)
        self.obj._ser_test = None
        with pytest.raises(SerialConnectionException):
            self.obj.test_serial_ports(ports)

    def test_wait_or_search_serial_connection(self):
        """Test wait_or_search_serial_connection method."""
        assert self.obj.wait_or_search_serial_connection(
            timeout=2
        )

        bad_serial_test = {
            'PID_test': {
                "typeTest": "value",
                "key": "PID",
                "value": "0x800"
            }
        }
        assert self.obj.init_serial_test(bad_serial_test)
        with pytest.raises(ReadTimeoutException):
            self.obj.wait_or_search_serial_connection(
                timeout=0.0000000000001
            )

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

        self.obj._ser_test = None
        assert not self.obj.search_serial_port()

    def test_init_data_read(self):
        """Test init_data_read method."""
        packet = self.obj.read_data_single()
        assert Ut.is_dict(packet, not_null=True)
        # init_data_read() is now called in read_data_single()
        assert not Ut.is_dict(self.obj.dict, not_null=True)

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

        with pytest.raises(ReadTimeoutException):
            self.obj.set_wait_timeout(3600)
            self.obj.read_data_callback(callback_function=func_callback,
                                        timeout=0.000001,
                                        max_loops=1
                                        )
