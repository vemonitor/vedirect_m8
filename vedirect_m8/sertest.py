# -*- coding: utf-8 -*-
"""
Test decoded serial vedirect data to identify a valid serial port.

 .. seealso: VedirectController
 .. raises: SettingInvalidException
"""
import logging
from vedirect_m8.serutils import SerialUtils as Ut
from vedirect_m8.exceptions import SettingInvalidException

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vedirect")


class SerialTestHelper:
    """
    Test decoded serial vedirect data to identify a valid serial port.

    :Example :
        > st = SerialTestHelper({
            "PIDTest": {
                "typeTest": "value",\n
                "key": "PID",\n
                "value": "0x204"\n
            },
            "columnsCheck": {
                "typeTest": "columns",\n
                "keys": ['V', 'VS', 'VM', 'DM', 'T']\n
            }
            })
     .. seealso: VedirectController
     .. raises: SettingInvalidException
    """
    def __init__(self, serial_tests: dict or None = None):
        """
        Constructor of SerialTestHelper class.
        :param serial_tests: The serialTests configuration settings
        :return: Nothing
        """
        self._tests = None
        if serial_tests is not None:
            self.set_serial_tests(serial_tests)

    def has_serial_tests(self) -> bool:
        """
        Test if it SerialTestHelper has valid self._tests property.
        :return: True if self._tests is a not empty dictionary.
        """
        return Ut.is_dict(self._tests, not_null=True)

    @staticmethod
    def is_value_test(data: dict) -> bool:
        """
        Test if data is valid value test configuration settings.

        :Example :
            >>> SerialTestHelper.is_value_test({
                "typeTest": "value",\n
                "key": "PID",\n
                "value": "0x204"\n
                })
            >>> True
        :param data: The value test configuration settings
        :return: True if data is a valid value test configuration settings.
        """
        return Ut.is_dict(data, not_null=True)\
            and data.get("typeTest") == "value"\
            and Ut.is_serial_key_pattern(data.get("key"))\
            and data.get("value") is not None

    @staticmethod
    def run_value_test(value_test: dict, serial_data: dict) -> bool:
        """
        Run value test on serial_data.

        Evaluates if the value_test is valid,
        if serial_data is a dictionary, and if serial_data contain a key value_test key value.
        Then evaluate if serial_data key value is equal to the value_test value.

        :Example :
            >>> SerialTestHelper.run_value_test(
                value_test = {
                    "typeTest": "value",\n
                    "key": "PID",\n
                    "value": "0x204"\n
                },\n
                serial_data = {"PID": "0x204"})
            >>> True
        :param value_test: The value test to evaluate on serial_data.
        :param serial_data: The serial data decoded from serial vedirect device.
        :return: True if value test success on serial_data.
        """
        if SerialTestHelper.is_value_test(value_test)\
                and Ut.is_dict(serial_data, not_null=True)\
                and value_test.get("key") in serial_data:
            key = value_test.get("key")
            return serial_data.get(key) == value_test.get("value")
        return False

    @staticmethod
    def is_columns_list_test(data: dict) -> bool:
        """
        Test if data is valid columns test configuration settings.

        :Example :
            >>> SerialTestHelper.is_columns_list_test({
                "typeTest": "columns",\n
                "keys": ["PID", "V"]\n
                })
            >>> True
        :param data: The columns test configuration settings
        :return: True if data is a valid columns test configuration settings.
        """
        return Ut.is_dict(data, not_null=True)\
            and data.get("typeTest") == "columns"\
            and Ut.is_list(data.get("keys"), not_null=True)

    @staticmethod
    def run_columns_test(columns_test: dict, serial_data: dict) -> bool:
        """
        Run columns test on serial_data.

        Evaluates if the columns_test is valid and
        if serial_data is a dictionary.
        Then evaluate if serial_data contain all columns_test keys.
        :Example :
            >>> SerialTestHelper.run_columns_test(
                columns_test = {
                    "typeTest": "columns",\n
                    "keys": ["PID", "V"]\n
                },\n
                serial_data = {"PID": "0x204", "V": 25})
            >>> True
        :param columns_test: The columns test to evaluate on serial_data
        :param serial_data: The serial data decoded from serial vedirect device
        :return: True if columns test success on serial_data.
        """
        result = False
        if SerialTestHelper.is_columns_list_test(columns_test)\
                and Ut.is_dict(serial_data, not_null=True):
            keys = columns_test.get("keys")
            serial_data_keys = serial_data.keys()
            result = all(key in serial_data_keys for key in keys)
        return result

    @staticmethod
    def get_valid_type_tests() -> list:
        """Get list of valid serialTest types"""
        return ["value", "columns"]

    @staticmethod
    def validate_serial_tests(data: dict) -> bool:
        """
        Validate serialTest configuration settings.

        :Example :
            >>> SerialTestHelper.validate_serial_tests(
                    data = {
                        "PIDTest": {
                            "typeTest": "value",\n
                            "key": "PID",\n
                            "value": "0x204"\n
                        },\n
                        "colsCheck": {
                            "typeTest": "columns",\n
                            "keys": ['V', 'VS']
                        }
                    })
            >>> True
        :return: True if is valid serialTest configuration settings.
        """
        tst = False
        if Ut.is_dict(data, not_null=True):
            tst = True
            for key, item in data.items():
                if Ut.is_key_pattern(key)\
                        and Ut.is_dict(item, not_null=True):

                    type_test = item.get("typeTest")

                    if type_test == "value"\
                            and not SerialTestHelper.is_value_test(item):
                        tst = False
                    elif type_test == "columns"\
                            and not SerialTestHelper.is_columns_list_test(item):
                        tst = False
                    elif type_test not in SerialTestHelper.get_valid_type_tests():
                        raise SettingInvalidException(
                            "[SerialTestHelper::validate_serial_tests] "
                            "unrecognized typeTest %s, from key %s."
                            "typeTest must be in : %s" %
                            (type_test, key, SerialTestHelper.get_valid_type_tests())
                        )
                else:
                    raise SettingInvalidException(
                            "[SerialTestHelper::validate_serial_tests] "
                            "invalid serialTest settings from key %s. "
                            "Key must start by char [a-zA-Z0-9], "
                            "and must contain only chars [a-zA-Z0-9_]." %
                            key
                        )
        return tst

    def set_serial_tests(self, data: dict) -> bool:
        """
        Set the serialTest configuration settings.

        First evaluate if data is valid serialTest configuration settings.
        :Example :
            > self.set_serial_tests(
                    data = {
                        "PIDTest": {
                            "typeTest": "value",\n
                            "key": "PID",\n
                            "value": "0x204"\n
                        },\n
                        "colsCheck": {
                            "typeTest": "columns",\n
                            "keys": ['V', 'VS']
                        }
                    })
            > True
        :return: True if is valid serialTest configuration settings.
        """
        if SerialTestHelper.validate_serial_tests(data):
            self._tests = data
            return True
        return False

    def run_serial_tests(self, serial_data: dict) -> bool:
        """
        Run the serialTests on serial_data from decoded vedirect serial data.

        :return: True if serial_data success serialTest evaluation.
        """
        tst = False
        if self.has_serial_tests():
            tst = True
            for item in self._tests.values():
                type_test = item.get("typeTest")

                if type_test == "value"\
                        and not SerialTestHelper.run_value_test(item, serial_data):
                    tst = False

                elif type_test == "columns"\
                        and not SerialTestHelper.run_columns_test(item, serial_data):
                    tst = False
        return tst
