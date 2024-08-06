"""Vedirect unittest class."""
from typing import Optional
import pytest

from ve_utils.utype import UType as Ut
from vedirect_m8.vedirect import Vedirect
from vedirect_m8.serconnect import SerialConnection
from vedirect_m8.exceptions import SettingInvalidException
from vedirect_m8.exceptions import InputReadException
from vedirect_m8.exceptions import PacketReadException
from vedirect_m8.exceptions import ReadTimeoutException
from vedirect_m8.exceptions import SerialConnectionException
from vedirect_m8.exceptions import SerialConfException
from vedirect_m8.exceptions import SerialVeException


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
                'timeout': 0,
            }

            self.obj = Vedirect(serial_conf=conf)

    return HelperManager()


# noinspection PyTypeChecker
class TestVedirect:
    """Vedirect unittest class."""

    def test_settings(self, helper_manager):
        """Test configuration settings from Vedirect constructor."""
        assert helper_manager.obj.is_serial_ready()
        assert helper_manager.obj.is_ready()
        assert helper_manager.obj.has_serial_com()
        assert helper_manager.obj.connect_to_serial()
        assert helper_manager.obj.get_serial_port(
        ) == SerialConnection.get_virtual_home_serial_port(
            "vmodem1"
        )
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
        assert Vedirect.is_serial_com(helper_manager.obj._com)
        assert not Vedirect.is_serial_com(dict())
        assert not Vedirect.is_serial_com(None)

    @staticmethod
    def test_is_timeout():
        """Test is_timeout method."""
        assert Vedirect.is_timeout(elapsed=59, timeout=60)
        with pytest.raises(ReadTimeoutException):
            Vedirect.is_timeout(elapsed=60, timeout=60)
        with pytest.raises(ReadTimeoutException):
            Vedirect.is_timeout(elapsed=102, timeout=60)

    def test_init_serial_connection_from_object(self, helper_manager):
        """Test init_serial_connection_from_object method base."""
        helper_manager.init_object()
        obj = helper_manager.obj._com.serialize()
        obj = SerialConnection(**obj)
        assert helper_manager.obj.init_serial_connection_from_object(obj)

        # test with bad serial port format
        obj = SerialConnection(
            serial_port="/etc/bad_port",
            source_name="TestVedirect"
        )
        with pytest.raises(SerialConfException):
            helper_manager.obj.init_serial_connection_from_object(obj)

        # test with bad serial port type
        obj = SerialConnection(
            serial_port=32,
            source_name="TestVedirect"
        )
        with pytest.raises(SerialConfException):
            helper_manager.obj.init_serial_connection_from_object(obj)

        # test with bad serial port connection
        obj = SerialConnection(
            serial_port=SerialConnection.get_virtual_home_serial_port(
                "vmodem255"
            ),
            source_name="TestVedirect"
        )
        with pytest.raises(SerialVeException):
            helper_manager.obj.init_serial_connection_from_object(obj)

    def test_init_serial_connection(self, helper_manager):
        """Test init_serial_connection method."""
        helper_manager.init_object()
        assert helper_manager.obj.init_serial_connection(
            {"serial_port": helper_manager.obj._com._serial_port},
            source_name="TestVedirect"
        )

        # test with bad serial port format
        with pytest.raises(SerialConfException):
            helper_manager.obj.init_serial_connection(
                {"serial_port": "/etc/bad_port"},
                source_name="TestVedirect"
            )

        # test with bad serial port type
        with pytest.raises(SerialConfException):
            helper_manager.obj.init_serial_connection(
                {"serial_port": 32},
                source_name="TestVedirect"
            )

        # test with bad serial port connection
        with pytest.raises(SerialVeException):
            helper_manager.obj.init_serial_connection(
                {"serial_port": SerialConnection.get_virtual_home_serial_port(
                    "vmodem255")},
                source_name="TestVedirectBadPort"
            )

    def test_init_settings(self, helper_manager):
        """Test init_settings method."""
        helper_manager.init_object()
        assert helper_manager.obj.init_settings(
            {"serial_port": helper_manager.obj._com._serial_port},
            source_name="TestVedirect"
        )

        # test with bad serial port format
        with pytest.raises(SerialConfException):
            helper_manager.obj.init_settings(
                {"serial_port": "/etc/bad_port"},
                source_name="TestVedirect"
            )

        # test with bad serial port type
        with pytest.raises(SerialConfException):
            helper_manager.obj.init_settings(
                {"serial_port": 32},
                source_name="TestVedirect"
            )

        # test with bad serial port connection
        with pytest.raises(SerialVeException):
            helper_manager.obj.init_settings(
                {"serial_port": SerialConnection.get_virtual_home_serial_port(
                    "vmodem255")},
                source_name="TestVedirect"
            )

    def test_init_data_read(self, helper_manager):
        """Test init_data_read method."""
        helper_manager.init_object()
        packet = helper_manager.obj.read_data_single()
        assert Ut.is_dict(packet, not_null=True)
        helper_manager.obj.init_data_read()
        assert not Ut.is_dict(helper_manager.obj.dict, not_null=True)

    def test_input_read(self, helper_manager):
        """Test input_read method."""
        datas = [
            b'\r', b'\n', b'P', b'I', b'D', b'\t',
            b'O', b'x', b'0', b'3', b'\r'
        ]
        for x in [b':', b'a', b'1'] + datas:
            helper_manager.obj.input_read(x)
        assert Ut.is_dict(helper_manager.obj.dict, not_null=True)\
            and helper_manager.obj.dict.get('PID') == "Ox03"
        helper_manager.obj.init_data_read()
        bad_datas = [
            b'\r', b'\n', b'C', b'h', b'e', b'c', b'k', b's', b'u', b'm',
            b'\t', b'O', b'\r', b'\n', b'\t', 'helloWorld'
        ]
        with pytest.raises(InputReadException):
            for x in bad_datas:
                helper_manager.obj.input_read(x)

        # Test max input blocks
        # if serial never has checksum
        with pytest.raises(PacketReadException):
            z, t = 0, 2
            for i in range(22):
                for x in datas:
                    if 0 <= z < 10 and x == datas[t]:
                        x = f'{z}'
                        x = x.encode('ASCII')
                        z = z + 1

                    if z == 10:
                        z = 0
                        t = t + 1
                    helper_manager.obj.input_read(x)
        helper_manager.obj.init_data_read()
        with pytest.raises(InputReadException):
            for x in datas:
                helper_manager.obj.input_read(x)
                helper_manager.obj.state = 12

    def test_read_global_packet(self, helper_manager):
        """Test read_serial_packet method."""
        helper_manager.init_object()
        data = helper_manager.obj.read_global_packet()
        assert Ut.is_dict(data, not_null=True)

        helper_manager.obj.init_serial_connection(
            {"serial_port": SerialConnection.get_virtual_home_serial_port(
                "vmodem0")},
            source_name="TestVedirect"
        )
        with pytest.raises(InputReadException):
            helper_manager.obj.read_global_packet()

    def test_read_data_single(self, helper_manager):
        """Test read_data_single method."""
        helper_manager.init_object()
        data = helper_manager.obj.read_data_single()
        assert Ut.is_dict(data, not_null=True)
        helper_manager.obj._com = None
        with pytest.raises(SerialConnectionException):
            helper_manager.obj.read_data_single()

    def test_read_data_callback(self, helper_manager):
        """Test read_data_callback method."""
        helper_manager.init_object()

        def func_callback(data: Optional[dict]):
            """Callback function."""
            assert Ut.is_dict(data, not_null=True)

        helper_manager.obj.read_data_callback(
            callback_function=func_callback,
            timeout=20,
            max_loops=1
        )

        with pytest.raises(ReadTimeoutException):
            helper_manager.obj.read_data_callback(
                callback_function=func_callback,
                timeout=0.1,
                max_loops=1
            )

        with pytest.raises(SerialConnectionException):
            helper_manager.obj._com = None
            helper_manager.obj.read_data_callback(
                callback_function=func_callback,
                timeout=20,
                max_loops=1
            )
