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

"""Module holding RunGroup class."""


class RunGroup(object):
    """Effectively a named touple of data and metadata.

    TODO: This feels like an abstract class.
    Most uses assume restrictions on metadata type.
    Can this be defined similarly to C++ templates?
    """

    def __init__(self, metadata, values):
        """Create the group from metadata and values.

        :param metadata: Metadata object to associate with the group.
        :param values: The runs belonging to this group.
        :type metadata: AbstractGroupMetadata
        :type values: Iterable of float or od AvgStdevMetadata
        """
        self.metadata = metadata
        self.values = values
