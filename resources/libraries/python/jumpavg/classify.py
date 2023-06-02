# Copyright (c) 2023 Cisco and/or its affiliates.
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

Classification is one of primary purposes of this package.

Minimal message length principle is used
for grouping results into the list of groups,
assuming each group is a population of different Gaussian distribution.
"""

from typing import Iterable, Optional, Union

from .avg_stdev_stats import AvgStdevStats
from .bit_counting_group_list import BitCountingGroupList


def classify(
    values: Iterable[Union[float, Iterable[float]]],
    unit: Optional[float] = None,
    sbps: Optional[float] = None,
) -> BitCountingGroupList:
    """Return the values in groups of optimal bit count.

    Here, a value is either a float, or an iterable of floats.
    Such iterables represent an undivisible sequence of floats.
    Int is accepted anywhere instead of float.

    Internally, such sequence is replaced by AvgStdevStats
    after maximal value is found.

    If the values are smaller than expected (below one unit),
    the underlying assumption break down and the classification is wrong.
    Use the "unit" parameter to hint at what the input resolution is.

    If the correct value of unit is not known beforehand,
    the argument "sbps" (Significant Bits Per Sample) can be used
    to set unit such that maximal sample value is this many ones in binary.
    If neither "unit" nor "sbps" are given, "sbps" of 12 is used by default.

    :param values: Sequence of runs to classify.
    :param unit: Typical resolution of the values.
        Zero and None means no unit given.
    :param sbps: Significant Bits Per Sample. None on zero means 12.
        If units is not set, this is used to compute unit from max sample value.
    :type values: Iterable[Union[float, Iterable[float]]]
    :type unit: Optional[float]
    :type sbps: Optional[float]
    :returns: Classified group list.
    :rtype: BitCountingGroupList
    """
    processed_values = []
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
    if not unit:
        if not sbps:
            sbps = 12.0
        max_in_units = pow(2.0, sbps + 1.0) - 1.0
        unit = max_value / max_in_units
    # Glist means group list (BitCountingGroupList).
    open_glists = []
    record_glist = BitCountingGroupList(max_value=max_value, unit=unit)
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
        if group.stats.avg < previous_average:
            group.comment = "regression"
        elif group.stats.avg > previous_average:
            group.comment = "progression"
        previous_average = group.stats.avg
    return record_glist
