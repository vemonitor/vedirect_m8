"""VedirectSim unittest class."""
import pytest
import serial
from ve_utils.utime import PerfStats
from vedirect_m8.vedirectsim import Vedirectsim
from vedirect_m8.serconnect import SerialConnection


@pytest.fixture(name="helper_manager", scope="class")
def helper_manager_fixture():
    """Json Schema test manager fixture"""
    class HelperManager:
        """Json Helper test manager fixture Class"""

        def __init__(self):
            self.init_object()

        def init_object(self):
            """Init Object"""
            serial_port = SerialConnection.get_virtual_home_serial_port(
                "vmodem0"
            )
            device = "bmv702"

            self.obj = Vedirectsim(serial_port, device)

    return HelperManager()


class TestVeDirectSim:
    """VedirectSim unittest class."""

    def test_is_ready(self, helper_manager):
        """Test is_ready method."""
        assert helper_manager.obj.is_ready()

    def test_has_serial_connection(self, helper_manager):
        """Test has_serial_connection method."""
        serial_port = SerialConnection.get_virtual_home_serial_port(
            "vmodem0"
        )
        helper_manager.obj.serial_port = serial_port
        assert helper_manager.obj.serial_connect() is True
        assert helper_manager.obj.has_serial_connection() is True
        with pytest.raises(serial.SerialException):
            helper_manager.obj.ser = None
            helper_manager.obj.has_serial_connection()

    def test_serial_connect(self, helper_manager):
        """Test serial_connect method."""
        assert helper_manager.obj.serial_connect()
        with pytest.raises((
                serial.SerialException,
                serial.SerialTimeoutException)):
            helper_manager.obj.serialport = "bad_port"
            helper_manager.obj.serial_connect()

    def test_get_dump_file_path(self, helper_manager):
        """Test get_dump_file_path method."""
        helper_manager.init_object()
        serial_port = SerialConnection.get_virtual_home_serial_port(
            "vmodem0"
        )
        helper_manager.obj.serial_port = serial_port
        assert helper_manager.obj.serial_connect()
        with pytest.raises(ValueError):
            helper_manager.obj.device = "bad_device"
            helper_manager.obj.get_dump_file_path()

    def test_set_device_and_device_path(self, helper_manager):
        """Test set_device and set_dump_file_path methods."""
        serial_port = SerialConnection.get_virtual_home_serial_port(
            "vmodem0"
        )
        helper_manager.obj.serial_port = serial_port
        assert helper_manager.obj.set_device("bmv702")
        assert helper_manager.obj.set_dump_file_path()
        assert helper_manager.obj.set_device("bluesolar_1.23")
        assert helper_manager.obj.set_dump_file_path()
        assert helper_manager.obj.set_device("smartsolar_1.39")
        assert helper_manager.obj.set_dump_file_path()
        assert not helper_manager.obj.set_device("hello")
        assert not helper_manager.obj.set_dump_file_path()

    def test_set_device_settings(self, helper_manager):
        """Test set_device_settings method."""
        assert helper_manager.obj.set_device_settings("bmv702")
        assert helper_manager.obj.set_device_settings("bluesolar_1.23")
        assert helper_manager.obj.set_device_settings("smartsolar_1.39")

        with pytest.raises(ValueError):
            helper_manager.obj.set_device_settings("hello")
            helper_manager.obj.set_device_settings(
                SerialConnection.get_virtual_home_serial_port("world.bat")
            )

    def test_send_packet(self, helper_manager):
        """Test send_packet method."""
        helper_manager.init_object()
        helper_manager.obj.perf = PerfStats()
        helper_manager.obj.perf.start_perf_key("writes")
        helper_manager.obj.dict = dict()
        helper_manager.obj.ser.write_timeout = 3
        for x in range(18):
            helper_manager.obj.dict.update({f"{x}Key": f"{x}Value"})
        assert helper_manager.obj.send_packet() is True

        helper_manager.obj.dict = dict()
        helper_manager.obj.ser.write_timeout = 3
        for x in range(1):
            helper_manager.obj.dict.update({f"{x}Key": f"{x}Value"})
        assert helper_manager.obj.send_packet() is True

        helper_manager.obj.dict = dict()
        for x in range(150):
            helper_manager.obj.dict.update({f"{x}Key": f"{x}Value"})
        helper_manager.obj.ser.write_timeout = 0.00000002
        assert helper_manager.obj.send_packet() is False

        helper_manager.obj.ser.write_timeout = 3
        helper_manager.obj.ser.close()
        with pytest.raises(serial.serialutil.PortNotOpenError):
            helper_manager.obj.send_packet()

    def test_process_data(self, helper_manager):
        """Test process_data method."""
        helper_manager.obj.dict = {}
        for x in range(16):
            helper_manager.obj.dict.update({f"{x}Key": f"{x}Value"})
        assert helper_manager.obj.process_data(
            key="ZKey", value="Ax125") is True

    def test_read_dump_file_line(self, helper_manager):
        """Test read_dump_file_lines method."""
        helper_manager.init_object()
        assert helper_manager.obj.read_dump_file_lines(max_writes=1)
        helper_manager.obj.set_device_settings("bluesolar_1.23")
        assert helper_manager.obj.read_dump_file_lines(max_writes=1)
        helper_manager.obj.set_device_settings("smartsolar_1.39")
        assert helper_manager.obj.read_dump_file_lines(max_writes=1)

    def test_run(self, helper_manager):
        """Test run method."""
        helper_manager.init_object()
        assert helper_manager.obj.run(max_writes=1)
        helper_manager.obj.set_device_settings("bluesolar_1.23")
        assert helper_manager.obj.run(max_writes=1)
        helper_manager.obj.set_device_settings("smartsolar_1.39")
        assert helper_manager.obj.run(max_writes=1)

        with pytest.raises(ValueError):
            helper_manager.obj.ser = None
            helper_manager.obj.run()
