"""
Used to get, set and analyse serial packets stats.
"""
import logging
from typing import Optional
from ve_utils.utype import UType as Ut

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vedirect")


class PacketStats:
    """
    Used to get, set and analyse serial packets stats.
    """
    def __init__(self):
        self._nb_packets = 10
        self._max_packets_ever = 0
        self._is_ordered_flow = False
        self._stats = list()
        self._count_bad_packets = 0

    MAX_STAT_PACKETS = 10

    def get_nb_packets(self) -> int:
        """Get number of packets available on serial reader."""
        return self._nb_packets

    def _set_nb_packets(self, value: int) -> int:
        """Set number of packets available on serial reader."""
        value = Ut.get_int(value, 0)
        if self.MAX_STAT_PACKETS > value > 0:
            self._nb_packets = value
        return self._nb_packets

    def init_nb_packets(self) -> int:
        """Initialise number of packets available on serial reader."""
        if self.has_stats():
            self._set_nb_packets(len(self._stats))
        return self._nb_packets

    def has_stats(self) -> bool:
        """Test if instance has available stats registered."""
        return Ut.is_list(self._stats, not_null=True)

    def can_add_stats(self) -> bool:
        """Test if stats is not full."""
        return Ut.is_list(self._stats)\
            and len(self._stats) + 1 < self.MAX_STAT_PACKETS

    def reset_stats(self) -> None:
        """Reset packet _stats class property."""
        self._stats = list()

    def add_stats(self, packet: dict) -> bool:
        """
        Add packet stats class property.
        """
        result = False
        packet_stats = PacketStats.get_stats_from_packet(packet)
        if Ut.is_dict(packet_stats, not_null=True)\
                and self.can_add_stats():
            self._stats.append(packet_stats)
            result = True
        return result

    def get_packet_index(self, packet: dict) -> int:
        """Get packet stat index in list."""
        result = -1
        packet_stats = PacketStats.get_stats_from_packet(packet)
        if Ut.is_dict(packet_stats, not_null=True):
            for i, last_stat in enumerate(self._stats):
                if PacketStats.is_equal_packet_stats(stat=packet_stats, last_stat=last_stat):
                    result = i
        return result

    def get_stats_packet_obj(self, packet: dict) -> dict:
        """Get packet stat item dictionary."""
        result = None
        stats_index = self.get_packet_index(packet)
        if stats_index >= 0:
            result = self._stats[stats_index]
        return result

    def is_packet_in_stats(self, packet: dict) -> bool:
        """Add packet stat"""
        stats_index = self.get_packet_index(packet)
        return stats_index >= 0

    def get_packet_stats_by_index(self, index: int) -> dict:
        """Add packet stat"""
        result = None
        index = Ut.get_int(index, -1)
        if self.has_stats() and 0 <= index < len(self._stats):
            result = self._stats[index]
        return result

    def set_packet_stats(self, index: int, packet: dict) -> dict:
        """Set packet flow stats."""
        result = None
        stats_packet = self.get_packet_stats_by_index(index)
        stats_equal = self.get_stats_packet_obj(packet)
        if not Ut.is_dict(stats_packet, not_null=True)\
                and Ut.is_dict(stats_equal, not_null=True):
            is_linear = True
            nb_linear, nb_resets = PacketStats.count_linear_index(
                is_linear=is_linear,
                stats_packet=stats_equal
            )
            step = index - stats_equal.get('last_index')
            index_stats = {
                "last_index": index,
                "step": step,
                "is_linear": is_linear,
                "nb_linear": nb_linear,
                "nb_resets": nb_resets
            }
            stats_equal.update(index_stats)
            result = stats_equal
        elif Ut.is_dict(stats_packet, not_null=True):
            new_stats = PacketStats.get_stats_from_packet(packet)
            is_packet_linear = PacketStats.is_equal_packet_stats(
                stat=new_stats,
                last_stat=stats_packet
            )
            is_index_linear = PacketStats.is_index_linear(
                index=index,
                last_index=stats_packet.get('last_index')
            )
            is_linear = is_packet_linear and is_index_linear
            nb_linear, nb_resets = PacketStats.count_linear_index(
                is_linear=is_linear,
                stats_packet=stats_packet
            )
            index_stats = {
                "last_index": index,
                "is_linear": is_linear,
                "nb_linear": nb_linear,
                "nb_resets": nb_resets
            }
            if not is_linear:
                stats_packet.update(new_stats)
            stats_packet.update(index_stats)
            result = stats_packet

        return result

    def set_loop_packet_stats(self, index: int, packet: dict) -> bool:
        """Set Loop Packet Stats"""
        result = False
        stats_packet = self.set_packet_stats(
            index=index,
            packet=packet
        )
        if not Ut.is_dict(stats_packet, not_null=True)\
                and self.add_stats(packet):
            stats_packet = self.set_packet_stats(
                index=index,
                packet=packet
            )

        if Ut.is_dict(stats_packet, not_null=True):
            result = True
        return result

    @staticmethod
    def get_stats_from_packet(packet: dict) -> dict:
        """
        Get packet stats from serial packet.
        Retrieve number and list of keys in packet.
        """
        result = None
        if Ut.is_dict(packet, not_null=True):
            result = {'nb': len(packet), 'keys': list(packet.keys())}
        return result

    @staticmethod
    def is_equal_packet_stats(stat: dict, last_stat: Optional[dict]) -> bool:
        """Test if actual packet stats is equal to registered packet stats."""
        return Ut.is_dict(stat, not_null=True)\
            and stat.get('nb') > 0\
            and stat.get('nb') == last_stat.get('nb')\
            and stat.get('keys') == last_stat.get('keys')

    @staticmethod
    def is_index_linear(index: int, last_index: Optional[int]) -> bool:
        """Test if actual index is equal to last index."""
        last_index = Ut.get_int(last_index, default=index)
        return last_index == index

    @staticmethod
    def count_linear_index(is_linear: bool, stats_packet: dict) -> tuple:
        """Add packet stat"""
        nb_linear = Ut.get_int(stats_packet.get('nb_linear'), 0)
        nb_resets = Ut.get_int(stats_packet.get('nb_resets'), 0)
        if is_linear is True:
            return nb_linear + 1, nb_resets
        else:
            return 0, nb_resets + 1
