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

"""Script for determining whether per-patch perf test votes -1.

This script assumes there exist two text files with processed BMRR results,
located at hardcoded relative paths (subdirs thereof), having several lines
of json-parseable lists of float values, corresponding to testcase results.
This script then uses jumpavg library to determine whether there was
a regression, progression or no change for each testcase.
If number of tests does not match, or there was a regression,
this script votes -1 (by exiting with code 1), otherwise it votes +1 (exit 0).
"""

import json
import sys

from jumpavg.BitCountingMetadataFactory import BitCountingMetadataFactory
from jumpavg.BitCountingClassifier import BitCountingClassifier


def hack(value_list):
    """Return middle two quartiles, hoping to reduce influence of outliers.

    Currently "middle two" is "all", but that can change in future.

    :param value_list: List to pick subset from.
    :type value_list: list of float
    :returns: New list containing middle values.
    :rtype: list of float
    """
    tmp = sorted(value_list)
    eight = len(tmp) / 8
    ret = tmp[3*eight:-eight]
    return tmp # ret


iteration = -1
parent_iterations = list()
current_iterations = list()
num_tests = None
while 1:
    iteration += 1
    parent_lines = list()
    current_lines = list()
    filename = f"csit_parent/{iteration}/results.txt"
    try:
        with open(filename) as parent_file:
            parent_lines = parent_file.readlines()
    except IOError:
        break
    num_lines = len(parent_lines)
    filename = f"csit_current/{iteration}/results.txt"
    with open(filename) as current_file:
        current_lines = current_file.readlines()
    if num_lines != len(current_lines):
        print(f"Number of tests does not match within iteration {iteration}")
        sys.exit(1)
    if num_tests is None:
        num_tests = num_lines
    elif num_tests != num_lines:
        print(
            f"Number of tests does not match previous at iteration {iteration}"
        )
        sys.exit(1)
    parent_iterations.append(parent_lines)
    current_iterations.append(current_lines)
classifier = BitCountingClassifier()
exit_code = 0
for test_index in range(num_tests):
    val_max = 1.0
    parent_values = list()
    current_values = list()
    for iteration_index in range(len(parent_iterations)):
        parent_values.extend(
            json.loads(parent_iterations[iteration_index][test_index])
        )
        current_values.extend(
            json.loads(current_iterations[iteration_index][test_index])
        )
    print(f"Time-ordered MRR values for parent build: {parent_values}")
    print(f"Time-ordered MRR values for current build: {current_values}")
    parent_values = hack(parent_values)
    current_values = hack(current_values)
    parent_max = BitCountingMetadataFactory.find_max_value(parent_values)
    current_max = BitCountingMetadataFactory.find_max_value(current_values)
    val_max = max(val_max, parent_max, current_max)
    factory = BitCountingMetadataFactory(val_max)
    parent_stats = factory.from_data(parent_values)
    current_factory = BitCountingMetadataFactory(val_max, parent_stats.avg)
    current_stats = current_factory.from_data(current_values)
    both_stats = factory.from_data(parent_values + current_values)
    print(f"Value-ordered MRR values for parent build: {parent_values}")
    print(f"Value-ordered MRR values for current build: {current_values}")
    difference = (current_stats.avg - parent_stats.avg) / parent_stats.avg
    print(f"Difference of averages relative to parent: {100 * difference}%")
    print(f"Jumpavg representation of parent group: {parent_stats}")
    print(f"Jumpavg representation of current group: {current_stats}")
    print(f"Jumpavg representation of both as one group: {both_stats}")
    bits = parent_stats.bits + current_stats.bits - both_stats.bits
    compared = u"longer" if bits >= 0 else u"shorter"
    print(
        f"Separate groups are {compared} than single group by {abs(bits)} bits"
    )
    classified_list = classifier.classify([parent_stats, current_stats])
    if len(classified_list) < 2:
        print(f"Test test_index {test_index}: normal (no anomaly)")
        continue
    anomaly = classified_list[1].metadata.classification
    if anomaly == u"regression":
        print(f"Test test_index {test_index}: anomaly regression")
        exit_code = 1
        continue
    print(f"Test test_index {test_index}: anomaly {anomaly}")
print(f"Exit code {exit_code}")
sys.exit(exit_code)
