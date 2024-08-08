"""
Used to get, set and analyse serial packets stats.
"""
import logging
from typing import Optional
from vedirect_m8.exceptions import InputReadException, SettingInvalidException
from vedirect_m8.serutils import SerialUtils as Ut

__author__ = "Eli Serra"
__copyright__ = "Copyright 2020, Eli Serra"
__license__ = "MIT"

logging.basicConfig()
logger = logging.getLogger("vedirect")


class PacketGlobalStats:
    """
    Used to get, set and analyse serial packets stats.
    """
    def __init__(self):
        self._max_packets_ever = 0
        self._nb_bad_packets = 0
        self._serial_read_errors = 0
        self._serial_reconnection = 0
        self._is_linear_flow = True

    MAX_COUNTER_VALUE = 1000

    def reset_global_counters(self):
        """Reset global counters."""
        self._max_packets_ever = 0
        self._nb_bad_packets = 0
        self._serial_read_errors = 0
        self._serial_reconnection = 0

    def reset_global_stats(self):
        """Reset global stats."""
        self.reset_global_counters()
        self._is_linear_flow = True

    def has_nb_bad_packets(self) -> int:
        """Test if instance has nb_bad_packets."""
        return Ut.is_int(self._nb_bad_packets, mini=0)

    def get_nb_bad_packets(self) -> int:
        """Get nb_bad_packets counter."""
        return self._nb_bad_packets

    def add_nb_bad_packets(self) -> int:
        """Increment to nb_bad_packets counter."""
        if Ut.is_int(self._nb_bad_packets, mini=0)\
                and self._nb_bad_packets < self.MAX_COUNTER_VALUE:
            self._nb_bad_packets += 1
        else:
            self._nb_bad_packets = 1
        return self._nb_bad_packets

    def has_serial_read_errors(self) -> int:
        """Test if instance has read errors."""
        return Ut.is_int(self._serial_read_errors, mini=0)

    def get_serial_read_errors(self) -> int:
        """Get read_errors counter."""
        return self._serial_read_errors

    def add_serial_read_errors(self) -> int:
        """Increment to read_errors counter."""
        if Ut.is_int(self._serial_read_errors, mini=0)\
                and self._serial_read_errors < self.MAX_COUNTER_VALUE:
            self._serial_read_errors += 1
        else:
            self._serial_read_errors = 1
        return self._serial_read_errors

    def has_serial_reconnection(self) -> int:
        """Test if instance has serial_reconnection."""
        return Ut.is_int(self._serial_reconnection, mini=0)

    def get_serial_reconnection(self) -> int:
        """Get serial_reconnection counter."""
        return self._serial_reconnection

    def add_serial_reconnection(self) -> int:
        """Increment to serial_reconnection counter."""
        if Ut.is_int(self._serial_reconnection, mini=0)\
                and self._serial_reconnection < self.MAX_COUNTER_VALUE:
            self._serial_reconnection += 1
        else:
            self._serial_reconnection = 1
        return self._serial_reconnection

    def set_linear_flow(self, value: bool) -> bool:
        """Increment to read_errors counter."""
        self._is_linear_flow = value is True
        return self._is_linear_flow is True

    def is_linear_flow(self) -> int:
        """Get number of packets available on serial reader."""
        return self._is_linear_flow is True

    def has_good_read_stats(self) -> int:
        """Get number of packets available on serial reader."""
        return self.is_linear_flow()\
            and self.get_serial_read_errors() == 0\
            and self.get_nb_bad_packets() == 0\
            and self.get_serial_reconnection() == 0


