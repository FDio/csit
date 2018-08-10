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

# This library defines functions used mainly by "per_patch.sh" entry script.
# Generally, the functions assume "common.sh" library has been sourced already.

# Keep functions ordered alphabetically, please.

# TODO: Add a link to bash style guide.


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
    # If make detects installed vpp-dpdk-dev with matching version,
    # it skips building vpp-dpdk-dkms entirely, but we need that file.
    # On the other hand, if parent uses different dpdk version,
    # The new vpp-dpdk-dkms is built, but the old one is not removed
    # from the build directory if present. (Further functions move both,
    # and during test dpkg decides on its own which version gets installed.)
    # As per_patch is too dumb (yet) to detect any of that,
    # the only safe solution is to clean build directory and force rebuild.
    # TODO: Make this function smarter and skip DPDK rebuilds if possible.
    installed_deb_ver=$(sudo dpkg-query --showformat='${Version}'\
         --show vpp-dpdk-dev || true)
    if [[ -n "${installed_deb_ver}" ]]; then
        sudo dpkg --purge "vpp-dpdk-dev" || {
            die "Dpdk package uninstalation failed."
        }
    fi
    make UNATTENDED=yes dpdk-install-dev || {
        die "Make dpdk-install-dev failed."
    }
    "build-root/vagrant/build.sh" || die "Vagrant VPP build script failed."
    # CSIT also needs the DPDK artifacts, which is not in build-root.
    mv -v "dpdk/vpp-dpdk-dkms"*".deb" "build-root"/ || {
        die "*.deb move failed."
    }

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
    rm -rf "csit_parent" || die "Remove operation failed."
    mkdir -p "csit_parent" || die "Directory creation failed."
    for filename in "output.xml" "log.html" "report.html"; do
        mv "${ARCHIVE_DIR}/${filename}" "csit_parent/${filename}" || {
            die "Attempt to move '${filename}' failed."
        }
    done
    parse_bmrr_results "csit_parent" || {
        die "The function should have died on error."
    }

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
    # - DOWNLOAD_DIR - Path to directory pybot takes the build to test from.
    # Directories created:
    # - archive - Ends up empty, not to be confused with ${ARCHIVE_DIR}.
    # - build_new - Holding built artifacts of the patch under test (PUT).
    # - built_parent - Holding built artifacts of parent of PUT.
    # - csit_new - (Re)set to a symlink to archive robot results on failure.
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
    cp -r "build_new"/*".deb" "${DOWNLOAD_DIR}" || {
        die "Copy operation failed."
    }
    # Create symlinks so that if job fails on robot, results can be archived.
    ln -s "${ARCHIVE_DIR}" "csit_new" || die "Symbolic link creation failed."
}


function parse_bmrr_results () {

    set -exuo pipefail

    # Currently "parsing" is just two greps.
    # TODO: Re-use PAL parsing code, make parsing more general and centralized.
    #
    # Arguments:
    # - $1 - Path to (existing) directory holding robot output.xml result.
    # Files read:
    # - output.xml - From argument location.
    # Files updated:
    # - results.txt - (Re)created, in argument location.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    rel_dir=$(readlink -e "$1") || die "Readlink failed."
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
    # e.g. DPDK artifacts of different version.
    # "make -C dpdk clean" does not actually remove such .deb file.
    # Also, there usually is a copy of dpdk artifact in build-root.
    git clean -dffx "dpdk"/ "build-root"/ || die "Git clean operation failed."
    # Finally, check out the parent commit.
    git checkout HEAD~ || die "Git checkout operation failed."
    # Display any other leftovers.
    git status || die "Git status operation failed."
}


function prepare_test_new () {

    set -exuo pipefail

    # Variables read:
    # - VPP_DIR - Path to existing directory, parent of accessed directories.
    # - DOWNLOAD_DIR - Path to directory where Robot takes builds to test from.
    # - ARCHIVE_DIR - Path to where robot result files are created in.
    # Directories read:
    # - build-root - Existing directory with built VPP artifacts (also DPDK).
    # Directories updated:
    # - build_parent - Old directory removed, build-root moved to become this.
    # - ${DOWNLOAD_DIR} - Old content removed, files from build_new copied here.
    # - csit_new - Currently a symlink to to archive robot results on failure.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    cd "${VPP_DIR}" || die "Change directory operationf failed."
    rm -rf "build_parent" "csit_new" "${DOWNLOAD_DIR}"/* || die "Rm failed."
    mkdir -p "build_parent" || die "Directory creation operation failed."
    mv "build-root"/*".deb" "build_parent"/ || die "Move operation failed."
    cp "build_new"/*".deb" "${DOWNLOAD_DIR}" || die "Copy operation failed."
    # Create symlinks so that if job fails on robot, results can be archived.
    ln -s "${ARCHIVE_DIR}" "csit_new" || die "Symbolic link creation failed."
}


function prepare_test_parent () {

    set -exuo pipefail

    # Variables read:
    # - VPP_DIR - Path to existing directory, parent of accessed directories.
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # - ARCHIVE_DIR and DOWNLOAD_DIR - Paths to directories to update.
    # Directories read:
    # - build_parent - Build artifacts (to test next) are copied from here.
    # Directories updated:
    # - csit_new - Deleted, then recreated and latest robot results copied here.
    # - ${CSIT_DIR} - Subjected to git reset and git clean.
    # - ${ARCHIVE_DIR} - Created if not existing (if deleted by git clean).
    # - ${DOWNLOAD_DIR} - Created after git clean, parent build copied here.
    # - csit_parent - Currently a symlink to csit/ to archive robot results.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh
    # - parse_bmrr_results - See definition in this file.

    cd "${VPP_DIR}" || die "Change directory operation failed."
    rm -rf "csit_new" "csit_parent" || die "Remove operation failed."
    mkdir -p "csit_new" || die "Create directory operation failed."
    for filename in "output.xml" "log.html" "report.html"; do
        mv "${ARCHIVE_DIR}/${filename}" "csit_new/${filename}" || {
            die "Move operation of '${filename}' failed."
        }
    done
    parse_bmrr_results "csit_new" || {
        die "The function should have died on error."
    }

    pushd "${CSIT_DIR}" || die "Change directory operation failed."
    git reset --hard HEAD || die "Git reset operation failed."
    git clean -dffx || die "Git clean operation failed."
    popd || die "Change directory operation failed."
    mkdir -p "${ARCHIVE_DIR}" "${DOWNLOAD_DIR}" || die "Dir creation failed."

    cp "build_parent"/*".deb" "${DOWNLOAD_DIR}"/ || die "Copy failed."
    # Create symlinks so that if job fails on robot, results can be archived.
    ln -s "${ARCHIVE_DIR}" "csit_parent" || die "Symlink creation failed."
}


function select_perpatch_tags () {

    set -exuo pipefail

    # Variables set:
    # - DUT - CSIT test/ subdirectory containing suites to execute.
    # - TAGS - Array of processed tag boolean expressions.
    # Hardcoded values:
    # - List of tag expressions selecting few suites.
    # - Prefix, selecting test type and NIC.

    DUT="vpp"

    # Hardcoded for perpatch. TODO: Make this configurable.
    test_tag_array=("l2xcbaseAND1cAND64b"
                    "l2bdbaseAND1cAND64b"
                    "ip4baseAND1cAND64b"
                    "ip6baseAND1cAND78b")
    TAGS=()
    # We will prefix with perftest to prevent running other tests
    # (e.g. Functional).
    prefix="perftestAND"
    # Automatic prefixing for VPP jobs to limit the NIC used and
    # traffic evaluation to MRR.
    prefix="${prefix}mrrANDnic_intel-x710AND"
    for TAG in "${test_tag_array[@]}"; do
        if [[ ${TAG} == "!"* ]]; then
            # Exclude tags are not prefixed.
            TAGS+=("${TAG}")
        else
            TAGS+=("${prefix}${TAG}")
        fi
    done
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
    VPP_DIR=$(readlink -e "${CSIT_DIR}/..") || die "Readlink failed."
}
