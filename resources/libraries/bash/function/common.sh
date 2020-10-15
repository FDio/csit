# Copyright (c) 2021 Cisco and/or its affiliates.
# Copyright (c) 2021 PANTHEON.tech and/or its affiliates.
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

# This library defines functions used by multiple entry scripts.
# Keep functions ordered alphabetically, please.

# TODO: Add a link to bash style guide.
# TODO: Consider putting every die into a {} block,
#   the code might become more readable (but longer).


function activate_docker_topology () {

    # Create virtual vpp-device topology. Output of the function is topology
    # file describing created environment saved to a file.
    #
    # Variables read:
    # - BASH_FUNCTION_DIR - Path to existing directory this file is located in.
    # - TOPOLOGIES - Available topologies.
    # - NODENESS - Node multiplicity of desired testbed.
    # - FLAVOR - Node flavor string, usually describing the processor.
    # - IMAGE_VER_FILE - Name of file that contains the image version.
    # - CSIT_DIR - Directory where ${IMAGE_VER_FILE} is located.
    # Variables set:
    # - WORKING_TOPOLOGY - Path to topology file.

    set -exuo pipefail

    source "${BASH_FUNCTION_DIR}/device.sh" || {
        die "Source failed!"
    }
    device_image="$(< ${CSIT_DIR}/${IMAGE_VER_FILE})"
    case_text="${NODENESS}_${FLAVOR}"
    case "${case_text}" in
        "1n_skx" | "1n_tx2")
            # We execute reservation over csit-shim-dcr (ssh) which runs sourced
            # script's functions. Env variables are read from ssh output
            # back to localhost for further processing.
            # Shim and Jenkins executor are in the same network on the same host
            # Connect to docker's default gateway IP and shim's exposed port
            ssh="ssh root@172.17.0.1 -p 6022"
            run="activate_wrapper ${NODENESS} ${FLAVOR} ${device_image}"
            # The "declare -f" output is long and boring.
            set +x
            # backtics to avoid https://midnight-commander.org/ticket/2142
            env_vars=`${ssh} "$(declare -f); ${run}"` || {
                die "Topology reservation via shim-dcr failed!"
            }
            set -x
            set -a
            source <(echo "$env_vars" | grep -v /usr/bin/docker) || {
                die "Source failed!"
            }
            set +a
            ;;
        "1n_vbox")
            # We execute reservation on localhost. Sourced script automatially
            # sets environment variables for further processing.
            activate_wrapper "${NODENESS}" "${FLAVOR}" "${device_image}" || die
            ;;
        *)
            die "Unknown specification: ${case_text}!"
    esac

    trap 'deactivate_docker_topology' EXIT || {
         die "Trap attempt failed, please cleanup manually. Aborting!"
    }

    # Replace all variables in template with those in environment.
    source <(echo 'cat <<EOF >topo.yml'; cat ${TOPOLOGIES[0]}; echo EOF;) || {
        die "Topology file create failed!"
    }

    WORKING_TOPOLOGY="/tmp/topology.yaml"
    mv topo.yml "${WORKING_TOPOLOGY}" || {
        die "Topology move failed!"
    }
    cat ${WORKING_TOPOLOGY} | grep -v password || {
        die "Topology read failed!"
    }
}


function activate_virtualenv () {

    # Update virtualenv pip package, delete and create virtualenv directory,
    # activate the virtualenv, install requirements, set PYTHONPATH.

    # Arguments:
    # - ${1} - Path to existing directory for creating virtualenv in.
    #          If missing or empty, ${CSIT_DIR} is used.
    # - ${2} - Path to requirements file, ${CSIT_DIR}/requirements.txt if empty.
    # Variables read:
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # Variables exported:
    # - PYTHONPATH - CSIT_DIR, as CSIT Python scripts usually need this.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    root_path="${1-$CSIT_DIR}"
    env_dir="${root_path}/env"
    req_path=${2-$CSIT_DIR/requirements.txt}
    rm -rf "${env_dir}" || die "Failed to clean previous virtualenv."
    pip3 install virtualenv==20.0.20 || {
        die "Virtualenv package install failed."
    }
    virtualenv --no-download --python=$(which python3) "${env_dir}" || {
        die "Virtualenv creation for $(which python3) failed."
    }
    set +u
    source "${env_dir}/bin/activate" || die "Virtualenv activation failed."
    set -u
    pip3 install -r "${req_path}" || {
        die "Requirements installation failed."
    }
    # Most CSIT Python scripts assume PYTHONPATH is set and exported.
    export PYTHONPATH="${CSIT_DIR}" || die "Export failed."
}


function archive_tests () {

    # Create .tar.xz of generated/tests for archiving.
    # To be run after generate_tests, kept separate to offer more flexibility.

    # Directory read:
    # - ${GENERATED_DIR}/tests - Tree of executed suites to archive.
    # File rewriten:
    # - ${ARCHIVE_DIR}/tests.tar.xz - Archive of generated tests.

    set -exuo pipefail

    tar c "${GENERATED_DIR}/tests" | xz -3 > "${ARCHIVE_DIR}/tests.tar.xz" || {
        die "Error creating archive of generated tests."
    }
}


