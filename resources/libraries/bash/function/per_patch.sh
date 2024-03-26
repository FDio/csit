# Copyright (c) 2023 Cisco and/or its affiliates.
# Copyright (c) 2023 PANTHEON.tech s.r.o.
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


function build_vpp_ubuntu () {

    # This function is using make pkg-verify to build VPP with all dependencies
    # that is ARCH/OS aware. VPP repo is SSOT for building mechanics and CSIT
    # is consuming artifacts. This way if VPP will introduce change in building
    # mechanics they will not be blocked by CSIT repo.
    #
    # Arguments:
    # - ${1} - String identifier for echo, can be unset.
    # Variables read:
    # - MAKE_PARALLEL_FLAGS - Make flags when building VPP.
    # - MAKE_PARALLEL_JOBS - Number of cores to use when building VPP.
    # - VPP_DIR - Path to existing directory, parent to accessed directories.
    # Directories updated:
    # - ${VPP_DIR} - Whole subtree, many files (re)created by the build process.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    set -exuo pipefail

    cd "${VPP_DIR}" || die "Change directory command failed."
    if [ -n "${MAKE_PARALLEL_FLAGS-}" ]; then
        echo "Building VPP. Number of cores for build set with" \
             "MAKE_PARALLEL_FLAGS='${MAKE_PARALLEL_FLAGS}'."
    elif [ -n "${MAKE_PARALLEL_JOBS-}" ]; then
        echo "Building VPP. Number of cores for build set with" \
             "MAKE_PARALLEL_JOBS='${MAKE_PARALLEL_JOBS}'."
    else
        echo "Building VPP. Number of cores not set, " \
             "using build default ($(grep -c ^processor /proc/cpuinfo))."
    fi

    make UNATTENDED=y install-dep install-ext-deps pkg-deb-debug VPP_EXTRA_CMAKE_ARGS=-DVPP_ENABLE_SANITIZE_ADDR=ON || die
    echo "* VPP ${1-} BUILD SUCCESSFULLY COMPLETED" || {
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


function initialize_csit_dirs () {

    set -exuo pipefail

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
        name_part="${1}" || die
        shift || die
        dir_name="csit_${name_part}" || die
        rm -rf "${dir_name}" || die "Directory deletion failed."
        mkdir -p "${dir_name}" || die "Directory creation failed."
    done
}


function main_bisect_loop () {

    # Perform the iterative part of bisect entry script.
    #
    # The logic is too complex to remain in the entry script.
    #
    # At the start, the loop assumes git bisect old/new has just been executed,
    # and verified more iterations are needed.
    # The iteration cleans the build directory and builds the new mid commit.
    # Then, testbed is reserved, tests run, and testbed unreserved.
    # Results are moved from default to archive location
    # (indexed by iteration number) and analyzed.
    # The new adjective ("old" or "new") is selected,
    # and git bisect with the adjective is executed.
    # The symlinks csit_early and csit_late are updated to tightest bounds.
    # The git.log file is examined and if the bisect is finished, loop ends.

    iteration=0
    while true
    do
        let iteration+=1
        git clean -dffx "build"/ "build-root"/ || die
        build_vpp_ubuntu "MIDDLE" || die
        select_build "build-root" || die
        check_download_dir || die
        reserve_and_cleanup_testbed || die
        run_robot || die
        move_test_results "csit_middle/${iteration}" || die
        untrap_and_unreserve_testbed || die
        rm -vf "csit_mid" || die
        ln -s -T "csit_middle/${iteration}" "csit_mid" || die
        set +e
        python3 "${TOOLS_DIR}/integrated/compare_bisect.py"
        bisect_rc="${?}"
        set -e
        if [[ "${bisect_rc}" == "3" ]]; then
            adjective="new"
            rm -v "csit_late" || die
            ln -s -T "csit_middle/${iteration}" "csit_late" || die
        elif [[ "${bisect_rc}" == "0" ]]; then
            adjective="old"
            rm -v "csit_early" || die
            ln -s -T "csit_middle/${iteration}" "csit_early" || die
        else
            die "Unexpected return code: ${bisect_rc}"
        fi
        git bisect "${adjective}" | tee "git.log" || die
        git describe || die
        git status || die
        if head -n 1 "git.log" | cut -b -11 | fgrep -q "Bisecting:"; then
            echo "Still bisecting..."
        else
            echo "Bisecting done."
            break
        fi
    done
}


function move_test_results () {

    # Arguments:
    # - ${1}: Directory to archive to. Required. Parent has to exist.
    # Variable set:
    # - TARGET - Target archival directory, equivalent to the argument.
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
    file_list=("output.xml" "log.html" "report.html" "tests")
    for filename in "${file_list[@]}"; do
        mv "${ARCHIVE_DIR}/${filename}" "${TARGET}/${filename}" || die
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
    dir_name="build_${1}" || die
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
