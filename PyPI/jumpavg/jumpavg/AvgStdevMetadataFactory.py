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
        sum_0 = 0
        sum_1 = 0.0
        sum_2 = 0.0
        for value in values:
            if isinstance(value, AvgStdevMetadata):
                sum_0 += value.size
                sum_1 += value.avg * value.size
                sum_2 += value.stdev * value.stdev * value.size
                sum_2 += value.avg * value.avg * value.size
            else:  # The value is assumed to be float.
                sum_0 += 1
                sum_1 += value
                sum_2 += value * value
        if sum_0 < 1:
            return AvgStdevMetadata()
        avg = sum_1 / sum_0
        stdev = math.sqrt(sum_2 / sum_0 - avg * avg)
        ret_obj = AvgStdevMetadata(size=sum_0, avg=avg, stdev=stdev)
        return ret_obj
