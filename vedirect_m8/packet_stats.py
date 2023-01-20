"""
Used to get, set and analyse serial packets stats.
"""
import logging
import time
from ve_utils.utype import UType as Ut
from vedirect_m8.exceptions import PacketReadException

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__deprecated__ = False
__license__ = "MIT"
__status__ = "Production"
__version__ = "1.0.0"

logging.basicConfig()
logger = logging.getLogger("vedirect")


class PacketsConf:
    """
        Used to control validity of packets flow.


        """

    def __init__(self,
                 active: bool = True,
                 nb_packets: int or None = None,
                 nb_blocks: int or None = None,
                 max_packet_errors: int or None = None
                 ) -> None:
        """

        :param active: Define if
        :param nb_packets:
        :param nb_blocks:
        :param max_packet_errors:
        """
        self._active = True
        self._nb_packets = None
        self._nb_blocks = None
        self._max_packet_errors = self.MAX_PACKETS_ERROR
        self.init_conf(active=active,
                       nb_packets=nb_packets,
                       nb_blocks=nb_blocks,
                       max_packet_errors=max_packet_errors
                       )
    MAX_PACKETS_ERROR = 10
    MAX_STAT_PACKETS = 10

    def has_packets_or_blocks_limit(self) -> bool:
        """Test if serial reader output is ordered."""
        return self.has_nb_packets() or self.has_nb_blocks()

    def has_nb_packets(self) -> bool:
        """Test if it has number of total packets defined."""
        return Ut.is_int(self._nb_packets, positive=True)

    def get_nb_packets(self) -> int:
        """Get number of packets available on serial reader."""
        return self._nb_packets

    def set_nb_packets(self, value: int) -> bool:
        """
        Set number of packets in group from data flow.
        """
        result = False
        value = Ut.get_int(value, 0)
        self._nb_packets = 0
        if self.MAX_STAT_PACKETS > value > 0:
            self._nb_packets = value
            result = True
        return result

    def has_nb_blocks(self) -> bool:
        """Test if it has number of total blocks defined."""
        return Ut.is_int(self._nb_blocks, positive=True)

    def get_nb_blocks(self) -> int:
        """Get number total of blocks on packets available on serial reader."""
        return self._nb_blocks

    def set_nb_blocks(self, value: int) -> bool:
        """Set number of blocks available on serial reader."""
        result = False
        value = Ut.get_int(value, 0)
        self._nb_blocks = 0
        if value >= 0:
            self._nb_blocks = value
            result = True
        return result

    def set_max_packet_errors(self, value: int) -> bool:
        """Set number of blocks available on serial reader."""
        result = False
        if Ut.is_int(value) and value >= -1:
            self._max_packet_errors = value
            result = True
        return result

    def init_conf(self,
                  active: bool = True,
                  nb_packets: int or None = None,
                  nb_blocks: int or None = None,
                  max_packet_errors: int or None = None
                  ) -> bool:
        """
        Initialize packets configuration parameters.

        Set active, nb_packets and nb_blocks values
        :param active: define if packet controller is active
        :param nb_packets: Number of packets in group flow
        :param nb_blocks: Number of blocks in group flow
        :param max_packet_errors: Maximum of packet errors accepted
        :return: True if all defined parameters set.
        """
        self._active = Ut.str_to_bool(active)
        return (nb_packets is None
                or self.set_nb_packets(nb_packets))\
            and (nb_blocks is None
                 or self.set_nb_blocks(nb_blocks))\
            and (max_packet_errors is None
                 or self.set_max_packet_errors(max_packet_errors))


