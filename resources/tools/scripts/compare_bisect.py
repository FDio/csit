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
from jumpavg.BitCountingGroup import BitCountingGroup
from jumpavg.BitCountingGroupList import BitCountingGroupList
from jumpavg.BitCountingMetadataFactory import BitCountingMetadataFactory

def read_from_file(filename):
    results = list()
    with open(filename) as in_file:
        for line in in_file:
            result.append(AvgStdevMetadataFactory.from_data(json.loads(line)))
    return results

parent_results = read_from_file("csit_parent/results.txt")
current_results = read_from_file("csit_current/results.txt")
new_results = read_from_file("csit_new/results.txt")
#parent_with_new = parent_results + new_results
#current_with_new = current_results + new_results
val_max = max(map(BitCountingMetadataFactory.find_max_value, [
    parent_results, current_results, new_results]))
factory = BitCountingMetadataFactory(val_max)
# Create group lists with forced gouping.
good_group_list = BitCountingGroupList([BitCountingGroup(
    factory, parent_results)])
for result in new_results:
    good_group_list = good_group_list.with_value_added_to_last_group(result)
good_group_list = good_group_list.with_group_appended([BitCountingGroup(
    factory, current_results)])
print "Good group list: {g!r}".format(g=good_group_list)
# Now the same, but in a different order.
bad_group_list = BitCountingGroupList([BitCountingGroup(
    factory, parent_results)])
bad_group_list = bad_group_list.with_group_appended([
    factory.from_data(current_results)])
for result in new_results:
    bad_group_list = bad_group_list.with_value_added_to_last_group(result)
print "Bad group list: {g!r}".format(g=bad_group_list)
if good_group_list.bits > bad_group_list.bits:
    print "The new results are bad."
    exit_code = 2
else:
    print "The new results are good."
    exit_code = 0
print "Exit code {code}".format(code=exit_code)
sys.exit(exit_code)
# Moving the new results to parent or current will be done in bash.
