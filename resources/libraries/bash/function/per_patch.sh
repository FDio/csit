# Copyright (c) 2020 Cisco and/or its affiliates.
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

# This library defines functions used mainly by per patch entry scripts.
# Generally, the functions assume "common.sh" library has been sourced already.
# Keep functions ordered alphabetically, please.

function archive_test_results () {

    # Arguments:
    # - ${1}: Directory to archive to. Required. Parent has to exist.
    # Variable set:
    # - TARGET - Target directory.
    # Variables read:
    # - ARCHIVE_DIR - Path to where robot result files are created in.
    # - VPP_DIR - Path to existing directory, root for to relative paths.
    # Directories updated:
    # - ${1} - Created, and robot and parsing files are moved/created there.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    set -exuo pipefail

    cd "${VPP_DIR}" || die "Change directory command failed."
    TARGET="$(readlink -f "$1")"
    mkdir -p "${TARGET}" || die "Directory creation failed."
    for filename in "output.xml" "log.html" "report.html"; do
        mv "${ARCHIVE_DIR}/${filename}" "${TARGET}/${filename}" || {
            die "Attempt to move '${filename}' failed."
        }
    done
}


function archive_parse_test_results () {

    # Arguments:
    # - ${1}: Directory to archive to. Required. Parent has to exist.
    # - ${2} - Control word "fake" to fake data on failure. Optional.
    # Variables read:
    # - TARGET - Target directory.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh
    # - archive_test_results - Archiving results.
    # - parse_results - See definition in this file.

    set -exuo pipefail

    archive_test_results "$1" || die
    parse_results "${TARGET}" "${2-}" || {
        die "The function should have died on error."
    }
}


function build_vpp_ubuntu () {

    # This function is using make pkg-verify to build VPP with all dependencies
    # that is ARCH/OS aware. VPP repo is SSOT for building mechanics and CSIT
    # is consuming artifacts. This way if VPP will introduce change in building
    # mechanics they will not be blocked by CSIT repo.
    #
    # Arguments:
    # - ${1} - String identifier for echo, can be unset.
    # Variables read:
    # - VPP_DIR - Path to existing directory, parent to accessed directories.
    # Directories updated:
    # - ${VPP_DIR} - Whole subtree, many files (re)created by the build process.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    set -exuo pipefail

    cd "${VPP_DIR}" || die "Change directory command failed."
    echo "*** VPP ${1-} BUILD STARTS" || die "Argument not found."
    make UNATTENDED=y pkg-verify || die "VPP build failed."
    echo "*** VPP ${1-} BUILD SUCCESSFULLY COMPLETED" || {
        die "Argument not found."
    }
}


function compare_test_results () {

    # Variables read:
    # - VPP_DIR - Path to directory with VPP git repo (at least built parts).
    # - ARCHIVE_DIR - Path to where robot result files are created in.
    # - PYTHON_SCRIPTS_DIR - Path to directory holding comparison utility.
    # Directories recreated:
    # - csit_parent - Sibling to csit directory, for holding results
    #   of parent build.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh
    # Exit code:
    # - 0 - If the comparison utility sees no regression (nor data error).
    # - 1 - If the comparison utility sees a regression (or data error).

    set -exuo pipefail

    cd "${VPP_DIR}" || die "Change directory operation failed."
    # Reusing CSIT main virtualenv.
    python3 "${TOOLS_DIR}/integrated/compare_perpatch.py"
    # The exit code determines the vote result.
}


function download_builds () {

    # This is mostly useful only for Sandbox testing, to avoid recompilation.
    #
    # Arguments:
    # - ${1} - URL to download VPP builds from.
    # Variables read:
    # - VPP_DIR - Path to WORKSPACE, parent of created directories.
    # Directories created:
    # - archive - Ends up empty, not to be confused with ${ARCHIVE_DIR}.
    # - build_current - Holding built artifacts of the patch under test (PUT).
    # - built_parent - Holding built artifacts of parent of PUT.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    set -exuo pipefail

    cd "${VPP_DIR}" || die "Change directory operation failed."
    dirs=("build-root" "build_parent" "build_current" "archive" "csit_current")
    rm -rf ${dirs[@]} || {
        die "Directory removal failed."
    }
    wget -N --progress=dot:giga "${1}" || die "Wget download failed."
    unzip "archive.zip" || die "Archive extraction failed."
    mv "archive/build_parent" ./ || die "Move operation failed."
    mv "archive/build_current" ./ || die "Move operation failed."
}


