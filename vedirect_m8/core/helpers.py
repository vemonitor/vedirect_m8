"""Helpers class"""
import time
from ve_utils.utype import UType as Ut

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "1.0.0"


MAX_COUNTER_VALUE = 1000000000


class DataDictHelper:
    """TimeoutHelper class"""

    def __init__(self):
        self.data = {}


class TimeoutHelper:
    """TimeoutHelper class"""

    def __init__(self):
        self.now = time.time()
        self.start = time.time()

    def set_now(self):
        """Set time now"""
        self.now = time.time()

    def set_start(self):
        """Set time start"""
        self.start = self.now = time.time()

    def get_elapsed(self):
        """Get time interval between start and now"""
        return self.now - self.start

    def is_timeout(self, timeout: int or float or None):
        """Test if is timeout"""
        result = False
        if timeout is not None\
                and 0 < timeout < self.get_elapsed():
            result = True
        return result

    def is_timeout_callback(self,
                            timeout: int or float or None,
                            callback
                            ):
        """Test if is timeout"""
        elapsed = self.get_elapsed()
        if timeout is not None \
                and 0 < timeout < elapsed:
            callback(elapsed, timeout)


class CounterHelper:
    """CounterHelper class"""
    def __init__(self):
        self.counter = 0
        self.total_time = 0

    def get_value(self):
        """Get counter value"""
        return self.counter

    def get_moy_time(self):
        """Get moy time"""
        result = None
        if self.total_time > 0 and self.counter > 0:
            result = self.total_time / self.counter
        return result

    def set_moy_time(self, start_time: float or int = 0):
        """Get moy time"""
        result = None
        moy = CounterHelper.get_elapsed(start_time)
        if Ut.is_float(moy, not_null=True):
            self.total_time += moy
            result = self.total_time / self.counter
        return result

    def set_timer(self,
                  timer_active: bool = False,
                  start_time: float or int = 0
                  ):
        """Set timer"""
        if Ut.str_to_bool(timer_active):
            self.set_moy_time(start_time)

    def save_timer(self,
                   timer_active: bool = False,
                   start_time: float or int = 0
                   ):
        """Save timer"""
        if Ut.str_to_bool(timer_active):
            moy = CounterHelper.get_elapsed(start_time)
            if Ut.is_float(moy, not_null=True):
                self.total_time = moy / self.counter + 1

    @staticmethod
    def get_elapsed(start_time: float or int = 0):
        """Get elapsed time"""
        result = None
        if Ut.is_float(start_time, not_null=True):
            result = time.time() - start_time
        return result

    def add(self,
            timer_active: bool = False,
            start_time: float or int = 0
            ):
        """Add counter"""
        if self.counter < MAX_COUNTER_VALUE:
            self.counter = self.counter + 1
            # self.set_timer(timer_active, start_time)
        else:
            # self.save_timer(timer_active, start_time)
            self.counter = 1

    def reset_timer(self):
        """Reset the timer"""
        self.total_time = 0

    def reset(self):
        """Reset all properties"""
        self.counter = 0
        self.reset_timer()

    def is_max(self, max_counter: int or None):
        """Is counter max"""
        return Ut.is_int(max_counter) \
            and 0 < max_counter <= self.counter

    def is_min(self, min_counter: int or None):
        """Is counter min"""
        return Ut.is_int(min_counter, positive=True) \
            and 0 <= self.counter < min_counter


class CountersHelper:
    """CountersHelper class"""
    def __init__(self):
        self.counters = {}

    def has_counter(self):
        """Test if instance has perf property."""
        return Ut.is_dict(self.counters, not_null=True)

    def has_counter_key(self, key: str):
        """Test if instance has perf property."""
        return self.has_counter()\
            and Ut.is_str(key, not_null=True)\
            and isinstance(self.counters.get(key), CounterHelper)

    def get_counter_key(self, key: str):
        """Set time now"""
        result = None
        if self.has_counter_key(key):
            result = self.counters.get(key)
        return result

    def add_counter_key(self, key: str, reset: bool = False):
        """Set time now"""
        if not self.has_counter_key(key) or reset is True:
            self.counters[key] = CounterHelper()

    def pop_counter_key(self, key: str):
        """Set time now"""
        result = None
        if self.has_counter_key(key):
            result = self.counters.pop(key)
        return result

    def get_key_value(self, key: str):
        """Set time now"""
        result = None
        if self.has_counter_key(key):
            result = self.get_counter_key(key).get_value()
        return result

    def add_to_key(self, key: str):
        """Set time now"""
        result = False
        if self.has_counter_key(key):
            self.get_counter_key(key).add()
            result = True
        return result

    def reset_key(self, key: str):
        """Set time now"""
        result = False
        if self.has_counter_key(key):
            self.get_counter_key(key).reset()
            result = True
        return result

    def is_max_key(self, key: str, max_counter: int or None):
        """Set time now"""
        result = None
        if self.has_counter_key(key):
            result = self.get_counter_key(key).is_max(max_counter)
        return result

    def is_min_key(self, key: str, min_counter: int or None):
        """Set time now"""
        result = None
        if self.has_counter_key(key):
            result = self.get_counter_key(key).is_min(min_counter)
        return result
