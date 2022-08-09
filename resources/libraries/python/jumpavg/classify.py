# Copyright (c) 2022 Cisco and/or its affiliates.
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

import typing

from .AvgStdevStats import AvgStdevStats
from .BitCountingGroupList import BitCountingGroupList


def classify(
    values: typing.Iterable[typing.Union[float, typing.Iterable[float]]]
) -> BitCountingGroupList:
    """Return the values in groups of optimal bit count.

    Here, a value is either a float, or an iterable of floats.
    Such iterables represent an undivisible sequence of floats.
    Int is accepted anywhere instead of float.

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
    # Glist means group list (BitCountingGroupList).
    open_glists = list()
    record_glist = BitCountingGroupList(max_value=max_value)
    for value in processed_values:
        new_open_glist = record_glist.copy_fast().append_group_of_runs([value])
        record_glist = new_open_glist
        for old_open_glist in open_glists:
            old_open_glist.append_run_to_to_last_group(value)
            if old_open_glist.bits < record_glist.bits:
                record_glist = old_open_glist
        open_glists.append(new_open_glist)
    previous_average = record_glist[0].stats.avg
    for group in record_glist:
        if group.stats.avg == previous_average:
            group.comment = "normal"
        elif group.stats.avg < previous_average:
            group.comment = "regression"
        elif group.stats.avg > previous_average:
            group.comment = "progression"
        previous_average = group.stats.avg
    return record_glist