function check_download_dir () {

    # Fail if there are no files visible in ${DOWNLOAD_DIR}.
    #
    # Variables read:
    # - DOWNLOAD_DIR - Path to directory pybot takes the build to test from.
    # Directories read:
    # - ${DOWNLOAD_DIR} - Has to be non-empty to proceed.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    if [[ ! "$(ls -A "${DOWNLOAD_DIR}")" ]]; then
        die "No artifacts downloaded!"
    fi
}


function check_prerequisites () {

    # Fail if prerequisites are not met.
    #
    # Functions called:
    # - installed - Check if application is installed/present in system.
    # - die - Print to stderr and exit.

    set -exuo pipefail

    if ! installed sshpass; then
        die "Please install sshpass before continue!"
    fi
}


function common_dirs () {

    # Set global variables, create some directories (without touching content).

    # Variables set:
    # - BASH_FUNCTION_DIR - Path to existing directory this file is located in.
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # - TOPOLOGIES_DIR - Path to existing directory with available topologies.
    # - JOB_SPECS_DIR - Path to existing directory with job test specifications.
    # - RESOURCES_DIR - Path to existing CSIT subdirectory "resources".
    # - TOOLS_DIR - Path to existing resources subdirectory "tools".
    # - PYTHON_SCRIPTS_DIR - Path to existing tools subdirectory "scripts".
    # - ARCHIVE_DIR - Path to created CSIT subdirectory "archives".
    #   The name is chosen to match what ci-management expects.
    # - DOWNLOAD_DIR - Path to created CSIT subdirectory "download_dir".
    # - GENERATED_DIR - Path to created CSIT subdirectory "generated".
    # Directories created if not present:
    # ARCHIVE_DIR, DOWNLOAD_DIR, GENERATED_DIR.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    this_file=$(readlink -e "${BASH_SOURCE[0]}") || {
        die "Some error during locating of this source file."
    }
    BASH_FUNCTION_DIR=$(dirname "${this_file}") || {
        die "Some error during dirname call."
    }
    # Current working directory could be in a different repo, e.g. VPP.
    pushd "${BASH_FUNCTION_DIR}" || die "Pushd failed"
    relative_csit_dir=$(git rev-parse --show-toplevel) || {
        die "Git rev-parse failed."
    }
    CSIT_DIR=$(readlink -e "${relative_csit_dir}") || die "Readlink failed."
    popd || die "Popd failed."
    TOPOLOGIES_DIR=$(readlink -e "${CSIT_DIR}/topologies/available") || {
        die "Readlink failed."
    }
    JOB_SPECS_DIR=$(readlink -e "${CSIT_DIR}/docs/job_specs") || {
        die "Readlink failed."
    }
    RESOURCES_DIR=$(readlink -e "${CSIT_DIR}/resources") || {
        die "Readlink failed."
    }
    TOOLS_DIR=$(readlink -e "${RESOURCES_DIR}/tools") || {
        die "Readlink failed."
    }
    DOC_GEN_DIR=$(readlink -e "${TOOLS_DIR}/doc_gen") || {
        die "Readlink failed."
    }
    PYTHON_SCRIPTS_DIR=$(readlink -e "${TOOLS_DIR}/scripts") || {
        die "Readlink failed."
    }

    ARCHIVE_DIR=$(readlink -f "${CSIT_DIR}/archives") || {
        die "Readlink failed."
    }
    mkdir -p "${ARCHIVE_DIR}" || die "Mkdir failed."
    DOWNLOAD_DIR=$(readlink -f "${CSIT_DIR}/download_dir") || {
        die "Readlink failed."
    }
    mkdir -p "${DOWNLOAD_DIR}" || die "Mkdir failed."
    GENERATED_DIR=$(readlink -f "${CSIT_DIR}/generated") || {
        die "Readlink failed."
    }
    mkdir -p "${GENERATED_DIR}" || die "Mkdir failed."
}


function compose_pybot_arguments () {

    # Variables read:
    # - WORKING_TOPOLOGY - Path to topology yaml file of the reserved testbed.
    # - DUT - CSIT test/ subdirectory, set while processing tags.
    # - TAGS - Array variable holding selected tag boolean expressions.
    # - TOPOLOGIES_TAGS - Tag boolean expression filtering tests for topology.
    # - TEST_CODE - The test selection string from environment or argument.
    # - SELECTION_MODE - Selection criteria [test, suite, include, exclude].
    # Variables set:
    # - PYBOT_ARGS - String holding part of all arguments for pybot.
    # - EXPANDED_TAGS - Array of strings pybot arguments compiled from tags.

    set -exuo pipefail

    # No explicit check needed with "set -u".
    PYBOT_ARGS=("--loglevel" "TRACE")
    PYBOT_ARGS+=("--variable" "TOPOLOGY_PATH:${WORKING_TOPOLOGY}")

    case "${TEST_CODE}" in
        *"device"*)
            PYBOT_ARGS+=("--suite" "tests.${DUT}.device")
            ;;
        *"perf"*)
            PYBOT_ARGS+=("--suite" "tests.${DUT}.perf")
            ;;
        *)
            die "Unknown specification: ${TEST_CODE}"
    esac

    EXPANDED_TAGS=()
    for tag in "${TAGS[@]}"; do
        if [[ ${tag} == "!"* ]]; then
            EXPANDED_TAGS+=("--exclude" "${tag#$"!"}")
        else
            if [[ ${SELECTION_MODE} == "--test" ]]; then
                EXPANDED_TAGS+=("--test" "${tag}")
            else
                EXPANDED_TAGS+=("--include" "${TOPOLOGIES_TAGS}AND${tag}")
            fi
        fi
    done

    if [[ ${SELECTION_MODE} == "--test" ]]; then
        EXPANDED_TAGS+=("--include" "${TOPOLOGIES_TAGS}")
    fi
}