class FlowPackets(PacketsConf):
    """
    Used to control validity of packets flow.


    """
    def __init__(self,
                 active: bool = True,
                 nb_packets: int or None = None,
                 nb_blocks: int or None = None,
                 max_packet_errors: int or None = None
                 ) -> None:
        PacketsConf.__init__(self,
                             active=active,
                             nb_packets=nb_packets,
                             nb_blocks=nb_blocks,
                             max_packet_errors=max_packet_errors
                             )
        self._loop_counter = 0
        self._error_counter = 0
        self._data_cache = None

    MAX_FLOW_BLOCKS = 150

    def is_active(self) -> bool:
        """Test if serial reader output is ordered."""
        return self._active is True

    def has_data_cache(self) -> bool:
        """Test if instance has valid data cache value"""
        return Ut.is_tuple(self._data_cache)\
            and Ut.is_numeric(self._data_cache[0], not_null=True)\
            and Ut.is_dict(self._data_cache[1], not_null=True)

    def get_time_cache(self) -> float:
        """Get data cache time value"""
        result = None
        if self.has_data_cache():
            result = self._data_cache[0]
        return result

    def get_data_cache(self) -> dict:
        """Get data cache value"""
        result = None
        if self.has_data_cache():
            result = self._data_cache[1]
        return result

    def count_data_cache_blocks(self) -> int:
        """Get nb of blocks in data cache."""
        result = 0
        if self.has_data_cache():
            result = len(self._data_cache[1])
        return result

    def reset_data_cache(self):
        """Reset data cache to None value."""
        self._data_cache = None

    def init_data_cache(self,
                        data: dict
                        ) -> bool:
        """
        Initialize cache tuple values.

        :param data: dict: Data to add in cache,
        :return: True if data cache is set, or False
        """
        result = False
        self._data_cache = None
        if Ut.is_dict(data, not_null=True):
            self._data_cache = (time.time(), dict(data))
            result = True
        return result

    def add_data_cache(self,
                       data: dict
                       ) -> bool:
        """Add data to cache."""
        result = False
        if self.has_data_cache():
            if Ut.is_dict(data, not_null=True):
                self._data_cache[1].update(dict(data))
                result = True
        else:
            result = self.init_data_cache(data)
        return result

    def _add_loop_counter(self) -> int:
        """Get number of packets available on serial reader."""
        self._loop_counter = self._loop_counter + 1
        return self._loop_counter

    def get_loop_counter(self):
        """Reset data cache to None value."""
        return self._loop_counter

    def add_loose_counter(self) -> int:
        """Get number of packets available on serial reader."""
        self._error_counter = self._error_counter + 1
        return self._error_counter

    def reset_loose_counter(self) -> int:
        """Reset data cache to None value."""
        self._error_counter = 0
        return self._error_counter

    def get_loose_counter(self):
        """Reset data cache to None value."""
        return self._error_counter

    def reset_from_loop(self):
        """Reset data cache to None value."""
        self._data_cache = None
        self._loop_counter = 0
        self._error_counter = 0

    def is_packet_in_data_cache(self, packet: dict) -> tuple:
        """Test if packet keys are in data cache."""
        result, nb_new = False, 0
        if Ut.is_dict(packet, not_null=True):

            if self.has_data_cache():
                cache = self.get_data_cache()
                result = True
                for key in packet.keys():
                    if key not in cache:
                        result, nb_new = False, nb_new + 1
            else:
                nb_new = len(packet)
        return result, nb_new

    def is_cache_full(self, nb_new_blocks: int = 0) -> bool:
        """Test if cache is full"""
        return (not self.has_nb_packets()
                and self.has_full_blocks(nb_new_blocks))\
            or (not self.has_nb_blocks()
                and self.has_full_packets())\
            or (self.has_full_blocks(nb_new_blocks)
                and self.has_full_packets())

    def has_full_packets(self) -> bool:
        """Test if all packets received."""
        return self.has_nb_packets()\
            and self.get_nb_packets() <= self._loop_counter + 1

    def is_over_loop_counter(self) -> bool:
        """Test if nb_packets value have been over passed."""
        return self.has_nb_packets()\
            and self.get_nb_packets() < self._loop_counter + 1

    def has_full_blocks(self, nb_new_blocks: int = 0) -> bool:
        """Test if all blocks received."""
        return self.has_nb_blocks() \
            and self.get_nb_blocks() <= self.count_data_cache_blocks() + nb_new_blocks <= self.MAX_FLOW_BLOCKS

    def is_over_blocks_counter(self, nb_new_blocks: int = 0) -> bool:
        """Test if nb_blocks value have been over passed."""
        return self.has_nb_blocks() \
            and self.get_nb_blocks() < self.count_data_cache_blocks() + nb_new_blocks

    def is_all_packets(self,
                       packet: dict
                       ) -> bool:
        """
        Add data to cache and test if all packets and all blocks retrieved.

        """
        result = False
        if self.is_active()\
                and self.has_packets_or_blocks_limit()\
                and Ut.is_dict(packet, not_null=True):
            is_packet_exist, nb_new_blocks = self.is_packet_in_data_cache(packet)

            if self.is_over_loop_counter() or is_packet_exist is True:
                self.add_loose_counter()

            if self.is_over_blocks_counter(nb_new_blocks):
                raise PacketReadException(
                    "[SerialPackets] "
                    "Invalid packets from serial. "
                    "Reached maximum blocks %s / %s. "
                    "Errors %s / %s. nb_loops: %s" % (
                        self.count_data_cache_blocks() + nb_new_blocks,
                        self.get_nb_blocks(),
                        self._error_counter,
                        self._max_packet_errors,
                        self._loop_counter
                    )
                )
            if self._error_counter >= self._max_packet_errors:
                raise PacketReadException(
                    "[SerialPackets] "
                    "Invalid packets from serial. "
                    "Reached maximum errors %s / %s. nb_loops: %s "
                    "Blocks %s / %s. " % (
                        self._error_counter,
                        self._max_packet_errors,
                        self._loop_counter,
                        self.count_data_cache_blocks() + nb_new_blocks,
                        self.get_nb_blocks(),
                    )
                )

            if self.add_data_cache(packet):
                self._add_loop_counter()

            result = self.is_cache_full()
        return result


