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
    "ipsec1k": "IMIX-2c-ethip4ipsec1000tnlsw-ip4base-int-aes256gcm-ndrpdr",
    "ipsecasync": "IMIX-2c-ethip4ipsec8tnlswasync-scheduler-ip4base-int-aes256gcm-ndrpdr",
    "dot1qip4": "IMIX-2c-dot1q-ip4base-ndrpdr",
    "vxlanscale": "IMIX-2c-dot1q--ethip4vxlan-l2bdscale100l2bd100vlan100vxlan-ndrpdr",
    "wireguard": "IMIX-2c-ethip4udpwireguard8tnlsw-ip4base-ndrpdr",
    "dot1qip6": "IMIX-2c-dot1q-ip6base-ndrpdr",
    "lispip6": "IMIX-2c-ethip6lispip6-ip6base-ndrpdr",
    "dot1ql2xcbase": "IMIX-2c-dot1q-l2xcbase-ndrpdr",
    "macip": "IMIX-2c-eth-l2bdbasemaclrn-macip-iacl50sl-10kflows-ndrpdr",
    "srv6masq": "IMIX-2c-ethip6srhip6-ip6base-srv6proxy-masq-ndrpdr",
    "1lbonding": "IMIX-2c-1lbvpplacp-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2...",
}
case_keys = list(cases.keys())
revisions = {
    "8b77f3a549bdc69b043b1eddac4462a30a65d849": "MLRv2 (rls2306)",
    "d965f1720128163f4ecb3bbb5d06cd3d71327e52": "MLRv7 (continuity)",
    "84066977f54738ef3d94581be7dabac50f5cc0d3": "MLRv7a (aggressive)",
}

cols_in, cols_out = [], []
infixes = ("dur", "ndr", "pdr")
for case in case_keys:
    for infix in infixes:
        cols_in.append(f"{case}_{infix}")

stats = {key: {} for key in revisions}
with open("3n_results.csv", "rt") as fin:
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
with open("3n_comparison.csv", "wt") as fout:
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
