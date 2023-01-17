"""Serial test helper class."""
import time
from threading import Thread
from vedirect_m8.vedirectsim import Vedirectsim
from ve_utils.utype import UType as Ut
from ve_utils.usys import USys


class SerialTestHelper:
    """Serial test helper class."""
    def __init__(self,
                 serial_port: str,
                 data_source: str or None = None
                 ):
        self.ve_sim = Vedirectsim(serialport=serial_port)
        self.thread = None

    def is_active(self):
        """Test if ve simulator is active."""
        return True

    def has_thread(self):
        """Test if instance has valid thread."""
        return isinstance(self.thread, Thread)

    def has_active_thread(self):
        """Test if instance has active thread."""
        return self.has_thread() and self.thread.is_alive()

    def join(self):
        """Join the thread if is active."""
        if self.has_active_thread():
            self.thread.join()

    def run_vedirect_sim_callback(self,
                                  callback,
                                  nb_packets: int = 1,
                                  sleep: int or float = 0.5
                                  ):
        """Run vedirect simulator before the callback function and join thread."""
        self.thread = self.run_vedirect_sim(nb_packets)
        callback()
        self.join()

    def run_vedirect_sim(self,
                         nb_packets: int = 1,
                         sleep: int or float = 0.5
                         ) -> Thread:
        """Run vedirect simulator to send packet in dummy ports."""
        if self.is_active():
            sleep = Ut.get_float(sleep, 0.5)
            nb_packets = Ut.get_int(nb_packets, 1)
            self.thread = Thread(
                target=self.ve_sim.run,
                kwargs={"max_writes": nb_packets},
                daemon=True
            )
            self.thread.start()
            if sleep > 0:
                time.sleep(sleep)
