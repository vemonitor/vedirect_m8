"""PacketStats unittest class."""
from ve_utils.utype import UType as Ut
import pytest
from vedirect_m8.packet_stats import PacketStats
from vedirect_m8.exceptions import InputReadException, SettingInvalidException


@pytest.fixture(name="helper_manager", scope="class")
def helper_manager_fixture():
    """Json Schema test manager fixture"""
    class HelperManager:
        """Json Helper test manager fixture Class"""
        def __init__(self):
            self.init_object()

        def init_object(self):
            """Init Object"""
            self.obj = PacketStats()

    return HelperManager()


class TestPacketStats:
    """PacketStats unittest class."""

    @staticmethod
    def get_dummy_packets_1():
        """Test is_app_block method."""
        return [
            {"cc": 2, "dd": 3},
            {"ee": 4, "ff": 5, "gg": 6, "hh": 7},
            {"ii": 8, "jj": 9, "kk": 10}
        ]

    @staticmethod
    def get_dummy_packets_2():
        """Test is_app_block method."""
        return [
            {"a": 0, "b": 1, "c": 2, "d": 3},
            {"e": 4, "f": 5, "g": 6, "h": 7},
            {"i": 8, "j": 9, "k": 10}
        ]

    def test_nb_packets(self, helper_manager):
        """Test nb_packets methods."""
        packets = TestPacketStats.get_dummy_packets_1()
        assert helper_manager.obj.add_stats(packets[0])
        assert Ut.is_int(helper_manager.obj.get_nb_packets())
        assert Ut.is_int(helper_manager.obj._set_nb_packets(32))
        assert Ut.is_int(helper_manager.obj.init_nb_packets())

    def test_accepted_keys(self, helper_manager):
        """Test accepted_keys methods."""
        helper_manager.init_object()
        packets = TestPacketStats.get_dummy_packets_1()
        nb_packets = len(packets)
        # test valid packet keys
        assert helper_manager.obj.set_accepted_keys(
            values=['cc', 'dd', 'ee', 'ff', 'gg', 'hh', 'ii', 'jj', 'kk']
        )

        for i in range(nb_packets):
            assert helper_manager.obj.is_accepted_packet_keys(
                packets[i]
            ) is True

        # test invalid packet keys
        assert helper_manager.obj.set_accepted_keys(
            values=['dd', 'ee', 'ff', 'hh', 'ii', 'jj']
        )

        for i in range(nb_packets):
            assert helper_manager.obj.is_accepted_packet_keys(
                packets[i]
            ) is False
        # test get_accepted_keys
        data = helper_manager.obj.get_accepted_keys()
        assert data == ['dd', 'ee', 'ff', 'hh', 'ii', 'jj']

        # test None packet keys
        assert helper_manager.obj.set_accepted_keys(
            values=None
        ) is False

        for i in range(nb_packets):
            assert helper_manager.obj.is_accepted_packet_keys(
                packets[i]
            ) is True

        # test get_accepted_keys
        data = helper_manager.obj.get_accepted_keys()
        assert data is None

    def test_set_accepted_keys_error(self, helper_manager):
        """Test accepted_keys methods."""
        helper_manager.init_object()
        # test exception packet keys
        with pytest.raises(SettingInvalidException):
            helper_manager.obj.set_accepted_keys(
                values=['dd', 'ee$', 'ff', 'hh', 'ii', 'jj']
            )

        with pytest.raises(SettingInvalidException):
            helper_manager.obj.set_accepted_keys(
                values=['dd', 'aaaaaaaaaaaaaaaaaaaa!', 'ff', 'hh', 'ii', 'jj']
            )

        with pytest.raises(SettingInvalidException):
            helper_manager.obj.set_accepted_keys(
                values=['dd', '%20aa%20', 'ff', 'hh', 'ii', 'jj']
            )

    def test_reset_global_stats(self, helper_manager):
        """Test is_app_block method."""
        # test init state
        assert helper_manager.obj.has_good_read_stats() is True
        assert helper_manager.obj.has_nb_bad_packets() is True
        assert helper_manager.obj.has_serial_reconnection() is True
        assert helper_manager.obj.has_serial_read_errors() is True
        # Add max_red_error value
        assert helper_manager.obj.set_max_read_error(
            value=2
        ) is True
        # Add two global read errors and set linear_flow to False
        assert helper_manager.obj.add_nb_bad_packets() == 1
        assert helper_manager.obj.add_serial_read_errors() == 1
        assert helper_manager.obj.add_serial_reconnection() == 1
        assert helper_manager.obj.set_linear_flow(False) is False
        # test success set values
        assert helper_manager.obj.get_nb_bad_packets() == 1
        assert helper_manager.obj.get_serial_read_errors() == 1
        assert helper_manager.obj.get_serial_reconnection() == 1
        assert helper_manager.obj.is_linear_flow() is False
        # Test has_reached_max_errors
        assert helper_manager.obj.has_reached_max_errors(
            raise_exception=False
        ) is False
        # Test new global state
        assert helper_manager.obj.has_good_read_stats() is False

        # Add more global read errors
        # serial_reconnection has no effect
        assert helper_manager.obj.add_serial_reconnection() == 2
        # Test has_reached_max_errors
        assert helper_manager.obj.has_reached_max_errors(
            raise_exception=False
        ) is False

        # Add more global read errors
        assert helper_manager.obj.add_nb_bad_packets() == 2
        assert helper_manager.obj.add_serial_read_errors() == 2
        # Test has_reached_max_errors
        assert helper_manager.obj.has_reached_max_errors(
            raise_exception=False
        ) is True
        # Test has_reached_max_errors with exception
        with pytest.raises(InputReadException):
            helper_manager.obj.has_reached_max_errors()

        # Reset global stats
        helper_manager.obj.reset_global_stats()
        # control new global state
        assert helper_manager.obj.has_good_read_stats() is True
        assert helper_manager.obj.get_nb_bad_packets() == 0
        assert helper_manager.obj.get_serial_read_errors() == 0
        assert helper_manager.obj.get_serial_reconnection() == 0
        assert helper_manager.obj.is_linear_flow() is True

    def test_add_stats(self, helper_manager):
        """Test is_app_block method."""
        helper_manager.init_object()
        packets = TestPacketStats.get_dummy_packets_1()
        assert not helper_manager.obj.has_stats()
        assert helper_manager.obj.add_stats(packets[0])
        assert helper_manager.obj.has_stats()
        helper_manager.obj.reset_stats()
        assert not helper_manager.obj.has_stats()

    def test_set_packet_stats(self, helper_manager):
        """Test set_packet_stats method."""
        packets_1 = TestPacketStats.get_dummy_packets_1()
        packets_2 = TestPacketStats.get_dummy_packets_2()
        nb_packets_1 = len(packets_1)
        nb_packets_2 = len(packets_2)
        z = 0
        for i in range(nb_packets_1):
            assert helper_manager.obj.set_loop_packet_stats(i, packets_1[i])

        for y in range(3):
            for i in range(nb_packets_1):
                assert helper_manager.obj.set_packet_stats(z, packets_1[i])
                z = z + 1

        for y in range(6):
            for i in range(nb_packets_2):
                result = helper_manager.obj.set_packet_stats(z, packets_2[i])
                assert result is None\
                    or Ut.is_dict(result, not_null=True)
                z = z + 1

    def test_set_loop_packet_stats(self, helper_manager):
        """Test set_loop_packet_stats method."""
        helper_manager.init_object()
        packets_1 = TestPacketStats.get_dummy_packets_1()
        packets_2 = TestPacketStats.get_dummy_packets_2()
        nb_packets_1 = len(packets_1)
        nb_packets_2 = len(packets_2)
        for i in range(nb_packets_1):
            assert helper_manager.obj.set_loop_packet_stats(
                index=i,
                packet=packets_1[i]
            )

        for y in range(9):
            for i in range(nb_packets_2):
                assert helper_manager.obj.set_loop_packet_stats(
                    index=i,
                    packet=packets_2[i]
                )
        stats = helper_manager.obj.get_packet_stats_by_index(0)
        assert stats.get('nb_resets') == 1

    def test_count_linear_index(self, helper_manager):
        """Test set_packet_stats method."""
        helper_manager.init_object()
        packets = TestPacketStats.get_dummy_packets_1()

        assert helper_manager.obj.add_stats(packets[0])
        stats = helper_manager.obj.get_packet_stats_by_index(0)
        assert helper_manager.obj.count_linear_index(
            is_linear=True,
            stats_packet=stats
        ) == (1, 0)
        assert helper_manager.obj.count_linear_index(
            is_linear=False,
            stats_packet=stats
        ) == (0, 1)
