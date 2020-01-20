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
    git checkout 63882357549a39c7be4b23b48418b8febb5b0e12
    target="csit_current"
    mkdir -p "${target}"
    echo "[19556284.0, 19554015.0, 19510811.0, 19557095.0, 19526518.0, 19569428.0, 19539004.0, 19503050.0, 19535215.0, 19541372.0, 19578392.0, 19579959.0, 19599191.0, 19578238.0, 18525559.0, 19524901.0, 19578399.0, 19515853.0, 19531435.0, 19588207.0, 19567439.0, 19568263.0, 19541738.0, 19576578.0, 19552836.0, 19549918.0, 19563941.0, 18451705.0, 19511959.0, 19061374.0, 19496460.0, 18637182.0, 19533365.0, 18501305.0, 18520803.0, 18443914.0, 19483565.0, 18712576.0, 19477383.0, 19516628.0, 19495118.0, 19508902.0, 19500465.0, 19501094.0, 19407205.0, 19490076.0, 18503239.0, 18488004.0, 19216212.0, 19500432.0, 19024637.0, 19517008.0, 19500030.0, 19504357.0, 19500136.0, 19508824.0, 19516968.0, 18835160.0, 19319465.0, 18637230.0]" > "${target}/results.txt"
    git bisect new
    git checkout 1f8eeb7cb90b51c8682818bb0d68cc121f08b481
    target="csit_parent"
    mkdir -p "${target}"
    echo "[18343518.0, 19056918.0, 18971590.0, 18855412.0, 18806817.0, 18815673.0, 18709271.0, 18244205.0, 19092829.0, 18692404.0, 18652722.0, 19121841.0, 18729903.0, 18880295.0, 19181235.0, 18515424.0, 18783431.0, 19108421.0, 19099341.0, 18840608.0, 18679728.0, 18263107.0, 19094580.0, 18151312.0, 19122858.0, 19065571.0, 18077174.0, 19105037.0, 18893459.0, 18515952.0, 18667659.0, 19001587.0, 19113727.0, 18670775.0, 19124839.0, 18664188.0, 18582332.0, 18048558.0, 18641462.0, 18860139.0, 18111163.0, 18973753.0, 18911611.0, 18432041.0, 19140840.0, 19121234.0, 18671410.0, 18686795.0, 18735605.0, 18771264.0, 18821200.0, 18726711.0, 18735820.0, 18654552.0, 19128638.0, 18498190.0, 18851712.0, 18671918.0, 18637728.0, 19132407.0]" > "${target}/results.txt"
    git bisect old | tee git.log
    git describe
    iteration=0

    if head -n 1 "git.log" | cut -b -11 | fgrep -q "Bisecting:"; then
        echo "Still bisecting..."
    else
        echo "Bisecting done."
        break
    fi
    let iteration+=1
    target="csit_new"
    mkdir -p "${target}"
    echo "[19136821.0, 19108806.0, 18633348.0, 18367350.0, 18203427.0, 19317117.0, 19277629.0, 18486114.0, 18234749.0, 18422179.0, 18382620.0, 18376513.0, 18445860.0, 18501312.0, 18221632.0, 18663067.0, 19312497.0, 19289853.0, 18989744.0, 18227719.0, 19280405.0, 19287310.0, 19014035.0, 18343625.0, 19309760.0, 18203772.0, 18256134.0, 18367859.0, 19219928.0, 19248852.0, 18397680.0, 18341877.0, 18603611.0, 19245990.0, 18761879.0, 18311022.0, 19220087.0, 18413986.0, 19187374.0, 18705972.0, 18507306.0, 18291247.0, 18125666.0, 18149388.0, 18141736.0, 18153041.0, 19227954.0, 19256264.0, 18233452.0, 18173973.0, 19252279.0, 18246701.0, 18115557.0, 19127211.0, 19215037.0, 19216625.0, 19236891.0, 19238723.0, 18361181.0, 18404771.0]" > "${target}/results.txt"
    set +e
    python "csit/resources/tools/integrated/compare_bisect.py"
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
    git describe

}

doit