class PacketStats(FlowPackets):
    """
    Used to get, set and analyse serial packets stats.
    """
    def __init__(self,
                 active: bool = True,
                 nb_packets: int or None = None,
                 nb_blocks: int or None = None
                 ):
        FlowPackets.__init__(self,
                             active=active,
                             nb_packets=nb_packets,
                             nb_blocks=nb_blocks
                             )
        self._max_packets_ever = 0
        self._is_ordered_flow = True
        self._stats = []
        self._count_bad_packets = 0
        self._loop_counter = 0

    MAX_STAT_PACKETS = 10

    def is_ordered_flow(self) -> bool:
        """Test if serial reader output is ordered."""
        return self._is_ordered_flow

    def init_nb_packets(self) -> int:
        """Initialise number of packets available on serial reader."""
        if self.has_stats():
            self.set_nb_packets(len(self._stats))
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
        self._stats = []

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
                if PacketStats.is_packet_stats_equal(stat=packet_stats, last_stat=last_stat):
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

    @staticmethod
    def is_packet_stats_params(index: int,
                               stats_packet: dict
                               ) -> bool:
        """Test if valid packet stats parameters."""
        return Ut.is_dict(stats_packet, not_null=True)\
            and Ut.is_int(index)

    @staticmethod
    def set_packet_stats_from_index(index: int,
                                    stats_packet: dict,
                                    packet: dict
                                    ):
        """Set packet flow stats from index."""
        result = None
        if PacketStats.is_packet_stats_params(index, stats_packet):
            item_stats = PacketStats.get_stats_from_packet(packet)
            is_packet_linear = PacketStats.is_packet_stats_equal(
                stat=item_stats,
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
                stats_packet.update(item_stats)
            stats_packet.update(index_stats)
            result = stats_packet
        return result

    @staticmethod
    def set_packet_stats_from_stats(index: int,
                                    stats_packet: dict
                                    ):
        """Set packet flow stats from packet stats."""
        result = None
        if PacketStats.is_packet_stats_params(index, stats_packet):
            is_linear = True
            nb_linear, nb_resets = PacketStats.count_linear_index(
                is_linear=is_linear,
                stats_packet=stats_packet
            )
            step = index - stats_packet.get('last_index')
            index_stats = {
                "last_index": index,
                "step": step,
                "is_linear": is_linear,
                "nb_linear": nb_linear,
                "nb_resets": nb_resets
            }
            stats_packet.update(index_stats)
            result = stats_packet
        return result

    def set_packet_stats(self, index: int, packet: dict) -> dict:
        """Set packet flow stats."""
        result = None
        stats_packet = self.get_packet_stats_by_index(index)
        stats_equal = self.get_stats_packet_obj(packet)
        if not Ut.is_dict(stats_packet, not_null=True)\
                and Ut.is_dict(stats_equal, not_null=True):
            result = PacketStats.set_packet_stats_from_stats(
                index=index,
                stats_packet=stats_equal
            )
        elif Ut.is_dict(stats_packet, not_null=True):
            result = PacketStats.set_packet_stats_from_index(
                index=index,
                stats_packet=stats_packet,
                packet=packet
            )

        return result

    def set_loop_packet_stats(self, index: int, packet: dict) -> bool:
        """"""
        result = False
        stats_packet = self.set_packet_stats(
            index=index,
            packet=packet
        )
        # if new stat
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
    def is_packet_stats(stat: dict) -> bool:
        """Test if actual packet stats is equal to registered packet stats."""
        return Ut.is_dict(stat, not_null=True) \
            and stat.get('nb') > 0 \
            and Ut.is_list(stat.get('keys'), not_null=True)

    @staticmethod
    def is_packet_stats_equal(stat: dict, last_stat: dict or None) -> bool:
        """Test if actual packet stats is equal to registered packet stats."""
        return PacketStats.is_packet_stats(stat) \
            and PacketStats.is_packet_stats(last_stat) \
            and stat.get('nb') == last_stat.get('nb') \
            and stat.get('keys') == last_stat.get('keys')

    @staticmethod
    def is_in_packet_stats(stat: dict, last_stat: dict or None) -> bool:
        """Test if actual packet stats is equal to registered packet stats."""
        result = False
        if PacketStats.is_packet_stats(stat) \
                and PacketStats.is_packet_stats(last_stat):
            if stat.get('nb') > 0 == last_stat.get('nb')\
                    and stat.get('keys') == last_stat.get('keys'):
                result = True
            else:
                set_stat = set(stat.get('keys'))
                result = set_stat.issubset(last_stat.get('keys'))\
                    or set_stat.issuperset(last_stat.get('keys'))\

        return result

    @staticmethod
    def is_index_linear(index: int, last_index: int or None) -> bool:
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
