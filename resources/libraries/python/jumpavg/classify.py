# Copyright (c) 2019 Cisco and/or its affiliates.
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

"""Module holding the classify function

Classification os one of primary purposes of this package.

Minimal message length principle is used
for grouping results into the list of groups,
assuming each group is a population of different Gaussian distribution.
"""

from .AvgStdevStats import AvgStdevStats
from .BitCountingGroupList import BitCountingGroupList


def classify(values):
    """Return the values in groups of optimal bit count.

    Here, a value is either a float, or an iterable of floats.
    Such iterables represent an undivisible sequence of floats.

    Internally, such sequence is replaced by AvgStdevStats
    after maximal value is found.

    :param values: Sequence of runs to classify.
    :type values: Iterable[Union[float, Iterable[float]]]
    :returns: Classified group list.
    :rtype: BitCountingGroupList
    """
    processed_values = list()
    max_value = 0.0
    for value in values:
        if isinstance(value, (float, int)):
            if value > max_value:
                max_value = value
            processed_values.append(value)
        else:
            for subvalue in value:
                if subvalue > max_value:
                    max_value = subvalue
            processed_values.append(AvgStdevStats.for_runs(value))
    open_at = list()
    closed_before = [BitCountingGroupList(max_value=max_value)]
    for index, value in enumerate(processed_values):
        newly_open = closed_before[index].copy()
        newly_open.append_group_of_runs([value])
        open_at.append(newly_open)
        record_group_list = newly_open
        for previous_index, old_open in enumerate(open_at[:index]):
            new_open = old_open.copy().append_run_to_to_last_group(value)
            open_at[previous_index] = new_open
            if new_open.bits < record_group_list.bits:
                record_group_list = new_open
        closed_before.append(record_group_list)
    partition = closed_before[-1]
    previous_average = partition[0].stats.avg
    for group in partition:
        if group.stats.avg == previous_average:
            group.comment = u"normal"
        elif group.stats.avg < previous_average:
            group.comment = u"regression"
        elif group.stats.avg > previous_average:
            group.comment = u"progression"
        previous_average = group.stats.avg
    return partition
