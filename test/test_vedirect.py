import pytest
from vedirect_m8.vedirect import Vedirect
from ve_utils.utils import UType as Ut, USys as USys


class TestVedirect:

    def setup_method(self):
        """ setup any state tied to the execution of the given function.
        Invoked for every test function in the module.
        """
        conf = {
            'serialPort': "COM1",
        }

        if USys.is_op_sys_type("unix"):
            conf['serialPort'] = "/tmp/vmodem1"
            conf['serialPath'] = "/tmp/"
        self.obj = Vedirect(**conf)

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
