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

"""FIXME"""

import json
import sys

from jumpavg.AvgStdevMetadataFactory import AvgStdevMetadataFactory
from jumpavg.BitCountingMetadataFactory import BitCountingMetadataFactory
from jumpavg.BitCountingClassifier import BitCountingClassifier


from_data = AvgStdevMetadataFactory().from_data
def read_from_file(filename):
    results = list()
    with open(filename) as in_file:
        for line in in_file:
            result.append(from_data(json.loads(line)))
    return results
parent_results = read_from_file("csit_parent/results.txt")
current_results = read_from_file("csit_current/results.txt")
new_results = read_from_file("csit_new/results.txt")
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
