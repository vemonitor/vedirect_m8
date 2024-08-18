"""VedirectApp unittest class."""
from .serial_test_helper import SerialTestHelper
from vedirect_m8.vedirect_app import VedirectApp
from vedirect_m8.serconnect import SerialConnection
from ve_utils.utype import UType as Ut


class TestVedirectApp:
    """VedirectApp unittest class."""
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
        }

        self.obj = VedirectApp(serial_conf=conf)

    def test_read_all_packets(self):
        """Test read_all_packets method."""
        def main_test():
            """Main read_data_callback tests."""
            self.obj.flush_serial_cache()
            self.obj.read_all_packets(nb_blocks=60,
                                      options={
                                        'timeout': 1,
                                        'max_packet_errors': 3,
                                        'max_loops': 8
                                      })
            a = 2

        self.ve_sim.run_vedirect_sim_callback(
            callback=main_test,
            nb_packets=20,
            sleep=1
        )