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

"""Module holding BitCountingGroup class."""

import copy

from .AvgStdevStats import AvgStdevStats
from .BitCountingStats import BitCountingStats


class BitCountingGroup:
    # TODO: Inherit from collections.abc.Sequence in Python 3.
    """Group of runs which tracks bit count in an efficient manner.

    This class contains methods that mutate the internal state,
    use copy() method to save the previous state.

    The Sequence-like access is related to the list of runs,
    for example group[0] returns the first run in the list.
    Writable list-like methods are not implemented.

    As the group bit count depends on previous average
    and overall maximal value, those values are assumed
    to be known beforehand (and immutable).

    As the caller is allowed to divide runs into groups in any way,
    a method to add a single run in an efficient manner is provided.
    """

    def __init__(self, run_list=None, stats=None, bits=None,
                 max_value=None, prev_avg=None, comment="unknown"):
        """Set the internal state and partially the stats.

        A "group" stands for an Iterable of runs, where "run" is either
        a float value, or a stats-like object (only size, avg and stdev
        are accessed). Run is a hypothetical abstract class,
        defining it in Python 2 is too much hassle.

        Only a copy of the run list argument value is stored in the instance,
        so it is not a problem if the value object is mutated afterwards.

        It is not verified whether the user provided values are valid,
        e.g. whether the stats and bits values reflect the runs.

        :param run_list: List of run to compose into this group. Default: empty.
        :param stats: Stats object used for computing bits.
        :param bits: Cached value of information content.
        :param max_value: Maximal sample value to be used for computing.
        :param prev_avg: Average of the previous group, affects bits.
        :param comment: Any string giving more info, e.g. "regression".
        :type run_list: Iterable[Run]
        :type stats: Optional[AvgStdevStats]
        :type bits: Optional[float]
        :type max_value: float
        :type prev_avg: Optional[float]
        :type comment: str
        """
        self.run_list = copy.deepcopy(run_list) if run_list else list()
        self.stats = stats
        self.cached_bits = bits
        self.max_value = max_value
        self.prev_avg = prev_avg
        self.comment = comment
        if self.stats is None:
            self.stats = AvgStdevStats.for_runs(self.run_list)

    def __str__(self):
        """Return string with human readable description of the group.

        :returns: Readable description.
        :rtype: str
        """
        return f"stats={self.stats} bits={self.cached_bits}"

    def __repr__(self):
        """Return string executable as Python constructor call.

        :returns: Executable constructor call.
        :rtype: str
        """
        return (
            f"BitCountingGroup(run_list={self.run_list!r},stats={self.stats!r}"
            f",bits={self.cached_bits!r},max_value={self.max_value!r}"
            f",prev_avg={self.prev_avg!r},comment={self.comment!r})"
        )

    def __getitem__(self, index):
        """Return the run at the index.

        :param index: Index of the run to return.
        :type index: int
        :returns: The run at the index.
        :rtype: Run
        """
        return self.run_list[index]

    def __len__(self):
        """Return the number of runs in the group.

        :returns: The Length of run_list.
        :rtype: int
        """
        return len(self.run_list)

    def copy(self):
        """Return a new instance with copied internal state.

        :returns: The copied instance.
        :rtype: BitCountingGroup
        """
        stats = AvgStdevStats.for_runs([self.stats])
        return self.__class__(
            run_list=self.run_list, stats=stats, bits=self.cached_bits,
            max_value=self.max_value, prev_avg=self.prev_avg,
            comment=self.comment)

    @property
    def bits(self):
        """Return overall bit content of the group list.

        If not cached, compute from stats and cache.

        :returns: The overall information content in bits.
        :rtype: float
        """
        if self.cached_bits is None:
            self.cached_bits = BitCountingStats.for_runs(
                [self.stats], self.max_value, self.prev_avg).bits
        return self.cached_bits

    def append(self, run):
        """Mutate to add the new run, return self.

        Stats are updated, but old bits value is deleted from cache.

        :param run: The run value to add to the group.
        :type value: Run
        :returns: The updated self.
        :rtype: BitCountingGroup
        """
        self.run_list.append(run)
        self.stats = AvgStdevStats.for_runs([self.stats, run])
        self.cached_bits = None
        return self

    def extend(self, runs):
        """Mutate to add the new runs, return self.

        This is saves small amount of computation
        compared to adding runs one by one in a loop.

        Stats are updated, but old bits value is deleted from cache.

        :param runs: The runs to add to the group.
        :type value: Iterable[Run]
        :returns: The updated self.
        :rtype: BitCountingGroup
        """
        self.run_list.extend(runs)
        self.stats = AvgStdevStats.for_runs([self.stats] + runs)
        self.cached_bits = None
        return self
