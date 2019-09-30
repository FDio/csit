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

"""Module holding BitCountingClassifier class.

This is the main class to be used by callers."""

from AbstractGroupClassifier import AbstractGroupClassifier
from BitCountingGroup import BitCountingGroup
from BitCountingGroupList import BitCountingGroupList
from BitCountingMetadataFactory import BitCountingMetadataFactory
from ClassifiedMetadataFactory import ClassifiedMetadataFactory


class BitCountingClassifier(AbstractGroupClassifier):
    """Classifier using Minimal Description Length principle."""

    def classify(self, values):
        """Return the values in groups of optimal bit count.

        The current implementation could be a static method,
        but we might support options in later versions,
        for example for chosing encodings.

        :param values: Sequence of runs to classify.
        :type values: Iterable of float or of AvgStdevMetadata
        :returns: Classified group list.
        :rtype: BitCountingGroupList
        """
        max_value = BitCountingMetadataFactory.find_max_value(values)
        factory = BitCountingMetadataFactory(max_value)
        opened_at = []
        closed_before = [BitCountingGroupList()]
        for index, value in enumerate(values):
            singleton = BitCountingGroup(factory, [value])
            newly_opened = closed_before[index].with_group_appended(singleton)
            opened_at.append(newly_opened)
            record_group_list = newly_opened
            for previous in range(index):
                previous_opened_list = opened_at[previous]
                still_opened = (
                    previous_opened_list.with_value_added_to_last_group(value))
                opened_at[previous] = still_opened
                if still_opened.bits < record_group_list.bits:
                    record_group_list = still_opened
            closed_before.append(record_group_list)
        partition = closed_before[-1]
        previous_average = partition[0].metadata.avg
        for group in partition:
            if group.metadata.avg == previous_average:
                group.metadata = ClassifiedMetadataFactory.with_classification(
                    group.metadata, "normal")
            elif group.metadata.avg < previous_average:
                group.metadata = ClassifiedMetadataFactory.with_classification(
                    group.metadata, "regression")
            elif group.metadata.avg > previous_average:
                group.metadata = ClassifiedMetadataFactory.with_classification(
                    group.metadata, "progression")
            previous_average = group.metadata.avg
        return partition
