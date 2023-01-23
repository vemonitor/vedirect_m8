"""PacketStats unittest class."""
import pytest
from ve_utils.utype import UType as Ut
from vedirect_m8.core.packet_stats import PacketsConf
from vedirect_m8.core.packet_stats import FlowPackets
from vedirect_m8.core.packet_stats import PacketStats
from vedirect_m8.core.exceptions import PacketReadException


def get_dummy_packets_1():
    """Get dummy packets 2 with partial data."""
    return {
        'PID': '0x203', 'V': '12063', 'I': '-7577',
        'P': '-91', 'CE': '-65604', 'SOC': '838',
        'TTG': '949'
    }


def get_dummy_packets_2():
    """Get dummy packet 2 with valid blocks."""
    return {
        'H1': '-149322', 'H2': '-82854', 'H3': '0',
        'H4': '0', 'H5': '0', 'H6': '-5526822', 'H7': '11733',
        'H8': '16161', 'H9': '368413', 'H10': '26', 'H11': '0',
        'H12': '0', 'H17': '6843', 'H18': '8527'
    }


def get_dummy_packets_3():
    """Get dummy packet 3 with valid blocks."""
    return {
        'PID': '0x203', 'V': '12160', 'I': '-2659',
        'P': '-32', 'CE': '-65869', 'SOC': '837',
        'TTG': '1863', 'Alarm': 'OFF', 'Relay': 'OFF',
        'AR': '0', 'BMV': '700', 'FW': '0308'
    }


def get_valid_flow_packets():
    """
    Get dummy flow packets.

    In first loop return dummy packet 1 and 2 (partial data).
    Then in next loops return dummy packet 2 and 3.

    """
    packets = [
        get_dummy_packets_1(),
        get_dummy_packets_2(),
        get_dummy_packets_3()
    ]

    for z in range(10):

        for i, packet in enumerate(packets):
            if z > 0 and i > 0 or z == 0:
                yield z, packet


class TestPacketsConf:
    def setup_method(self):
        """
        Setup any state tied to the execution of the given function.

        Invoked for every test function in the module.
        """
        self.obj = PacketsConf(
            active=True,
            nb_packets=2,
            nb_blocks=31,
            max_packet_errors=4
        )

    def test_constructor(self):
        """Test is_app_block method."""
        obj = FlowPackets(active=False)
        assert obj.has_nb_packets() is False
        assert obj.has_nb_blocks() is False
        assert obj.is_active() is False
        assert self.obj.has_packets_or_blocks_limit()
        assert self.obj.init_conf(
            active=True,
            nb_packets=None,
            nb_blocks=26,
            max_packet_errors=4
        )

    def test_nb_packets(self):
        """Test nb_packets methods."""
        assert self.obj.has_nb_packets()
        assert self.obj.get_nb_packets() == 2
        assert self.obj.has_packets_or_blocks_limit()
        assert not self.obj.set_nb_packets(None)

    def test_nb_blocks(self):
        """Test nb_blocks methods."""
        assert self.obj.has_nb_blocks()
        assert self.obj.get_nb_blocks() == 31
        assert self.obj.has_packets_or_blocks_limit()
        assert Ut.is_int(self.obj.set_nb_blocks(None))


