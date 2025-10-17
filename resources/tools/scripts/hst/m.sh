# Copyright (c) 2025 Cisco and/or its affiliates.
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


# https://logs.fd.io/vex-yul-rot-jenkins-1/csit-vpp-perf-hoststack-daily-master-3na-spr/512/
arch="$1"

rm -f "index.html"
jobname="https://logs.fd.io/vex-yul-rot-jenkins-1/csit-vpp-perf-hoststack-daily-master-${arch}"
curl -sf "${jobname}/index.html" > "index.html"
for i in `grep -o '"[0-9]\+/index.html' index.html | cut -d '"' -f 2- | cut -d '/' -f 1 | sort -rn`; do
    if ! curl -sf "${jobname}/${i}/log.html.gz" | zcat > "log.html"; then
        echo "${i}: failed to download. Aborted run?"
        continue
    fi
    fgrep '"strings"' log.html | sed 's/"/\n/g' | grep '.\{999\}' > s.txt
    python3 m0.py
    python3 m1.py | tee -a "summ-${arch}.txt"
done
