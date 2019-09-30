# Copyright (c) 2019 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module holding BitCountingGroupList class."""

import copy

#from BitCountingGroup import BitCountingGroup
from .BitCountingStats import BitCountingStats


class BitCountingGroupList(object):
    """List of data groups which tracks overall bit count.

    The overall bit count is the sum of bit counts of each group.
    Group is a sequence of data samples accompanied by their stats.
    Different partitioning of data samples into the groups
    results in different overall bit count.
    This can be used to group samples in various contexts.

    As the group bit count depends on previous average
    and overall maximal value, order of groups is important.
    Having the logic encapsulated here spares the caller
    the effort to pass averages around.

    The data can be only added, and there is some logic to skip
    recalculations if the bit count is not needed.

    TODO: Split off AvgStdevStats to speed up thing when samples are added
    one by one.
    """

    def __init__(self, group_list=[], stats_list=[], bit_sum_list=[],
                 first_invalid=0, max_value=0.0):
        """Set the internal state without any calculations.

        A "group" stands for an Iterable of runs, where "run" is either
        a float value, or a stats-like object (only size, avg and stdev
        and max_value are accessed). Run is a hypothetical abstract class,
        defining it in Python 2 is too much hassle.

        The first_invalid field is used to track which part of computation
        can be skipped. It points to the index of first group which has
        incorrect bit content stored (as partial sum with previous groups).
        Value of 0 means no partial sum is valid,
        value of len(group_list) means all bit sums are valid.

        It is not verified whether the user provided values are valid,
        e.g. whether the two lists have the same length,
        or whether the bit sums are correct up to last_valid.

        The max_value field is always updated, others only on accessing bits.

        :param group_list: List of groups to compose this group list.
        :param stats_list: List of stats instances computed from groups.
        :param bits_sum_list: List of partial sums of groups' bits.
        :param first_invalid: Index of first invalid partial sum.
        :param max_value: Maximal sample value within the group list.
        :type group_list: Iterable[Iterable[Run]]
        :type stats_list: Iterable[BitCountingStats]
        :type bits_sum_list: List[float]
        :type first_invalid: int
        :type max_value: float
        """
        self.group_list = copy.deepcopy(group_list)
        self.stats_list = copy.deepcopy(stats_list)
        self.bit_sum_list = copy.deepcopy(bit_sum_list)
        self.first_invalid = first_invalid
        self.max_value = max_value

    @property
    def bits(self):
        """Return overall bit content of the group list.

        :returns: The overall information content in bits.
        :rtype: float
        """
        index = self.first_invalid
        while index < len(group_list):
            prev_avg = stats_list[index - 1] if index else None
            stats = BitCountingStats.for_runs(
                group_list[index], self.max_value, prev_avg)
            stats_list[index] = stats
            prev_bits = bit_sum_list[index - 1] if index else 0.0
            bit_sum_list[index] = prev_bits + stats.bits
            index += 1
        self.first_invalid = index
        return bit_sum_list[-1] if bit_sum_list else 0.0

    def _get_max_value(self, group):
        """Return max value after adding data from group.

        Internal function, just a form of de-duplicating code.
        For adding a single run, use 1-tuple as the group.

        :params group: Next group to be appended to the group list.
        :type group: Iterable[Run]
        :returns: New overall maximal value.
        :rtype: float
        """
        new_max_value = self.max_value
        for run in group:
            if isinstance(run, float):
                run_max_value = run
            else:
                run_max_value = run.max_value
            if run_max_value > new_max_value:
                new_max_value = run_max_value
        return new_max_value

    def with_group_appended(self, group):
        """Create and return a new group list with given group more than self.

        :param group: Next group to be appended to the group list.
        :type group: Iterable[Run]
        :returns: New group list with added group.
        :rtype: BitCountingGroupList
        """
        group_list = copy.deepcopy(self.group_list).append(group)
        stats_list = copy.deepcopy(self.stats_list).append(None)
        bit_sum_list = copy.deepcopy(self.bit_sum_list).append(None)
        max_value = self._get_max_value(group)
        first_invalid = 0 if max_value > self.max_value else self.first_invalid
        ret_obj = BitCountingGroupList(
            group_list, stats_list, bit_sum_list, first_invalid, max_value)
        return ret_obj

#####

    def with_value_added_to_last_group(self, value):
        """Create and return new group list with value added to last group.

        :param value: The run value to add to the last group.
        :type value: float or od AvgStdevMetadata
        :returns: New group list with the last group updated.
        :rtype: BitCountingGroupList
        """
        group_list = list(self)
        last_group = group_list[-1]
        bits_before = last_group.metadata.bits
        last_group = last_group.with_run_added(value)
        group_list[-1] = last_group
        bits = self.bits - bits_before + last_group.metadata.bits
        return BitCountingGroupList(group_list, bits)
