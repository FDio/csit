# Copyright (c) 2018 Cisco and/or its affiliates.
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

"""Module holding BitCountingMetadata class."""

import math

from AvgStdevMetadata import AvgStdevMetadata


class BitCountingMetadata(AvgStdevMetadata):
    """Class for metadata which includes information content of a group.

    The information content is based on an assumption
    that the data consists of independent random values
    from a normal distribution.
    """

    def __init__(self, max_value, size=0, avg=0.0, stdev=0.0, prev_avg=None):
        """Construct the metadata by computing from the values needed.

        The bit count is not real, as that would depend on numeric precision
        (number of significant bits in values).
        The difference is assumed to be constant per value,
        which is consistent with Gauss distribution
        (but not with floating point mechanic).
        The hope is the difference will have
        no real impact on the classification procedure.

        :param max_value: Maximal expected value.
            TODO: This might be more optimal,
            but max-invariant algorithm will be nicer.
        :param size: Number of values participating in this group.
        :param avg: Population average of the participating sample values.
        :param stdev: Population standard deviation of the sample values.
        :param prev_avg: Population average of the previous group.
            If None, no previous average is taken into account.
            If not None, the given previous average is used to discourage
            consecutive groups with similar averages
            (opposite triangle distribution is assumed).
        :type max_value: float
        :type size: int
        :type avg: float
        :type stdev: float
        :type prev_avg: float or None
        """
        super(BitCountingMetadata, self).__init__(size, avg, stdev)
        self.max_value = max_value
        self.prev_avg = prev_avg
        self.bits = 0.0
        if self.size < 1:
            return
        # Length of the sequence must be also counted in bits,
        # otherwise the message would not be decodable.
        # Model: probability of k samples is 1/k - 1/(k+1)
        # == 1/k/(k+1)
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
        return "size={size} avg={avg} stdev={stdev} bits={bits}".format(
            size=self.size, avg=self.avg, stdev=self.stdev, bits=self.bits)

    def __repr__(self):
        """Return string executable as Python constructor call.

        :returns: Executable constructor call.
        :rtype: str
        """
        return ("BitCountingMetadata(max_value={max_value},size={size}," +
                "avg={avg},stdev={stdev},prev_avg={prev_avg})").format(
                    max_value=self.max_value, size=self.size, avg=self.avg,
                    stdev=self.stdev, prev_avg=self.prev_avg)
