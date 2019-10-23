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

from resources.libraries.python import jumpavg

def read_from_file(filename):
    """FIXME"""
    samples = list()
    with open(filename) as in_file:
        for line in in_file:
            samples.extend(json.loads(line))
    print "Read {f}: {m!r}".format(f=filename, m=samples)
    print "Stats: {s!r}".format(s=jumpavg.AvgStdevStats.for_runs(samples))
    return samples

def main():
    """FIXME"""
    parent_results = read_from_file("csit_parent/results.txt")
    current_results = read_from_file("csit_current/results.txt")
    new_results = read_from_file("csit_new/results.txt")
    max_value = max(parent_results + current_results + new_results)
    # Start group list by empty group, defining factory.
    parent_group_list = jumpavg.BitCountingGroupList(
        max_value=max_value).append_group_of_runs(parent_results)
    good_group_list = parent_group_list.copy()
    good_group_list.extend_runs_to_last_group(new_results)
    good_group_list.append_group_of_runs(current_results)
    good_bits = good_group_list.bits
    print "Good group list: {g!r}".format(g=good_group_list)
    # Now the same, but in a different order.
    bad_group_list = parent_group_list.copy()
    bad_group_list.append_group_of_runs(current_results)
    bad_group_list.extend_runs_to_last_group(new_results)
    bad_bits = bad_group_list.bits
    print "Bad group list: {g!r}".format(g=bad_group_list)
    diff = good_bits - bad_bits
    if good_bits > bad_bits:
        print "The new results are bad."
        print "Saved {b} ({p}%) bits.".format(
            b=diff, p=100*diff/good_bits)
        # rc==1 is when command is not found.
        # rc==2 is when python interpreter does not find the script to execute.
        exit_code = 3
    else:
        print "The new results are good."
        print "Saved {b} ({p}%) bits.".format(
            b=-diff, p=-100*diff/bad_bits)
        exit_code = 0
    print "Exit code {code}".format(code=exit_code)
    return exit_code

sys.exit(main())
# Moving the new results to parent or current will be done in bash.
