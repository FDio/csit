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

import os

with open("results.csv", "wt") as fout:
    fout.write("CSIT_rls,job_name_fragment,run_number,VPP_version,TG_host,NIC_model,test_ID,PDR_lower\n")
    for subdir, dirs, files in os.walk("."):
        if "version.txt" not in files:
            #print(f"version not in {subdir}")
            continue
        slashes = subdir.split("/")
        dashes = slashes[1].split("-")
        with open(f"{subdir}/version.txt", "rt") as fin:
            content = fin.read()
        if not content:
            #print(f"empty version in {subdir}")
            continue
        version = content.split(" ")[2].strip()
        prelude = f"{dashes[0]},{dashes[1]}-{dashes[2]},{slashes[2]},{version}"
        if "2306,3n-icx,9,23.02-release" in prelude:
            continue
        with open(f"{subdir}/hosts_raw.txt", "rt") as fin:
            content = fin.read()
        idx0 = content.find("'host': '")
        idx0 += 9
        idx1 = content.find("'", idx0)
        prelude += f",{content[idx0:idx1]}"
        with open(f"{subdir}/results.txt", "rt") as fin:
            testcase = ""
            pdr_lower = ""
            nic_model = ""
            status = ""
            for line in fin:
                if line.startswith("<test "):
                    idx0 = line.find('name="')
                    idx0 += 6
                    idx1 = line.find('"', idx0)
                    testcase = line[idx0:idx1].lower()
                    # TODO: Separate framesize, cores, drivers?
                    pdr_lower = ""
                    nic_model = ""
                    status = ""
                elif line.startswith("PDR_LOWER: "):
                    idx0 = 11
                    idx1 = line.find(" ", idx0)
                    pdr_lower = line[idx0:idx1]
                elif line.startswith("<tag>NIC_"):
                    if pdr_lower:
                        idx0 = 9
                        idx1 = line.find("<", idx0)
                        nic_model = line[idx0:idx1].lower()
                elif line.startswith('<status status="'):
                    if nic_model and not status:
                        idx0 = 16
                        idx1 = line.find('"', idx0)
                        status = line[idx0:idx1]
                        if status == "PASS":
                            fout.write(f"{prelude},{nic_model},{testcase},{pdr_lower}\n")
                        nic_model = ""
                else:
                    raise RuntimeError(f"unrecognized result line {line}")
