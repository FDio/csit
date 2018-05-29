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

"""Module holding AvgStdevMetadataFactory class."""

import math

from AvgStdevMetadata import AvgStdevMetadata


class AvgStdevMetadataFactory(object):
    """Class factory which creates avg,stdev metadata from data."""

    @staticmethod
    def from_data(values):
        """Return new metadata object fitting the values.

        :param values: Run values to be processed.
        :type values: Iterable of float or of AvgStdevMetadata
        :returns: The metadata matching the values.
        :rtype: AvgStdevMetadata
        """
        # Using Welford method to be more resistant to rounding errors.
        # Adapted from code for sample standard deviation at:
        # https://www.johndcook.com/blog/standard_deviation/
        # The logic of plus operator is taken from
        # https://www.johndcook.com/blog/skewness_kurtosis/
        size = 0
        avg = 0.0
        moment_2 = 0.0
        for value in values:
            if not isinstance(value, AvgStdevMetadata):
                value = AvgStdevMetadata(size=1, avg=value)
            old_size = size
            delta = value.avg - avg
            size += value.size
            avg += delta * value.size / size
            moment_2 += value.stdev * value.stdev * value.size
            moment_2 += delta * delta * old_size * value.size / size
        if size < 1:
            return AvgStdevMetadata()
        stdev = math.sqrt(moment_2 / size)
        ret_obj = AvgStdevMetadata(size=size, avg=avg, stdev=stdev)
        return ret_obj
