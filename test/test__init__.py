"""Test __init__ module"""
import logging
from vedirect_m8 import configure_logging

logging.basicConfig()
logger = logging.getLogger("vedirect")


class TestInit:
    """Test __init__ module"""

    def test_logger_debug(self):
        """Test Logger debug"""
        configure_logging(True)
        assert logger.level == logging.DEBUG

    def test_logger_default(self):
        """Test Logger Default"""
        configure_logging()
        assert logger.level == logging.INFO
