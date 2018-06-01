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

from BitCountingGroup import BitCountingGroup
from BitCountingGroupList import BitCountingGroupList
from BitCountingMetadataFactory import BitCountingMetadataFactory
from ClassifiedMetadataFactory import ClassifiedMetadataFactory


class BitCountingClassifier(object):

    @staticmethod
    def classify(values):
        """Return the values in groups of optimal bit count.

        :param values: Sequence of runs to classify.
        :type values: Iterable of float or of AvgStdevMetadata
        :returns: Classified group list.
        :rtype: list of BitCountingGroup
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
        average = None
        for group in partition:
            if average is None:
                average = group.metadata.avg
            if group.metadata.avg == average:
                group.metadata = ClassifiedMetadataFactory.add_classification(
                    group.metadata, "normal")
                average = group.metadata.avg
            elif group.metadata.avg < average:
                group.metadata = ClassifiedMetadataFactory.add_classification(
                    group.metadata, "regression")
                average = group.metadata.avg
            elif group.metadata.avg > average:
                group.metadata = ClassifiedMetadataFactory.add_classification(
                    group.metadata, "progression")
                average = group.metadata.avg
        return partition.group_list
