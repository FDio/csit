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
    filename = "csit_parent/{iter}/results.txt".format(iter=iteration)
    try:
        with open(filename) as parent_file:
            parent_lines = parent_file.readlines()
    except IOError:
        break
    num_lines = len(parent_lines)
    filename = "csit_current/{iter}/results.txt".format(iter=iteration)
    with open(filename) as current_file:
        current_lines = current_file.readlines()
    if num_lines != len(current_lines):
        print "Number of tests does not match within iteration", iteration
        sys.exit(1)
    if num_tests is None:
        num_tests = num_lines
    elif num_tests != num_lines:
        print "Number of tests does not match previous at iteration", iteration
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
            json.loads(parent_iterations[iteration_index][test_index]))
        current_values.extend(
            json.loads(current_iterations[iteration_index][test_index]))
    print "Time-ordered MRR values for parent build: {p}".format(
        p=parent_values)
    print "Time-ordered MRR values for current build: {c}".format(
        c=current_values)
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
    print "Value-ordered MRR values for parent build: {p}".format(
        p=parent_values)
    print "Value-ordered MRR values for current build: {c}".format(
        c=current_values)
    difference = (current_stats.avg - parent_stats.avg) / parent_stats.avg
    print "Difference of averages relative to parent: {d}%".format(
        d=100 * difference)
    print "Jumpavg representation of parent group: {p}".format(
        p=parent_stats)
    print "Jumpavg representation of current group: {c}".format(
        c=current_stats)
    print "Jumpavg representation of both as one group: {b}".format(
        b=both_stats)
    bits = parent_stats.bits + current_stats.bits - both_stats.bits
    compared = "longer" if bits >= 0 else "shorter"
    print "Separate groups are {cmp} than single group by {bit} bits".format(
        cmp=compared, bit=abs(bits))
    classified_list = classifier.classify([parent_stats, current_stats])
    if len(classified_list) < 2:
        print "Test test_index {test_index}: normal (no anomaly)".format(
            test_index=test_index)
        continue
    anomaly = classified_list[1].metadata.classification
    if anomaly == "regression":
        print "Test test_index {test_index}: anomaly regression".format(
            test_index=test_index)
        exit_code = 1
        continue
    print "Test test_index {test_index}: anomaly {anomaly}".format(
        test_index=test_index, anomaly=anomaly)
print "Exit code {code}".format(code=exit_code)
sys.exit(exit_code)
