# Copyright (c) 2023 Cisco and/or its affiliates.
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

import collections
import dataclasses
import typing

from .avg_stdev_stats import AvgStdevStats  # Just for type hints.
from .bit_counting_group import BitCountingGroup


@dataclasses.dataclass
class BitCountingGroupList(collections.abc.Sequence):
    """List of data groups which tracks overall bit count.

    The Sequence-like access is related to the list of groups,
    for example group_list[0] returns the first group in the list.
    Writable list-like methods are not implemented.

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
    """

    max_value: float
    """Maximal sample value to base bits computation on."""
    unit: float = 1.0
    """Typical resolution of the values."""
    group_list: typing.List[BitCountingGroup] = None
    """List of groups to compose this group list.
    Init also accepts None standing for an empty list.
    This class takes ownership of the list,
    so caller of init should clone their copy to avoid unexpected mutations.
    """
    bits_except_last: float = 0.0
    """Partial sum of all but one group bits."""

    def __post_init__(self):
        """Turn possible None into an empty list.

        It is not verified whether the user provided values are valid,
        e.g. whether the cached bits values (and bits_except_last) make sense.
        """
        if self.group_list is None:
            self.group_list = []

    def __getitem__(self, index: int) -> BitCountingGroup:
        """Return the group at the index.

        :param index: Index of the group to return.
        :type index: int
        :returns: The group at the index.
        :rtype: BitCountingGroup
        """
        return self.group_list[index]

    def __len__(self) -> int:
        """Return the length of the group list.

        :returns: The Length of group_list.
        :rtype: int
        """
        return len(self.group_list)

    def copy(self) -> "BitCountingGroupList":
        """Return a new instance with copied internal state.

        :returns: The copied instance.
        :rtype: BitCountingGroupList
        """
        return self.__class__(
            max_value=self.max_value,
            unit=self.unit,
            group_list=[group.copy() for group in self.group_list],
            bits_except_last=self.bits_except_last,
        )

    def copy_fast(self) -> "BitCountingGroupList":
        """Return a new instance with minimaly copied internal state.

        The assumption here is that only the last group will ever be mutated
        (in self, probably never in the return value),
        so all the previous groups can be "copied by reference".

        :returns: The copied instance.
        :rtype: BitCountingGroupList
        """
        group_list = list(self.group_list)
        if group_list:
            group_list[-1] = group_list[-1].copy()
            # Further speedup is possible by keeping the last group
            # as a singly linked (from end) list,
            # but for CSIT sample sizes, copy of whole Python list is faster.
            # TODO: Implement linked list as an option
            # for users with many samples.
        return self.__class__(
            max_value=self.max_value,
            unit=self.unit,
            group_list=group_list,
            bits_except_last=self.bits_except_last,
        )

    @property
    def bits(self) -> float:
        """Return overall bit content of the group list.

        :returns: The overall information content in bits.
        :rtype: float
        """
        if not self.group_list:
            return 0.0
        # TODO: Is it worth to cache the overall result?
        return self.bits_except_last + self.group_list[-1].bits

    def append_group_of_runs(
        self,
        runs: typing.Union[
            BitCountingGroup, typing.List[typing.Union[float, AvgStdevStats]]
        ],
    ) -> "BitCountingGroupList":
        """Mutate to add a new group based on the runs, return self.

        The list argument is NOT copied before adding to the group list,
        so further edits MAY not affect the grup list.
        The list from BitCountingGroup is shallow copied though.

        :param runs: Runs to form the next group to be appended to self.
        :type runs: Union[Iterable[Run], BitCountingGroup]
        :returns: The updated self.
        :rtype: BitCountingGroupList
        """
        prev_avg = self.group_list[-1].stats.avg if self.group_list else None
        if isinstance(runs, BitCountingGroup):
            # It is faster to avoid stats recalculation.
            new_group = runs.copy()
            new_group.max_value = self.max_value
            # Unit is common.
            new_group.prev_avg = prev_avg
            new_group.cached_bits = None
        else:
            new_group = BitCountingGroup(
                run_list=runs,
                max_value=self.max_value,
                unit=self.unit,
                prev_avg=prev_avg,
            )
        self.bits_except_last = self.bits
        self.group_list.append(new_group)
        return self

    def append_run_to_to_last_group(
        self, run: typing.Union[float, AvgStdevStats]
    ) -> "BitCountingGroupList":
        """Mutate to add new run at the end of the last group.

        Basically a one-liner, only returning group list instead of last group.

        :param run: The run value to add to the last group.
        :type run: Run
        :returns: The updated self.
        :rtype: BitCountingGroupList
        :raises IndexError: If group list is empty, no last group to add to.
        """
        self.group_list[-1].append(run)
        return self

    def extend_runs_to_last_group(
        self, runs: typing.Iterable[typing.Union[float, AvgStdevStats]]
    ) -> "BitCountingGroupList":
        """Mutate to add new runs to the end of the last group.

        A faster alternative to appending runs one by one in a loop.

        :param runs: The runs to add to the last group.
        :type runs: Iterable[Run]
        :returns: The updated self
        :rtype: BitCountingGroupList
        :raises IndexError: If group list is empty, no last group to add to.
        """
        self.group_list[-1].extend(runs)
        return self
