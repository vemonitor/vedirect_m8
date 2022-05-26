import pytest
from vedirect_m8.ve_controller import VedirectController
from ve_utils.utils import UType as Ut, USys as USys


class TestVedirectController:

    def setup_method(self):
        """ setup any state tied to the execution of the given function.
        Invoked for every test function in the module.
        """
        conf = {
            'serialPort': "COM1",
            'timeout': 2,
            "serialTest": {
                'PID_test': { 
                    "typeTest": "value",
                    "key": "PID",
                    "value": "0x203"
                }
            }
        }
        if USys.is_op_sys_type("unix"):
            conf['serialPort'] = "/tmp/vmodem1"
        self.obj = VedirectController(**conf)

    def teardown_method(self):
        """ teardown any state that was previously setup with a setup_function
        call.
        """
        pass

    def test_is_serial_ready(self):
        """"""
        assert self.obj.is_serial_ready()

    def test_read_data_single(self):
        """"""
        data = self.obj.read_data_single()
        assert Ut.is_dict_not_empty(data)
