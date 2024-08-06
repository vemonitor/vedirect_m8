"""VedirectController unittest class."""
import time
from typing import Optional
import pytest
from ve_utils.utype import UType as Ut
from vedirect_m8.ve_controller import VedirectController
from vedirect_m8.serconnect import SerialConnection
from vedirect_m8.exceptions import SettingInvalidException
from vedirect_m8.exceptions import ReadTimeoutException
from vedirect_m8.exceptions import SerialConnectionException
from vedirect_m8.exceptions import SerialVeException
from vedirect_m8.exceptions import VedirectException


@pytest.fixture(name="helper_manager", scope="class")
def helper_manager_fixture():
    """Json Schema test manager fixture"""
    class HelperManager:
        """Json Helper test manager fixture Class"""
        def __init__(self):
            self.init_object()

        def init_object(self):
            """Init Object"""
            conf = {
                'serial_port': SerialConnection.get_virtual_home_serial_port(
                    "vmodem1"
                ),
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

    return HelperManager()


class TestVedirectController:
    """VedirectController unittest class."""
    def test_settings(self, helper_manager):
        """Test configuration settings from Vedirect constructor."""
        assert helper_manager.obj.is_serial_ready()
        assert helper_manager.obj.is_ready()
        assert helper_manager.obj.has_serial_com()
        assert helper_manager.obj.connect_to_serial()
        assert helper_manager.obj.has_serial_test()
        assert helper_manager.obj.get_wait_timeout()
        helper_manager.obj._com = None
        with pytest.raises(SerialConnectionException):
            helper_manager.obj.connect_to_serial()

    def test_set_max_packet_blocks(self, helper_manager):
        """Test set_max_packet_blocks method."""
        assert helper_manager.obj.has_free_block()
        assert helper_manager.obj.set_max_packet_blocks(2)
        assert helper_manager.obj.set_max_packet_blocks(None)
        with pytest.raises(SettingInvalidException):
            helper_manager.obj.set_max_packet_blocks("error")

    def test_is_serial_com(self, helper_manager):
        """Test is_serial_com method."""
        helper_manager.init_object()
        assert VedirectController.is_serial_com(helper_manager.obj._com)

    @staticmethod
    def test_is_timeout():
        """Test is_timeout method."""
        assert VedirectController.is_timeout(elapsed=59, timeout=60)
        with pytest.raises(ReadTimeoutException):
            VedirectController.is_timeout(elapsed=60, timeout=60)
            VedirectController.is_timeout(elapsed=102, timeout=60)

    def test_init_serial_test(self, helper_manager):
        """Test init_serial_test method."""
        assert helper_manager.obj.init_serial_test({
            'PID_test': {
                "typeTest": "value",
                "key": "PID",
                "value": "0x203"
            }
        })

        with pytest.raises(SettingInvalidException):
            helper_manager.obj.init_serial_test(serial_test=dict())

        with pytest.raises(SettingInvalidException):
            helper_manager.obj.init_serial_test(serial_test={
                'PID_test': {
                    "typeTest": "value",
                    "key": "PID"
                }
            })

    def test_init_settings(self, helper_manager):
        """Test init_settings method."""
        helper_manager.init_object()
        good_serial_port = helper_manager.obj._com._serial_port
        helper_manager.obj.set_wait_timeout(20)

        assert helper_manager.obj.init_settings(
            {'serial_port': good_serial_port},
            source_name="TestVedirectController"
        )

        # test with bad serial port format
        # now on bad serial port scan, test and connect valid port.
        # Don't raise exception if valid port available.
        helper_manager.obj.init_settings(
            {"serial_port": "/etc/bad_port"},
            source_name="TestVedirect"
        )

        # test with bad serial port type
        # now on bad serial port scan, test and connect valid port.
        # Don't raise exception if valid port available.
        helper_manager.obj.init_settings(
            {"serial_port": 32},
            source_name="TestVedirect"
        )

        # test with bad serial port connection
        # now on bad serial port scan, test and connect valid port.
        # Don't raise exception if valid port available.
        helper_manager.obj.init_settings(
            {"serial_port": SerialConnection.get_virtual_home_serial_port(
                "vmodem255"
                )},
            source_name="TestVedirect"
        )

        # now serial port is same as start
        assert good_serial_port == helper_manager.obj._com._serial_port

        with pytest.raises(VedirectException):
            helper_manager.obj._ser_test = None
            helper_manager.obj.set_wait_timeout(0.5)
            helper_manager.obj.init_settings(
                {'serial_port': SerialConnection.get_virtual_home_serial_port(
                    "vmodem255")},
                source_name="TestVedirectController"
            )

    def test_read_data_to_test(self, helper_manager):
        """Test read_data_to_test method."""
        helper_manager.init_object()
        data = helper_manager.obj.read_data_to_test()
        assert Ut.is_dict(data, not_null=True)

    def test__get_test_data(self, helper_manager):
        """Test _get_test_data method."""
        helper_manager.init_object()
        helper_manager.obj.init_settings(
                {'serial_port': SerialConnection.get_virtual_home_serial_port(
                    "vmodem1")},
                source_name="TestVedirectController"
            )
        data = helper_manager.obj._get_test_data()
        assert Ut.is_dict(data, not_null=True)

        helper_manager.obj._com.ser.close()
        data = helper_manager.obj._get_test_data()
        assert data is None

    def test_test_serial_port(self, helper_manager):
        """Test test_serial_port method."""
        helper_manager.init_object()
        assert helper_manager.obj.test_serial_port(
            port=helper_manager.obj.get_serial_port()
        )

        bad_serial_test = {
            'PID_test': {
                "typeTest": "value",
                "key": "PID",
                "value": "0x800"
            }
        }
        assert helper_manager.obj.init_serial_test(bad_serial_test)
        assert not helper_manager.obj.test_serial_port(
            port=helper_manager.obj.get_serial_port()
        )
        with pytest.raises(SerialVeException):
            helper_manager.obj.test_serial_port(
                port=SerialConnection.get_virtual_home_serial_port("vmodem255")
            )

    def test_test_serial_ports(self, helper_manager):
        """Test test_serial_ports method."""
        helper_manager.init_object()
        ports = helper_manager.obj._com.get_serial_ports_list()
        assert helper_manager.obj.test_serial_ports(ports)
        helper_manager.obj._ser_test = None
        with pytest.raises(SerialConnectionException):
            helper_manager.obj.test_serial_ports(ports)

    def test_wait_or_search_serial_connection(self, helper_manager):
        """Test wait_or_search_serial_connection method."""
        helper_manager.init_object()
        assert helper_manager.obj.wait_or_search_serial_connection(
            timeout=2
        )

        bad_serial_test = {
            'PID_test': {
                "typeTest": "value",
                "key": "PID",
                "value": "0x800"
            }
        }
        assert helper_manager.obj.init_serial_test(bad_serial_test)
        with pytest.raises(ReadTimeoutException):
            helper_manager.obj.wait_or_search_serial_connection(
                timeout=0.0000000000001
            )

    def test_search_serial_port(self, helper_manager):
        """Test search_serial_port method."""
        helper_manager.init_object()
        try:
            helper_manager.obj.init_serial_connection(
                {'serial_port': SerialConnection.get_virtual_home_serial_port(
                    "vmodem255")},
                source_name="TestVedirectController"
            )
        except VedirectException:
            tst = False
            for i in range(20):
                if helper_manager.obj.search_serial_port():
                    tst = True
                    break
                time.sleep(0.8)
            assert tst

        helper_manager.obj._ser_test = None
        assert not helper_manager.obj.search_serial_port()

    def test_init_data_read(self, helper_manager):
        """Test init_data_read method."""
        helper_manager.init_object()
        packet = helper_manager.obj.read_data_single()
        assert Ut.is_dict(packet, not_null=True)
        # init_data_read() is now called in read_data_single()
        assert not Ut.is_dict(helper_manager.obj.dict, not_null=True)

    def test_read_data_single(self, helper_manager):
        """Test read_data_single method."""
        helper_manager.init_object()
        data = helper_manager.obj.read_data_single()
        assert Ut.is_dict(data, not_null=True)

    def test_run_callback_on_packet(self, helper_manager):
        """Test run_callback_on_packet method."""
        helper_manager.init_object()

        def func_callback(data: Optional[dict]):
            """Callback function."""
            assert Ut.is_dict(data, not_null=True)
        helper_manager.obj._com.ser.close()
        helper_manager.obj.set_wait_timeout(10)
        res = helper_manager.obj.run_callback_on_packet(
            callback_function=func_callback,
            timeout=10,
            max_loops=1
        )
        assert res is True

    def test_read_data_callback(self, helper_manager):
        """Test run_callback_on_packet method."""
        helper_manager.init_object()

        def func_callback(data: Optional[dict]):
            """Callback function."""
            assert Ut.is_dict(data, not_null=True)

        def is_error_callback(data: None):
            """Callback function."""
            assert data is None

        helper_manager.obj.set_wait_timeout(10)
        helper_manager.obj.run_callback_on_packet(
            callback_function=func_callback,
            timeout=20,
            max_loops=1
        )

        with pytest.raises(ReadTimeoutException):
            helper_manager.obj.set_wait_timeout(30)
            helper_manager.obj.read_data_callback(
                callback_function=func_callback,
                timeout=0.000001,
                max_loops=1
            )

        helper_manager.obj._com = None
        data = helper_manager.obj.read_data_callback(
            callback_function=is_error_callback,
            timeout=20,
            max_loops=1
        )
        assert data is None
