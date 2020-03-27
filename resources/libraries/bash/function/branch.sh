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

# This library defines functions related to handling VPP and CSIT git branches.
# Keep functions ordered alphabetically, please.

# TODO: Add a link to bash style guide.


function checkout_csit_for_vpp () {

    # This should be useful mainly for vpp-csit jobs (and timed csit-vpp jobs),
    # which want to use csit oper branches (especially for vpp stable branches).
    # This allows the Jenkins job to checkout CSIT master branch,
    # and use this function to compute and checkout the final CSIT branch.
    # When the refspec is overriden, the computation is still performed,
    # in order to show (on Sandbox) the computation is correct.
    #
    # On failure, working directory could remain changed to ${CSIT_DIR}.
    # TODO: It could be possible to use ERR trap to force popd,
    #   but with "set -x" the noise is not worth it,
    #   especially if several levels of pushd are to be supported.
    #
    # Arguments:
    # - ${1} - Git branch of VPP code, e.g. GERRIT_BRANCH set by Jenkins.
    #   This is not read from GERRIT_BRANCH directly,
    #   because in csit-vpp jobs that refers to CSIT branch instead.
    #   Required.
    # Variables read:
    # - CSIT_REF - If set and non-empty, override the computed refspec.
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    #   The repository could be cloned with "--depth 1",
    #   but it is required to be cloned with "--no-single-branch",
    #   as otherwise the "git checkout" this function performs probably fails.
    # Directoried updated:
    # - ${CSIT_DIR} - Probably "git checkout"ed into new refspec.
    # Functions called:
    # - die - Print to stderr and exit, defined in "common" library.

    set -exuo pipefail

    case "${1}" in
        "stable/"*)
            branch_id="origin/${1/stable\//oper-rls}"
            ;;
        "rls"*)
            branch_id="origin/oper-${1}"
            ;;
        *)  # This includes "master".
            branch_id="origin/oper"
    esac
    # Get the latest verified version of the required branch.
    pushd "${CSIT_DIR}" || die
    csit_branches="$(git branch -r | grep -E "${branch_id}-[0-9]+")" || {
        # We might be in time when VPP has cut their new branch,
        # but CSIT not, yet. Use master oper branch in this case.
        csit_branches="$(git branch -r | grep -E "origin/oper-[0-9]+")" || die
    }
    # The xargs is there just to remove leading (or trailing) spaces.
    csit_branch="$(echo "${csit_branches}" | tail -n 1 | xargs)" || die
    if [[ -z "${csit_branch}" ]]; then
        die "No verified CSIT branch found - exiting."
    fi
    # Remove 'origin/' from the branch name.
    csit_branch="${csit_branch#origin/}" || die
    override_ref="${CSIT_REF-}"
    if [[ -n "${override_ref}" ]]; then
        git fetch --depth=1 https://gerrit.fd.io/r/csit "${override_ref}" || die
        git checkout FETCH_HEAD || die
    else
        git checkout "${csit_branch}" || die
    fi
    popd || die
}
