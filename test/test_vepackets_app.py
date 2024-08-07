"""VePackets unittest class."""
import time
import pytest
from ve_utils.utype import UType as Ut
from vedirect_m8.serconnect import SerialConnection
from vedirect_m8.vepackets_app import VePacketsApp
from vedirect_m8.exceptions import SerialConnectionException


@pytest.fixture(name="helper_manager", scope="class")
def helper_manager_fixture():
    """Json Schema test manager fixture"""
    class HelperManager:
        """Json Helper test manager fixture Class"""
        def __init__(self):
            self.obj = None

        def init_vedirect_app(self):
            """Init Object"""
            conf = {
                'serial_port': SerialConnection.get_virtual_home_serial_port(
                    "vmodem1"
                ),
                'baud': 19200,
                'timeout': 0
            }
            serial_test = {
                'PIDTest': {
                    "typeTest": "value",
                    "key": "PID",
                    "value": "0x203"
                }
            }

            self.obj = VePacketsApp(
                serial_conf=conf,
                serial_test=serial_test,
                source_name="PyTest",
                auto_start=True,
                wait_connection=True,
                wait_timeout=5
            )

        def read_serial_data(self):
            """Read Serial Data"""
            assert self.obj.try_serial_connection(
                "PyTest"
            ) is True
            assert self.obj.has_data_cache() is False
            result = self.obj.read_data(
                caller_name="PyTest",
                timeout=2
            )
            assert Ut.is_dict(result, eq=26)
            assert self.obj.has_data_cache() is True

    return HelperManager()


