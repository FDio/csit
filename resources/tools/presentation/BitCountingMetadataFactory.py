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

import math

from AvgStdevMetadata import AvgStdevMetadata
from AvgStdevMetadataFactory import AvgStdevMetadataFactory
from BitCountingMetadata import BitCountingMetadata


class BitCountingMetadataFactory(object):
    """Class for factory which creates bit counting metadata from data."""

    @staticmethod
    def find_max_value(values):
        """Return the max value.

        This is a separate helper method,
        because the set of values is usually larger than in from_data().

        :param values: Run values to be processed.
        :type values: Iterable of float
        :returns: 0.0 or the biggest value found.
        :rtype: float
        """
        max_value = 0.0
        for value in values:
            if isinstance(value, AvgStdevMetadata):
                if value.avg > max_value:
                    max_value = value.avg
            else:  # Assuming value is float.
                if value > max_value:
                    max_value = value
        return max_value

    def __init__(self, max_value):
        """Construct the factory instance with given max value.

        :param max_value: Maximal expected value.
        :type max_value: float
        """
        self.max_value = max_value

    def from_avg_stdev_metadata(self, metadata):
        """Return new metadata object by adding bits to existing metadata.

        :param metadata: Metadata to count bits for.
        :type metadata: AvgStdevMetadata
        :returns: The metadata with bits counted.
        :rtype: BitCountingMetadata
        """
        return BitCountingMetadata(
            max_value=self.max_value, size=metadata.size,
            avg=metadata.avg, stdev=metadata.stdev)

    def from_data(self, values):
        """Return new metadata object fitting the values.

        :param values: Run values to be processed.
        :type values: Iterable of float or of AvgStdevMetadata
        :returns: The metadata matching the values.
        :rtype: BitCountingMetadata
        """
        metadata = AvgStdevMetadataFactory.from_data(values)
        return self.from_avg_stdev_metadata(metadata)
