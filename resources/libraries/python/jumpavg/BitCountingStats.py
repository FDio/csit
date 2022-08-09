# Copyright (c) 2022 Cisco and/or its affiliates.
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

from .AvgStdevStats import AvgStdevStats


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
        # Length of the sequence must be also counted in bits,
        # otherwise the message would not be decodable.
        # Model: probability of k samples is 1/k - 1/(k+1) == 1/k/(k+1)
        # This is compatible with zero size leading to zero bits.
        self.bits += math.log(self.size * (self.size + 1), 2)
        if self.prev_avg is None:
            # Avg is considered to be uniformly distributed
            # from zero to max_value.
            self.bits += math.log(self.max_value + 1.0, 2)
        else:
            # Opposite triangle distribution with minimum.
            self.bits += math.log(
                (self.max_value * (self.max_value + 1))
                / (abs(self.avg - self.prev_avg) + 1),
                2,
            )
        if self.size < 2:
            return
        # Stdev is considered to be uniformly distributed
        # from zero to max_value. That is quite a bad expectation,
        # but resilient to negative samples etc.
        self.bits += math.log(self.max_value + 1.0, 2)
        # Now we know the samples lie on sphere in size-1 dimensions.
        # So it is (size-2)-sphere, with radius^2 == stdev^2 * size.
        # https://en.wikipedia.org/wiki/N-sphere
        sphere_area_ln = math.log(2)
        sphere_area_ln += math.log(math.pi) * ((self.size - 1) / 2.0)
        sphere_area_ln -= math.lgamma((self.size - 1) / 2.0)
        sphere_area_ln += math.log(self.stdev + 1.0) * (self.size - 2)
        sphere_area_ln += math.log(self.size) * ((self.size - 2) / 2.0)
        self.bits += sphere_area_ln / math.log(2)

    # TODO: Rename, so pylint stops complaining about signature change.
    @classmethod
    def for_runs(
        cls,
        runs: typing.Iterable[typing.Union[float, AvgStdevStats]],
        max_value: float,
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
        :param prev_avg: Population average of the previous group, if any.
        :type runs: Iterable[Union[float, AvgStdevStats]]
        :type max_value: Union[float, NoneType]
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
            prev_avg=prev_avg,
        )
        return ret_obj
