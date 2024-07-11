import logging
from vedirect_m8 import configure_logging

logging.basicConfig()
logger = logging.getLogger("vedirect")


class TestInit:

    def test_logger_debug(self):
        """"""
        configure_logging(True)
        assert logger.level == logging.DEBUG

    def test_logger_default(self):
        """"""
        configure_logging()
        assert logger.level == logging.INFO
