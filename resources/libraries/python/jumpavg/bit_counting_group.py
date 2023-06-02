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

"""Module holding BitCountingGroup class."""

import collections
import dataclasses
import typing

from .avg_stdev_stats import AvgStdevStats
from .bit_counting_stats import BitCountingStats


@dataclasses.dataclass
class BitCountingGroup(collections.abc.Sequence):
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

    run_list: typing.List[typing.Union[float, AvgStdevStats]]
    """List of run to compose into this group.
    The init call takes ownership of the list,
    so the caller should clone it to avoid unexpected muations."""
    max_value: float
    """Maximal sample value to expect."""
    unit: float = 1.0
    """Typical resolution of the values"""
    comment: str = "normal"
    """Any string giving more info, e.g. "regression"."""
    prev_avg: typing.Optional[float] = None
    """Average of the previous group, if any."""
    stats: AvgStdevStats = None
    """Stats object used for computing bits.
    Almost always recomputed, except when non-None in init."""
    cached_bits: typing.Optional[float] = None
    """Cached value of information content.
    Noned on edit, recomputed if needed and None."""

    def __post_init__(self):
        """Recompute stats is None.

        It is not verified whether the user provided values are valid,
        e.g. whether the stats and bits values reflect the runs.
        """
        if self.stats is None:
            self.stats = AvgStdevStats.for_runs(runs=self.run_list)

    @property
    def bits(self) -> float:
        """Return overall bit content of the group list.

        If not cached, compute from stats and cache.

        :returns: The overall information content in bits.
        :rtype: float
        """
        if self.cached_bits is None:
            self.cached_bits = BitCountingStats.for_runs_and_params(
                runs=[self.stats],
                max_value=self.max_value,
                unit=self.unit,
                prev_avg=self.prev_avg,
            ).bits
        return self.cached_bits

    def __getitem__(self, index: int) -> typing.Union[float, AvgStdevStats]:
        """Return the run at the index.

        :param index: Index of the run to return.
        :type index: int
        :returns: The run at the index.
        :rtype: typing.Union[float, AvgStdevStats]
        """
        return self.run_list[index]

    def __len__(self) -> int:
        """Return the number of runs in the group.

        :returns: The Length of run_list.
        :rtype: int
        """
        return len(self.run_list)

    def copy(self) -> "BitCountingGroup":
        """Return a new instance with copied internal state.

        Stats are preserved to avoid re-computation.
        As both float and AvgStdevStats are effectively immutable,
        only a shallow copy of the runs list is performed.

        :returns: The copied instance.
        :rtype: BitCountingGroup
        """
        stats = AvgStdevStats.for_runs([self.stats])
        return self.__class__(
            run_list=list(self.run_list),
            stats=stats,
            cached_bits=self.cached_bits,
            max_value=self.max_value,
            unit=self.unit,
            prev_avg=self.prev_avg,
            comment=self.comment,
        )

    def append(
        self, run: typing.Union[float, AvgStdevStats]
    ) -> "BitCountingGroup":
        """Mutate to add the new run, return self.

        Stats are updated, but old bits value is deleted from cache.

        :param run: The run value to add to the group.
        :type value: typing.Union[float, AvgStdevStats]
        :returns: The updated self.
        :rtype: BitCountingGroup
        """
        self.run_list.append(run)
        self.stats = AvgStdevStats.for_runs([self.stats, run])
        self.cached_bits = None
        return self

    def extend(
        self, runs: typing.Iterable[typing.Union[float, AvgStdevStats]]
    ) -> "BitCountingGroup":
        """Mutate to add the new runs, return self.

        This is saves small amount of computation
        compared to adding runs one by one in a loop.

        Stats are updated, but old bits value is deleted from cache.

        :param runs: The runs to add to the group.
        :type value: typing.Iterable[typing.Union[float, AvgStdevStats]]
        :returns: The updated self.
        :rtype: BitCountingGroup
        """
        self.run_list.extend(runs)
        self.stats = AvgStdevStats.for_runs([self.stats] + runs)
        self.cached_bits = None
        return self
