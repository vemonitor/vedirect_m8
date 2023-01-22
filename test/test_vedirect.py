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
from .serial_test_helper import SerialTestHelper


# noinspection PyTypeChecker
class TestVedirect:
    """Vedirect unittest class."""
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
        assert self.obj.helper.has_free_block()
        assert self.obj.helper.set_max_packet_blocks(2)
        assert self.obj.helper.set_max_packet_blocks(None)
        with pytest.raises(SettingInvalidException):
            self.obj.helper.set_max_packet_blocks("error")

    def test_is_serial_com(self):
        """Test is_serial_com method."""
        assert Vedirect.is_serial_com(self.obj._com)
        assert not Vedirect.is_serial_com({})
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
        assert self.obj.init_serial_connection_from_object(obj, False)
        assert self.obj.init_serial_connection_from_object(obj, True)
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
        assert self.obj.flush_serial_cache()
        # test with bad serial port format
        with pytest.raises(SerialConfException):
            self.obj.init_serial_connection(
                serial_conf={
                    'exclusive': True,
                    "set_default": False
                }
            )

        # test with bad serial port type
        with pytest.raises(SerialConfException):
            self.obj.init_serial_connection({
                "serial_port": 32,
                "set_default": False
            })

        # test with bad serial port connection
        with pytest.raises(SerialVeException):
            self.obj.init_serial_connection(
                {
                    "serial_port": SerialConnection.get_virtual_home_serial_port("vmodem255"),
                    "source_name": "TestVedirectBadPort",
                    "set_default": True
                },
            )

    def test_init_settings(self):
        """Test init_settings method."""
        assert self.obj.get_serial_port() == SerialConnection.get_virtual_home_serial_port(
            "vmodem1"
        )
        assert self.obj.helper.max_blocks == 18
        assert self.obj._com.get_source_name() == "TestVedirect"
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
        assert self.obj.helper.max_blocks == 17
        assert self.obj._com.get_source_name() == "NewTestVedirect"
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
        assert self.obj.get_serial_port() == SerialConnection.get_virtual_home_serial_port(
            "vmodem1"
        )
        assert self.obj.helper.max_blocks == 18
        assert self.obj._com.get_source_name() == "TestVedirect"

        # test with bad serial port format
        with pytest.raises(SerialConfException):
            self.obj.init_settings({
                    "serial_port": "/etc/bad_port",
                    "set_default": False
                },
               options=options
            )

        # test with bad serial port type
        with pytest.raises(SerialConfException):
            self.obj.init_settings(
                {
                    "serial_port": 32,
                    "set_default": False
                },
                options=options
            )

        # test with bad serial port connection
        with pytest.raises(SerialVeException):
            self.obj.init_settings(
                {
                    "serial_port": SerialConnection.get_virtual_home_serial_port("vmodem255")
                },
                options=options
            )

    def test_init_data_read(self):
        """Test init_data_read method."""
        self.obj.helper.dict = {"a": 2, "b": 3}
        assert self.obj.helper.reset_data_read() is None
        assert not Ut.is_dict(self.obj.helper.dict, not_null=True)
        assert self.obj.helper.key == ''
        assert self.obj.helper.value == ''
        assert self.obj.helper.bytes_sum == 0
        assert self.obj.helper.state == self.obj.helper.WAIT_HEADER

    def test_input_read(self):
        """Test input_read method."""
        # Test good packet format
        datas = [
            b'\r', b'\n', b'P', b'I', b'D', b'\t',
            b'O', b'x', b'0', b'3', b'\r'
        ]
        for data in [b':', b'a', b'1'] + datas:
            self.obj.input_read(data)
        assert Ut.is_dict(self.obj.helper.dict, not_null=True) \
               and self.obj.helper.dict.get('PID') == "Ox03"
        self.obj.helper.reset_data_read()

        # Test InputReadException on bad byte
        with pytest.raises(InputReadException):
            for data in datas + [b'']:
                self.obj.input_read(data)
        self.obj.helper.reset_data_read()

        # Test PacketReadException on unexpected header2 in key
        with pytest.raises(PacketReadException):
            for data in datas + [b'\n', b'P', b'\n']:
                self.obj.input_read(data)
        self.obj.helper.reset_data_read()

        # Test PacketReadException on unexpected header1 in key
        with pytest.raises(PacketReadException):
            for data in datas + [b'\n', b'P', b'\r']:
                self.obj.input_read(data)
        self.obj.helper.reset_data_read()

        # Test PacketReadException on unexpected header2 in value
        with pytest.raises(PacketReadException):
            for data in datas + [b'\n', b'P', b'\t', b'1', b'\n']:
                self.obj.input_read(data)
        self.obj.helper.reset_data_read()

        # test PacketReadException in bad packet checksum
        bad_datas = [
            b'\r', b'\n', b'C', b'h', b'e', b'c', b'k', b's', b'u', b'm', b'\t',
            b'O', b''
        ]
        with pytest.raises(PacketReadException):
            for data in bad_datas:
                self.obj.input_read(data)
        self.obj.helper.reset_data_read()

        # Test max input blocks
        # if serial never has checksum max block limit throw PacketReadException
        with pytest.raises(PacketReadException):
            counter, key = 0, 2
            for step in range(22):
                for data in datas:
                    if 0 <= counter < 10 and data == datas[key]:
                        data = f'{counter}'
                        data = data.encode('ASCII')
                        counter = counter + 1

                    if counter == 10:
                        counter = 0
                        key = key + 1
                    self.obj.input_read(data)
        self.obj.helper.reset_data_read()

        # Test InputReadException on bad state flow
        with pytest.raises(InputReadException):
            for data in datas:
                self.obj.input_read(data)
                self.obj.helper.state = 12

    @staticmethod
    def test_get_read_data_params():
        """Test get_read_data_params method."""
        assert Ut.is_dict(Vedirect.get_read_data_params(), not_null=True)
        options = {
            'timeout': 3,
            'sleep_time': 3,
            'max_loops': 3,
            'max_block_errors': 3,
            'max_packet_errors': 3
        }
        params = Vedirect.get_read_data_params(
            options=options
        )
        assert Ut.is_dict(params, eq=5)
        assert params == options

        with pytest.raises(SettingInvalidException):
            Vedirect.get_read_data_params(
                {'timeout': 'a'}
            )

        with pytest.raises(SettingInvalidException):
            Vedirect.get_read_data_params(
                {'sleep_time': 'a'}
            )

        with pytest.raises(SettingInvalidException):
            Vedirect.get_read_data_params(
                {'max_loops': 'a'}
            )

        with pytest.raises(SettingInvalidException):
            Vedirect.get_read_data_params(
                {'max_block_errors': 'a'}
            )

        with pytest.raises(SettingInvalidException):
            Vedirect.get_read_data_params(
                {'max_packet_errors': 'a'}
            )

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
            with pytest.raises(InputReadException):
                assert Ut.is_dict(
                    self.obj.read_data_single(max_block_errors=5),
                    not_null=True
                )

        self.ve_sim.run_vedirect_sim_callback(
            callback=main_test,
            nb_packets=2,
            sleep=0.5
        )

        # test SerialConnectionException (instance not ready)
        self.obj._com = None
        with pytest.raises(SerialConnectionException):
            assert Ut.is_dict(self.obj.read_data_single(), not_null=True)

    def test_sleep_on_read_single_loop(self):
        """Test read_data_callback method."""
        self.obj._counter.add_counter_key('single_byte')
        self.obj._counter.add_to_key('single_byte')
        self.obj._counter.add_to_key('single_byte')
        assert self.obj.sleep_on_read_single_loop(1)
        assert self.obj.sleep_on_read_single_loop(1, 0.3)
        self.obj._com = None
        assert self.obj.sleep_on_read_single_loop(1) is False
        assert self.obj.sleep_on_read_single_loop(-2) is None

    def test_read_data_callback(self):
        """Test read_data_callback method."""

        def func_callback(data: dict or None):
            """Callback function."""
            assert Ut.is_dict(data, not_null=True)

        def main_test():
            """Main read_data_callback tests."""
            self.obj.read_data_callback(callback_function=func_callback,
                                        options={
                                            'timeout': 20,
                                            'max_loops': 1,
                                        })

            with pytest.raises(ReadTimeoutException):
                self.obj.read_data_callback(callback_function=func_callback,
                                            options={
                                                'timeout': 0.000001,
                                                'max_loops': 1,
                                            })

            with pytest.raises(InputReadException):
                self.obj.read_data_callback(callback_function=func_callback,
                                            options={
                                                'timeout': 2,
                                                'max_loops': 4,
                                                'max_block_errors': 0
                                            })

            with pytest.raises(SerialConnectionException):
                self.obj._com = None
                self.obj.read_data_callback(callback_function=func_callback,
                                            options={
                                                'timeout': 20,
                                                'max_loops': 1,
                                            })

        self.ve_sim.run_vedirect_sim_callback(
            callback=main_test,
            nb_packets=3,
            sleep=0.5
        )