class TestFlowPackets:
    def setup_method(self):
        """
        Setup any state tied to the execution of the given function.

        Invoked for every test function in the module.
        """
        self.obj = FlowPackets(
            active=True,
            nb_packets=2,
            nb_blocks=31
        )

    def test_constructor(self):
        """Test is_app_block method."""
        obj = FlowPackets(active=False)
        assert obj.has_nb_packets() is False
        assert obj.has_nb_blocks() is False
        assert obj.is_active() is False
        assert self.obj.has_packets_or_blocks_limit()

    def test_nb_packets(self):
        """Test nb_packets methods."""
        assert self.obj.has_nb_packets()
        assert self.obj.get_nb_packets() == 2
        assert self.obj.has_packets_or_blocks_limit()
        assert not self.obj.set_nb_packets(None)

    def test_nb_blocks(self):
        """Test nb_blocks methods."""
        assert self.obj.has_nb_blocks()
        assert self.obj.get_nb_blocks() == 31
        assert self.obj.has_packets_or_blocks_limit()
        assert Ut.is_int(self.obj.set_nb_blocks(None))

    def test_data_cache(self):
        """Test data_cache methods."""
        packet = get_dummy_packets_1()
        assert self.obj.add_data_cache(packet)
        assert self.obj.get_time_cache() is not None
        assert self.obj.get_data_cache() is not None
        assert self.obj.has_data_cache()
        assert self.obj.is_packet_in_data_cache(packet)
        assert self.obj.add_data_cache(packet)
        assert self.obj.init_data_cache(packet)
        assert self.obj.reset_data_cache() is None

    def test_counters(self):
        """Test counters methods."""
        assert self.obj.get_loose_counter() == 0
        assert self.obj.add_loose_counter() == 1
        assert self.obj.reset_loose_counter() == 0
        assert self.obj.get_loop_counter() == 0
        assert self.obj._add_loop_counter() == 1
        assert self.obj.reset_from_loop() is None

    def test_is_packet_in_data_cache(self):
        """Test is_packet_in_data_cache methods."""
        packet = get_dummy_packets_1()
        packet_3 = get_dummy_packets_3()
        result, nb_new = self.obj.is_packet_in_data_cache(packet)
        assert result is False
        assert nb_new == len(packet)
        assert self.obj.add_data_cache(packet)
        result, nb_new = self.obj.is_packet_in_data_cache(packet)
        assert result is True
        assert nb_new == 0
        result, nb_new = self.obj.is_packet_in_data_cache(packet_3)
        assert result is False
        assert nb_new == 5

    def test_is_cache_full(self):
        """Test is_packet_in_data_cache methods."""
        assert self.obj.is_cache_full() is False
        assert self.obj.init_conf(
            nb_packets=1,
            nb_blocks=0
        )
        assert self.obj._add_loop_counter() == 1
        assert self.obj._add_loop_counter() == 2
        assert self.obj.is_cache_full() is True

    def test_is_all_packets(self):
        """Test is_all_packets method."""

        def run_for_test():
            """"""
            count_success = 0
            with pytest.raises(PacketReadException):
                for i, packet_flow in get_valid_flow_packets():
                    if self.obj.is_all_packets(packet_flow):
                        self.obj.reset_from_loop()
                        count_success = count_success + 1
            return count_success

        # test limit nb errors, nb blocks never reached.
        assert self.obj.init_conf(
            nb_packets=1,
            nb_blocks=55
        )
        assert run_for_test() == 0

        # test limit of nb blocks
        # Here limit by params to 4 blocks
        # And data has 26 blocks
        # resulting an exception for nb blocks limit
        self.obj.reset_from_loop()
        assert self.obj.init_conf(
            nb_packets=1,
            nb_blocks=4
        )
        assert run_for_test() == 0
        # test success getting 26 blocks from flow packets
        self.obj.reset_from_loop()
        assert self.obj.init_conf(
            nb_packets=2,
            nb_blocks=26,
            max_packet_errors=4
        )
        count = 0
        for z, packet in get_valid_flow_packets():
            if self.obj.is_all_packets(packet):
                assert self.obj.count_data_cache_blocks() == 26
                if z == 0:
                    # in first loop get 3 packets with 1 partial
                    assert self.obj.get_loop_counter() == 3
                    assert self.obj.get_loose_counter() == 1
                else:
                    # next in loop get 2 valid packets
                    assert self.obj.get_loop_counter() == 2
                    assert self.obj.get_loose_counter() == 0
                self.obj.reset_from_loop()
                count = count + 1
        assert count == 10


class TestPacketStats:

    def setup_method(self):
        """
        Setup any state tied to the execution of the given function.

        Invoked for every test function in the module.
        """
        self.obj = PacketStats()

    def test_stats(self):
        """Test is_app_block method."""
        packet = get_dummy_packets_1()
        assert not self.obj.add_stats({})
        assert not self.obj.has_stats()
        assert self.obj.add_stats(packet)
        assert self.obj.has_stats()
        assert self.obj.can_add_stats()
        assert self.obj.reset_stats() is None
        assert not self.obj.has_stats()

    def test_is_packet_in_stats(self):
        """Test is_app_block method."""
        packet2 = get_dummy_packets_2()
        packet3 = get_dummy_packets_3()
        assert not self.obj.has_stats()

        for z, packet_flow in get_valid_flow_packets():
            self.obj.add_stats(packet_flow)
        assert self.obj.is_packet_in_stats(packet2)
        assert self.obj.is_packet_in_stats(packet3)
        self.obj.reset_stats()
        assert not self.obj.has_stats()

    def test_set_packet_stats(self):
        """Test set_packet_stats method."""
        assert not self.obj.has_stats()
        i = 0
        for z, packet_flow in get_valid_flow_packets():
            if z == 0:
                assert self.obj.set_loop_packet_stats(i, packet_flow)
            else:
                assert self.obj.set_packet_stats(i, packet_flow)
            i = i + 1

    @staticmethod
    def test_packet_stats():
        """Test set_loop_packet_stats method."""

        packet_stats = (
                {'nb': 12, 'keys': ['PID', 'V', 'I', 'P', 'CE', 'SOC', 'TTG', 'Alarm', 'Relay', 'AR', 'BMV', 'FW']},
                {'nb': 10, 'keys': ['PID', 'V', 'I', 'P', 'CE', 'SOC', 'TTG', 'Alarm', 'Relay', 'AR']}
            )
        assert PacketStats.is_packet_stats_equal(packet_stats[0], packet_stats[0])
        assert PacketStats.is_packet_stats_equal(packet_stats[1], packet_stats[1])
        assert not PacketStats.is_packet_stats_equal(packet_stats[1], packet_stats[0])

        assert PacketStats. is_in_packet_stats(packet_stats[0], packet_stats[1])
        assert PacketStats.is_in_packet_stats(packet_stats[1], packet_stats[0])
        assert not PacketStats.is_in_packet_stats(packet_stats[1], [])
        assert not PacketStats.is_in_packet_stats(packet_stats[1], {'nb': 10, 'keys': []})

    def test_set_loop_packet_stats(self):
        """Test set_loop_packet_stats method."""
        count = 0
        for z, packet in get_valid_flow_packets():
            assert self.obj.set_loop_packet_stats(count, packet)
            count = count + 1
        stats = self.obj.get_packet_stats_by_index(0)
        assert stats.get('nb_resets') == 0

    def test_count_linear_index(self):
        """Test set_packet_stats method."""
