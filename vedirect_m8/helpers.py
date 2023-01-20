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

    def get_value(self):
        """Set time now"""
        return self.counter

    def add(self):
        """Set time now"""
        if self.counter < MAX_COUNTER_VALUE:
            self.counter = self.counter + 1
        else:
            self.reset()

    def reset(self):
        """Set time now"""
        self.counter = 0

    def is_max(self, max_counter: int or None):
        """Set time now"""
        return Ut.is_int(max_counter) \
            and 0 < max_counter <= self.counter

    def is_min(self, min_counter: int or None):
        """Set time now"""
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

    def add_counter_key(self, key: str):
        """Set time now"""
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
