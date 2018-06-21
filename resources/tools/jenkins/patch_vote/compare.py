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

FIXME: Docstrings, line lengths, and so on.
"""

import json
import sys

from jumpavg.BitCountingMetadataFactory import BitCountingMetadataFactory
from jumpavg.BitCountingClassifier import BitCountingClassifier

parent_lines = list()
new_lines = list()
with open("csit/results.txt") as parent_file:
    parent_lines = parent_file.readlines()
with open("csit_/results.txt") as new_file:
    new_lines = new_file.readlines()
# TODO: Figure out what to do if only parent fails.
if len(parent_lines) != len(new_lines):
    print "Number of passed tests does not match!"
    sys.exit(1)
classifier = BitCountingClassifier()
num_tests = len(parent_lines)
exit_code = 0
for index in range(num_tests):
    parent_values = json.loads(parent_lines[index])
    new_values = json.loads(new_lines[index])
    parent_max = BitCountingMetadataFactory.find_max_value(parent_values)
    new_max = BitCountingMetadataFactory.find_max_value(new_values)
    factory = BitCountingMetadataFactory(max(parent_max, new_max))
    parent_stats = factory.from_data(parent_values)
    new_stats = factory.from_data(new_values)
    print "DEBUG parent {p} new {n}".format(p=parent_stats, n=new_stats)
    classified_list = classifier.classify([parent_stats, new_stats])
    if len(classified_list) < 2:
        print "DEBUG group {g}".format(g=classified_list[0].metadata)
        print "Test index {index} no group boundary detected".format(
            index=index)
        continue
    anomaly = classified_list[1].metadata.classification
    if anomaly == "regression":
        print "Regression in test index {index}".format(index=index)
        print "Parent stats {stats}".format(stats=parent_stats)
        print "New stats {stats}".format(stats=new_stats)
        print "Parent values: {values}".format(values=parent_values)
        print "New values: {values}".format(values=new_values)
        exit_code = 1
        continue
    print "Test index {index} anomaly {anomaly}".format(
        index=index, anomaly=anomaly)
print "DEBUG exit code {code}".format(code=exit_code)
sys.exit(exit_code)
