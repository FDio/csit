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

# This library defines functions used mainly by "per_patch_perf.sh" entry script.
# Generally, the functions assume "common.sh" library has been sourced already.

# Keep functions ordered alphabetically, please.

# TODO: Add a link to bash style guide.


function archive_parse_test_results () {

    set -exuo pipefail

    # Arguments:
    # - ${1}: Directory to archive to. Required. Parent has to exist.
    # Variables read:
    # - ARCHIVE_DIR - Path to where robot result files are created in.
    # - VPP_DIR - Path to existing directory, root for to relative paths.
    # Directories updated:
    # - ${1} - Created, and robot and parsing files are moved/created there.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh
    # - parse_bmrr_results - See definition in this file.

    cd "${VPP_DIR}" || die "Change directory command failed."
    target="$(readlink -f "$1")"
    mkdir -p "${target}" || die "Directory creation failed."
    for filename in "output.xml" "log.html" "report.html"; do
        mv "${ARCHIVE_DIR}/${filename}" "${target}/${filename}" || {
            die "Attempt to move '${filename}' failed."
        }
    done
    parse_bmrr_results "${target}" || {
        die "The function should have died on error."
    }
}


function build_vpp_ubuntu_amd64 () {

    set -exuo pipefail

    # TODO: Make sure whether this works on other distros/archs too.

    # Arguments:
    # - ${1} - String identifier for echo, can be unset.
    # Variables read:
    # - VPP_DIR - Path to existing directory, parent to accessed directories.
    # Directories updated:
    # - ${VPP_DIR} - Whole subtree, many files (re)created by the build process.
    # - ${VPP_DIR}/build-root - Final build artifacts for CSIT end up here.
    # - ${VPP_DIR}/dpdk - The dpdk artifact is built, but moved to build-root/.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    cd "${VPP_DIR}" || die "Change directory command failed."
    echo 'Building using "make build-root/vagrant/build.sh"'
    # TODO: Do we want to support "${DRYRUN}" == "True"?
    make UNATTENDED=yes install-dep || die "Make install-dep failed."
    # The per_patch script calls this function twice, first for the new commit,
    # then for its parent commit. On Jenkins, no dpdk is installed at first,
    # locally it might have been installed. New dpdk is installed second call.
    # If make detects installed vpp-ext-deps with matching version,
    # it skips building vpp-ext-deps entirely.
    # On the other hand, if parent uses different dpdk version,
    # the new vpp-ext-deps is built, but the old one is not removed
    # from the build directory if present. (Further functions move both,
    # and during test dpkg would decide randomly which version gets installed.)
    # As per_patch is too dumb (yet) to detect any of that,
    # the only safe solution is to clean build directory and force rebuild.
    # TODO: Make this function smarter and skip DPDK rebuilds if possible.
    cmd=("dpkg-query" "--showformat='$${Version}'" "--show" "vpp-ext-deps")
    installed_deb_ver="$(sudo "${cmd[@]}" || true)"
    if [[ -n "${installed_deb_ver}" ]]; then
        sudo dpkg --purge "vpp-ext-deps" || {
            die "DPDK package uninstalation failed."
        }
    fi
    make UNATTENDED=yes install-ext-deps || {
        die "Make install-ext-deps failed."
    }
    build-root/vagrant/"build.sh" || die "Vagrant VPP build script failed."
    echo "*******************************************************************"
    echo "* VPP ${1-} BUILD SUCCESSFULLY COMPLETED" || {
        die "Argument not found."
    }
    echo "*******************************************************************"
}


function compare_test_results () {

    set -exuo pipefail

    # Variables read:
    # - VPP_DIR - Path to directory with VPP git repo (at least built parts).
    # - ARCHIVE_DIR - Path to where robot result files are created in.
    # - PYTHON_SCRIPTS_DIR - Path to directory holding comparison utility.
    # Directories recreated:
    # - csit_parent - Sibling to csit directory, for holding results
    #   of parent build.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh
    # - parse_bmrr_results - See definition in this file.
    # Exit code:
    # - 0 - If the comparison utility sees no regression (nor data error).
    # - 1 - If the comparison utility sees a regression (or data error).

    cd "${VPP_DIR}" || die "Change directory operation failed."
    # Reusing CSIT main virtualenv.
    pip install -r "${PYTHON_SCRIPTS_DIR}/perpatch_requirements.txt" || {
        die "Perpatch Python requirements installation failed."
    }
    python "${PYTHON_SCRIPTS_DIR}/compare_perpatch.py"
    # The exit code determines the vote result.
}


