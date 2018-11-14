# Copyright (c) 2018 Cisco and/or its affiliates.
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

    :param value_list: List to pick subset from.
    :type value_list: list of float
    :returns: New list containing middle values.
    :rtype: list of float
    """
    tmp = sorted(value_list)
    eight = len(tmp) / 8
    ret = tmp[3*eight:-eight]
    return ret

iteration = -1
parent_iterations = list()
new_iterations = list()
num_tests = None
while 1:
    iteration += 1
    parent_lines = list()
    new_lines = list()
    filename = "csit_parent/{iter}/results.txt".format(iter=iteration)
    try:
        with open(filename) as parent_file:
            parent_lines = parent_file.readlines()
    except IOError:
        break
    num_lines = len(parent_lines)
    filename = "csit_new/{iter}/results.txt".format(iter=iteration)
    with open(filename) as new_file:
        new_lines = new_file.readlines()
    if num_lines != len(new_lines):
        print "Number of tests does not match within iteration", iteration
        sys.exit(1)
    if num_tests is None:
        num_tests = num_lines
    elif num_tests != num_lines:
        print "Number of tests does not match previous at iteration", iteration
        sys.exit(1)
    parent_iterations.append(parent_lines)
    new_iterations.append(new_lines)
classifier = BitCountingClassifier()
exit_code = 0
for test_index in range(num_tests):
    val_max = 1.0
    parent_values = list()
    new_values = list()
    for iteration_index in range(len(parent_iterations)):
        parent_values.extend(
            json.loads(parent_iterations[iteration_index][test_index]))
        new_values.extend(
            json.loads(new_iterations[iteration_index][test_index]))
    print "TRACE pre-hack parent: {p}".format(p=parent_values)
    print "TRACE pre-hack new: {n}".format(n=new_values)
    parent_values = hack(parent_values)
    new_values = hack(new_values)
    parent_max = BitCountingMetadataFactory.find_max_value(parent_values)
    new_max = BitCountingMetadataFactory.find_max_value(new_values)
    val_max = max(val_max, parent_max, new_max)
    factory = BitCountingMetadataFactory(val_max)
    parent_stats = factory.from_data(parent_values)
    new_factory = BitCountingMetadataFactory(val_max, parent_stats.avg)
    new_stats = new_factory.from_data(new_values)
    print "TRACE parent: {p}".format(p=parent_values)
    print "TRACE new: {n}".format(n=new_values)
    print "DEBUG parent: {p}".format(p=parent_stats)
    print "DEBUG new: {n}".format(n=new_stats)
    common_max = max(parent_stats.avg, new_stats.avg)
    difference = (new_stats.avg - parent_stats.avg) / common_max
    print "DEBUG difference: {d}%".format(d=100 * difference)
    classified_list = classifier.classify([parent_stats, new_stats])
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
print "DEBUG exit code {code}".format(code=exit_code)
sys.exit(exit_code)
