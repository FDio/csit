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

function parse_bmrr_results () {

    set -exuo pipefail

    # Currently "parsing" is just two greps.
    # TODO: Re-use PAL parsing code to make parsing more general and centralized.
    #
    # Arguments:
    # - $1 - Path to (existing) directory holding robot output.xml result.
    # Files read:
    # - output.xml - From argument location.
    # Files updated:
    # - results.txt - (Re)created, in argument location.
    # Functions called:
    # - die - Print to stderr and exit, defined in common_functions.sh

    rel_dir=$(readlink -e "$1") || die 1 "Readlink failed."
    in_file="${rel_dir}/output.xml"
    out_file="${rel_dir}/results.txt"

    # TODO: Do we need to check echo exit code explicitly?
    echo "Parsing ${in_file} putting results into ${out_file}"
    echo "TODO: Re-use parts of PAL when they support subsample test parsing."

    # TODO: How should we wrap this line?
    grep -o "Maximum Receive Rate trial results in packets per second: .*\]</status>"\
        "${in_file}" | grep -o '\[.*\]' > "${out_file}" || {
        die 1 "Some grep for parsing has failed."
    }
}
