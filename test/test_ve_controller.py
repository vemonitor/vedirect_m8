"""VedirectController unittest class."""
import pytest
from ve_utils.utype import UType as Ut
from vedirect_m8.ve_controller import VedirectController
from vedirect_m8.serconnect import SerialConnection
from vedirect_m8.exceptions import SettingInvalidException
from vedirect_m8.exceptions import ReadTimeoutException
from vedirect_m8.exceptions import SerialConnectionException
from vedirect_m8.exceptions import SerialVeException
from vedirect_m8.exceptions import VedirectException
from .serial_test_helper import SerialTestHelper


class TestVedirectController:
    """VedirectController unittest class."""
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
            'source_name': "TestVedirectController"
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
        assert self.obj._helper.has_free_block()
        assert self.obj._helper.set_max_packet_blocks(2)
        assert self.obj._helper.set_max_packet_blocks(None)
        with pytest.raises(SettingInvalidException):
            self.obj._helper.set_max_packet_blocks("error")

    def test_is_serial_com(self):
        """Test is_serial_com method."""
        assert VedirectController.is_serial_com(self.obj._com)
        assert not VedirectController.is_serial_com({})
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
            self.obj.init_serial_test(serial_test=[])

        with pytest.raises(SettingInvalidException):
            self.obj.init_serial_test(serial_test={})

        with pytest.raises(SettingInvalidException):
            self.obj.init_serial_test(serial_test={
                'PID_test': {
                    "typeTest": "value",
                    "key": "PID"
                }
            })

    def test_init_settings(self):
        """Test init_settings method."""
        good_serial_port = self.obj._com.get_serial_port()

        def good_port_test():
            """Test init_settings with good serial_port."""

            assert self.obj.init_settings(
                {'serial_port': good_serial_port},
                {
                    'wait_connection': True,
                    'wait_timeout': 20
                }
            )

        self.ve_sim.run_vedirect_sim_callback(
            callback=good_port_test,
            nb_packets=2,
            sleep=0.5
        )

        # test with bad serial port format
        # now on bad serial port scan, test and connect valid port.
        # Don't raise exception if valid port available.

        def bad_port_test():
            """Test init_settings with bad serial_port."""
            with pytest.raises(SerialConnectionException):
                self.obj.init_settings(
                    {"serial_port": "/etc/bad_port"}
                )

        self.ve_sim.run_vedirect_sim_callback(
            callback=bad_port_test,
            nb_packets=20,
            sleep=0.5
        )

        # test with bad serial port connection
        # now on bad serial port scan, test and connect valid port.
        # Don't raise exception if valid port available.

        def bad_port_test():
            """Test init_settings with bad serial_port."""
            assert self.obj.init_settings(
                {"serial_port": SerialConnection.get_virtual_home_serial_port("vmodem255")}
            )
            # now serial port is same as start
            assert good_serial_port == self.obj._com.get_serial_port()

            with pytest.raises(VedirectException):
                self.obj._ser_test = None
                self.obj.set_wait_timeout(2)
                self.obj.init_settings(
                    {'serial_port': SerialConnection.get_virtual_home_serial_port("vmodem255")}
                )

        self.ve_sim.run_vedirect_sim_callback(
            callback=bad_port_test,
            nb_packets=40,
            sleep=0.5
        )

    def test_read_data_to_test(self):
        """Test read_data_to_test method."""

        def main_test():
            """Main read_data_to_test tests."""
            assert Ut.is_dict(self.obj.read_data_to_test(), not_null=True)

        self.ve_sim.run_vedirect_sim_callback(
            callback=main_test,
            nb_packets=2,
            sleep=0.5
        )

    def test_test_serial_port(self):
        """Test test_serial_port method."""

        def main_test():
            """Main test_serial_port tests."""
            assert self.obj.test_serial_port(
                port=self.obj.get_serial_port()
            )

        self.ve_sim.run_vedirect_sim_callback(
            callback=main_test,
            nb_packets=20,
            sleep=0.5
        )

        def bad_port_test():
            """Test test_serial_port with bad serial_port."""
            assert not self.obj.test_serial_port(
                port=32
            )

        self.ve_sim.run_vedirect_sim_callback(
            callback=bad_port_test,
            nb_packets=1,
            sleep=0.5
        )

        def bad_port_test():
            """Test test_serial_port with bad serial_port."""
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

        self.ve_sim.run_vedirect_sim_callback(
            callback=bad_port_test,
            nb_packets=20,
            sleep=0.5
        )

        def bad_port_test():
            """Test test_serial_port with bad serial_port."""
            with pytest.raises(SerialConnectionException):
                self.obj.test_serial_port(
                    port=SerialConnection.get_virtual_home_serial_port("vmodem255")
                )

        self.ve_sim.run_vedirect_sim_callback(
            callback=bad_port_test,
            nb_packets=20,
            sleep=0.5
        )

    def test_test_serial_ports(self):
        """Test test_serial_ports method."""
        ports = self.obj._com.get_serial_ports_list()

        def main_test():
            """Main test_serial_ports tests."""
            assert self.obj.test_serial_ports(ports)

        self.ve_sim.run_vedirect_sim_callback(
            callback=main_test,
            nb_packets=40,
            sleep=0.1
        )

        def bad_port_test():
            """Test init_settings with bad serial_port."""
            self.obj._ser_test = None
            with pytest.raises(SerialConnectionException):
                self.obj.test_serial_ports(ports)

        self.ve_sim.run_vedirect_sim_callback(
            callback=bad_port_test,
            nb_packets=20,
            sleep=0.5
        )

    def test_wait_or_search_serial_connection(self):
        """Test wait_or_search_serial_connection method."""

        def main_test():
            """Main wait_or_search_serial_connection tests."""
            assert self.obj.wait_or_search_serial_connection(
                timeout=20,
                sleep_time=0.01
            )

        self.ve_sim.run_vedirect_sim_callback(
            callback=main_test,
            nb_packets=20,
            sleep=0.5
        )

        def error_test():
            """Test wait_or_search_serial_connection with bad serial_port."""
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
                    timeout=0.0000000000001,
                    sleep_time=-2
                )

        self.ve_sim.run_vedirect_sim_callback(
            callback=error_test,
            nb_packets=20,
            sleep=0.5
        )

    def test_search_serial_port(self):
        """Test search_serial_port method."""

        def main_test():
            """Main test_search_serial_port tests."""
            try:
                self.obj.init_serial_connection(
                    {
                        'serial_port': SerialConnection.get_virtual_home_serial_port("vmodem255"),
                        'source_name': "TestVedirectController"
                    }
                )
            except SerialVeException:
                test_port = False
                for i in range(10):
                    if self.obj.search_serial_port():
                        test_port = True
                        print("\n search_serial_port: serial port retrieved at %s" % i)
                        break
                assert test_port

        self.ve_sim.run_vedirect_sim_callback(
            callback=main_test,
            nb_packets=40,
            sleep=0.5
        )

        def error_test():
            """Test test_search_serial_port with bad serial_port."""
            self.obj._ser_test = None
            assert not self.obj.search_serial_port()

        self.ve_sim.run_vedirect_sim_callback(
            callback=error_test,
            nb_packets=20,
            sleep=0.5
        )

    def test_init_data_read(self):
        """Test init_data_read method."""

        def main_test():
            """Main read_data_single tests."""
            assert Ut.is_dict(self.obj.read_data_single(), not_null=True)
            # init_data_read() is now called in read_data_single()
            assert not Ut.is_dict(self.obj._helper.dict, not_null=True)

        self.ve_sim.run_vedirect_sim_callback(
            callback=main_test,
            nb_packets=2,
            sleep=0.5
        )

    def test_read_data_single(self):
        """Test read_data_single method."""

        def main_test():
            """Main read_data_single tests."""
            assert Ut.is_dict(self.obj.read_data_single(), not_null=True)
            # init_data_read() is now called in read_data_single()
            assert not Ut.is_dict(self.obj._helper.dict, not_null=True)

        self.ve_sim.run_vedirect_sim_callback(
            callback=main_test,
            nb_packets=2,
            sleep=0.5
        )

    def test_read_data_callback(self):
        """Test read_data_callback method."""

        def func_callback(data: dict or None):
            """Callback function."""
            assert Ut.is_dict(data, not_null=True)

        def func_bad_callback(data: dict or None):
            """Callback function."""
            assert data is None

        def main_test():
            """Main read_data_single tests."""
            self.obj.set_wait_timeout(10)
            self.obj.read_data_callback(callback_function=func_callback,
                                        timeout=20,
                                        max_loops=1
                                        )
            with pytest.raises(ReadTimeoutException):
                self.obj.set_wait_timeout(10)
                self.obj.read_data_callback(callback_function=func_callback,
                                            timeout=0.000001,
                                            max_loops=1
                                            )
            self.obj._com = None
            self.obj.read_data_callback(callback_function=func_bad_callback,
                                        timeout=20,
                                        max_loops=1
                                        )

        self.ve_sim.run_vedirect_sim_callback(
            callback=main_test,
            nb_packets=1,
            sleep=0.5
        )