function deactivate_docker_topology () {

    # Deactivate virtual vpp-device topology by removing containers.
    #
    # Variables read:
    # - NODENESS - Node multiplicity of desired testbed.
    # - FLAVOR - Node flavor string, usually describing the processor.

    set -exuo pipefail

    case_text="${NODENESS}_${FLAVOR}"
    case "${case_text}" in
        "1n_skx" | "1n_tx2")
            ssh="ssh root@172.17.0.1 -p 6022"
            env_vars=$(env | grep CSIT_ | tr '\n' ' ' ) || die
            # The "declare -f" output is long and boring.
            set +x
            ${ssh} "$(declare -f); deactivate_wrapper ${env_vars}" || {
                die "Topology cleanup via shim-dcr failed!"
            }
            set -x
            ;;
        "1n_vbox")
            enter_mutex || die
            clean_environment || {
                die "Topology cleanup locally failed!"
            }
            exit_mutex || die
            ;;
        *)
            die "Unknown specification: ${case_text}!"
    esac
}


function die () {

    # Print the message to standard error end exit with error code specified
    # by the second argument.
    #
    # Hardcoded values:
    # - The default error message.
    # Arguments:
    # - ${1} - The whole error message, be sure to quote. Optional
    # - ${2} - the code to exit with, default: 1.

    set -x
    set +eu
    warn "${1:-Unspecified run-time error occurred!}"
    exit "${2:-1}"
}


function die_on_pybot_error () {

    # Source this fragment if you want to abort on any failed test case.
    #
    # Variables read:
    # - PYBOT_EXIT_STATUS - Set by a pybot running fragment.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    if [[ "${PYBOT_EXIT_STATUS}" != "0" ]]; then
        die "Test failures are present!" "${PYBOT_EXIT_STATUS}"
    fi
}


function generate_tests () {

    # Populate ${GENERATED_DIR}/tests based on ${CSIT_DIR}/tests/.
    # Any previously existing content of ${GENERATED_DIR}/tests is wiped before.
    # The generation is done by executing any *.py executable
    # within any subdirectory after copying.

    # This is a separate function, because this code is called
    # both by autogen checker and entries calling run_pybot.

    # Directories read:
    # - ${CSIT_DIR}/tests - Used as templates for the generated tests.
    # Directories replaced:
    # - ${GENERATED_DIR}/tests - Overwritten by the generated tests.

    set -exuo pipefail

    rm -rf "${GENERATED_DIR}/tests" || die
    cp -r "${CSIT_DIR}/tests" "${GENERATED_DIR}/tests" || die
    cmd_line=("find" "${GENERATED_DIR}/tests" "-type" "f")
    cmd_line+=("-executable" "-name" "*.py")
    # We sort the directories, so log output can be compared between runs.
    file_list=$("${cmd_line[@]}" | sort) || die

    for gen in ${file_list}; do
        directory="$(dirname "${gen}")" || die
        filename="$(basename "${gen}")" || die
        pushd "${directory}" || die
        ./"${filename}" || die
        popd || die
    done
}


function get_test_code () {

    # Arguments:
    # - ${1} - Optional, argument of entry script (or empty as unset).
    #   Test code value to override job name from environment.
    # Variables read:
    # - JOB_NAME - String affecting test selection, default if not argument.
    # Variables set:
    # - TEST_CODE - The test selection string from environment or argument.
    # - NODENESS - Node multiplicity of desired testbed.
    # - FLAVOR - Node flavor string, usually describing the processor.

    set -exuo pipefail

    TEST_CODE="${1-}" || die "Reading optional argument failed, somehow."
    if [[ -z "${TEST_CODE}" ]]; then
        TEST_CODE="${JOB_NAME-}" || die "Reading job name failed, somehow."
    fi

    case "${TEST_CODE}" in
        *"1n-vbox"*)
            NODENESS="1n"
            FLAVOR="vbox"
            ;;
        *"1n-skx"*)
            NODENESS="1n"
            FLAVOR="skx"
            ;;
       *"1n-tx2"*)
            NODENESS="1n"
            FLAVOR="tx2"
            ;;
        *"2n-skx"*)
            NODENESS="2n"
            FLAVOR="skx"
            ;;
        *"2n-zn2"*)
            NODENESS="2n"
            FLAVOR="zn2"
            ;;
        *"3n-skx"*)
            NODENESS="3n"
            FLAVOR="skx"
            ;;
        *"2n-clx"*)
            NODENESS="2n"
            FLAVOR="clx"
            ;;
        *"2n-dnv"*)
            NODENESS="2n"
            FLAVOR="dnv"
            ;;
        *"3n-dnv"*)
            NODENESS="3n"
            FLAVOR="dnv"
            ;;
        *"2n-tx2"*)
            NODENESS="2n"
            FLAVOR="tx2"
            ;;
        *"3n-tsh"*)
            NODENESS="3n"
            FLAVOR="tsh"
            ;;
        *)
            # Fallback to 3-node Haswell by default (backward compatibility)
            NODENESS="3n"
            FLAVOR="hsw"
            ;;
    esac
}


