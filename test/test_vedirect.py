"""Vedirect unittest class."""
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


# noinspection PyTypeChecker
class TestVedirect:

    def setup_method(self):
        """
        Setup any state tied to the execution of the given function.

        Invoked for every test function in the module.
        """
        conf = {
            'serial_port': SerialConnection.get_virtual_home_serial_port("vmodem1"),
            'baud': 19200,
            'timeout': 0,
        }

        self.obj = Vedirect(serial_conf=conf)

    def test_settings(self):
        """Test configuration settings from Vedirect constructor."""
        assert self.obj.is_serial_ready()
        assert self.obj.is_ready()
        assert self.obj.has_serial_com()
        assert self.obj.connect_to_serial()
        assert self.obj.get_serial_port() == SerialConnection.get_virtual_home_serial_port("vmodem1")
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
        assert Vedirect.is_serial_com(self.obj._com)
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

    def test_init_serial_connection_from_object(self):
        """Test init_serial_connection_from_object method base."""
        obj = self.obj._com.serialize()
        obj = SerialConnection(**obj)
        assert self.obj.init_serial_connection_from_object(obj)

        # test with bad serial port format
        obj = SerialConnection(
            serial_port="/etc/bad_port",
            source_name="TestVedirect"
        )
        with pytest.raises(SerialConfException):
            self.obj.init_serial_connection_from_object(obj)

        # test with bad serial port type
        obj = SerialConnection(
            serial_port=32,
            source_name="TestVedirect"
        )
        with pytest.raises(SerialConfException):
            self.obj.init_serial_connection_from_object(obj)

        # test with bad serial port connection
        obj = SerialConnection(
            serial_port=SerialConnection.get_virtual_home_serial_port("vmodem255"),
            source_name="TestVedirect"
        )
        with pytest.raises(SerialVeException):
            self.obj.init_serial_connection_from_object(obj)

    def test_init_serial_connection(self):
        """Test init_serial_connection method."""
        assert self.obj.init_serial_connection({"serial_port": self.obj._com._serial_port},
                                               source_name="TestVedirect"
                                               )

        # test with bad serial port format
        with pytest.raises(SerialConfException):
            self.obj.init_serial_connection({"serial_port": "/etc/bad_port"},
                                            source_name="TestVedirect"
                                            )

        # test with bad serial port type
        with pytest.raises(SerialConfException):
            self.obj.init_serial_connection({"serial_port": 32},
                                            source_name="TestVedirect"
                                            )

        # test with bad serial port connection
        with pytest.raises(SerialVeException):
            self.obj.init_serial_connection({"serial_port": SerialConnection.get_virtual_home_serial_port("vmodem255")},
                                            source_name="TestVedirectBadPort"
                                            )

    def test_init_settings(self):
        """Test init_settings method."""
        assert self.obj.init_settings({"serial_port": self.obj._com._serial_port},
                                      source_name="TestVedirect"
                                      )

        # test with bad serial port format
        with pytest.raises(SerialConfException):
            self.obj.init_settings({"serial_port": "/etc/bad_port"},
                                   source_name="TestVedirect"
                                   )

        # test with bad serial port type
        with pytest.raises(SerialConfException):
            self.obj.init_settings({"serial_port": 32},
                                   source_name="TestVedirect"
                                   )

        # test with bad serial port connection
        with pytest.raises(SerialVeException):
            self.obj.init_settings({"serial_port": SerialConnection.get_virtual_home_serial_port("vmodem255")},
                                   source_name="TestVedirect"
                                   )

    def test_init_data_read(self):
        """Test init_data_read method."""
        packet = self.obj.read_data_single()
        assert Ut.is_dict(packet, not_null=True)
        self.obj.init_data_read()
        assert not Ut.is_dict(self.obj.dict, not_null=True)

    def test_input_read(self):
        """Test input_read method."""
        datas = [
            b'\r', b'\n', b'P', b'I', b'D', b'\t',
            b'O', b'x', b'0', b'3', b'\r'
        ]
        for x in [b':', b'a', b'1'] + datas:
            self.obj.input_read(x)
        assert Ut.is_dict(self.obj.dict, not_null=True) and self.obj.dict.get('PID') == "Ox03"
        self.obj.init_data_read()
        bad_datas = [
            b'\r', b'\n', b'C', b'h', b'e', b'c', b'k', b's', b'u', b'm', b'\t',
            b'O', b'\r', b'\n', b'\t', 'helloWorld'
        ]
        with pytest.raises(InputReadException):
            for x in bad_datas:
                self.obj.input_read(x)

        # Test max input blocks
        # if serial never has checksum
        with pytest.raises(PacketReadException):
            z, t = 0, 2
            for i in range(22):
                for x in datas:
                    if 0 <= z < 10 and x == datas[t]:
                        x = '%s' % z
                        x = x.encode('ASCII')
                        z = z + 1

                    if z == 10:
                        z = 0
                        t = t + 1
                    self.obj.input_read(x)
        self.obj.init_data_read()
        with pytest.raises(InputReadException):
            for x in datas:
                self.obj.input_read(x)
                self.obj.state = 12

    def test_read_global_packet(self):
        """Test read_serial_packet method."""
        data = self.obj.read_global_packet()
        assert Ut.is_dict(data, not_null=True)

        self.obj.init_serial_connection(
            {"serial_port": SerialConnection.get_virtual_home_serial_port("vmodem0")},
            source_name="TestVedirect"
        )
        with pytest.raises(InputReadException):
            self.obj.read_global_packet()

    def test_read_data_single(self):
        """Test read_data_single method."""
        data = self.obj.read_data_single()
        assert Ut.is_dict(data, not_null=True)
        self.obj._com = None
        with pytest.raises(SerialConnectionException):
            self.obj.read_data_single()

    def test_read_data_callback(self):
        """Test read_data_callback method."""

        def func_callback(data: dict or None):
            """Callback function."""
            assert Ut.is_dict(data, not_null=True)

        self.obj.read_data_callback(callback_function=func_callback,
                                    timeout=20,
                                    max_loops=1
                                    )

        with pytest.raises(ReadTimeoutException):
            self.obj.read_data_callback(callback_function=func_callback,
                                        timeout=0.1,
                                        max_loops=1
                                        )

        with pytest.raises(SerialConnectionException):
            self.obj._com = None
            self.obj.read_data_callback(callback_function=func_callback,
                                        timeout=20,
                                        max_loops=1
                                        )
