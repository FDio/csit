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

from ClassifiedBitCountingMetadata import ClassifiedBitCountingMetadata


class ClassifiedMetadataFactory(object):
    """Class for factory which adds classification to bit counting metadata."""

    @staticmethod
    def with_classification(metadata, classification):
        """Return new metadata object with added classification.

        TODO: Is there a way to add classification to any metadata,
        without messing up constructors and __repr__()?

        FIXME: Factories take raw resources. Find a name for the thing
        which takes semi-finished products. Transformer?

        :param metadata: Existing metadata without classification.
        :param classification: Arbitrary object classifying this group.
        :type metadata: BitCountingMetadata
        :type classification: object
        :returns: The metadata with added classification.
        :rtype: ClassifiedBitCountingMetadata
        """
        return ClassifiedBitCountingMetadata(
            max_value=metadata.max_value, size=metadata.size, avg=metadata.avg,
            stdev=metadata.stdev, prev_avg=metadata.prev_avg,
            classification=classification)
