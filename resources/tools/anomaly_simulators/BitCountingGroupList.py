
from BitCountingGroup import BitCountingGroup


class BitCountingGroupList(object):

    def __init__(self, group_list=[], bits=None):
        """Create a group list from given list of groups.

        :param group_list: List of groups to compose this group.
        :param bits: Bit count if known, else None.
        :type group_list: list of BitCountingGroup
        :type bits: float or None
        """
        self.group_list = group_list
        if bits is not None:
            self.bits = bits
            return
        bits = 0.0
        for group in group_list:
            bits += group.metadata.bits
        self.bits = bits

    def __getitem__(self, index):
        """Return group at the index. this makes self iterable.

        :param index: The position in the array of groups.
        :type index: int
        :returns: Group at the position.
        :rtype: BitCountingGroup
        """
        return self.group_list[index]

    def with_group_appended(self, group):
        """Create and return new group list with given group more than self.

        :param group: Next group to be appended to the group list.
        :type group: BitCountingGroup
        :returns: New group list with added group.
        :rtype: BitCountingGroupList
        """
        group_list = list(self.group_list)
        group_list.append(group)
        bits = self.bits + group.metadata.bits
        return BitCountingGroupList(group_list, bits)

    def with_value_added_to_last_group(self, value):
        """Create and return new group list with value added to last group.

        :param value: The run value to add to the last group.
        :type value: float or od AvgStdevMetadata
        :returns: New group list with the last group updated.
        :rtype: BitCountingGroupList
        """
        last_group = self.group_list[-1]
        bits_before = last_group.metadata.bits
        last_group = last_group.with_run_added(value)
        group_list = list(self.group_list)
        group_list[-1] = last_group
        bits = self.bits - bits_before + last_group.metadata.bits
        return BitCountingGroupList(group_list, bits)
