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

"""Module holding ClassifiedBitCountingMetadata class."""

from BitCountingMetadata import BitCountingMetadata


class ClassifiedBitCountingMetadata(BitCountingMetadata):
    """Class for metadata which includes classification.

    TODO: Can we create ClassifiedMetadata and inherit (also) from that?
    """

    def __init__(
            self, max_value, size=0, avg=0.0, stdev=0.0, prev_avg=None,
            classification=None):
        """Delegate to ancestor constructors and set classification.

        :param max_value: Maximal expected value.
        :param size: Number of values participating in this group.
        :param avg: Population average of the participating sample values.
        :param stdev: Population standard deviation of the sample values.
        :param prev_avg: Population average of the previous group.
            If None, no previous average is taken into account.
            If not None, the given previous average is used to discourage
            consecutive groups with similar averages
            (opposite triangle distribution is assumed).
        :param classification: Arbitrary object classifying this group.
        :type max_value: float
        :type size: int
        :type avg: float
        :type stdev: float
        :type prev_avg: float
        :type classification: object
        """
        super(ClassifiedBitCountingMetadata, self).__init__(
            max_value, size, avg, stdev, prev_avg)
        self.classification = classification

    def __str__(self):
        """Return string with human readable description of the group.

        :returns: Readable description.
        :rtype: str
        """
        # str(super(...)) describes the proxy, not the proxied object.
        super_str = super(ClassifiedBitCountingMetadata, self).__str__()
        return super_str + " classification={classification}".format(
            classification=self.classification)

    def __repr__(self):
        """Return string executable as Python constructor call.

        :returns: Executable constructor call.
        :rtype: str
        """
        return ("ClassifiedBitCountingMetadata(max_value={max_value}," +
                "size={size},avg={avg},stdev={stdev},prev_avg={prev_avg}," +
                "classification={cls})").format(
                    max_value=self.max_value, size=self.size, avg=self.avg,
                    stdev=self.stdev, prev_avg=self.prev_avg,
                    cls=self.classification)
