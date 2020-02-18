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

"""Script fo analyzing 3 result sets for "git bisect" purposes.

Jumpavg library is used for comparing description length of two groupings.
The middle result is grouped with old or new result.
The jump we are looking for is between middle and the smaller group
of the grouping with less bits.
Except when the smallest grouping has all three sets as a separate group.
In that case we look at the bigger difference in averages.
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
    parent_results, parent_avg = read_from_file(u"csit_parent/results.txt")
    current_results, current_avg = read_from_file(u"csit_current/results.txt")
    new_results, new_avg = read_from_file(u"csit_new/results.txt")
    rel_diff_to_good = abs(parent_avg - new_avg) / max(parent_avg, new_avg)
    rel_diff_to_bad = abs(current_avg - new_avg) / max(current_avg, new_avg)
    max_value = max(parent_results + current_results + new_results)
    # Create a common parent group.
    parent_group_list = jumpavg.BitCountingGroupList(
        max_value=max_value).append_group_of_runs(parent_results)
    # Try grouping the middle with the old/good.
    good_group_list = parent_group_list.copy()
    good_group_list.extend_runs_to_last_group(new_results)
    good_group_list.append_group_of_runs(current_results)
    good_bits = good_group_list.bits
    print(f"Good group list bits: {good_bits}")
    # Now the same, but grouping the middle with the new/bad.
    bad_group_list = parent_group_list.copy()
    bad_group_list.append_group_of_runs(new_results)
    bad_group_list.extend_runs_to_last_group(current_results)
    bad_bits = bad_group_list.bits
    print(f"Bad group list bits: {bad_bits}")
    # Finally, group each separately, as if double anomaly happened.
    double_group_list = parent_group_list.copy()
    double_group_list.append_group_of_runs(new_results)
    double_group_list.append_group_of_runs(current_results)
    double_bits = double_group_list.bits
    print(f"Double group list bits: {double_bits}")
    single_bits = min(good_bits, bad_bits)
    if double_bits <= single_bits:
        # In this case, comparing good_bits with bad_bits is not the best,
        # as that would probably select based on stdev, not based on diff.
        # Example: New (small stdev) is closer to parent (small stdev),
        # and farther from current (big stdev).
        # As grouping new with parent would increase their combined stdev,
        # it is not selected. This means a noisy old bound can affect
        # what human perceives as the more interesting region.
        # So we select only based on averages.
        print(u"Perhaps two different anomalies. Selecting by averages only.")
        diff = single_bits - double_bits
        print(f"Saved {diff} ({100*diff/single_bits}%) bits.")
        if rel_diff_to_good > rel_diff_to_bad:
            print(u"The new results are bad.")
            print(u"Preferring relative difference of averages:")
            print(f"{100*rel_diff_to_good}% to {100*rel_diff_to_bad}%.")
            # rc==1 is when command is not found.
            # rc==2 is when python interpreter does not find the script.
            exit_code = 3
        else:
            print(u"The new results are good.")
            print(u"Preferring relative difference of averages:")
            print(f"{100*rel_diff_to_bad}% to {100*rel_diff_to_good}%.")
            exit_code = 0
    else:
        # When difference of averages is within stdev,
        # we let jumpavg decide, as here difference in stdev
        # can be the more interesting signal.
        diff = good_bits - bad_bits
        if good_bits > bad_bits:
            print(u"The new results are bad.")
            print(f"Saved {diff} ({100*diff/good_bits}%) bits.")
            print(f"New relative difference is {100*rel_diff_to_good}%.")
            exit_code = 3
        else:
            print(u"The new results are good.")
            print(f"Saved {-diff} ({-100*diff/bad_bits}%) bits.")
            print(f"New relative difference is {100*rel_diff_to_bad}%.")
            exit_code = 0
    print(f"Exit code {exit_code}")
    return exit_code
    # Moving the new results.txt to parent or current dir is done in bash.

if __name__ == u"__main__":
    sys.exit(main())
