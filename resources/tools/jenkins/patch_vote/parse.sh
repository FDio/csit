#!/bin/bash
# Copyright (c) 2018 Cisco and/or its affiliates.
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

set -exu -o pipefail

# TODO: Absolute paths via "readlink -e"?
REL_DIR="$1"
IN_FILE="$REL_DIR/output.xml"
OUT_FILE="$REL_DIR/results.txt"

echo "Parsing $IN_FILE putting results into $OUT_FILE"
echo "TODO: Re-use parts of PAL when they support subsample test parsing."

grep -o "Maximum Receive Rate trial results in packets per second: .*\]</status>" "$IN_FILE" | grep -o '\[.*\]' > "$OUT_FILE"
