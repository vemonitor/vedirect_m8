"""PacketStats unittest class."""
from vedirect_m8.packet_stats import PacketStats
from ve_utils.utype import UType as Ut


class TestPacketStats:

    def setup_method(self):
        """
        Setup any state tied to the execution of the given function.

        Invoked for every test function in the module.
        """
        self.obj = PacketStats()

    @staticmethod
    def get_dummy_packets_1():
        """Test is_app_block method."""
        return [
            {"c": 2, "d": 3},
            {"e": 4, "f": 5, "g": 6, "h": 7},
            {"i": 8, "j": 9, "k": 10}
        ]

    @staticmethod
    def get_dummy_packets_2():
        """Test is_app_block method."""
        return [
            {"a": 0, "b": 1, "c": 2, "d": 3},
            {"e": 4, "f": 5, "g": 6, "h": 7},
            {"i": 8, "j": 9, "k": 10}
        ]

    def test_nb_packets(self):
        """Test is_app_block method."""
        packets = TestPacketStats.get_dummy_packets_1()
        assert self.obj.add_stats(packets[0])
        assert Ut.is_int(self.obj.get_nb_packets())
        assert Ut.is_int(self.obj._set_nb_packets(32))
        assert Ut.is_int(self.obj.init_nb_packets())

    def test_add_stats(self):
        """Test is_app_block method."""
        packets = TestPacketStats.get_dummy_packets_1()
        assert not self.obj.add_stats(packets)
        assert not self.obj.has_stats()
        assert self.obj.add_stats(packets[0])
        assert self.obj.has_stats()
        self.obj.reset_stats()
        assert not self.obj.has_stats()

    def test_is_packet_in_stats(self):
        """Test is_app_block method."""
        packets = TestPacketStats.get_dummy_packets_1()
        assert not self.obj.has_stats()
        assert self.obj.add_stats(packets[0])
        assert self.obj.add_stats(packets[1])
        assert self.obj.is_packet_in_stats(packets[0])
        assert not self.obj.is_packet_in_stats(packets[2])
        self.obj.reset_stats()
        assert not self.obj.has_stats()

    def test_set_packet_stats(self):
        """Test set_packet_stats method."""
        packets_1 = TestPacketStats.get_dummy_packets_1()
        packets_2 = TestPacketStats.get_dummy_packets_2()
        nb_packets_1 = len(packets_1)
        nb_packets_2 = len(packets_2)
        z = 0
        for i in range(nb_packets_1):
            assert self.obj.set_loop_packet_stats(i, packets_1[i])

        for y in range(3):
            for i in range(nb_packets_1):
                assert self.obj.set_packet_stats(z, packets_1[i])
                z = z + 1

        for y in range(6):
            for i in range(nb_packets_2):
                result = self.obj.set_packet_stats(z, packets_2[i])
                assert result is None\
                    or Ut.is_dict(result, not_null=True)
                z = z + 1

    def test_set_loop_packet_stats(self):
        """Test set_loop_packet_stats method."""
        packets_1 = TestPacketStats.get_dummy_packets_1()
        packets_2 = TestPacketStats.get_dummy_packets_2()
        nb_packets_1 = len(packets_1)
        nb_packets_2 = len(packets_2)
        for i in range(nb_packets_1):
            assert self.obj.set_loop_packet_stats(i, packets_1[i])

        for y in range(9):
            for i in range(nb_packets_2):
                assert self.obj.set_loop_packet_stats(i, packets_2[i])
        stats = self.obj.get_packet_stats_by_index(0)
        assert stats.get('nb_resets') == 1

    def test_count_linear_index(self):
        """Test set_packet_stats method."""
        packets = TestPacketStats.get_dummy_packets_1()

        assert self.obj.add_stats(packets[0])
        stats = self.obj.get_packet_stats_by_index(0)
        assert self.obj.count_linear_index(
            is_linear=True,
            stats_packet=stats
        ) == (1, 0)
        assert self.obj.count_linear_index(
            is_linear=False,
            stats_packet=stats
        ) == (0, 1)
