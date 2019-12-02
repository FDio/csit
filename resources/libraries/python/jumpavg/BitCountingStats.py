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

"""Module holding BitCountingStats class."""

import math

from AvgStdevStats import AvgStdevStats


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

    def __init__(
            self, size=0, avg=None, stdev=0.0, max_value=None, prev_avg=None):
        """Construct the stats object by computing from the values needed.

        The values are not sanitized, faulty callers can cause math errors.

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

        :param size: Number of values participating in this group.
        :param avg: Population average of the participating sample values.
        :param stdev: Population standard deviation of the sample values.
        :param max_value: Maximal expected value.
            TODO: This might be more optimal,
            but max-invariant algorithm will be nicer.
        :param prev_avg: Population average of the previous group.
            If None, no previous average is taken into account.
            If not None, the given previous average is used to discourage
            consecutive groups with similar averages
            (opposite triangle distribution is assumed).
        :type avg: float
        :type size: int
        :type stdev: float
        :type max_value: Union[float, NoneType]
        :type prev_avg: Union[float, NoneType]
        """
        self.avg = avg
        self.size = size
        self.stdev = stdev
        self.max_value = max_value
        self.prev_avg = prev_avg
        # Zero size should in principle have non-zero bits (coding zero size),
        # but zero allows users to add empty groups without affecting bits.
        self.bits = 0.0
        if self.size < 1:
            return
        if avg is None:
            raise ValueError(f"Avg is None: {self!r}")
        if max_value is None or max_value <= 0.0:
            raise ValueError(f"Invalid max value: {self!r}")
        # Length of the sequence must be also counted in bits,
        # otherwise the message would not be decodable.
        # Model: probability of k samples is 1/k - 1/(k+1) == 1/k/(k+1)
        # This is compatible with zero size leading to zero bits.
        self.bits += math.log(size * (size + 1), 2)
        if prev_avg is None:
            # Avg is considered to be uniformly distributed
            # from zero to max_value.
            self.bits += math.log(max_value + 1.0, 2)
        else:
            # Opposite triangle distribution with minimum.
            self.bits += math.log(
                max_value * (max_value + 1) / (abs(avg - prev_avg) + 1), 2)
        if self.size < 2:
            return
        # Stdev is considered to be uniformly distributed
        # from zero to max_value. That is quite a bad expectation,
        # but resilient to negative samples etc.
        self.bits += math.log(max_value + 1.0, 2)
        # Now we know the samples lie on sphere in size-1 dimensions.
        # So it is (size-2)-sphere, with radius^2 == stdev^2 * size.
        # https://en.wikipedia.org/wiki/N-sphere
        sphere_area_ln = math.log(2) + math.log(math.pi) * ((size - 1) / 2.0)
        sphere_area_ln -= math.lgamma((size - 1) / 2.0)
        sphere_area_ln += math.log(stdev + 1.0) * (size - 2)
        sphere_area_ln += math.log(size) * ((size - 2) / 2.0)
        self.bits += sphere_area_ln / math.log(2)

    def __str__(self):
        """Return string with human readable description of the group.

        :returns: Readable description.
        :rtype: str
        """
        return (
            f"size={self.size} avg={self.avg} stdev={self.stdev}"
            f" bits={self.bits}"
        )

    def __repr__(self):
        """Return string executable as Python constructor call.

        :returns: Executable constructor call.
        :rtype: str
        """
        return (
            f"BitCountingStats(size={self.size!r},avg={self.avg!r}"
            f",stdev={self.stdev!r},max_value={self.max_value!r}"
            f",prev_avg={self.prev_avg!r})"
        )

    @classmethod
    def for_runs(cls, runs, max_value=None, prev_avg=None):
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
        ret_obj = cls(size=asd.size, avg=asd.avg, stdev=asd.stdev,
                      max_value=max_value, prev_avg=prev_avg)
        return ret_obj
