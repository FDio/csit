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

"""Script for determining whether per-patch perf test votes -1.

This script expects a particular tree created on a filesystem by
per_patch_perf.sh bootstrap script, including test results
exported as json files according to a current model schema.
This script extracts the results (according to result type)
and joins them into one list of floats for parent and one for current.

This script then uses jumpavg library to determine whether there was
a regression, progression or no change for each testcase.

If the set of test names does not match, or there was a regression,
this script votes -1 (by exiting with code 1), otherwise it votes +1 (exit 0).
"""

import sys

from resources.libraries.python import jumpavg
from resources.libraries.python.model.parse import parse


def main() -> int:
    """Execute the main logic, return a number to return as the return code.

    Call parse to get parent and current data.
    Use higher fake value for parent, so changes that keep a test failing
    are marked as regressions.

    If there are multiple iterations, the value lists are joined.
    For each test, call jumpavg.classify to detect possible regression.

    If there is at least one regression, return 3.

    :returns: Return code, 0 or 3 based on the comparison result.
    :rtype: int
    """
    iteration = -1
    parent_aggregate = {}
    current_aggregate = {}
    test_names = None
    while 1:
        iteration += 1
        parent_results = {}
        current_results = {}
        parent_results = parse(f"csit_parent/{iteration}", fake_value=2.0)
        parent_names = set(parent_results.keys())
        if test_names is None:
            test_names = parent_names
        if not parent_names:
            # No more iterations.
            break
        assert parent_names == test_names, f"{parent_names} != {test_names}"
        current_results = parse(f"csit_current/{iteration}", fake_value=1.0)
        current_names = set(current_results.keys())
        assert (
            current_names == parent_names
        ), f"{current_names} != {parent_names}"
        for name in test_names:
            if name not in parent_aggregate:
                parent_aggregate[name] = []
            if name not in current_aggregate:
                current_aggregate[name] = []
            parent_aggregate[name].extend(parent_results[name])
            current_aggregate[name].extend(current_results[name])
    exit_code = 0
    for name in test_names:
        parent_values = parent_aggregate[name]
        current_values = current_aggregate[name]
        print(f"Time-ordered MRR values for parent build: {parent_values}")
        print(f"Time-ordered MRR values for current build: {current_values}")
        parent_values = sorted(parent_values)
        current_values = sorted(current_values)
        max_value = max([1.0] + parent_values + current_values)
        parent_stats = jumpavg.AvgStdevStats.for_runs(parent_values)
        current_stats = jumpavg.AvgStdevStats.for_runs(current_values)
        parent_group_list = jumpavg.BitCountingGroupList(
            max_value=max_value
        ).append_group_of_runs([parent_stats])
        combined_group_list = (
            parent_group_list.copy().extend_runs_to_last_group([current_stats])
        )
        separated_group_list = parent_group_list.append_group_of_runs(
            [current_stats]
        )
        print(f"Value-ordered MRR values for parent build: {parent_values}")
        print(f"Value-ordered MRR values for current build: {current_values}")
        avg_diff = (current_stats.avg - parent_stats.avg) / parent_stats.avg
        print(f"Difference of averages relative to parent: {100 * avg_diff}%")
        print(f"Jumpavg representation of parent group: {parent_stats}")
        print(f"Jumpavg representation of current group: {current_stats}")
        print(
            f"Jumpavg representation of both as one group:"
            f" {combined_group_list[0].stats}"
        )
        bits_diff = separated_group_list.bits - combined_group_list.bits
        compared = "longer" if bits_diff >= 0 else "shorter"
        print(
            f"Separate groups are {compared} than single group"
            f" by {abs(bits_diff)} bits"
        )
        # TODO: Version of classify that takes max_value and list of stats?
        # That matters if only stats (not list of floats) are given.
        classified_list = jumpavg.classify([parent_values, current_values])
        if len(classified_list) < 2:
            print(f"Test {name}: normal (no anomaly)")
            continue
        anomaly = classified_list[1].comment
        if anomaly == "regression":
            print(f"Test {name}: anomaly regression")
            exit_code = 3  # 1 or 2 can be caused by other errors
            continue
        print(f"Test {name}: anomaly {anomaly}")
    print(f"Exit code: {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
