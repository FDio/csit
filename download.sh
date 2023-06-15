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

set -xuo pipefail

logs_fd_io="dc7f1y83kdjnx.cloudfront.net"
URL_BASE="https://${logs_fd_io}/vex-yul-rot-jenkins-1/csit-vpp-perf-report-iterative"

rel_n_archs=(
    "2302-2n-aws"
    "2302-2n-clx"
    "2302-2n-icx"
    "2302-2n-spr"
    "2302-2n-tx2"
    "2302-2n-zn2"
    "2302-3n-alt"
    "2302-3n-aws"
    "2302-3n-icx"
    "2302-3n-snr"
    "2302-3n-tsh"
    "2306-2n-aws"
    "2306-2n-clx"
    "2306-2n-icx"
    "2306-2n-spr"
    "2306-2n-tx2"
    "2306-2n-zn2"
    "2306-3n-alt"
    "2306-3n-aws"
    "2306-3n-icx"
    "2306-3n-snr"
    "2306-3n-tsh"
)

for rna in "${rel_n_archs[@]}"; do
    mkdir -p "${rna}"
    pushd "${rna}"
    wget -N "${URL_BASE}-${rna}/index.html"
    for run in `grep -o '"[0-9]*/index\.html"' index.html | cut -d '"' -f 2 | cut -d '/' -f 1 | sort -un`; do
        mkdir -p "${run}"
        pushd "${run}"
        if [[ ! -f "output_info.xml.gz" ]]; then
            wget -N "${URL_BASE}-${rna}/${run}/output_info.xml.gz" || true
        fi
        if [[ ! -f "results.txt" ]]; then
            if [[ -f "output_info.xml.gz" && ! -f "output_info.xml" ]]; then
                gunzip -k "output_info.xml.gz"
            fi
            if [[ -f "output_info.xml" ]]; then
                fgrep -m 1 'VPP version:' output_info.xml | cut -d '>' -f 2 > "version.txt"
                fgrep -m 1 'hosts=' output_info.xml > "hosts_raw.txt"
                grep '<test\|PDR_LOWER.*,<\|<tag>NIC_\|^<status status' output_info.xml > "results.txt"
            fi
        fi
        if [[ -f "output_info.xml" ]]; then
            rm "output_info.xml"
        fi
        popd
    done
    popd
done