function download_builds () {

    set -exuo pipefail

    # This is mostly useful only for Sandbox testing, to avoid recompilation.
    #
    # Arguments:
    # - ${1} - URL to download VPP builds from.
    # Variables read:
    # - VPP_DIR - Path to WORKSPACE, parent of created directories.
    # Directories created:
    # - archive - Ends up empty, not to be confused with ${ARCHIVE_DIR}.
    # - build_new - Holding built artifacts of the patch under test (PUT).
    # - built_parent - Holding built artifacts of parent of PUT.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    cd "${VPP_DIR}" || die "Change directory operation failed."
    rm -rf "build-root" "build_parent" "build_new" "archive" "csit_new" || {
        die "Directory removal failed."
    }
    wget -N --progress=dot:giga "${1}" || die "Wget download failed."
    unzip "archive.zip" || die "Archive extraction failed."
    mv "archive/build_parent" ./ || die "Move operation failed."
    mv "archive/build_new" ./ || die "Move operation failed."
}


function initialize_csit_dirs () {

    set -exuo pipefail

    # This could be in prepare_test, but download_builds also needs this.
    #
    # Variables read:
    # - VPP_DIR - Path to WORKSPACE, parent of created directories.
    # Directories created:
    # - csit_new - Holding test results of the patch under test (PUT).
    # - csit_parent - Holding test results of parent of PUT.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    cd "${VPP_DIR}" || die "Change directory operation failed."
    rm -rf "csit_new" "csit_parent" || {
        die "Directory deletion failed."
    }
    mkdir -p "csit_new" "csit_parent" || {
        die "Directory creation failed."
    }
}


function parse_bmrr_results () {

    set -exuo pipefail

    # Currently "parsing" is just two greps.
    # TODO: Re-use PAL parsing code, make parsing more general and centralized.
    #
    # Arguments:
    # - ${1} - Path to (existing) directory holding robot output.xml result.
    # Files read:
    # - output.xml - From argument location.
    # Files updated:
    # - results.txt - (Re)created, in argument location.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    rel_dir="$(readlink -e "${1}")" || die "Readlink failed."
    in_file="${rel_dir}/output.xml"
    out_file="${rel_dir}/results.txt"
    # TODO: Do we need to check echo exit code explicitly?
    echo "Parsing ${in_file} putting results into ${out_file}"
    echo "TODO: Re-use parts of PAL when they support subsample test parsing."
    pattern='Maximum Receive Rate trial results in packets'
    pattern+=' per second: .*\]</status>'
    grep -o "${pattern}" "${in_file}" | grep -o '\[.*\]' > "${out_file}" || {
        die "Some parsing grep command has failed."
    }
}


function prepare_build_parent () {

    set -exuo pipefail

    # Variables read:
    # - VPP_DIR - Path to existing directory, parent to accessed directories.
    # Directories read:
    # - build-root - Existing directory with built VPP artifacts (also DPDK).
    # Directories updated:
    # - ${VPP_DIR} - A local git repository, parent commit gets checked out.
    # - build_new - Old contents removed, content of build-root copied here.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    cd "${VPP_DIR}" || die "Change directory operation failed."
    rm -rf "build_new" || die "Remove operation failed."
    mkdir -p "build_new" || die "Directory creation failed."
    mv "build-root"/*".deb" "build_new"/ || die "Move operation failed."
    # The previous build could have left some incompatible leftovers,
    # e.g. DPDK artifacts of different version (in build/external).
    # Also, there usually is a copy of dpdk artifact in build-root.
    git clean -dffx "build"/ "build-root"/ || die "Git clean operation failed."
    # Finally, check out the parent commit.
    git checkout HEAD~ || die "Git checkout operation failed."
    # Display any other leftovers.
    git status || die "Git status operation failed."
}


function prepare_test () {

    set -exuo pipefail

    # Variables read:
    # - VPP_DIR - Path to existing directory, parent of accessed directories.
    # Directories read:
    # - build-root - Existing directory with built VPP artifacts (also DPDK).
    # Directories updated:
    # - build_parent - Old directory removed, build-root debs moved here.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    cd "${VPP_DIR}" || die "Change directory operation failed."
    rm -rf "build_parent" || die "Remove failed."
    mkdir -p "build_parent" || die "Directory creation operation failed."
    mv "build-root"/*".deb" "build_parent"/ || die "Move operation failed."
}


function select_build () {

    set -exuo pipefail

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

    cd "${VPP_DIR}" || die "Change directory operation failed."
    source_dir="$(readlink -e "$1")"
    rm -rf "${DOWNLOAD_DIR}"/* || die "Cleanup of download dir failed."
    cp "${source_dir}"/*".deb" "${DOWNLOAD_DIR}" || die "Copy operation failed."
    # TODO: Is there a nice way to create symlinks,
    #   so that if job fails on robot, results can be archived?
}


function set_perpatch_dut () {

    set -exuo pipefail

    # Variables set:
    # - DUT - CSIT test/ subdirectory containing suites to execute.

    # TODO: Detect DUT from job name, when we have more than just VPP perpatch.

    DUT="vpp"
}


function set_perpatch_vpp_dir () {

    set -exuo pipefail

    # Variables read:
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # Variables set:
    # - VPP_DIR - Path to existing root of local VPP git repository.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    # In perpatch, CSIT is cloned inside VPP clone.
    VPP_DIR="$(readlink -e "${CSIT_DIR}/..")" || die "Readlink failed."
}
