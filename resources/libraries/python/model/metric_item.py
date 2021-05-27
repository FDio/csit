# Copyright (c) 2021 Cisco and/or its affiliates.
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

"""Module with class containing one metric item.
"""


class metric_item():
    """A type for metric items.
    """
    def __init__(self, name, value, labels):
        """Store values.

        TODO: Should we support numeric label values?

        :param name: Metric item quantity name, e.g. "rx_packets".
        :param value: The value of the metric item.
        :param labels: Attributes to distinguish from similar items.
        :type name: str
        :type value: Union[int, float]
        :type labels: Mapping[str, str]
        """
        self.name = str(name)
        self.value = value
        self.labels = {str(key): str(labels[key]) for key in labels}

    def __eq__(self, other):
        """Return whether it is the same quantity.

        Values are not compared, so that adding a "new" value
        could replace the old one (depending on the code doing the add).
        Order of labels does not matter.
        Class/type is not compared.

        :param other: Metric item to compare self with.
        :returns: Whether name and labels are the same.
        """
        return self.name == other.name and self.labels == other.labels
