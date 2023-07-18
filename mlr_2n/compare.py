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

cases = {
    "memif": "64B-1c-rdma-eth-l2xcbase-eth-2memif-1dcr-ndrpdr",
    "ip4scale": "64B-1c-rdma-ethip4-ip4scale2m-rnd-ndrpdr",
    "cps": "64B-1c-rdma-ethip4tcp-nat44ed-h65536-p63-s4128768-cps-ndrpdr",
    "tput": "100B-1c-rdma-ethip4tcp-nat44ed-h65536-p63-s4128768-tput-ndrpdr",
    "det": "64B-1c-rdma-ethip4udp-nat44det-h65536-p63-s4128758-ndrpdr",
    "geneve": "64B-1c-rdma-ethip4--ethip4udpgeneve-16tun-ip4base-ndrpdr",
    "ip6scale": "78B-1c-rdma-ethip6-ip6scale2m-rnd-ndrpdr",
    "maglev": "64B-1c-rdma-ethip4-loadbalancer-maglev-ndrpdr",
    "virtio": "64B-1c-rdma-dot1q-l2bdbasemaclrn-eth-2virtiovr1024-1vm-vppl2xc-ndrpdr",
    "vhost": "64B-1c-rdma-eth-l2xcbase-eth-2vhostvr1024-1vm-ndrpdr",
    "vts": "114B-1c-rdma-ethip4vxlan-l2bdbasemaclrn-eth-iacldstbase-aclpermitr...",
}
case_keys = list(cases.keys())
revisions = {
    "3909fec961a9d2d8b1784535c909e5cb38bc06e8": "MLRv2 (rls2306)",
    "cf74df8eea5566d2a18a79e26ebc2de010ce2732": "MLRv7 (continuity)",
    "c0744e6901d37f9b14b0446e67951f6e80f31029": "MLRv7a (aggressive)",
}

cols_in, cols_out = [], []
infixes = ("dur", "ndr", "pdr")
for case in case_keys:
    for infix in infixes:
        cols_in.append(f"{case}_{infix}")

stats = {key: {} for key in revisions}
with open("results.csv", "rt") as fin:
    reader = DictReader(fin)
    for row in reader:
        ver_key = row["refspec"]
        if ver_key not in revisions:
            continue
        for col in cols_in:
            value = row[col]
            if "NA" == value:
                continue
            value = float(value)
            stat_dict = stats[ver_key]
            if col in stat_dict:
                stat_dict[col] = AvgStdevStats.for_runs([stat_dict[col], value])
            else:
                stat_dict[col] = AvgStdevStats.for_runs([value])
with open("comparison.csv", "wt") as fout:
    fout.write("refspec")
    for col in cols_in:
        if col[-3:] == "dur":
            fout.write(f",{col}_siz")
        fout.write(f",{col}_avg,{col}_std")
    fout.write("\n")
    for ver_key in stats:
        fout.write(f"{revisions[ver_key]}")
        stat_dict = stats[ver_key]
        for col in cols_in:
            if col in stat_dict:
                stat = stat_dict[col]
                if col[-3:] == "dur":
                    fout.write(f",{stat.size}")
                fout.write(f",{stat.avg},{stat.stdev}")
            else:
                if col[-3:] == "dur":
                    fout.write(f",0")
                fout.write(f",NA,NA")
        fout.write(f"\n")
