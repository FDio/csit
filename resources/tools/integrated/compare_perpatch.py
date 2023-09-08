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

FIXME

This script assumes there exist two text files with processed BMRR results,
located at hardcoded relative paths (subdirs thereof), having several lines
of json-parseable lists of float values, corresponding to testcase results.
This script then uses jumpavg library to determine whether there was
a regression, progression or no change for each testcase.
If number of tests does not match, or there was a regression,
this script votes -1 (by exiting with code 1), otherwise it votes +1 (exit 0).
"""

import json
import os
import sys

from resources.libraries.python import jumpavg


def parse(dirpath):
    """FIXME"""
    results = {}
    for root, _, files in os.walk(dirpath):
        for filename in files:
            if not filename.endswith(".json"):
                continue
            filepath = os.path.join(root, filename)
            with open(filepath, "rt", encoding="utf8") as file_in:
                data = json.load(file_in)
            if "test_name_long" not in data:
                continue
            name = data["test_name_long"]
            if not data["passed"]:
                results[name] = [2.0]
                continue
            result_object = data["result"]
            result_type = result_object["type"]
            if result_type == "mrr":
                results[name] = result_object["receive_rate"]["rate"]["values"]
            elif result_type == "ndrpdr":
                results[name] = [result_object["pdr"]["lower"]["rate"]["value"]]
            elif result_type == "soak":
                results[name] = [
                    result_object["critical_rate"]["lower"]["rate"]["value"]
                ]
            elif result_type == "reconf":
                results[name] = [result_object["loss"]["time"]["value"]]
            elif result_type == "hoststack":
                results[name] = [result_object["bandwidth"]["value"]]
            else:
                raise RuntimeError(f"Unknown result type: {result_type}")
    return results


def main():
    """Execute the main logic, return the code to return as return code.

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
        parent_results = parse(f"csit_parent/{iteration}")
        parent_names = set(parent_results.keys())
        if test_names is None:
            test_names = parent_names
        if not parent_names:
            # No more iterations.
            break
        assert parent_names == test_names, f"{parent_names} != {test_names}"
        current_results = parse(f"csit_current/{iteration}")
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
        print(f"Test name: {name}")
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
