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

import base64
import zlib

started = False
date = ""
good = 0
zero = 0
part = 0
segment = 0
reset = 0
with open('u.txt', 'r', encoding='utf-8') as fin, open('f.txt', 'w') as fout:
    for line in fin:
        if not started:
            if "telemetry.bundle_vppctl - vppctl" in line:
                started = True
            continue
        splitline = line.split(" ")
        if "telemetry.bundle_vppctl" in line:
            date = f"{splitline[0]} {splitline[1]}"
        if "Packets pushed into" in line:
            for substr in splitline:
                if substr:
                    good = int(substr)
                    break
        if "Zero receive window" in line:
            for substr in splitline:
                if substr:
                    zero = int(substr)
                    break
        if "Packets partially" in line:
            for substr in splitline:
                if substr:
                    part = int(substr)
                    break
        if "Segment not in recei" in line:
            for substr in splitline:
                if substr:
                    segment = int(substr)
                    break
        if "tcp4-reset" in line and "Resets sent" in line:
            for substr in splitline:
                if substr:
                    reset = int(substr)
                    break
        if "Arguments:" in line:
            print(f"{date=} {good=} {zero=} {part=} {segment=} {reset=}")
            break
        fout.write(line)
