# Copyright (c) 2020 Cisco and/or its affiliates.
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

"""Script for analyzing 3 result sets for "git bisect" purposes.

Jumpavg library is used for comparing description length of three groupings.
The middle result is grouped with early or late result, or as a separate group.
The jump we are looking for is between the middle and the smaller group
of the grouping with less bits.
Except when a grouping with all three sets as separate groups is the smallest.
In that case we chose the bigger difference in averages.
"""

import json
import sys

from io import open

from resources.libraries.python import jumpavg


def read_from_file(filename):
    """Read samples from file, print them and stats, return them as list.

    :param filename: The file name (maybe with path) to open for reading.
    :type filename: str
    :returns: The samples, deserialized from json, and the average.
    :rtype: List[float], float
    """
    samples = list()
    with open(filename, u"rt") as in_file:
        for line in in_file:
            samples.extend(json.loads(line))
    print(f"Read {filename}: {samples!r}")
    stats = jumpavg.AvgStdevStats.for_runs(samples)
    print(f"Stats: {stats!r}")
    return samples, stats.avg

def main():
    """Execute the main logic, return the return code.

    :returns: The return code, 0 or 3 depending on the comparison result.
    :rtype: int
    """
    early_results, early_avg = read_from_file(u"csit_early/results.txt")
    late_results, late_avg = read_from_file(u"csit_late/results.txt")
    middle_results, middle_avg = read_from_file(u"csit_middle/results.txt")
    rel_diff_to_early = abs(early_avg - middle_avg) / max(early_avg, middle_avg)
    rel_diff_to_late = abs(late_avg - middle_avg) / max(late_avg, middle_avg)
    max_value = max(early_results + middle_results + late_results)
    # Create a common group list with just the early group.
    common_group_list = jumpavg.BitCountingGroupList(
        max_value=max_value).append_group_of_runs(early_results)
    # Try grouping the middle with the early.
    early_group_list = common_group_list.copy()
    early_group_list.extend_runs_to_last_group(middle_results)
    early_group_list.append_group_of_runs(late_results)
    early_bits = early_group_list.bits
    print(f"Early group list bits: {early_bits}")
    # Now the same, but grouping the middle with the late.
    late_group_list = common_group_list.copy()
    late_group_list.append_group_of_runs(middle_results)
    late_group_list.extend_runs_to_last_group(late_results)
    late_bits = late_group_list.bits
    print(f"Late group list bits: {late_bits}")
    # Finally, group each separately, as if double anomaly happened.
    double_group_list = common_group_list.copy()
    double_group_list.append_group_of_runs(middle_results)
    double_group_list.append_group_of_runs(late_results)
    double_bits = double_group_list.bits
    print(f"Double group list bits: {double_bits}")
    single_bits = min(early_bits, late_bits)
    if double_bits <= single_bits:
        # In this case, comparing early_bits with late_bits is not the best,
        # as that would probably select based on stdev, not based on diff.
        # Example: middle (small stdev) is closer to early (small stdev),
        # and farther from late (big stdev).
        # As grouping middle with early would increase their combined stdev,
        # it is not selected. This means a noisy late bound can affect
        # what human perceives as the more interesting region.
        # So we select only based on averages.
        print(u"Perhaps two different anomalies. Selecting by averages only.")
        diff = single_bits - double_bits
        print(f"Saved {diff} ({100*diff/single_bits}%) bits.")
        if rel_diff_to_early > rel_diff_to_late:
            print(u"The middle results are considered late.")
            print(u"Preferring relative difference of averages:")
            print(f"{100*rel_diff_to_early}% to {100*rel_diff_to_late}%.")
            # rc==1 is when command is not found.
            # rc==2 is when python interpreter does not find the script.
            exit_code = 3
        else:
            print(u"The middle results are considered early.")
            print(u"Preferring relative difference of averages:")
            print(f"{100*rel_diff_to_late}% to {100*rel_diff_to_early}%.")
            exit_code = 0
    else:
        # When difference of averages is within stdev,
        # we let jumpavg decide, as here difference in stdev
        # can be the more interesting signal.
        diff = early_bits - late_bits
        if early_bits > late_bits:
            print(u"The middle results are considered late.")
            print(f"Saved {diff} ({100*diff/early_bits}%) bits.")
            print(f"New relative difference is {100*rel_diff_to_early}%.")
            exit_code = 3
        else:
            print(u"The middle results are considered early.")
            print(f"Saved {-diff} ({-100*diff/late_bits}%) bits.")
            print(f"New relative difference is {100*rel_diff_to_late}%.")
            exit_code = 0
    print(f"Exit code {exit_code}")
    return exit_code
    # Moving the middle results.txt to early or late dir is done in bash.

if __name__ == u"__main__":
    sys.exit(main())
