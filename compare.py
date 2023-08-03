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

from csv import DictReader
from math import sqrt
from resources.libraries.python.jumpavg import AvgStdevStats

ver_map = {
    "rls2302+VPPv23.02-rc1~0-g42b5a8767~b2": "",
    "rls2302+VPPv23.02-rc2~0-gbe1b84421~b12": "",
    "rls2302+VPPv23.02-rc2~2-g5e1efcc56~b14": "",
    "rls2302+VPPv23.02-release": "",#"c2v2",
    "rls2306+VPPv23.06-rc1~0-gb60a6477e~b2": "",#"c6v6r1",
    "rls2306+VPPv23.06-rc2~0-g5e6bc730e~b15": "",#"c6v6r2",
    "rls2306+VPPv23.02-release": "c6v2",
    "rls2306+VPPv23.06-rc1~2-gb4b65194e~b4": "",#"c6v6r1",
    "rls2306+VPPv23.06-release": "c6v6",
}

# TODO: Access from csit.infra.dash/app/cdash/utils/utils.py
def relative_change_stdev(mean1, mean2, std1, std2):
    """Compute relative standard deviation of change of two values.

    The "1" values are the base for comparison.
    Results are returned as percentage (and percentual points for stdev).
    Linearized theory is used, so results are wrong for relatively large stdev.

    :param mean1: Mean of the first number.
    :param mean2: Mean of the second number.
    :param std1: Standard deviation estimate of the first number.
    :param std2: Standard deviation estimate of the second number.
    :type mean1: float
    :type mean2: float
    :type std1: float
    :type std2: float
    :returns: Relative change and its stdev.
    :rtype: float
    """
    if "NA" in (mean1, mean2):# or not std1 or not std2:
        return "NA", "NA"
    mean1, mean2 = float(mean1), float(mean2)
    quotient = mean2 / mean1
    first = float(std1) / mean1
    second = float(std2) / mean2
    std = quotient * sqrt(first * first + second * second)
    return (quotient - 1) * 100, std * 100

rlsver2column = {}
case_keys = set()
with open("results.csv", "rt") as fin:
    reader = DictReader(fin)
    for row in reader:
        ver_key = ver_map[f"rls{row['CSIT_rls']}+VPPv{row['VPP_version']}"]
        if not ver_key:
            continue
        case_key = f"{row['job_name_fragment']}-{row['TG_host']}-{row['NIC_model']}-{row['test_ID']}"
#        if 0:#"2vhostvr1" in case_key or "-af-xdp-" in case_key or "-4c" in case_key:
            # TODO: Allow single-worker and single-numa vhosts.
            # TODO: Investigate which 4c results are really bad.
#        if not ("c2v2" in ver_key and "xxv710" in case_key) and not ("c6v6" in ver_key and "810cq" in case_key):
#            continue
        if "2n-icx" not in case_key or "-avf-" in case_key or "-af-xdp-" in case_key:
            key_list = case_key.split("-")
            key_list = key_list[0:2] + key_list[3:]
            case_key = "-".join(key_list)
        case_key = case_key.replace("xxv710", "")
        case_key = case_key.replace("e810cq", "")
        case_keys.add(case_key)
        if ver_key not in rlsver2column:
            rlsver2column[ver_key] = {}
        column = rlsver2column[ver_key]
        pdr = float(row["PDR_lower"])
        if case_key in column:
            column[case_key] = AvgStdevStats.for_runs([pdr, column[case_key]])
        else:
            column[case_key] = AvgStdevStats.for_runs([pdr])
with open("comparison.csv", "wt") as fout:
    fout.write("case_key,")
    for rls in sorted(rlsver2column):
        fout.write(f"{rls}_avg,{rls}_stdev,")
    fout.write("c6v2dc6v6_avg,c6v2dc6v6_stdev\n")
    for case_key in case_keys:
        row = {}
        fout.write(f"{case_key},")
        for rls, column in rlsver2column.items():
            if case_key in column:
                stats = column[case_key]
                avg, stdev = stats.avg, stats.stdev
            else:
                avg, stdev = "NA", "NA"
            row[f"{rls}_avg"], row[f"{rls}_std"] = avg, stdev
            fout.write(f"{avg},{stdev},")
        diff_avg, diff_std = relative_change_stdev(
            row["c6v2_avg"], row["c6v6_avg"], row["c6v2_std"], row["c6v6_std"]
        )
        fout.write(f"{diff_avg},{diff_std}\n")
