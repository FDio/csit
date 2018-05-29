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

"""Module holding BitCountingGroup class."""

from RunGroup import RunGroup


class BitCountingGroup(RunGroup):
    """RunGroup with BitCountingMetadata.

    Support with_run_added() method to simplify extending the group.
    As bit content has to be re-counted, metadata factory is stored.
    """

    def __init__(self, metadata_factory, values=[]):
        """Create the group from metadata factory and values.

        :param metadata_factory: Factory object to create metadata with.
        :param values: The runs belonging to this group.
        :type metadata_factory: BitCountingMetadataFactory
        :type values: Iterable of float or of AvgStdevMetadata
        """
        self.metadata_factory = metadata_factory
        metadata = metadata_factory.from_data(values)
        super(BitCountingGroup, self).__init__(metadata, values)

    def with_run_added(self, value):
        """Create and return a new group with one more run that self.

        :param value: The run value to add to the group.
        :type value: float or od AvgStdevMetadata
        :returns: New group with the run added.
        :rtype: BitCountingGroup
        """
        values = list(self.values)
        values.append(value)
        return BitCountingGroup(self.metadata_factory, values)
        # TODO: Is there a good way to save some computation
        # by copy&updating the metadata incrementally?