function initialize_csit_dirs () {

    # Create directories of form ${VPP_DIR}/csit_<arg>
    # If the directory exists it is deleted before created anew.
    #
    # Arguments:
    # - ${n} - Name part of n-th directory to create.
    # Variables read:
    # - VPP_DIR - Path to WORKSPACE, parent of created directories.
    # Directories created:
    # - csit_{part} - See the caller what it is used for.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    set -exuo pipefail

    cd "${VPP_DIR}" || die "Change directory operation failed."
    while true; do
        if [[ ${#} < 1 ]]; then
            # All directories created.
            break
        fi
        name_part="${1}"
        shift
        dir_name="csit_${name_part}"
        rm -rf "${dir_name}" || {
            die "Directory deletion failed."
        }
        mkdir -p "${dir_name}" || {
            die "Directory creation failed."
        }
    done
}


function main_bisect_loop () {

    # Perform the iterative part of bisect entry script.
    #
    # The logic was deemed too complex to remain in the entry script.
    #
    # FIXME.

    iteration=0
    while true
    do
        if head -n 1 "git.log" | cut -b -11 | fgrep -q "Bisecting:"; then
            echo "Still bisecting..."
        else
            echo "Bisecting done."
            break
        fi
        let iteration+=1
        git clean -dffx "build"/ "build-root"/ || die
        build_vpp_ubuntu "MIDDLE" || die
        reserve_and_cleanup_testbed || die
        select_build "build-root" || die
        check_download_dir || die
        run_and_parse "csit_middle/${iteration}" || die
        untrap_and_unreserve_testbed || die
        cp -f "csit_middle/${iteration}/results.txt" "csit_middle/results.txt" || die
        set +e
        python3 "${TOOLS_DIR}/integrated/compare_bisect.py"
        bisect_rc="${?}"
        set -e
        if [[ "${bisect_rc}" == "3" ]]; then
            adjective="new"
            cp -f "csit_middle/results.txt" "csit_late/results.txt" || die
        elif [[ "${bisect_rc}" == "0" ]]; then
            adjective="old"
            cp -f "csit_middle/results.txt" "csit_early/results.txt" || die
        else
            die "Unexpected return code ${bisect_rc}"
        fi
        git bisect "${adjective}" | tee "git.log" || die
        git describe || die
    done
}


function parse_results () {

    # Currently "parsing" is just few greps.
    # TODO: Re-use PAL parsing code, make parsing more general and centralized.
    #
    # The current implementation attempts to parse for PDR,
    # if parsing for BMRR fails.
    #
    # If the results are malformed or missing, the behavior is configurable.
    # By default, die is called. But optionally fake results are constructed.
    # Fake results are useful for bisection, as we do not want to die there.
    # Bisection with mixed result finds the cause (or the fix) of the failure.
    #
    # Arguments:
    # - ${1} - Path to (existing) directory holding robot output.xml result.
    # - ${2} - Control word "fake" to fake data on failure. Optional.
    # Files read:
    # - output.xml - From argument location.
    # Files updated:
    # - results.txt - (Re)created, in argument location.
    # Variables read:
    # - CSIT_PERF_TRIAL_MULTIPLICITY - To create fake results of this length.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    set -exuo pipefail

    rel_dir="$(readlink -e "${1}")" || die "Readlink failed."
    in_file="${rel_dir}/output.xml"
    out_file="${rel_dir}/results.txt"
    # TODO: Do we need to check echo exit code explicitly?
    echo "Parsing ${in_file} putting results into ${out_file}"
    echo "TODO: Re-use parts of PAL when they support subsample test parsing."
    pattern='Maximum Receive Rate trial results in packets'
    pattern+=' per second: .*\]</status>'
    set +e
    grep -o "${pattern}" "${in_file}" | grep -o '\[.*\]' > "${out_file}"
    rc="${?}"
    set -e
    if [[ "${rc}" == "0" ]]; then
        # Parsing succeeded, return early.
        return 0
    fi
    # BMRR parsing failed. Attempt PDR.
    pattern1='PDR_LOWER: .*, .*<'
    # Adapted from https://superuser.com/a/377084
    pattern2='(?<=: ).*(?= pps)'
    set +e
    grep "${pattern1}" "${in_file}" | grep -Po "${pattern2}" >> "${out_file}"
    rc="${?}"
    set -e
    # Add brackets. https://www.shellhacks.com/sed-awk-add-end-beginning-line/
    sed -i 's/.*/[&]/' "${out_file}"
    if [[ "${rc}" == "0" ]]; then
        # Parsing succeeded, return early.
        return 0
    fi
    # PDR parsing failed.
    if [[ "${2-}" != "fake" ]]; then
        die "Malformed or missing test results."
    fi
    warn "Faking test results to allow bisect script locate the cause."
    out_arr=("[")
    for i in `seq "${CSIT_PERF_TRIAL_MULTIPLICITY:-1}"`; do
        out_arr+=("2.0" ",")
    done
    # The Python part uses JSON parser, the last comma has to be removed.
    # Requires Bash 4.3 https://stackoverflow.com/a/36978740
    out_arr[-1]="]"
    # TODO: Is it possible to avoid space separation by manipulating IFS?
    echo "${out_arr[@]}" > "${out_file}"
}


function run_and_parse () {

    # Run test and parse results (creating fake ones on failure).
    # Retry few times if there was a failure in the test.
    # Else leave fake results.

    # Variables read:
    # - TARGET - Directory to store parsed test results.
    # Files rewritten:
    # - ${TARGET}/results.txt - Stored parsed (or fake) results.
    # Functions called:
    # - run_pybot - see common.sh
    # - copy_archives - see common.sh
    # - archive_parse_test_results - see this file

    set -exuo pipefail

    for try in {1..5}; do
        run_pybot || die
        copy_archives || die
        archive_parse_test_results "${1}" "fake" || die
        results=$(<"${TARGET}/results.txt")
        if [[ "[ 2.0 "* != "${results}" ]]; then
            break
        fi
    done
}


function select_build () {

    # Arguments:
    # - ${1} - Path to directory to copy VPP artifacts from. Required.
    # Variables read:
    # - DOWNLOAD_DIR - Path to directory where Robot takes builds to test from.
    # - VPP_DIR - Path to existing directory, root for relative paths.
    # Directories read:
    # - ${1} - Existing directory with built new VPP artifacts (and DPDK).
    # Directories updated:
    # - ${DOWNLOAD_DIR} - Old content removed, .deb files from ${1} copied here.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    set -exuo pipefail

    cd "${VPP_DIR}" || die "Change directory operation failed."
    source_dir="$(readlink -e "$1")"
    rm -rf "${DOWNLOAD_DIR}"/* || die "Cleanup of download dir failed."
    cp "${source_dir}"/*".deb" "${DOWNLOAD_DIR}" || die "Copy operation failed."
    # TODO: Is there a nice way to create symlinks,
    #   so that if job fails on robot, results can be archived?
}


function set_aside_build_artifacts () {

    # Function used to save VPP .deb artifacts from currently finished build.
    #
    # After the artifacts are copied to the target directory,
    # the main git tree is cleaned up to not interfere with next build.
    #
    # Arguments:
    # - ${1} - String to derive the target directory name from. Required.
    # Variables read:
    # - VPP_DIR - Path to existing directory, parent to accessed directories.
    # Directories read:
    # - build-root - Existing directory with built VPP artifacts (also DPDK).
    # Directories updated:
    # - ${VPP_DIR} - A local git repository, parent commit gets checked out.
    # - build_${1} - Old contents removed, content of build-root copied here.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    set -exuo pipefail

    cd "${VPP_DIR}" || die "Change directory operation failed."
    dir_name="build_${1}"
    rm -rf "${dir_name}" || die "Remove operation failed."
    mkdir -p "${dir_name}" || die "Directory creation failed."
    mv "build-root"/*".deb" "${dir_name}"/ || die "Move operation failed."
    # The previous build could have left some incompatible leftovers,
    # e.g. DPDK artifacts of different version (in build/external).
    # Also, there usually is a copy of dpdk artifact in build-root.
    git clean -dffx "build"/ "build-root"/ || die "Git clean operation failed."
    git status || die
}


function set_perpatch_dut () {

    # Variables set:
    # - DUT - CSIT test/ subdirectory containing suites to execute.

    # TODO: Detect DUT from job name, when we have more than just VPP perpatch.

    set -exuo pipefail

    DUT="vpp"
}


function set_perpatch_vpp_dir () {

    # Variables read:
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # Variables set:
    # - VPP_DIR - Path to existing root of local VPP git repository.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    set -exuo pipefail

    # In perpatch, CSIT is cloned inside VPP clone.
    VPP_DIR="$(readlink -e "${CSIT_DIR}/..")" || die "Readlink failed."
}
