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

set -exuo pipefail

# Currently "parsing" is just two greps.
# TODO: Re-use PAL parsing code to make output more general and deduplicated.
#
# Arguments:
# - $1 - Path to (existing) directory holding robot output.xml result.
# Variables (re)set:
# - REL_DIR - Path normalized from argument value.
# - IN_FILE - Normalized path to existing output.xml file.
# - OUT_FILE - Normalized path to created results.txt file.
# Functions called:
# - die - Print to stderr and exit, defined in common_functions.sh

REL_DIR=$(readlink -e "$1") || die 1 "Readlink failed."
IN_FILE="$REL_DIR/output.xml"
OUT_FILE="$REL_DIR/results.txt"

# TODO: Do we need to check echo exit code explicitly?
echo "Parsing $IN_FILE putting results into $OUT_FILE"
echo "TODO: Re-use parts of PAL when they support subsample test parsing."

# TODO: How should we wrap this line?
grep -o "Maximum Receive Rate trial results in packets per second: .*\]</status>" "$IN_FILE" | grep -o '\[.*\]' > "$OUT_FILE" || {
    die 1 "Some grep for parsing has failed."
}
