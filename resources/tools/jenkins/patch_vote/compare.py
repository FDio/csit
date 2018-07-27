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


def hack(value_list):
    print "TRACE Hacking:", repr(value_list)
    tmp = sorted(value_list)
    quarter = len(tmp) / 4
    ret = tmp[quarter:-quarter]
    print "TRACE Hacked:", repr(ret)
    return ret

parent_lines = list()
new_lines = list()
with open("csit_parent/results.txt") as parent_file:
    parent_lines = parent_file.readlines()
with open("csit_new/results.txt") as new_file:
    new_lines = new_file.readlines()
# TODO: Figure out what to do if only parent fails.
if len(parent_lines) != len(new_lines):
    print "Number of passed tests does not match!"
    sys.exit(1)
classifier = BitCountingClassifier()
num_tests = len(parent_lines)
exit_code = 0
for index in range(num_tests):
    parent_values = hack(json.loads(parent_lines[index]))
    new_values = hack(json.loads(new_lines[index]))
    parent_max = BitCountingMetadataFactory.find_max_value(parent_values)
    new_max = BitCountingMetadataFactory.find_max_value(new_values)
    cmax = max(parent_max, new_max)
    factory = BitCountingMetadataFactory(cmax)
    parent_stats = factory.from_data(parent_values)
    factory = BitCountingMetadataFactory(cmax, parent_stats.avg)
    new_stats = factory.from_data(new_values)
    print "DEBUG parent: {p}".format(p=parent_stats)
    print "DEBUG new: {n}".format(n=new_stats)
    common_max = max(parent_stats.avg, new_stats.avg)
    difference = (new_stats.avg - parent_stats.avg) / common_max
    print "DEBUG difference: {d}%".format(d=100*difference)
    classified_list = classifier.classify([parent_stats, new_stats])
    if len(classified_list) < 2:
        print "Test index {index}: normal (no anomaly)".format(
            index=index)
        continue
    anomaly = classified_list[1].metadata.classification
    if anomaly == "regression":
        print "Test index {index}: anomaly regression".format(index=index)
        exit_code = 1
        continue
    print "Test index {index}: anomaly {anomaly}".format(
        index=index, anomaly=anomaly)
print "DEBUG exit code {code}".format(code=exit_code)
sys.exit(exit_code)
