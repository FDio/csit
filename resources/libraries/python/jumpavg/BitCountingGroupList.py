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

from BitCountingGroup import BitCountingGroup


class BitCountingGroupList:
    # TODO: Inherit from collections.abc.Sequence in Python 3.
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

    def __init__(self, group_list=None, bits_except_last=0.0, max_value=None):
        """Set the internal state without any calculations.

        The group list argument is copied deeply, so it is not a problem
        if the value object is mutated afterwards.

        A "group" stands for an Iterable of runs, where "run" is either
        a float value, or a stats-like object (only size, avg and stdev
        are accessed). Run is a hypothetical abstract class,
        defining it in Python 2 is too much hassle.

        It is not verified whether the user provided values are valid,
        e.g. whether the cached bits values make sense.

        The max_value is required and immutable,
        it is recommended the callers find their maximum beforehand.

        :param group_list: List of groups to compose this group list (or empty).
        :param bits_except_last: Partial sum of all but one group bits.
        :param max_value: Maximal sample value to base bits computation on.
        :type group_list: Iterable[BitCountingGroup]
        :type bits_except_last: float
        :type max_value: float
        """
        self.group_list = copy.deepcopy(group_list) if group_list else list()
        self.bits_except_last = bits_except_last
        self.max_value = max_value

    def __str__(self):
        """Return string with human readable description of the group list.

        :returns: Readable description.
        :rtype: str
        """
        return u"group_list={self.group_list} bits={self.bits}"

    def __repr__(self):
        """Return string executable as Python constructor call.

        :returns: Executable constructor call.
        :rtype: str
        """
        return (
            f"BitCountingGroupList(group_list={self.group_list!r}"
            f",bits_except_last={self.bits_except_last!r}"
            f",max_value={self.max_value!r})"
        )

    def __getitem__(self, index):
        """Return the group at the index.

        :param index: Index of the group to return.
        :type index: int
        :returns: The group at the index.
        :rtype: BitCountingGroup
        """
        return self.group_list[index]

    def __len__(self):
        """Return the length of the group list.

        :returns: The Length of group_list.
        :rtype: int
        """
        return len(self.group_list)

    def copy(self):
        """Return a new instance with copied internal state.

        :returns: The copied instance.
        :rtype: BitCountingGroupList
        """
        return self.__class__(
            group_list=self.group_list, bits_except_last=self.bits_except_last,
            max_value=self.max_value
        )

    @property
    def bits(self):
        """Return overall bit content of the group list.

        :returns: The overall information content in bits.
        :rtype: float
        """
        if not self.group_list:
            return 0.0
        # TODO: Is it worth to cache the overall result?
        return self.bits_except_last + self.group_list[-1].bits

    def append_group_of_runs(self, runs):
        """Mutate to add a new group based on the runs, return self.

        The argument is copied before adding to the group list,
        so further edits do not affect the grup list.
        The argument can also be a group, only runs from it are used.

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
            new_group.prev_avg = prev_avg
            new_group.cached_bits = None
        else:
            new_group = BitCountingGroup(
                run_list=runs, max_value=self.max_value, prev_avg=prev_avg)
        self.bits_except_last = self.bits
        self.group_list.append(new_group)
        return self

    def append_run_to_to_last_group(self, run):
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

    def extend_runs_to_last_group(self, runs):
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
