# Copyright (c) 2021 Cisco and/or its affiliates.
# Copyright (c) 2021 PANTHEON.tech s.r.o.
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
    # Variables read:
    # - TARGET - Target directory.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh
    # - archive_test_results - Archiving results.
    # - parse_results - See definition in this file.

    set -exuo pipefail

    archive_test_results "$1" || die
    parse_results "${TARGET}" || {
        die "The function should have died on error."
    }
}


function build_vpp_ubuntu_amd64 () {

    # This function is using make pkg-verify to build VPP with all dependencies
    # that is ARCH/OS aware. VPP repo is SSOT for building mechanics and CSIT
    # is consuming artifacts. This way if VPP will introduce change in building
    # mechanics they will not be blocked by CSIT repo.
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

    make UNATTENDED=y pkg-verify || die "VPP build using make pkg-verify failed."
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
    # - csit_current - Holding test results of the patch under test (PUT).
    # - csit_parent - Holding test results of parent of PUT.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    set -exuo pipefail

    cd "${VPP_DIR}" || die "Change directory operation failed."
    rm -rf "csit_current" "csit_parent" || {
        die "Directory deletion failed."
    }
    mkdir -p "csit_current" "csit_parent" || {
        die "Directory creation failed."
    }
}


function parse_results () {

    # Currently "parsing" is just few greps.
    # TODO: Re-use PAL parsing code, make parsing more general and centralized.
    #
    # The current implementation attempts to parse for BMRR, PDR and passrate.
    # If failures are present, they are reported as fake throughput values,
    # enabling bisection to focus on the cause (or the fix) of the failures.
    #
    # The fake values are created with MRR multiplicity,
    # otherwise jumpavg (which dislikes short groups) could misclassify them.
    #
    # Arguments:
    # - ${1} - Path to (existing) directory holding robot output.xml result.
    # Files read:
    # - output.xml - From argument location.
    # Files updated:
    # - results.txt - (Re)created, in argument location.
    # Variables read:
    # - CSIT_PERF_TRIAL_MULTIPLICITY - To create fake results of this length.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh
    # - parse_results_mrr - See definition in this file.
    # - parse_results_ndrpdr - See definition in this file.
    # - parse_results_passrate - See definition in this file.
    # - parse_results_soak - See definition in this file.

    set -exuo pipefail

    rel_dir="$(readlink -e "${1}")" || die "Readlink failed."
    in_file="${rel_dir}/output.xml" || die
    out_file="${rel_dir}/results.txt" || die
    echo "Parsing ${in_file} putting results into ${out_file}" || die
    # Frst attempt: (B)MRR.
    if parse_results_mrr "${in_file}" "${out_file}"; then
        return 0
    fi
    # BMRR parsing failed. Attempt PDR/NDR.
    if parse_results_ndrpdr "${in_file}" "${out_file}"; then
        return 0
    fi
    # PDR/NDR parsing failed. Attempt soak.
    if parse_results_soak "${in_file}" "${out_file}"; then
        return 0
    fi
    # Soak parsing failed.
    # Probably not a perf test at all (or a failed one),
    # but we can still bisect by passrate.
    parse_results_passrate "${in_file}" "${out_file}" || die
}


function parse_results_mrr () {

    # Parse MRR test message(s) into JSON-readable output.
    #
    # Return non-zero if parsing fails.
    #
    # Arguments:
    # - ${1} - Path to (existing) input file. Required.
    # - ${2} - Path to (overwritten if exists) output file. Required.
    # Files read:
    # - output.xml - The input file from argument location.
    # Files updated:
    # - results.txt - (Re)created, in argument location.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    set -exuo pipefail

    in_file="${1}" || die "Two arguments needed."
    out_file="${2}" || die "Two arguments needed."
    pattern='Maximum Receive Rate trial results in .*' || die
    pattern+=' per second: .*\]</status>' || die
    # RC of the following line is returned.
    grep -o "${pattern}" "${in_file}" | grep -o '\[.*\]' > "${out_file}"
}


function parse_results_ndrpdr () {

    # Parse NDRPDR test message(s) for PDR_LOWER, into JSON-readable output.
    #
    # Return non-zero if parsing fails.
    # Parse for PDR, unless environment variable says NDR.
    #
    # Arguments:
    # - ${1} - Path to (existing) input file. Required.
    # - ${2} - Path to (overwritten if exists) output file. Required.
    # Variables read:
    # - FDIO_CSIT_PERF_PARSE_NDR - If defined and "yes", parse for NDR, not PDR.
    # Files read:
    # - output.xml - The input file from argument location.
    # Files updated:
    # - results.txt - (Re)created, in argument location.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    set -exuo pipefail

    in_file="${1}" || die "Two arguments needed."
    out_file="${2}" || die "Two arguments needed."
    if [[ "${FDIO_CSIT_PERF_PARSE_NDR:-no}" == "yes" ]]; then
        pattern1='NDR_LOWER: .*, .*<' || die
    else
        pattern1='PDR_LOWER: .*, .*<' || die
    fi
    # Adapted from https://superuser.com/a/377084
    pattern2='(?<=: ).*(?= pps)' || die
    if grep "${pattern1}" "${in_file}" | grep -Po "${pattern2}" >> "${out_file}"
    then
        # Add bracket https://www.shellhacks.com/sed-awk-add-end-beginning-line/
        sed -i 's/.*/[&]/' "${out_file}"
        # Returns nonzero if fails.
    else
        return 1
    fi
}


