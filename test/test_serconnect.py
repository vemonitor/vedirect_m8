"""
SerialConnection unittest class.

Use pytest package.
"""
import os
import pytest
from vedirect_m8.serconnect import SerialConnection
from vedirect_m8.serutils import SerialUtils as Ut
from vedirect_m8.exceptions import SerialConfException
from vedirect_m8.exceptions import OpenSerialVeException
from vedirect_m8.exceptions import SerialVeException

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "1.0.0"


class TestSerialConnection:

    def setup_method(self):
        """
        Setup any state tied to the execution of the given function.

        Invoked for every test function in the module.
        """
        conf = {
            'serial_port': SerialConnection.get_virtual_home_serial_port("vmodem1"),
            'baudrate': 19200,
            'timeout': 0,
            'source_name': "TestSerialConnection",
        }

        self.obj = SerialConnection(**conf)

    def test_settings(self):
        """Test configuration settings from SerialConnection constructor."""
        assert self.obj.is_settings()
        assert self.obj.get_serial_port() == SerialConnection.get_virtual_home_serial_port("vmodem1")
        assert self.obj.get_conf_key("hello") is None
        assert self.obj.get_source_name() == "TestSerialConnection"
        assert self.obj.get_timeout() == 0
        conf = {
            'serial_port': SerialConnection.get_virtual_home_serial_port("vmodem0"),
            'baudrate': 19200,
            'timeout': 0,
            'write_timeout': 0,
            'exclusive': True
        }
        assert self.obj._init_settings(conf)
        assert self.obj.is_settings()
        assert self.obj.get_conf_key("exclusive") is True
        assert self.obj.is_serial_port_exists(
            SerialConnection.get_virtual_home_serial_port("vmodem1")
        )

    def test_set_serial_conf(self):
        """Test set_serial_conf method."""
        conf = {
            'serial_port': SerialConnection.get_virtual_home_serial_port("vmodem0"),
            'baudrate': 19200,
            'timeout': 0,
            'write_timeout': 0,
            'exclusive': True
        }
        result = self.obj._set_serial_conf(conf)
        assert Ut.is_dict(result, eq=5)
        # test bad conf
        conf.update({'serial_port': 32})
        result = self.obj._set_serial_conf(conf)
        assert result is None

    def test_connect(self):
        """Test connect method."""
        assert self.obj.connect()
        assert self.obj._is_serial_ready()
        assert self.obj.is_ready()
        assert self.obj.flush_serial_cache()
        # test valid but unavailable port.
        with pytest.raises(SerialVeException):
            self.obj.connect(
                conf={'serial_port': "/dev/ttyUSB99"}
            )
        # test valid serial device configuration,
        # Serial is initialized but port is not open.
        with pytest.raises(OpenSerialVeException):
            self.obj.connect(
                conf={'serial_port': None}
            )
        # test invalid configuration parameter
        with pytest.raises(SerialConfException):
            self.obj._conf.pop('baudrate')
            self.obj.connect(
                conf={'exclusive': True},
                set_default=False
            )

    def test_get_serial_ports_list(self):
        """Test get_serial_ports_list method."""
        serial_ports = self.obj.get_serial_ports_list()
        assert Ut.is_list(serial_ports) and len(serial_ports) >= 2

    def test_get_unix_virtual_serial_ports_list(self):
        """Test get_unix_virtual_serial_ports_list method."""
        serial_ports = self.obj.get_unix_virtual_serial_ports_list()
        assert Ut.is_list(serial_ports) and len(serial_ports) >= 2

    def test_serialize(self):
        """Test serialize method."""
        obj = self.obj.serialize()
        assert Ut.is_dict(obj) and len(obj) == 5
        assert obj.get('source_name') == 'TestSerialConnection'

    @staticmethod
    def test_get_virtual_ports_paths():
        """Test get_virtual_ports_paths method."""
        paths = SerialConnection._get_virtual_ports_paths()
        assert Ut.is_list(paths) and len(paths) == 1
        assert paths[0] == os.path.expanduser('~')

    # noinspection PyTypeChecker
    @staticmethod
    def test_get_virtual_home_serial_port():
        """Test get_virtual_home_serial_port method."""
        v_ports = [
            SerialConnection.get_virtual_home_serial_port("vmodem999"),
            SerialConnection.get_virtual_home_serial_port("vmodem0"),
            SerialConnection.get_virtual_home_serial_port("vmodem"),
            SerialConnection.get_virtual_home_serial_port("vmodem9999"),
            SerialConnection.get_virtual_home_serial_port("z9999"),
            SerialConnection.get_virtual_home_serial_port(1),
            SerialConnection.get_virtual_home_serial_port(dict())
        ]
        tests = [x for x in v_ports if x is not None]
        assert len(tests) == 2

    # noinspection PyTypeChecker
    @staticmethod
    def test_is_virtual_serial_port():
        """Test is_virtual_serial_port method."""
        virtual_ports = [
            SerialConnection.get_virtual_home_serial_port("vmodem999"),
            SerialConnection.get_virtual_home_serial_port("vmodem0"),
            SerialConnection.get_virtual_home_serial_port("vmodem"),
            SerialConnection.get_virtual_home_serial_port("vmodem9999"),
            SerialConnection.get_virtual_home_serial_port("z9999"),
            SerialConnection.get_virtual_home_serial_port(1),
            SerialConnection.get_virtual_home_serial_port(dict())
        ]
        tests = [x for x in virtual_ports if SerialConnection._is_virtual_serial_port(x)]
        assert len(tests) == 2

    @staticmethod
    def test_split_serial_port():
        """Test split_serial_port method."""
        ports = [
            "r",
            "/r",
            "a/b/c/r",
            "/r/",
            "\\r"
        ]
        tests = [x for x in ports if SerialConnection._split_serial_port(x)[0] == 'r']
        assert len(tests) == 3

    @staticmethod
    def test_is_serial_port_exists():
        """Test is_serial_port_exists method."""
        ports = [
            SerialConnection.get_virtual_home_serial_port("vmodem0"),
            SerialConnection.get_virtual_home_serial_port("vmodem1")
        ]
        tests = [x for x in ports if SerialConnection.is_serial_port_exists(x)]
        assert len(tests) == 2

    @staticmethod
    def test_is_serial_port():
        """Test is_serial_port method."""
        ports = [
            SerialConnection.get_virtual_home_serial_port("vmodem0"),
            SerialConnection.get_virtual_home_serial_port("vmodem1"),
            "/dev/ttyUSB1",
            "/dev/ttyACM1",
            "/dev/vmodem0",
            "/dev/vmodem1",
            "/dev/COM1",
            "COM1",
            "COM1999",  # false
            "/dev/USB1",  # false
            "/dev/ACM1",  # false
            "/dev/1",  # false
        ]
        tests = [x for x in ports if SerialConnection.is_serial_port(x)]
        assert len(tests) == 8

    @staticmethod
    def test_is_serial_path():
        """Test is_serial_path method."""
        paths = [
            os.path.expanduser('~'),  # true
            "/dev",  # true
            "/dev/pts/",
            "/var",
            "/var/run/",
            1,
            1.1,
            ("COM1999", 1),
            dict(),
            None
        ]
        tests = [x for x in paths if SerialConnection.is_serial_path(x)]
        assert len(tests) == 2

    @staticmethod
    def test_is_baud():
        """Test is_baud method."""
        bauds = [
            110, 300, 600, 1200,
            2400, 4800, 9600, 14400,
            19200, 38400, 57600, 115200,
            128000, 256000, 0, 1, 10, 302,
            2500, 4900, "300"
        ]
        tests = [x for x in bauds if SerialConnection.is_baud(x)]
        assert len(tests) == 14

    @staticmethod
    def test_is_timeout():
        """Test is_timeout method."""
        timeouts = [
            1, 5, 10, 0.1, 0, None,
            "2400"
        ]
        tests = [x for x in timeouts if SerialConnection.is_timeout(x)]
        assert len(tests) == 6

    @staticmethod
    def test_set_serial_conf():
        """Test set_serial_conf method."""
        data = {
            "serial_port": "/dev/ttyUSB0",
            "baudrate": 19200,
            "timeout": 6,
            "write_timeout": 4,
            "exclusive": True,
            "source_name": "TestSerialConnection"
        }
        result = SerialConnection.set_serial_conf(data)
        assert Ut.is_dict(SerialConnection.get_default_serial_conf(), not_null=True)
        assert SerialConnection.is_serial_conf(result)
        assert result.get('serial_port') == "/dev/ttyUSB0"
        assert result.get('baudrate') == 19200
        assert result.get('timeout') == 6
        assert result.get('write_timeout') == 4
        assert result.get('exclusive') is True
        assert result.get('source_name') == "TestSerialConnection"
        data.update({"serial_port": "/dev/ttyUSB3"})
        result = SerialConnection.set_serial_conf(data, result)
        assert result.get('serial_port') == "/dev/ttyUSB3"