class PacketStats(PacketGlobalStats):
    """
    Used to get, set and analyse serial packets stats.
    """
    def __init__(self,
                 nb_packets: int = 10,
                 accepted_keys: Optional[list] = None,
                 max_read_error: int = 0
                 ):
        PacketGlobalStats.__init__(self)
        self._nb_packets = 10
        self._max_read_error = 11
        self._stats = []
        self._accepted_keys = None
        self._set_nb_packets(nb_packets)
        self.set_accepted_keys(accepted_keys)
        self.set_max_read_error(
            value=max_read_error,
            default=self._nb_packets + 1
        )

    MAX_STAT_PACKETS, NB_PACKETS_SCAN = 20, 10

    def get_nb_packets(self) -> int:
        """Get number of packets available on serial reader."""
        return self._nb_packets

    def _set_nb_packets(self, value: int) -> int:
        """Set number of packets available on serial reader."""
        value = Ut.get_int(value, 0)
        self._nb_packets = self.NB_PACKETS_SCAN
        if self.MAX_STAT_PACKETS > value > 0:
            self._nb_packets = value
        return self._nb_packets

    def get_max_read_error(self) -> Optional[list]:
        """Get max_read_error value."""
        return self._max_read_error

    def set_max_read_error(self,
                           value: int,
                           default: Optional[int] = 0
                           ) -> bool:
        """Set max_read_error value."""
        result = False
        max_read_error = Ut.get_int(value, default)
        if max_read_error >= 0:
            self._max_read_error = max_read_error
            result = True
        return result

    def has_accepted_keys(self) -> Optional[list]:
        """Get number of packets available on serial reader."""
        return Ut.is_list(self._accepted_keys, not_null=True)

    def get_accepted_keys(self) -> Optional[list]:
        """Get number of packets available on serial reader."""
        return self._accepted_keys

    def set_accepted_keys(self, values: Optional[list]) -> bool:
        """Set accepted block keys on serial reader."""
        result = False
        self._accepted_keys = None
        if Ut.is_list(values, not_null=True):
            accepted_keys = [
                x
                for x in values
                if Ut.is_serial_key_pattern(x)
            ]
            if not len(values) == len(accepted_keys):
                raise SettingInvalidException(
                    "[PacketStats: set_accepted_keys] "
                    "Fatal Error: Invalid accepted_keys property values. "
                    "Can only contain alphanumeric character , '_' and '#'. "
                    "And must start by alphanumeric character or '#'"
                )
            self._accepted_keys = accepted_keys
            result = True
        return result

    def is_accepted_packet_keys(self, packet: dict) -> Optional[list]:
        """Test if packet keys contain only accepted keys if defined."""
        result = True
        if Ut.is_dict(packet, not_null=True)\
                and self.has_accepted_keys():
            packet_keys = list(packet.keys())
            for packet_key in packet_keys:
                if packet_key not in self._accepted_keys:
                    result = False
            if result is False:
                self.add_nb_bad_packets()
        return result

    def has_reached_max_errors(self,
                               raise_exception: bool = True
                               ) -> int:
        """Get number of packets available on serial reader."""
        result = False
        max_read_error = Ut.get_int(self.get_max_read_error(), default=-1)
        if max_read_error > 0:
            max_seial_read = self.get_serial_read_errors() >= max_read_error
            max_bad_packets = self.get_nb_bad_packets() >= max_read_error
            has_max_errors = max_seial_read\
                or max_bad_packets

            if raise_exception is True\
                    and has_max_errors:
                raise InputReadException(
                    "Fatal Error: "
                    "Max read errors reached. "
                    "Max Seial Read : "
                    f"{self.get_serial_read_errors()} / {max_read_error} "
                    "Max Malformed Packets : "
                    f"{self.get_nb_bad_packets()} / {max_read_error}"
                )
            if has_max_errors:
                result = True
        return result

    def init_nb_packets(self) -> int:
        """Initialise number of packets available on serial reader."""
        if self.has_stats():
            nb_packets = len(self._stats)
            self._set_nb_packets(nb_packets)
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
        Add packet stats.
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
                if PacketStats.is_equal_packet_stats(
                        stat=packet_stats,
                        last_stat=last_stat):
                    result = i
        return result

    def get_stats_packet_obj(self, packet: dict) -> dict:
        """Get packet stat item dictionary."""
        result = None
        stats_index = self.get_packet_index(packet)
        if stats_index >= 0:
            result = self._stats[stats_index]
        return result

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
        is_accepted_keys = self.is_accepted_packet_keys(
                packet=packet
            )
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
                "nb_resets": nb_resets,
                "has_accepted_keys": self.has_accepted_keys(),
                "is_accepted_keys": is_accepted_keys,
                "nb_bad_packets": self.get_nb_bad_packets()
            }
            stats_equal.update(index_stats)
            result = stats_equal
            if not is_linear:
                self.set_linear_flow(False)
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
                "nb_resets": nb_resets,
                "has_accepted_keys": self.has_accepted_keys(),
                "is_accepted_keys": is_accepted_keys,
                "nb_bad_packets": self.get_nb_bad_packets()
            }
            if not is_linear:
                stats_packet.update(new_stats)
                self.set_linear_flow(False)
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
