#!/usr/bin/env bash

# Copyright (c) 2019 Cisco and/or its affiliates.
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

# FIXME: Update.
# This entry script does not change CSIT branch,
# use "with_oper_for_vpp.sh" wrapper for that.
#
# Assumptions:
# + There is a directory holding VPP repo with patch under test checked out.
# + It contains csit subdirectory with CSIT code to use (this script is there).
# + Everything needed to build VPP is already installed locally.
# Consequences:
# + At the end, VPP repo has parent commit checked out and built.
# + Directories build_root, build and csit are reset during the run.
# + The following directories (relative to VPP repo) are (re)created:
# ++ csit_new, csit_parent, build_new, build_parent,
# ++ archive, csit/archive, csit_download_dir.

# TODO: "git bisect skip" if test fails during the search?


function doit() {
    trap "git bisect reset" EXIT RETURN
    git bisect start
    target="csit_current"
    mkdir -p "${target}"
    echo "[1100000, 1110000]" > "${target}/results.txt"
    git bisect new
    git checkout fb0815d4ae4bb0fe27bd9313f34b45c8593b907e
    git bisect old | tee git.log
    target="csit_parent"
    mkdir -p "${target}"
    echo "[1190000, 1200000]" > "${target}/results.txt"
    iteration=0
    while true
    do
        if head -n 1 "git.log" | cut -b -11 | fgrep -q "Bisecting:"; then
            echo "Still bisecting..."
        else
            echo "Bisecting done."
            break
        fi
        sleep 1
        let iteration+=1
        target="csit_new"
        mkdir -p "${target}"
        echo | awk ' { srand('"${iteration}"'); print "[1" 100000 + 100000 * rand() ", 1" 100000 + 100000 * rand() "]" } ' | tee "${target}/results.txt"
        set +e
        python "csit/resources/tools/scripts/compare_bisect.py"
        bisect_rc="${?}"
        set -e
        if [[ "${bisect_rc}" == "3" ]]; then
            adjective="new"
            cat "${target}/results.txt" > "csit_current/results.txt"
        elif [[ "${bisect_rc}" == "0" ]]; then
            adjective="old"
            cat "${target}/results.txt" > "csit_parent/results.txt"
        else
            die "Unexpected return code ${bisect_rc}"
        fi
        git bisect "${adjective}" | tee "git.log"
    done
}

doit
