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
                    duration = (end - start).total_seconds()
                    if duration < 0:
                        duration += 24 * 60 * 60
                    outline += f",NA,NA,{duration}"
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
