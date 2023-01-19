"""Vedirect unittest class."""
import pytest
from .serial_test_helper import SerialTestHelper
from vedirect_m8.vedirect import Vedirect
from vedirect_m8.serconnect import SerialConnection
from ve_utils.utype import UType as Ut
from vedirect_m8.exceptions import SettingInvalidException
from vedirect_m8.exceptions import InputReadException
from vedirect_m8.exceptions import PacketReadException
from vedirect_m8.exceptions import ReadTimeoutException
from vedirect_m8.exceptions import SerialConnectionException
from vedirect_m8.exceptions import SerialConfException
from vedirect_m8.exceptions import SerialVeException


# noinspection PyTypeChecker
class TestVedirect:

    def setup_class(self):
        """
        Setup any state tied to the execution of the given function.

        Invoked for every test function in the module.
        """
        conf = {
            'serial_port': SerialConnection.get_virtual_home_serial_port("vmodem0")
        }

        self.ve_sim = SerialTestHelper(**conf)

    def setup_method(self):
        """
        Setup any state tied to the execution of the given function.

        Invoked for every test function in the module.
        """
        conf = {
            'serial_port': SerialConnection.get_virtual_home_serial_port("vmodem1"),
            'baud': 19200,
            'timeout': 0,
            'source_name': 'TestVedirect'
        }

        self.obj = Vedirect(serial_conf=conf)

    def test_settings(self):
        """Test configuration settings from Vedirect constructor."""
        assert self.obj.is_serial_ready()
        assert self.obj.is_ready()
        assert self.obj.has_serial_com()
        assert self.obj.connect_to_serial()

        self.obj._com = None
        with pytest.raises(SerialConnectionException):
            self.obj.connect_to_serial()

    def test_set_max_packet_blocks(self):
        """Test set_max_packet_blocks method."""
        assert self.obj._helper.has_free_block()
        assert self.obj._helper.set_max_packet_blocks(2)
        assert self.obj._helper.set_max_packet_blocks(None)
        with pytest.raises(SettingInvalidException):
            self.obj._helper.set_max_packet_blocks("error")

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
        assert self.obj.init_serial_connection(
            {"serial_port": self.obj._com.get_serial_port()}
        )

        # test with bad serial port format
        with pytest.raises(SerialConfException):
            self.obj.init_serial_connection(
                {"serial_port": "/etc/bad_port"}
            )

        # test with bad serial port type
        with pytest.raises(SerialConfException):
            self.obj.init_serial_connection(
                {"serial_port": 32}
            )

        # test with bad serial port connection
        with pytest.raises(SerialVeException):
            self.obj.init_serial_connection(
                {
                    "serial_port": SerialConnection.get_virtual_home_serial_port("vmodem255"),
                    "source_name": "TestVedirectBadPort"
                },
            )

    def test_init_settings(self):
        """Test init_settings method."""
        assert self.obj.get_serial_port() == SerialConnection.get_virtual_home_serial_port("vmodem1")
        assert self.obj._helper.max_blocks == 18
        assert self.obj._com._source_name == "TestVedirect"
        serial_conf = {
            'serial_port': SerialConnection.get_virtual_home_serial_port("vmodem1"),
            'baud': 19200,
            'timeout': 0,
            'source_name': 'NewTestVedirect'
        }
        options = {
            'max_packet_blocks': 17,
            'auto_start': False
        }
        assert self.obj.init_settings(
            serial_conf=serial_conf,
            options=options
        )
        assert self.obj._helper.max_blocks == 17
        assert self.obj._com._source_name == "NewTestVedirect"
        assert not self.obj.is_serial_ready()
        options = {
            'max_packet_blocks': 18,
            'auto_start': True
        }
        assert self.obj.init_settings(
            {
                "serial_port": self.obj._com.get_serial_port(),
                'source_name': 'TestVedirect'
             },
            options=options
        )
        assert self.obj.get_serial_port() == SerialConnection.get_virtual_home_serial_port("vmodem1")
        assert self.obj._helper.max_blocks == 18
        assert self.obj._com._source_name == "TestVedirect"

        # test with bad serial port format
        with pytest.raises(SerialConfException):
            self.obj.init_settings({"serial_port": "/etc/bad_port"},
                                   options=options
                                   )

        # test with bad serial port type
        with pytest.raises(SerialConfException):
            self.obj.init_settings({"serial_port": 32},
                                   options=options
                                   )

        # test with bad serial port connection
        with pytest.raises(SerialVeException):
            self.obj.init_settings({"serial_port": SerialConnection.get_virtual_home_serial_port("vmodem255")},
                                   options=options
                                   )

    def test_init_data_read(self):
        """Test init_data_read method."""
        self.obj._helper.dict = {"a": 2, "b": 3}
        assert self.obj._helper.init_data_read() is None
        assert not Ut.is_dict(self.obj._helper.dict, not_null=True)
        assert self.obj._helper.key == ''
        assert self.obj._helper.value == ''
        assert self.obj._helper.bytes_sum == 0
        assert self.obj._helper.state == self.obj._helper.WAIT_HEADER

    def test_input_read(self):
        """Test input_read method."""
        datas = [
            b'\r', b'\n', b'P', b'I', b'D', b'\t',
            b'O', b'x', b'0', b'3', b'\r'
        ]
        for x in [b':', b'a', b'1'] + datas:
            self.obj.input_read(x)
        assert Ut.is_dict(self.obj._helper.dict, not_null=True) and self.obj._helper.dict.get('PID') == "Ox03"
        self.obj._helper.init_data_read()
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
        self.obj._helper.init_data_read()
        with pytest.raises(InputReadException):
            for x in datas:
                self.obj.input_read(x)
                self.obj._helper.state = 12

    def test_read_data_single(self):
        """Test read_data_single method."""
        # test success, ReadTimeoutException and InputReadException
        def main_test():
            """Main read_data_single tests."""
            assert Ut.is_dict(self.obj.read_data_single(), not_null=True)
            with pytest.raises(ReadTimeoutException):
                assert Ut.is_dict(self.obj.read_data_single(timeout=0.00000000001), not_null=True)
            assert Ut.is_dict(self.obj.read_data_single(), not_null=True)
            with pytest.raises(InputReadException):
                assert Ut.is_dict(self.obj.read_data_single(), not_null=True)

        self.ve_sim.run_vedirect_sim_callback(
            callback=main_test,
            nb_packets=2,
            sleep=0.5
        )

        # test SerialConnectionException (instance not ready)
        self.obj._com = None
        with pytest.raises(SerialConnectionException):
            assert Ut.is_dict(self.obj.read_data_single(), not_null=True)

    def test_read_data_callback(self):
        """Test read_data_callback method."""

        def func_callback(data: dict or None):
            """Callback function."""
            assert Ut.is_dict(data, not_null=True)

        def main_test():
            """Main read_data_callback tests."""
            self.obj.read_data_callback(callback_function=func_callback,
                                        timeout=20,
                                        max_loops=1
                                        )

            with pytest.raises(ReadTimeoutException):
                self.obj.read_data_callback(callback_function=func_callback,
                                            timeout=0.00001,
                                            max_loops=1
                                            )

            with pytest.raises(SerialConnectionException):
                self.obj._com = None
                self.obj.read_data_callback(callback_function=func_callback,
                                            timeout=20,
                                            max_loops=1
                                            )

        self.ve_sim.run_vedirect_sim_callback(
            callback=main_test,
            nb_packets=4,
            sleep=0.5
        )
