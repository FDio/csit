# Copyright (c) 2024 Cisco and/or its affiliates.
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
The mid result is grouped with early or late result, or as a separate group.
The jump we are looking for is between the mid and the smaller group
of the grouping with less bits.
Except when a grouping with all three sets as separate groups is the smallest.
In that case we chose the bigger difference in averages.
"""

import sys

from typing import List, Tuple

from resources.libraries.python import jumpavg
from resources.libraries.python.model.parse import parse


def read_from_dir(dirname: str) -> Tuple[List[float], float]:
    """Parse samples from dir, print them and stats, return them as list.

    In case there are more test cases, their results are concatenated.

    :param direname: The directory name (maybe with path) to parse.
    :type dirname: str
    :returns: The samples, deserialized from json, and the average.
    :rtype: Tuple[List[float], float]
    :raises RuntimeError: On parsing error.
    """
    results = parse(dirname)
    samples = []
    for result in results.values():
        samples.extend(result)
    print(f"Read {dirname}: {samples!r}")
    stats = jumpavg.AvgStdevStats.for_runs(samples)
    print(f"Stats: {stats!r}")
    return samples, stats.avg


def main() -> int:
    """Execute the main logic, return the return code.

    :returns: The return code, 0 or 3 depending on the comparison result.
    :rtype: int
    """
    early_results, early_avg = read_from_dir("csit_early")
    late_results, late_avg = read_from_dir("csit_late")
    mid_results, mid_avg = read_from_dir("csit_mid")
    max_early, abs_diff_late = max(early_avg, mid_avg), abs(late_avg - mid_avg)
    max_late, abs_diff_early = max(late_avg, mid_avg), abs(early_avg - mid_avg)
    rel_diff_early = abs_diff_early / max_early if max_early else 0.0
    rel_diff_late = abs_diff_late / max_late if max_late else 0.0
    max_value = max(early_results + mid_results + late_results)
    # Create a common group list with just the early group.
    common_group_list = jumpavg.BitCountingGroupList(
        max_value=max_value
    ).append_group_of_runs(early_results)
    # Try grouping the mid with the early.
    early_group_list = common_group_list.copy()
    early_group_list.extend_runs_to_last_group(mid_results)
    early_group_list.append_group_of_runs(late_results)
    early_bits = early_group_list.bits
    print(f"Early group list bits: {early_bits}")
    # Now the same, but grouping the mid with the late.
    late_group_list = common_group_list.copy()
    late_group_list.append_group_of_runs(mid_results)
    late_group_list.extend_runs_to_last_group(late_results)
    late_bits = late_group_list.bits
    print(f"Late group list bits: {late_bits}")
    # Finally, group each separately, as if double anomaly happened.
    double_group_list = common_group_list.copy()
    double_group_list.append_group_of_runs(mid_results)
    double_group_list.append_group_of_runs(late_results)
    double_bits = double_group_list.bits
    print(f"Double group list bits: {double_bits}")
    single_bits = min(early_bits, late_bits)
    if double_bits <= single_bits:
        # In this case, comparing early_bits with late_bits is not the best,
        # as that would probably select based on stdev, not based on diff.
        # Example: mid (small stdev) is closer to early (small stdev),
        # and farther from late (big stdev).
        # As grouping mid with early would increase their combined stdev,
        # it is not selected. This means a noisy late bound can affect
        # what human perceives as the more interesting region.
        # So we select only based on averages.
        print("Perhaps two different anomalies. Selecting by averages only.")
        diff = single_bits - double_bits
        print(f"Saved {diff} ({100*diff/single_bits}%) bits.")
        if rel_diff_early > rel_diff_late:
            print("The mid results are considered late.")
            print("Preferring relative difference of averages:")
            print(f"{100*rel_diff_early}% to {100*rel_diff_late}%.")
            # rc==1 is when command is not found.
            # rc==2 is when python interpreter does not find the script.
            exit_code = 3
        else:
            print("The mid results are considered early.")
            print("Preferring relative difference of averages:")
            print(f"{100*rel_diff_late}% to {100*rel_diff_early}%.")
            exit_code = 0
    else:
        # When difference of averages is within stdev,
        # we let jumpavg decide, as here difference in stdev
        # can be the more interesting signal.
        diff = early_bits - late_bits
        if early_bits > late_bits:
            print("The mid results are considered late.")
            print(f"Saved {diff} ({100*diff/early_bits}%) bits.")
            print(f"New relative difference is {100*rel_diff_early}%.")
            exit_code = 3
        else:
            print("The mid results are considered early.")
            print(f"Saved {-diff} ({-100*diff/late_bits}%) bits.")
            print(f"New relative difference is {100*rel_diff_late}%.")
            exit_code = 0
    print(f"Exit code {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
