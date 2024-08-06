"""SerialTestHelper unittest class."""
import pytest
from vedirect_m8.sertest import SerialTestHelper
from vedirect_m8.exceptions import SettingInvalidException


@pytest.fixture(name="helper_manager", scope="class")
def helper_manager_fixture():
    """Json Schema test manager fixture"""
    class HelperManager:
        """Json Helper test manager fixture Class"""
        def __init__(self):
            self.dict = {
                'V': '12800', 'VS': '12800', 'VM': '1280', 'DM': '120',
                'VPV': '3350', 'PPV': '130', 'I': '15000', 'IL': '1500',
                'LOAD': 'ON', 'T': '25', 'P': '130', 'CE': '13500',
                'SOC': '876', 'TTG': '45', 'Alarm': 'OFF', 'Relay': 'OFF',
                'AR': '1', 'H1': '55000', 'H2': '15000', 'H3': '13000',
                'H4': '230', 'H5': '12', 'H6': '234000', 'H7': '11000',
                'H8': '14800', 'H9': '7200', 'H10': '45', 'H11': '5',
                'H12': '0', 'H13': '0', 'H14': '0', 'H15': '11500',
                'H16': '14800', 'H17': '34', 'H18': '45', 'H19': '456',
                'H20': '45', 'H21': '300', 'H22': '45', 'H23': '350',
                'ERR': '0', 'CS': '5', 'BMV': '702', 'FW': '1.19',
                'PID': '0x204', 'SER#': 'HQ141112345', 'HSDS': '0'
            }
            conf = {
                    "PIDTest": {
                        "typeTest": "value",
                        "key": "PID",
                        "value": "0x204"
                    },
                    "columnsCheck": {
                        "typeTest": "columns",
                        "keys": [
                                'V', 'VS', 'VM', 'DM', 'T', 'I', 'P', 'CE',
                                'SOC', 'TTG', 'Alarm', 'AR', 'Relay', 'PID',
                                'FW', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7',
                                'H8', 'H9', 'H10', 'H11', 'H12', 'H13', 'H14',
                                'H15', 'H16', 'H17', 'H18'
                            ]
                    }
            }
            self.obj = SerialTestHelper(conf)

    return HelperManager()


class TestSerialTestHelper:
    """SerialTestHelper unittest class."""

    def test_has_serial_tests(self, helper_manager):
        """Test has_serial_tests method."""
        assert helper_manager.obj.has_serial_tests()

    @staticmethod
    def test_is_value_test():
        """Test is_value_test method."""
        assert SerialTestHelper.is_value_test({
                                       "typeTest": "value",
                                       "key": "PIDs8_fggg#",
                                       "value": "0x203"
                                      })
        assert not SerialTestHelper.is_value_test({
                                       "typeTest": "values",
                                       "key": "PIDs8_fg#",
                                       "value": "0x203"
                                      })
        assert not SerialTestHelper.is_value_test({
                                       "typeTest": "values",
                                       "key": "PIDs 8_fg#",
                                       "value": "0x203"
                                      })
        assert not SerialTestHelper.is_value_test({
                                       "typeTest": "values",
                                       "key": "PIDs 8_fggg#"
                                      })

    def test_run_value_test(self, helper_manager):
        """Test run_value_test method."""
        assert SerialTestHelper.run_value_test({
                                       "typeTest": "value",
                                       "key": "PID",
                                       "value": "0x204"
                                       }, helper_manager.dict)
        assert not SerialTestHelper.run_value_test({
                                       "typeTest": "values",
                                       "key": "PID",
                                       "value": "0x203"
                                      }, helper_manager.dict)
        assert not SerialTestHelper.run_value_test({
                                       "typeTest": "values",
                                       "key": "PIDs 8_fg#",
                                       "value": "0x203"
                                      }, helper_manager.dict)
        assert not SerialTestHelper.run_value_test({
                                       "typeTest": "values",
                                       "key": "PIDs 8_fg#"
                                      }, helper_manager.dict)

    @staticmethod
    def test_is_columns_list_test():
        """Test is_columns_list_test method."""
        assert SerialTestHelper.is_columns_list_test({
                                       "typeTest": "columns",
                                       "keys": ["PIDs8_fg#", "dfsdf"]
                                      })
        assert not SerialTestHelper.is_columns_list_test({
                                       "typeTest": "columns",
                                       "key": "PIDs8_fg#"
                                      })
        assert not SerialTestHelper.is_columns_list_test({
                                       "typeTest": "columns",
                                       "key": ["PIDs 8_fg#"]
                                      })
        assert not SerialTestHelper.is_columns_list_test({
                                       "typeTest": "column",
                                       "keys": ["PIDs8_fg#"]
                                      })

    @staticmethod
    def test_run_columns_test():
        """Test is_columns_list_test method."""
        assert SerialTestHelper.is_columns_list_test({
                                       "typeTest": "columns",
                                       "keys": [
                                           "V", "VS", "VS", "HSDS", "HSDS",
                                           "SER#"
                                        ]
                                      })
        assert not SerialTestHelper.is_columns_list_test({
                                       "typeTest": "columns",
                                       "key": [
                                           "V#", "VS", "VS", "HSDS", "HSDS",
                                           "SER#"
                                        ]
                                      })
        assert not SerialTestHelper.is_columns_list_test({
                                       "typeTest": "columns",
                                       "key": [
                                           "V", "VS", "VSs", "HSDS", "HSDS",
                                           "SER#"
                                        ]
                                      })
        assert not SerialTestHelper.is_columns_list_test({
                                       "typeTest": "column",
                                       "keys": "PIDs8_fg#"
                                      })

    @staticmethod
    def test_validate_serial_tests():
        """Test validate_serial_tests method."""
        with pytest.raises(SettingInvalidException):
            SerialTestHelper.validate_serial_tests({
                "PIDTest": {
                    "typeTest": "badType",
                    "keys": ["V", "VS", "VS", "HSDS", "HSDS", "SER#"]
                }
            })

        with pytest.raises(SettingInvalidException):
            SerialTestHelper.validate_serial_tests({
                "PIDTest@": {
                    "typeTest": "columns",
                    "keys": ["V", "VS", "VS", "HSDS", "HSDS", "SER#"]
                }
            })

        assert not SerialTestHelper.validate_serial_tests({
            "PIDTest": {
                "typeTest": "columns",
                "maps": ["BadKey", "VS", "VS", "HSDS", "HSDS", "SER#"]
            }
        })

    def test_run_serial_tests(self, helper_manager):
        """Test run_serial_tests method."""
        assert helper_manager.obj.run_serial_tests(helper_manager.dict)
        last_pid = helper_manager.dict.get('PID')
        helper_manager.dict.update({'PID': "Azerty"})
        assert not helper_manager.obj.run_serial_tests(helper_manager.dict)
        helper_manager.dict.update({'PID': last_pid})
        del helper_manager.dict['V']
        assert not helper_manager.obj.run_serial_tests(helper_manager.dict)