class TestVePacketsApp:
    """VePacketsApp unittest class."""

    def test_settings(self, helper_manager):
        """Test configuration settings from VedirectController constructor."""
        helper_manager.init_vedirect_app()

        assert helper_manager.obj.is_serial_ready()
        assert helper_manager.obj.is_ready()
        assert helper_manager.obj.has_serial_com()
        assert helper_manager.obj.connect_to_serial()
        assert helper_manager.obj.has_serial_test()
        assert helper_manager.obj.get_wait_timeout()
        helper_manager.obj._com = None
        with pytest.raises(SerialConnectionException):
            helper_manager.obj.connect_to_serial()

    def test_has_data_cache(self, helper_manager):
        """Test has_items method """
        helper_manager.init_vedirect_app()
        helper_manager.read_serial_data()

    def test_get_time_cache(self, helper_manager):
        """Test get_time_cache method """
        helper_manager.init_vedirect_app()
        helper_manager.read_serial_data()

        time_cache = helper_manager.obj.get_time_cache()
        assert Ut.is_float(time_cache, not_null=True)

    def test_get_data_cache(self, helper_manager):
        """Test get_data_cache method """
        helper_manager.init_vedirect_app()
        helper_manager.read_serial_data()

        result = helper_manager.obj.get_data_cache()
        assert Ut.is_dict(result, eq=26)

    def test_set_min_interval(self, helper_manager):
        """Test set_min_interval method """
        helper_manager.init_vedirect_app()

        assert helper_manager.obj.set_min_interval(
            value=1
        ) == 1

        assert helper_manager.obj.set_min_interval(
            value=0
        ) == 1

        assert helper_manager.obj.set_min_interval(
            value=-1
        ) == 1

        assert helper_manager.obj.set_min_interval(
            value=99
        ) == 99

    def test_reset_data_cache(self, helper_manager):
        """Test reset_data_cache method """
        helper_manager.init_vedirect_app()
        helper_manager.read_serial_data()

        result = helper_manager.obj.get_data_cache()
        assert Ut.is_dict(result, eq=26)
        helper_manager.obj.reset_data_cache()

        result = helper_manager.obj.get_data_cache()
        assert result is None

    def test_set_data_cache(self, helper_manager):
        """Test set_data_cache method """
        helper_manager.init_vedirect_app()
        helper_manager.read_serial_data()

        assert helper_manager.obj.has_data_cache() is True
        time_cache_start = helper_manager.obj.get_time_cache()
        result = helper_manager.obj.set_data_cache(
            data={
                'V': 15,
                'I': 14
            }
        )
        assert result is True
        time_cache_end = helper_manager.obj.get_time_cache()
        assert time_cache_start != time_cache_end

        result = helper_manager.obj.get_data_cache()
        assert Ut.is_dict(result, eq=2)

    def test_update_data_cache(self, helper_manager):
        """Test update_data_cache method """
        helper_manager.init_vedirect_app()
        helper_manager.read_serial_data()

        time_cache_start = helper_manager.obj.get_time_cache()
        assert helper_manager.obj.has_data_cache() is True
        result = helper_manager.obj.update_data_cache(
            data={
                'V': 15,
                'I': 14
            }
        )
        assert result is True
        time_cache_end = helper_manager.obj.get_time_cache()
        assert time_cache_start == time_cache_end

        result = helper_manager.obj.get_data_cache()
        assert Ut.is_dict(result, eq=26)

    def test_search_available_serial_port(self, helper_manager):
        """Test search_available_serial_port method """
        helper_manager.init_vedirect_app()

        assert helper_manager.obj.search_available_serial_port(
            caller_name="PyTest"
        ) is True

        # Change to bad serial port and close serial connexion
        helper_manager.obj._com._serial_port = "/dev/vmodem8"
        helper_manager.obj._com.ser.close()
        # search and connect to valid serial port
        assert helper_manager.obj.search_available_serial_port(
            caller_name="PyTest"
        ) is True

    def test_try_serial_connection(self, helper_manager):
        """Test try_serial_connection method """
        helper_manager.init_vedirect_app()
        helper_manager.read_serial_data()

        # Test try_serial_connection unlocked serial
        result = helper_manager.obj.try_serial_connection(
            caller_name="PyTest"
        )
        assert result is True

        # Test try_serial_connection with bad serial port
        # Search and connect to new valid serial port
        helper_manager.obj._com._serial_port = "/dev/vmodem8"
        helper_manager.obj._com.ser.close()
        result = helper_manager.obj.try_serial_connection(
            caller_name="PyTest"
        )
        assert result is True

    def test_read_serial_data(self, helper_manager):
        """Test read_serial_data method """
        helper_manager.init_vedirect_app()
        helper_manager.read_serial_data()
        time.sleep(1)
        result = helper_manager.obj.read_serial_data(
            caller_name="PyTest",
            timeout=3
        )
        assert Ut.is_dict(result, not_null=True, max_items=19)
        # Try SerialVeTimeoutException
        result = helper_manager.obj.read_serial_data(
            caller_name="PyTest",
            timeout=0.0001
        )
        assert result is None
        # Try search new valid serial port
        helper_manager.obj._com._serial_port = "/dev/vmodem8"
        helper_manager.obj._com.ser.close()
        result = helper_manager.obj.read_serial_data(
            caller_name="PyTest",
            timeout=0.0001
        )
        assert result is None

    def test_get_all_packets(self, helper_manager):
        """Test get_all_packets method """
        helper_manager.init_vedirect_app()
        helper_manager.read_serial_data()

        helper_manager.obj.reset_data_cache()
        assert helper_manager.obj.has_data_cache() is False
        result = helper_manager.obj.get_all_packets(
            caller_name="PyTest",
            timeout=3
        )
        assert result is True
        assert helper_manager.obj.has_data_cache() is True

    def test_is_time_to_read_serial(self, helper_manager):
        """Test is_time_to_read_serial method """
        helper_manager.init_vedirect_app()
        helper_manager.read_serial_data()

        is_time_cache = helper_manager.obj.is_time_to_read_serial(
            now=time.time()
        )
        assert is_time_cache is False

        helper_manager.obj._data_cache = (1723021080, {'a': 1})
        is_time_cache = helper_manager.obj.is_time_to_read_serial(
            now=1723021164
        )
        assert is_time_cache is True

        helper_manager.obj._data_cache = (1723021080, {'a': 1})
        is_time_cache = helper_manager.obj.is_time_to_read_serial(
            now=1723021080
        )
        assert is_time_cache is False

        helper_manager.obj._data_cache = (1723021080, {'a': 1})
        is_time_cache = helper_manager.obj.is_time_to_read_serial(
            now=1723021081
        )
        assert is_time_cache is False

        helper_manager.obj._data_cache = (1723021080, {'a': 1})
        is_time_cache = helper_manager.obj.is_time_to_read_serial(
            now=1723021082
        )
        assert is_time_cache is True

    def test_read_data(self, helper_manager):
        """Test read_data method """
        helper_manager.init_vedirect_app()
        helper_manager.read_serial_data()

        # get data from serial
        time.sleep(1)
        helper_manager.obj.reset_data_cache()
        assert helper_manager.obj.has_data_cache() is False
        result = helper_manager.obj.read_data(
            caller_name="PyTest",
            timeout=3
        )
        assert Ut.is_dict(result, not_null=True, eq=26)
        # get data from cache
        # because two read_data calls executed
        # in less than 1 second
        result2 = helper_manager.obj.read_data(
            caller_name="PyTest",
            timeout=3
        )
        assert Ut.is_dict(result2, not_null=True, eq=26)
        assert result == result2
