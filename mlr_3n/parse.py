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

from datetime import datetime
import os

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
NO_VERSION = -1
WAITING_FOR_NAME = 0
WAITING_FOR_NDR_OR_FAIL = 1
WAITING_FOR_PDR = 2

with open("results.csv", "wt") as fout:
    fout.write("run_number,refspec")
    for case in case_keys:
        fout.write(f",{case}_ndr,{case}_pdr,{case}_dur")
    fout.write("\n")
    for subdir, dirs, files in os.walk("."):
        if "/" not in subdir:
            continue
        run = subdir.split("/")[1]
        outline = f"{run}"
        version = ""
        case_index = 0
        case_phase = NO_VERSION
        with open(f"{subdir}/timing.txt", "rt") as fin:
            for line in fin:
                line_split = line.split(" ")
                if not version:
                    version = line_split[5]
                    outline += f",{version}"
                    case_phase = WAITING_FOR_NAME
                    continue
                if case_phase == WAITING_FOR_NAME:
                    expected = cases[case_keys[case_index]]
                    if "-avf-" in line:
                        break
                    if expected not in line:
                        raise RuntimeError(f"{expected} not in {line}")
                    start = datetime.strptime(line_split[0], "%H:%M:%S")
                    case_phase = WAITING_FOR_NDR_OR_FAIL
                    continue
                if case_phase == WAITING_FOR_NDR_OR_FAIL:
                    end = datetime.strptime(line_split[0], "%H:%M:%S")
                    ndr = line_split[3] if "NDR_LOWER" in line else "NA"
                    if ndr != "NA":
                        case_phase = WAITING_FOR_PDR
                        continue
                    #duration = (end - start).total_seconds()
                    #if duration < 0:
                    #    duration += 24 * 60 * 60
                    #outline += f",NA,NA,{duration}"
                    outline += f",NA,NA,NA"
                    case_index += 1
                    case_phase = WAITING_FOR_NAME
                    continue
                if case_phase == WAITING_FOR_PDR:
                    if ndr == "NA" or "PDR_LOWER" not in line:
                        raise RuntimeError(f"PDR error {line}")
                    pdr = line_split[3]
                    duration = (end - start).total_seconds()
                    if duration < 0:
                        duration += 24 * 60 * 60
                    outline += f",{ndr},{pdr},{duration}"
                    case_index += 1
                    case_phase = WAITING_FOR_NAME
                    continue
                else:
                    raise RuntimeError(f"case phase {case_phase}")
        if not case_index or case_phase == NO_VERSION:
            print(f"skipping invalid {outline}")
        else:
            fout.write(f"{outline}\n")
print("Success.")
