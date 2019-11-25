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

from jumpavg.BitCountingGroup import BitCountingGroup
from jumpavg.BitCountingGroupList import BitCountingGroupList
from jumpavg.BitCountingMetadataFactory import BitCountingMetadataFactory

def read_from_file(filename):
    """FIXME"""
    samples = list()
    with open(filename) as in_file:
        for line in in_file:
            samples.extend(json.loads(line))
    # TODO: Next version of jumpavg the following is 1 line.
    bcmf = BitCountingMetadataFactory(
        max_value=BitCountingMetadataFactory.find_max_value(samples))
    bcg = BitCountingGroup(bcmf, samples)
    print "Read {f}: {m!r}".format(f=filename, m=bcg.metadata)
    return bcg

def main():
    """FIXME"""
    parent_results = read_from_file("csit_parent/results.txt")
    current_results = read_from_file("csit_current/results.txt")
    new_results = read_from_file("csit_new/results.txt")
    #parent_with_new = parent_results + new_results
    #current_with_new = current_results + new_results
    val_max = max(map(BitCountingMetadataFactory.find_max_value, [
        parent_results.values, current_results.values, new_results.values]))
    factory = BitCountingMetadataFactory(val_max)
    # Start group list by empty group, defining factory.
    good_group_list = BitCountingGroupList([BitCountingGroup(
        factory, list())])
    good_group_list = good_group_list.with_group_appended(parent_results)
    for result in new_results.values:
        good_group_list = good_group_list.with_value_added_to_last_group(result)
    good_group_list = good_group_list.with_group_appended(current_results)
    print "Good group list: {g!r}".format(g=good_group_list)
    # Now the same, but in a different order.
    bad_group_list = BitCountingGroupList([BitCountingGroup(
        factory, list())])
    bad_group_list = bad_group_list.with_group_appended(parent_results)
    bad_group_list = bad_group_list.with_group_appended(current_results)
    for result in new_results.values:
        bad_group_list = bad_group_list.with_value_added_to_last_group(result)
    print "Bad group list: {g!r}".format(g=bad_group_list)
    if good_group_list.bits > bad_group_list.bits:
        print "The new results are bad."
        diff = good_group_list.bits - bad_group_list.bits
        print "Saved {b} ({p}%) bits.".format(
            b=diff, p=100*diff/good_group_list.bits)
        # rc==1 is when command is not found,
        # rc==2 is when python interpreter does not find the script to execute.
        exit_code = 3
    else:
        print "The new results are good."
        diff = bad_group_list.bits - good_group_list.bits
        print "Saved {b} ({p}%) bits.".format(
            b=diff, p=100*diff/bad_group_list.bits)
        exit_code = 0
    print "Exit code {code}".format(code=exit_code)
    return exit_code

sys.exit(main())
# Moving the new results to parent or current will be done in bash.