function get_test_tag_string () {

    # Variables read:
    # - GERRIT_EVENT_TYPE - Event type set by gerrit, can be unset.
    # - GERRIT_EVENT_COMMENT_TEXT - Comment text, read for "comment-added" type.
    # - TEST_CODE - The test selection string from environment or argument.
    # Variables set:
    # - TEST_TAG_STRING - The string following trigger word in gerrit comment.
    #   May be empty, or even not set on event types not adding comment.
    # Variables exported optionally:
    # - GRAPH_NODE_VARIANT - Node variant to test with, set if found in trigger.

    # TODO: ci-management scripts no longer need to perform this.

    set -exuo pipefail

    if [[ "${GERRIT_EVENT_TYPE-}" == "comment-added" ]]; then
        case "${TEST_CODE}" in
            *"device"*)
                trigger="devicetest"
                ;;
            *"perf"*)
                trigger="perftest"
                ;;
            *)
                die "Unknown specification: ${TEST_CODE}"
        esac
        # Ignore lines not containing the trigger word.
        comment=$(fgrep "${trigger}" <<< "${GERRIT_EVENT_COMMENT_TEXT}" || true)
        # The vpp-csit triggers trail stuff we are not interested in.
        # Removing them and trigger word: https://unix.stackexchange.com/a/13472
        # (except relying on \s whitespace, \S non-whitespace and . both).
        # The last string is concatenated, only the middle part is expanded.
        cmd=("grep" "-oP" '\S*'"${trigger}"'\S*\s\K.+$') || die "Unset trigger?"
        # On parsing error, TEST_TAG_STRING probably stays empty.
        TEST_TAG_STRING=$("${cmd[@]}" <<< "${comment}" || true)
        if [[ -z "${TEST_TAG_STRING-}" ]]; then
            # Probably we got a base64 encoded comment.
            comment=$(base64 --decode <<< "${GERRIT_EVENT_COMMENT_TEXT}" || true)
            comment=$(fgrep "${trigger}" <<< "${comment}" || true)
            TEST_TAG_STRING=$("${cmd[@]}" <<< "${comment}" || true)
        fi
        if [[ -n "${TEST_TAG_STRING-}" ]]; then
            test_tag_array=(${TEST_TAG_STRING})
            if [[ "${test_tag_array[0]}" == "icl" ]]; then
                export GRAPH_NODE_VARIANT="icl"
                TEST_TAG_STRING="${test_tag_array[@]:1}" || true
            elif [[ "${test_tag_array[0]}" == "skx" ]]; then
                export GRAPH_NODE_VARIANT="skx"
                TEST_TAG_STRING="${test_tag_array[@]:1}" || true
            elif [[ "${test_tag_array[0]}" == "hsw" ]]; then
                export GRAPH_NODE_VARIANT="hsw"
                TEST_TAG_STRING="${test_tag_array[@]:1}" || true
            fi
        fi
    fi
}


function installed () {

    # Check if the given utility is installed. Fail if not installed.
    #
    # Duplicate of common.sh function, as this file is also used standalone.
    #
    # Arguments:
    # - ${1} - Utility to check.
    # Returns:
    # - 0 - If command is installed.
    # - 1 - If command is not installed.

    set -exuo pipefail

    command -v "${1}"
}