function parse_results_passrate () {

    # Create fake values for failed tests.
    #
    # This function always passes (or dies).
    #
    # A non-zero but small value is chosen for failed run, to distinguish from
    # real nonzero perf (which are big in general) and real zero values.
    # A medium sized value is chosen for a passed run.
    # This way bisect can search for breakages and fixes in device tests.
    # At least in theory, as device tests are bootstrapped too differently.
    #
    # The fake value is repeated according to BMRR multiplicity,
    # because a single value can be lost in high stdev data.
    # (And it does not hurt for single value outputs such as NDR.)
    #
    # TODO: Count number of tests and generate fake results for every one.
    #       Currently that would interfere with test retry logic.
    #
    # Arguments:
    # - ${1} - Path to (existing) input file. Required.
    # - ${2} - Path to (overwritten if exists) output file. Required.
    # Variables read:
    # - CSIT_PERF_TRIAL_MULTIPLICITY - To create fake results of this length.
    # Files read:
    # - output.xml - The input file from argument location.
    # Files updated:
    # - results.txt - (Re)created, in argument location.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    set -exuo pipefail

    in_file="${1}" || die "Two arguments needed."
    out_file="${2}" || die "Two arguments needed."
    # The last status is the top level (global) robot status.
    # It only passes if there were no (critical) test failures.
    if fgrep '<status status=' "${out_file}" | tail -n 1 | fgrep '"PASS"'; then
        fake_value="30.0" || die
    else
        fake_value="2.0" || die
    fi
    out_arr=("[") || die
    for i in `seq "${CSIT_PERF_TRIAL_MULTIPLICITY:-1}"`; do
        out_arr+=("${fake_value}" ",") || die
    done
    # The Python part uses JSON parser, the last comma has to be removed.
    # Requires Bash 4.3 https://stackoverflow.com/a/36978740
    out_arr[-1]="]" || die
    # TODO: Is it possible to avoid space separation by manipulating IFS?
    echo "${out_arr[@]}" > "${out_file}" || die
}


function parse_results_soak () {

    # Parse soak test message(s) for lower bound, into JSON-readable output.
    #
    # Return non-zero if parsing fails.
    #
    # Arguments:
    # - ${1} - Path to (existing) input file. Required.
    # - ${2} - Path to (overwritten if exists) output file. Required.
    # Files read:
    # - output.xml - The input file from argument location.
    # Files updated:
    # - results.txt - (Re)created, in argument location.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    set -exuo pipefail

    in_file="${1}" || die "Two arguments needed."
    out_file="${2}" || die "Two arguments needed."
    pattern1='PLRsearch lower bound: .*, .*<' || die
    # Adapted from https://superuser.com/a/377084
    pattern2='(?<=: ).*(?= pps)' || die
    if grep "${pattern1}" "${in_file}" | grep -Po "${pattern2}" >> "${out_file}"
    then
        # Add bracket https://www.shellhacks.com/sed-awk-add-end-beginning-line/
        sed -i 's/.*/[&]/' "${out_file}"
        # Returns nonzero if fails.
    else
        return 1
    fi
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


function set_aside_commit_build_artifacts () {

    # Function is copying VPP built artifacts from actual checkout commit for
    # further use and clean git.
    # Variables read:
    # - VPP_DIR - Path to existing directory, parent to accessed directories.
    # Directories read:
    # - build-root - Existing directory with built VPP artifacts (also DPDK).
    # Directories updated:
    # - ${VPP_DIR} - A local git repository, parent commit gets checked out.
    # - build_current - Old contents removed, content of build-root copied here.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    set -exuo pipefail

    cd "${VPP_DIR}" || die "Change directory operation failed."
    rm -rf "build_current" || die "Remove operation failed."
    mkdir -p "build_current" || die "Directory creation failed."
    mv "build-root"/*".deb" "build_current"/ || die "Move operation failed."
    # The previous build could have left some incompatible leftovers,
    # e.g. DPDK artifacts of different version (in build/external).
    # Also, there usually is a copy of dpdk artifact in build-root.
    git clean -dffx "build"/ "build-root"/ || die "Git clean operation failed."
    # Finally, check out the parent commit.
    git checkout HEAD~ || die "Git checkout operation failed."
    # Display any other leftovers.
    git status || die "Git status operation failed."
}


function set_aside_parent_build_artifacts () {

    # Function is copying VPP built artifacts from parent checkout commit for
    # further use. Checkout to parent is not part of this function.
    # Variables read:
    # - VPP_DIR - Path to existing directory, parent of accessed directories.
    # Directories read:
    # - build-root - Existing directory with built VPP artifacts (also DPDK).
    # Directories updated:
    # - build_parent - Old directory removed, build-root debs moved here.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    set -exuo pipefail

    cd "${VPP_DIR}" || die "Change directory operation failed."
    rm -rf "build_parent" || die "Remove failed."
    mkdir -p "build_parent" || die "Directory creation operation failed."
    mv "build-root"/*".deb" "build_parent"/ || die "Move operation failed."
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
