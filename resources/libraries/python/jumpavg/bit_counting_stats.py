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

"""Module holding BitCountingStats class."""

import dataclasses
import math
import typing

from .avg_stdev_stats import AvgStdevStats


@dataclasses.dataclass
class BitCountingStats(AvgStdevStats):
    """Class for statistics which include information content of a group.

    The information content is based on an assumption that the data
    consists of independent random values from a normal distribution.

    Instances are only statistics, the data itself is stored elsewhere.

    The coding needs to know the previous average, and a maximal value
    so both values are required as inputs.

    This is a subclass of AvgStdevStats, even though all methods are overriden.
    Only for_runs method calls the parent implementation, without using super().
    """

    max_value: float = None
    """Maximal sample value (real or estimated).
    Default value is there just for argument ordering reasons,
    leaving None leads to exceptions."""
    unit: float = 1.0
    """Typical resolution of the values."""
    prev_avg: typing.Optional[float] = None
    """Population average of the previous group (if any)."""
    bits: float = None
    """The computed information content of the group.
    It is formally an argument to init function, just to keep repr string
    a valid call. ut the init value is ignored and always recomputed.
    """

    def __post_init__(self):
        """Construct the stats object by computing from the values needed.

        The None values are allowed for stats for zero size data,
        but such stats can report arbitrary avg and max_value.
        Stats for nonzero size data cannot contain None,
        else ValueError is raised.

        The max_value needs to be numeric for nonzero size,
        but its relations to avg and prev_avg are not examined.

        The bit count is not real, as that would depend on numeric precision
        (number of significant bits in values).
        The difference is assumed to be constant per value,
        which is consistent with Gauss distribution
        (but not with floating point mechanic).
        The hope is the difference will have
        no real impact on the classification procedure.
        """
        # Zero size should in principle have non-zero bits (coding zero size),
        # but zero allows users to add empty groups without affecting bits.
        self.bits = 0.0
        if self.size < 1:
            return
        if self.max_value <= 0.0:
            raise ValueError(f"Invalid max value: {self!r}")
        max_value = self.max_value / self.unit
        avg = self.avg / self.unit
        # Length of the sequence must be also counted in bits,
        # otherwise the message would not be decodable.
        # Model: probability of k samples is 1/k - 1/(k+1) == 1/k/(k+1)
        # This is compatible with zero size leading to zero bits.
        self.bits += math.log(self.size * (self.size + 1), 2)
        if self.prev_avg is None:
            # Avg is considered to be uniformly distributed
            # from zero to max_value.
            self.bits += math.log(max_value + 1, 2)
        else:
            # Opposite triangle distribution with minimum.
            prev_avg = self.prev_avg / self.unit
            norm = prev_avg * prev_avg
            norm -= (prev_avg - 1) * max_value
            norm += max_value * max_value / 2
            self.bits -= math.log((abs(avg - prev_avg) + 1) / norm, 2)
        if self.size < 2:
            return
        stdev = self.stdev / self.unit
        # Stdev can be anything between zero and max value.
        # For size==2, sphere surface is 2 points regardless of radius,
        # we need to penalize large stdev already when encoding the stdev.
        # The simplest way is to use the same distribution as with size...
        self.bits += math.log((stdev + 1) * (stdev + 2), 2)
        # .. just with added normalization from the max value cut-off.
        self.bits += math.log(1 - 1 / (max_value + 2), 2)
        # Now we know the samples lie on sphere in size-1 dimensions.
        # So it is (size-2)-sphere, with radius^2 == stdev^2 * size.
        # https://en.wikipedia.org/wiki/N-sphere
        sphere_area_ln = math.log(2)
        sphere_area_ln += math.log(math.pi) * ((self.size - 1) / 2)
        sphere_area_ln -= math.lgamma((self.size - 1) / 2)
        sphere_area_ln += math.log(stdev + 1) * (self.size - 2)
        sphere_area_ln += math.log(self.size) * ((self.size - 2) / 2)
        self.bits += sphere_area_ln / math.log(2)

    @classmethod
    def for_runs_and_params(
        cls,
        runs: typing.Iterable[typing.Union[float, AvgStdevStats]],
        max_value: float,
        unit: float = 1.0,
        prev_avg: typing.Optional[float] = None,
    ):
        """Return new stats instance describing the sequence of runs.

        If you want to append data to existing stats object,
        you can simply use the stats object as the first run.

        Instead of a verb, "for" is used to start this method name,
        to signify the result contains less information than the input data.

        The two optional values can come from outside of the runs provided.

        The max_value cannot be None for non-zero size data.
        The implementation does not check if no datapoint exceeds max_value.

        TODO: Document the behavior for zero size result.

        :param runs: Sequence of data to describe by the new metadata.
        :param max_value: Maximal expected value.
        :param unit: Typical resolution of the values.
        :param prev_avg: Population average of the previous group, if any.
        :type runs: Iterable[Union[float, AvgStdevStats]]
        :type max_value: Union[float, NoneType]
        :type unit: float
        :type prev_avg: Union[float, NoneType]
        :returns: The new stats instance.
        :rtype: cls
        """
        asd = AvgStdevStats.for_runs(runs)
        ret_obj = cls(
            size=asd.size,
            avg=asd.avg,
            stdev=asd.stdev,
            max_value=max_value,
            unit=unit,
            prev_avg=prev_avg,
        )
        return ret_obj
