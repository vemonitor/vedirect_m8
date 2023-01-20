"""Helpers unittest class."""
import time

from ve_utils.utype import UType as Ut
from vedirect_m8.helpers import TimeoutHelper
from vedirect_m8.helpers import CounterHelper
from vedirect_m8.helpers import CountersHelper
from vedirect_m8.helpers import MAX_COUNTER_VALUE


class TestTimeoutHelper:
    """TimeoutHelper unittest class."""
    def setup_method(self):
        """
        Setup any state tied to the execution of the given function.

        Invoked for every test function in the module.
        """

        self.obj = TimeoutHelper()

    def test_timeout(self):
        """Test timeout methods."""
        time.sleep(0.5)
        self.obj.set_now()
        assert self.obj.get_elapsed() > 0
        assert not self.obj.is_timeout(timeout=None)
        assert not self.obj.is_timeout(timeout=0)
        assert self.obj.is_timeout(timeout=0.4)
        self.obj.set_start()
        assert self.obj.start == self.obj.now
        time.sleep(0.5)
        self.obj.set_now()

        def my_callback(elapsed, timeout):
            """Timeout callback test"""
            assert elapsed > 0
            assert timeout is not None
            assert 0 < timeout < elapsed

        self.obj.is_timeout_callback(
            timeout=0.1,
            callback=my_callback
        )

        self.obj.is_timeout_callback(
            timeout=50,
            callback=my_callback
        )


class TestCounterHelper:
    """CounterHelper unittest class."""
    def setup_method(self):
        """
        Setup any state tied to the execution of the given function.

        Invoked for every test function in the module.
        """

        self.obj = CounterHelper()

    def test_counter(self):
        """Test timeout methods."""
        assert self.obj.counter == 0
        self.obj.add()

        assert self.obj.counter == 1
        assert self.obj.is_max(1)
        assert not self.obj.is_max(2)
        self.obj.add()
        assert self.obj.counter == 2
        assert self.obj.is_min(3)
        assert not self.obj.is_min(2)
        assert not self.obj.is_min(1)
        self.obj.reset()
        assert self.obj.counter == 0
        self.obj.counter = MAX_COUNTER_VALUE
        self.obj.add()
        assert self.obj.counter == 0
        assert not self.obj.is_max(0)
        assert not self.obj.is_max(None)
        assert not self.obj.is_max(-1)
        assert not self.obj.is_max("-1")


class TestCountersHelper:
    """CountersHelper unittest class."""
    def setup_method(self):
        """
        Setup any state tied to the execution of the given function.

        Invoked for every test function in the module.
        """

        self.obj = CountersHelper()

    def test_counter(self):
        """Test timeout methods."""
        assert not self.obj.has_counter()
        assert self.obj.pop_counter_key("hello") is None
        self.obj.add_counter_key("t1")
        assert self.obj.has_counter_key("t1")
        assert self.obj.get_key_value("t1") == 0
        self.obj.add_to_key("t1")
        self.obj.add_to_key("t1")
        assert self.obj.get_key_value("t1") == 2
        assert self.obj.is_max_key("t1", 2)
        assert not self.obj.is_max_key("t1", 3)
        assert self.obj.is_min_key("t1", 3)
        assert not self.obj.is_min_key("t1", 1)

        my_counter = self.obj.get_counter_key("t1")
        assert my_counter == self.obj.pop_counter_key("t1")

        self.obj.add_counter_key("t1")
        assert self.obj.reset_key("t1")
        assert self.obj.reset_key("bad") is False