function move_archives () {

    # Move archive directory to top of workspace, if not already there.
    #
    # ARCHIVE_DIR is positioned relative to CSIT_DIR,
    # but in some jobs CSIT_DIR is not same as WORKSPACE
    # (e.g. under VPP_DIR). To simplify ci-management settings,
    # we want to move the data to the top. We do not want simple copy,
    # as ci-management is eager with recursive search.
    #
    # As some scripts may call this function multiple times,
    # the actual implementation use copying and deletion,
    # so the workspace gets "union" of contents (except overwrites on conflict).
    # The consequence is empty ARCHIVE_DIR remaining after this call.
    #
    # As the source directory is emptied,
    # the check for dirs being different is essential.
    #
    # Variables read:
    # - WORKSPACE - Jenkins workspace, move only if the value is not empty.
    #   Can be unset, then it speeds up manual testing.
    # - ARCHIVE_DIR - Path to directory with content to be moved.
    # Directories updated:
    # - ${WORKSPACE}/archives/ - Created if does not exist.
    #   Content of ${ARCHIVE_DIR}/ is moved.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    if [[ -n "${WORKSPACE-}" ]]; then
        target=$(readlink -f "${WORKSPACE}/archives")
        if [[ "${target}" != "${ARCHIVE_DIR}" ]]; then
            mkdir -p "${target}" || die "Archives dir create failed."
            cp -rf "${ARCHIVE_DIR}"/* "${target}" || die "Copy failed."
            rm -rf "${ARCHIVE_DIR}"/* || die "Delete failed."
        fi
    fi
}


function reserve_and_cleanup_testbed () {

    # Reserve physical testbed, perform cleanup, register trap to unreserve.
    # When cleanup fails, remove from topologies and keep retrying
    # until all topologies are removed.
    #
    # Variables read:
    # - TOPOLOGIES - Array of paths to topology yaml to attempt reservation on.
    # - PYTHON_SCRIPTS_DIR - Path to directory holding the reservation script.
    # - BUILD_TAG - Any string suitable as filename, identifying
    #   test run executing this function. May be unset.
    # Variables set:
    # - TOPOLOGIES - Array of paths to topologies, with failed cleanups removed.
    # - WORKING_TOPOLOGY - Path to topology yaml file of the reserved testbed.
    # Functions called:
    # - die - Print to stderr and exit.
    # - ansible_playbook - Perform an action using ansible, see ansible.sh
    # Traps registered:
    # - EXIT - Calls cancel_all for ${WORKING_TOPOLOGY}.

    set -exuo pipefail

    while true; do
        for topo in "${TOPOLOGIES[@]}"; do
            set +e
            scrpt="${PYTHON_SCRIPTS_DIR}/topo_reservation.py"
            opts=("-t" "${topo}" "-r" "${BUILD_TAG:-Unknown}")
            python3 "${scrpt}" "${opts[@]}"
            result="$?"
            set -e
            if [[ "${result}" == "0" ]]; then
                # Trap unreservation before cleanup check,
                # so multiple jobs showing failed cleanup improve chances
                # of humans to notice and fix.
                WORKING_TOPOLOGY="${topo}"
                echo "Reserved: ${WORKING_TOPOLOGY}"
                trap "untrap_and_unreserve_testbed" EXIT || {
                    message="TRAP ATTEMPT AND UNRESERVE FAILED, FIX MANUALLY."
                    untrap_and_unreserve_testbed "${message}" || {
                        die "Teardown should have died, not failed."
                    }
                    die "Trap attempt failed, unreserve succeeded. Aborting."
                }
                # Cleanup + calibration checks.
                set +e
                ansible_playbook "cleanup, calibration"
                result="$?"
                set -e
                if [[ "${result}" == "0" ]]; then
                    break
                fi
                warn "Testbed cleanup failed: ${topo}"
                untrap_and_unreserve_testbed "Fail of unreserve after cleanup."
            fi
            # Else testbed is accessible but currently reserved, moving on.
        done

        if [[ -n "${WORKING_TOPOLOGY-}" ]]; then
            # Exit the infinite while loop if we made a reservation.
            warn "Reservation and cleanup successful."
            break
        fi

        if [[ "${#TOPOLOGIES[@]}" == "0" ]]; then
            die "Run out of operational testbeds!"
        fi

        # Wait ~3minutes before next try.
        sleep_time="$[ ( ${RANDOM} % 20 ) + 180 ]s" || {
            die "Sleep time calculation failed."
        }
        echo "Sleeping ${sleep_time}"
        sleep "${sleep_time}" || die "Sleep failed."
    done
}


function run_pybot () {

    # Run pybot with options based on input variables. Create output_info.xml
    #
    # Variables read:
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # - ARCHIVE_DIR - Path to store robot result files in.
    # - PYBOT_ARGS, EXPANDED_TAGS - See compose_pybot_arguments.sh
    # - GENERATED_DIR - Tests are assumed to be generated under there.
    # Variables set:
    # - PYBOT_EXIT_STATUS - Exit status of most recent pybot invocation.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    all_options=("--outputdir" "${ARCHIVE_DIR}" "${PYBOT_ARGS[@]}")
    all_options+=("--noncritical" "EXPECTED_FAILING")
    all_options+=("${EXPANDED_TAGS[@]}")

    pushd "${CSIT_DIR}" || die "Change directory operation failed."
    set +e
    robot "${all_options[@]}" "${GENERATED_DIR}/tests/"
    PYBOT_EXIT_STATUS="$?"
    set -e

    # Generate INFO level output_info.xml for post-processing.
    all_options=("--loglevel" "INFO")
    all_options+=("--log" "none")
    all_options+=("--report" "none")
    all_options+=("--output" "${ARCHIVE_DIR}/output_info.xml")
    all_options+=("${ARCHIVE_DIR}/output.xml")
    rebot "${all_options[@]}" || true
    popd || die "Change directory operation failed."
}


function select_arch_os () {

    # Set variables affected by local CPU architecture and operating system.
    #
    # Variables set:
    # - VPP_VER_FILE - Name of file in CSIT dir containing vpp stable version.
    # - IMAGE_VER_FILE - Name of file in CSIT dir containing the image name.
    # - PKG_SUFFIX - Suffix of OS package file name, "rpm" or "deb."

    set -exuo pipefail

    os_id=$(grep '^ID=' /etc/os-release | cut -f2- -d= | sed -e 's/\"//g') || {
        die "Get OS release failed."
    }

    case "${os_id}" in
        "ubuntu"*)
            IMAGE_VER_FILE="VPP_DEVICE_IMAGE_UBUNTU"
            VPP_VER_FILE="VPP_STABLE_VER_UBUNTU_BIONIC"
            PKG_SUFFIX="deb"
            ;;
        "centos"*)
            IMAGE_VER_FILE="VPP_DEVICE_IMAGE_CENTOS"
            VPP_VER_FILE="VPP_STABLE_VER_CENTOS"
            PKG_SUFFIX="rpm"
            ;;
        *)
            die "Unable to identify distro or os from ${os_id}"
            ;;
    esac

    arch=$(uname -m) || {
        die "Get CPU architecture failed."
    }

    case "${arch}" in
        "aarch64")
            IMAGE_VER_FILE="${IMAGE_VER_FILE}_ARM"
            ;;
        *)
            ;;
    esac
}


function select_tags () {

    # Variables read:
    # - WORKING_TOPOLOGY - Path to topology yaml file of the reserved testbed.
    # - TEST_CODE - String affecting test selection, usually jenkins job name.
    # - DUT - CSIT test/ subdirectory, set while processing tags.
    # - TEST_TAG_STRING - String selecting tags, from gerrit comment.
    #   Can be unset.
    # - TOPOLOGIES_DIR - Path to existing directory with available tpologies.
    # - BASH_FUNCTION_DIR - Directory with input files to process.
    # Variables set:
    # - TAGS - Array of processed tag boolean expressions.
    # - SELECTION_MODE - Selection criteria [test, suite, include, exclude].

    set -exuo pipefail

    # NIC SELECTION
    start_pattern='^  TG:'
    end_pattern='^ \? \?[A-Za-z0-9]\+:'
    # Remove the TG section from topology file
    sed_command="/${start_pattern}/,/${end_pattern}/d"
    # All topologies DUT NICs
    available=$(sed "${sed_command}" "${TOPOLOGIES_DIR}"/* \
                | grep -hoP "model: \K.*" | sort -u)
    # Selected topology DUT NICs
    reserved=$(sed "${sed_command}" "${WORKING_TOPOLOGY}" \
               | grep -hoP "model: \K.*" | sort -u)
    # All topologies DUT NICs - Selected topology DUT NICs
    exclude_nics=($(comm -13 <(echo "${reserved}") <(echo "${available}"))) || {
        die "Computation of excluded NICs failed."
    }

    # Select default NIC tag.
    case "${TEST_CODE}" in
        *"3n-dnv"* | *"2n-dnv"*)
            default_nic="nic_intel-x553"
            ;;
        *"3n-tsh"*)
            default_nic="nic_intel-x520-da2"
            ;;
        *"3n-skx"* | *"2n-skx"* | *"2n-clx"* | *"2n-zn2"*)
            default_nic="nic_intel-xxv710"
            ;;
        *"3n-hsw"* | *"2n-tx2"* | *"mrr-daily-master")
            default_nic="nic_intel-xl710"
            ;;
        *)
            default_nic="nic_intel-x710"
            ;;
    esac

    sed_nic_sub_cmd="sed s/\${default_nic}/${default_nic}/"
    awk_nics_sub_cmd=""
    awk_nics_sub_cmd+='gsub("xxv710","25ge2p1xxv710");'
    awk_nics_sub_cmd+='gsub("x710","10ge2p1x710");'
    awk_nics_sub_cmd+='gsub("xl710","40ge2p1xl710");'
    awk_nics_sub_cmd+='gsub("x520-da2","10ge2p1x520");'
    awk_nics_sub_cmd+='gsub("x553","10ge2p1x553");'
    awk_nics_sub_cmd+='gsub("cx556a","100ge2p1cx556a");'
    awk_nics_sub_cmd+='gsub("vic1227","10ge2p1vic1227");'
    awk_nics_sub_cmd+='gsub("vic1385","40ge2p1vic1385");'
    awk_nics_sub_cmd+='if ($9 =="drv_avf") drv="avf-";'
    awk_nics_sub_cmd+='else if ($9 =="drv_rdma_core") drv ="rdma-";'
    awk_nics_sub_cmd+='else drv="";'
    awk_nics_sub_cmd+='print "*"$7"-" drv $11"-"$5"."$3"-"$1"-" drv $11"-"$5'

    # Tag file directory shorthand.
    tfd="${JOB_SPECS_DIR}"
    case "${TEST_CODE}" in
        # Select specific performance tests based on jenkins job type variable.
        *"ndrpdr-weekly"* )
            readarray -t test_tag_array <<< $(grep -v "#" \
                ${tfd}/mlr_weekly/${DUT}-${NODENESS}-${FLAVOR}.md |
                awk {"$awk_nics_sub_cmd"} || echo "perftest") || die
            SELECTION_MODE="--test"
            ;;
        *"mrr-daily"* )
            readarray -t test_tag_array <<< $(grep -v "#" \
                ${tfd}/mrr_daily/${DUT}-${NODENESS}-${FLAVOR}.md |
                awk {"$awk_nics_sub_cmd"} || echo "perftest") || die
            SELECTION_MODE="--test"
            ;;
        *"mrr-weekly"* )
            readarray -t test_tag_array <<< $(grep -v "#" \
                ${tfd}/mrr_weekly/${DUT}-${NODENESS}-${FLAVOR}.md |
                awk {"$awk_nics_sub_cmd"} || echo "perftest") || die
            SELECTION_MODE="--test"
            ;;
        *"report-iterative"* )
            test_sets=(${TEST_TAG_STRING//:/ })
            # Run only one test set per run
            report_file=${test_sets[0]}.md
            readarray -t test_tag_array <<< $(grep -v "#" \
                ${tfd}/report_iterative/${NODENESS}-${FLAVOR}/${report_file} |
                awk {"$awk_nics_sub_cmd"} || echo "perftest") || die
            SELECTION_MODE="--test"
            ;;
        *"report-coverage"* )
            test_sets=(${TEST_TAG_STRING//:/ })
            # Run only one test set per run
            report_file=${test_sets[0]}.md
            readarray -t test_tag_array <<< $(grep -v "#" \
                ${tfd}/report_coverage/${NODENESS}-${FLAVOR}/${report_file} |
                awk {"$awk_nics_sub_cmd"} || echo "perftest") || die
            SELECTION_MODE="--test"
            ;;
        * )
            if [[ -z "${TEST_TAG_STRING-}" ]]; then
                # If nothing is specified, we will run pre-selected tests by
                # following tags.
                test_tag_array=("mrrAND${default_nic}AND1cAND64bANDip4base"
                                "mrrAND${default_nic}AND1cAND78bANDip6base"
                                "mrrAND${default_nic}AND1cAND64bANDl2bdbase"
                                "mrrAND${default_nic}AND1cAND64bANDl2xcbase"
                                "!dot1q" "!drv_avf")
            else
                # If trigger contains tags, split them into array.
                test_tag_array=(${TEST_TAG_STRING//:/ })
            fi
            SELECTION_MODE="--include"
            ;;
    esac

    # Blacklisting certain tags per topology.
    #
    # Reasons for blacklisting:
    # - ipsechw - Blacklisted on testbeds without crypto hardware accelerator.
    # TODO: Add missing reasons here (if general) or where used (if specific).
    case "${TEST_CODE}" in
        *"2n-skx"*)
            test_tag_array+=("!ipsec")
            ;;
        *"3n-skx"*)
            test_tag_array+=("!ipsechw")
            # Not enough nic_intel-xxv710 to support double link tests.
            test_tag_array+=("!3_node_double_link_topoANDnic_intel-xxv710")
            ;;
        *"2n-clx"*)
            test_tag_array+=("!ipsec")
            ;;
        *"2n-zn2"*)
            test_tag_array+=("!ipsec")
            ;;
        *"2n-dnv"*)
            test_tag_array+=("!ipsechw")
            test_tag_array+=("!memif")
            test_tag_array+=("!srv6_proxy")
            test_tag_array+=("!vhost")
            test_tag_array+=("!vts")
            test_tag_array+=("!drv_avf")
            ;;
        *"2n-tx2"*)
            test_tag_array+=("!ipsechw")
            ;;
        *"3n-dnv"*)
            test_tag_array+=("!memif")
            test_tag_array+=("!srv6_proxy")
            test_tag_array+=("!vhost")
            test_tag_array+=("!vts")
            test_tag_array+=("!drv_avf")
            ;;
        *"3n-tsh"*)
            # 3n-tsh only has x520 NICs which don't work with AVF
            test_tag_array+=("!drv_avf")
            test_tag_array+=("!ipsechw")
            ;;
        *"3n-hsw"*)
            test_tag_array+=("!drv_avf")
            # All cards have access to QAT. But only one card (xl710)
            # resides in same NUMA as QAT. Other cards must go over QPI
            # which we do not want to even run.
            test_tag_array+=("!ipsechwNOTnic_intel-xl710")
            ;;
        *)
            # Default to 3n-hsw due to compatibility.
            test_tag_array+=("!drv_avf")
            test_tag_array+=("!ipsechwNOTnic_intel-xl710")
            ;;
    esac

    # We will add excluded NICs.
    test_tag_array+=("${exclude_nics[@]/#/!NIC_}")

    TAGS=()
    prefix=""

    # Automatic limiting of NIC used if not specified.
    if [[ "${TEST_TAG_STRING-}" == *"nic_"* ]]; then
        prefix=""
    else
        prefix="${default_nic}AND"
    fi
    set +x
    for tag in "${test_tag_array[@]}"; do
        if [[ "${tag}" == "!"* ]]; then
            # Exclude tags are not prefixed.
            TAGS+=("${tag}")
        elif [[ "${tag}" == " "* || "${tag}" == *"perftest"* ]]; then
            # Badly formed tag expressions can trigger way too much tests.
            set -x
            warn "The following tag expression hints at bad trigger: ${tag}"
            warn "Possible cause: Multiple triggers in a single comment."
            die "Aborting to avoid triggering too many tests."
        elif [[ "${tag}" == *"OR"* ]]; then
            # If OR had higher precedence than AND, it would be useful here.
            # Some people think it does, thus triggering way too much tests.
            set -x
            warn "The following tag expression hints at bad trigger: ${tag}"
            warn "Operator OR has lower precedence than AND. Use space instead."
            die "Aborting to avoid triggering too many tests."
        elif [[ "${tag}" != "" && "${tag}" != "#"* ]]; then
            # Empty and comment lines are skipped.
            # Other lines are normal tags, they are to be prefixed.
            TAGS+=("${prefix}${tag}")
        fi
    done
    set -x
}


function select_topology () {

    # Variables read:
    # - NODENESS - Node multiplicity of testbed, either "2n" or "3n".
    # - FLAVOR - Node flavor string, currently either "hsw" or "skx".
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # - TOPOLOGIES_DIR - Path to existing directory with available topologies.
    # Variables set:
    # - TOPOLOGIES - Array of paths to suitable topology yaml files.
    # - TOPOLOGIES_TAGS - Tag expression selecting tests for the topology.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    case_text="${NODENESS}_${FLAVOR}"
    case "${case_text}" in
        # TODO: Move tags to "# Blacklisting certain tags per topology" section.
        # TODO: Double link availability depends on NIC used.
        "1n_vbox")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*vpp_device*.template )
            TOPOLOGIES_TAGS="2_node_single_link_topo"
            ;;
        "1n_skx" | "1n_tx2")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*vpp_device*.template )
            TOPOLOGIES_TAGS="2_node_single_link_topo"
            ;;
        "2n_skx")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*2n_skx*.yaml )
            TOPOLOGIES_TAGS="2_node_*_link_topo"
            ;;
        "2n_zn2")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*2n_zn2*.yaml )
            TOPOLOGIES_TAGS="2_node_*_link_topo"
            ;;
        "3n_skx")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*3n_skx*.yaml )
            TOPOLOGIES_TAGS="3_node_*_link_topo"
            ;;
        "2n_clx")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*2n_clx*.yaml )
            TOPOLOGIES_TAGS="2_node_*_link_topo"
            ;;
        "2n_dnv")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*2n_dnv*.yaml )
            TOPOLOGIES_TAGS="2_node_single_link_topo"
            ;;
        "3n_dnv")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*3n_dnv*.yaml )
            TOPOLOGIES_TAGS="3_node_single_link_topo"
            ;;
        "3n_hsw")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*3n_hsw*.yaml )
            TOPOLOGIES_TAGS="3_node_single_link_topo"
            ;;
        "3n_tsh")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*3n_tsh*.yaml )
            TOPOLOGIES_TAGS="3_node_single_link_topo"
            ;;
        "2n_tx2")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*2n_tx2*.yaml )
            TOPOLOGIES_TAGS="2_node_single_link_topo"
            ;;
        *)
            # No falling back to 3n_hsw default, that should have been done
            # by the function which has set NODENESS and FLAVOR.
            die "Unknown specification: ${case_text}"
    esac

    if [[ -z "${TOPOLOGIES-}" ]]; then
        die "No applicable topology found!"
    fi
}


function select_vpp_device_tags () {

    # Variables read:
    # - TEST_CODE - String affecting test selection, usually jenkins job name.
    # - TEST_TAG_STRING - String selecting tags, from gerrit comment.
    #   Can be unset.
    # Variables set:
    # - TAGS - Array of processed tag boolean expressions.

    set -exuo pipefail

    case "${TEST_CODE}" in
        # Select specific device tests based on jenkins job type variable.
        * )
            if [[ -z "${TEST_TAG_STRING-}" ]]; then
                # If nothing is specified, we will run pre-selected tests by
                # following tags. Items of array will be concatenated by OR
                # in Robot Framework.
                test_tag_array=()
            else
                # If trigger contains tags, split them into array.
                test_tag_array=(${TEST_TAG_STRING//:/ })
            fi
            SELECTION_MODE="--include"
            ;;
    esac

    # Blacklisting certain tags per topology.
    #
    # Reasons for blacklisting:
    # - avf - AVF is not possible to run on enic driver of VirtualBox.
    # - vhost - VirtualBox does not support nesting virtualization on Intel CPU.
    case "${TEST_CODE}" in
        *"1n-vbox"*)
            test_tag_array+=("!avf")
            test_tag_array+=("!vhost")
            ;;
        *)
            ;;
    esac

    TAGS=()

    # We will prefix with devicetest to prevent running other tests
    # (e.g. Functional).
    prefix="devicetestAND"
    if [[ "${TEST_CODE}" == "vpp-"* ]]; then
        # Automatic prefixing for VPP jobs to limit testing.
        prefix="${prefix}"
    fi
    for tag in "${test_tag_array[@]}"; do
        if [[ ${tag} == "!"* ]]; then
            # Exclude tags are not prefixed.
            TAGS+=("${tag}")
        else
            TAGS+=("${prefix}${tag}")
        fi
    done
}

function untrap_and_unreserve_testbed () {

    # Use this as a trap function to ensure testbed does not remain reserved.
    # Perhaps call directly before script exit, to free testbed for other jobs.
    # This function is smart enough to avoid multiple unreservations (so safe).
    # Topo cleanup is executed (call it best practice), ignoring failures.
    #
    # Hardcoded values:
    # - default message to die with if testbed might remain reserved.
    # Arguments:
    # - ${1} - Message to die with if unreservation fails. Default hardcoded.
    # Variables read (by inner function):
    # - WORKING_TOPOLOGY - Path to topology yaml file of the reserved testbed.
    # - PYTHON_SCRIPTS_DIR - Path to directory holding Python scripts.
    # Variables written:
    # - WORKING_TOPOLOGY - Set to empty string on successful unreservation.
    # Trap unregistered:
    # - EXIT - Failure to untrap is reported, but ignored otherwise.
    # Functions called:
    # - die - Print to stderr and exit.
    # - ansible_playbook - Perform an action using ansible, see ansible.sh

    set -xo pipefail
    set +eu  # We do not want to exit early in a "teardown" function.
    trap - EXIT || echo "Trap deactivation failed, continuing anyway."
    wt="${WORKING_TOPOLOGY}"  # Just to avoid too long lines.
    if [[ -z "${wt-}" ]]; then
        set -eu
        warn "Testbed looks unreserved already. Trap removal failed before?"
    else
        ansible_playbook "cleanup" || true
        python3 "${PYTHON_SCRIPTS_DIR}/topo_reservation.py" -c -t "${wt}" || {
            die "${1:-FAILED TO UNRESERVE, FIX MANUALLY.}" 2
        }
        WORKING_TOPOLOGY=""
        set -eu
    fi
}


function warn () {

    # Print the message to standard error.
    #
    # Arguments:
    # - ${@} - The text of the message.

    set -exuo pipefail

    echo "$@" >&2
}
