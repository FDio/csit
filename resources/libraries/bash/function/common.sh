# Copyright (c) 2025 Cisco and/or its affiliates.
# Copyright (c) 2025 PANTHEON.tech and/or its affiliates.
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
        "1n_skx" | "1n_alt" | "1n_spr")
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

    parse_env_variables || die "Parse of environment variables failed!"

    # Replace all variables in template with those in environment.
    source <(echo 'cat <<EOF >topo.yml'; cat ${TOPOLOGIES[0]}; echo EOF;) || {
        die "Topology file create failed!"
    }

    WORKING_TOPOLOGY="${CSIT_DIR}/topologies/available/vpp_device.yaml"
    mv topo.yml "${WORKING_TOPOLOGY}" || {
        die "Topology move failed!"
    }
    cat ${WORKING_TOPOLOGY} | grep -v password || {
        die "Topology read failed!"
    }

    # Subfunctions to update data that may depend on topology reserved.
    set_environment_variables || die
    select_tags || die
    compose_robot_arguments || die

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

    ############################################################################
    # rm -rf "${env_dir}" || die "Failed to clean previous virtualenv."
    ############################################################################

    #pip3 install virtualenv==20.26.3 || {
    #    die "Virtualenv package install failed."
    #}
    virtualenv --no-download --python=$(which python3) "${env_dir}" || {
        die "Virtualenv creation for $(which python3) failed."
    }
    set +u
    source "${env_dir}/bin/activate" || die "Virtualenv activation failed."
    set -u
    pip3 install setuptools
    pip3 install -r "${req_path}" || {
        die "Requirements installation failed."
    }
    # Most CSIT Python scripts assume PYTHONPATH is set and exported.
    export PYTHONPATH="${CSIT_DIR}" || die "Export failed."
}


function archive_tests () {

    # Create .tar.gz of generated/tests for archiving.
    # To be run after generate_tests, kept separate to offer more flexibility.

    # Directory read:
    # - ${GENERATED_DIR}/tests - Tree of executed suites to archive.
    # File rewriten:
    # - ${ARCHIVE_DIR}/generated_tests.tar.gz - Archive of generated tests.

    set -exuo pipefail

    pushd "${ARCHIVE_DIR}" || die
    tar czf "generated_tests.tar.gz" "${GENERATED_DIR}/tests" || true
    popd || die
}


function check_download_dir () {

    # Fail if there are no files visible in ${DOWNLOAD_DIR}.
    #
    # Variables read:
    # - DOWNLOAD_DIR - Path to directory robot takes the build to test from.
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
    JOB_SPECS_DIR=$(readlink -e "${CSIT_DIR}/resources/job_specs") || {
        die "Readlink failed."
    }
    RESOURCES_DIR=$(readlink -e "${CSIT_DIR}/resources") || {
        die "Readlink failed."
    }
    TOOLS_DIR=$(readlink -e "${RESOURCES_DIR}/tools") || {
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


function compose_robot_arguments () {

    # This function is called by run_tests function.
    # The reason is that some jobs (bisect) perform reservation multiple times,
    # so WORKING_TOPOLOGY can be different each time.
    #
    # Variables read:
    # - WORKING_TOPOLOGY - Path to topology yaml file of the reserved testbed.
    # - DUT - CSIT test/ subdirectory, set while processing tags.
    # - TAGS - Array variable holding selected tag boolean expressions.
    # - TEST_CODE - The test selection string from environment or argument.
    # - SELECTION_MODE - Selection criteria [none, tags].
    # Variables set:
    # - ROBOT_ARGS - String holding part of all arguments for robot.
    # - EXPANDED_TAGS - Array of strings robot arguments compiled from tags.

    set -exuo pipefail

    # No explicit check needed with "set -u".
    ROBOT_ARGS=("--loglevel" "TRACE")
    ROBOT_ARGS+=("--variable" "TOPOLOGY_PATH:${WORKING_TOPOLOGY}")

    # TODO: The rest does not need to be recomputed on each reservation.
    #       Refactor TEST_CODE so this part can be called only once.
    case "${TEST_CODE}" in
        *"device"*)
            ROBOT_ARGS+=("--suite" "tests.${DUT}.device")
            ;;
        *"perf"* | *"bisect"*)
            ROBOT_ARGS+=("--suite" "tests.${DUT}.perf")
            ;;
        *)
            die "Unknown specification: ${TEST_CODE}"
    esac

    EXPANDED_TAGS=()
    for tag in "${TAGS[@]}"; do
        if [[ ${tag} == "!"* ]]; then
            EXPANDED_TAGS+=("--exclude" "${tag#$"!"}")
        else
            if [ -n "${SELECTION_MODE}" ]; then
                EXPANDED_TAGS+=("--include" "${tag}")
            fi
        fi
    done
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
        "1n_skx" | "1n_alt" | "1n_spr")
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


function die_on_robot_error () {

    # Source this fragment if you want to abort on any failed test case.
    #
    # Variables read:
    # - ROBOT_EXIT_STATUS - Set by a robot running fragment.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    if [[ "${ROBOT_EXIT_STATUS}" != "0" ]]; then
        die "Test failures are present!" "${ROBOT_EXIT_STATUS}"
    fi
}


function generate_tests () {

    # Populate ${GENERATED_DIR}/tests based on ${CSIT_DIR}/tests/.
    # Any previously existing content of ${GENERATED_DIR}/tests is wiped before.
    # The generation is done by executing any *.py executable
    # within any subdirectory after copying.

    # This is a separate function, because this code is called
    # both by autogen checker and entries calling run_robot.

    # Directories read:
    # - ${CSIT_DIR}/tests - Used as templates for the generated tests.
    # Directories replaced:
    # - ${GENERATED_DIR}/tests - Overwritten by the generated tests.

    set -exuo pipefail

    rm -rf "${GENERATED_DIR}/tests" || die
    pushd "${CSIT_DIR}/resources/libraries/python/suite_generator" || die

    # Works for periodical jobs (daily, weekly) only:
    suite_gen_params=("--job" "${TEST_CODE}")
    suite_gen_params+=("--gen-tests-dir" "${GENERATED_DIR}")
    # To make on-demand jobs working, add:
    # suite_gen_params+=("--test-type" "")
    # suite_gen_params+=("--test-set" "")
    ./suite_generator.py "${suite_gen_params[@]}" || die
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
    # - VPP_PLATFORM - VPP build optimisation string.

    set -exuo pipefail

    TEST_CODE="${1-}" || die "Reading optional argument failed, somehow."
    if [[ -z "${TEST_CODE}" ]]; then
        TEST_CODE="${JOB_NAME-}" || die "Reading job name failed, somehow."
    fi

    case "${TEST_CODE}" in
        *"1n-vbox")
            NODENESS="1n"
            FLAVOR="vbox"
            ;;
        *"1n-skx")
            NODENESS="1n"
            FLAVOR="skx"
            ;;
        *"1n-spr")
            NODENESS="1n"
            FLAVOR="spr"
            ;;
        *"1n-alt")
            NODENESS="1n"
            FLAVOR="alt"
            ;;
        *"1n-aws")
            NODENESS="1n"
            FLAVOR="aws"
            ;;
        *"2n-aws")
            NODENESS="2n"
            FLAVOR="aws"
            ;;
        *"3n-aws")
            NODENESS="3n"
            FLAVOR="aws"
            ;;
        *"2n-c7gn")
            NODENESS="2n"
            FLAVOR="c7gn"
            ;;
        *"3n-c7gn")
            NODENESS="3n"
            FLAVOR="c7gn"
            ;;
        *"1n-c6in")
            NODENESS="1n"
            FLAVOR="c6in"
            ;;
        *"2n-c6in")
            NODENESS="2n"
            FLAVOR="c6in"
            ;;
        *"3n-c6in")
            NODENESS="3n"
            FLAVOR="c6in"
            ;;
        *"2n-zn2")
            NODENESS="2n"
            FLAVOR="zn2"
            ;;
        *"2n-icx")
            NODENESS="2n"
            FLAVOR="icx"
            ;;
        *"2n-spr")
            NODENESS="2n"
            FLAVOR="spr"
            ;;
        *"3n-icx")
            NODENESS="3n"
            FLAVOR="icx"
            ;;
        *"3na-spr")
            NODENESS="3na"
            FLAVOR="spr"
            ;;
        *"3nb-spr")
            NODENESS="3nb"
            FLAVOR="spr"
            ;;
        *"3n-snr")
            NODENESS="3n"
            FLAVOR="snr"
            ;;
        *"3n-icxd")
            NODENESS="3n"
            FLAVOR="icxd"
            ;;
        *"3n-alt")
            NODENESS="3n"
            FLAVOR="alt"
            ;;
        *"2n-grc")
            NODENESS="2n"
            FLAVOR="grc"
            ;;
        *"2n-emr")
            NODENESS="2n"
            FLAVOR="emr"
            ;;
        *"3n-emr")
            NODENESS="3n"
            FLAVOR="emr"
            ;;
        *"3n-oct")
            NODENESS="3n"
            FLAVOR="oct"
            VPP_PLATFORM="octeon10"
            ;;
        *"-x-2n"*)
            TESTBED="${TEST_CODE#${TEST_CODE%2n*}}"
            NODENESS="${TESTBED%-${TEST_CODE#*-x-2n*-}}"
            FLAVOR="${TEST_CODE#*-x-2n*-}"
            ;;
        *"-x-3n"*)
            TESTBED="${TEST_CODE#${TEST_CODE%3n*}}"
            NODENESS="${TESTBED%-${TEST_CODE#*-x-3n*-}}"
            FLAVOR="${TEST_CODE#*-x-3n*-}"
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
    # - GIT_BISECT_FROM - If bisecttest, the commit hash to bisect from.
    #   Else not set.
    # Variables exported optionally:
    # - GRAPH_NODE_VARIANT - Node variant to test with, set if found in trigger.

    # TODO: ci-management scripts no longer need to perform this.

    set -exuo pipefail

    if [[ "${GERRIT_EVENT_TYPE-}" == "comment-added" ]]; then
        case "${TEST_CODE}" in
            # Order matters, bisect job contains "perf" in its name.
            *"bisect"*)
                trigger="bisecttest"
                ;;
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
            comment="${GERRIT_EVENT_COMMENT_TEXT}"
            comment=$(base64 --decode <<< "${comment}" || true)
            comment=$(fgrep "${trigger}" <<< "${comment}" || true)
            TEST_TAG_STRING=$("${cmd[@]}" <<< "${comment}" || true)
        fi
        if [[ "${trigger}" == "bisecttest" ]]; then
            # Intentionally without quotes, so spaces delimit elements.
            test_tag_array=(${TEST_TAG_STRING}) || die "How could this fail?"
            # First "argument" of bisecttest is a commit hash.
            GIT_BISECT_FROM="${test_tag_array[0]}" || {
                die "Bisect job requires commit hash."
            }
            # Update the tag string (tag expressions only, no commit hash).
            TEST_TAG_STRING="${test_tag_array[@]:1}" || {
                die "Bisect job needs a single test, no default."
            }
        fi
        if [[ -n "${TEST_TAG_STRING-}" ]]; then
            test_tag_array=(${TEST_TAG_STRING})
            if [[ "${test_tag_array[0]}" == "icl" ]]; then
                export GRAPH_NODE_VARIANT="icl"
                TEST_TAG_STRING="${test_tag_array[@]:1}" || true
            elif [[ "${test_tag_array[0]}" == "skx" ]]; then
                export GRAPH_NODE_VARIANT="skx"
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


function prepare_topology () {

    # Prepare virtual testbed topology if needed based on flavor.

    # Variables read:
    # - TEST_CODE - String affecting test selection, usually jenkins job name.
    # - NODENESS - Node multiplicity of testbed, either "2n" or "3n".
    # - FLAVOR - Node flavor string, e.g. "clx" or "skx".
    # Variables set:
    # - TERRAFORM_MODULE_DIR - Terraform module directory.
    # Functions called:
    # - die - Print to stderr and exit.
    # - terraform_init - Terraform init topology.
    # - terraform_apply - Terraform apply topology.

    set -exuo pipefail

    case_text="${NODENESS}_${FLAVOR}"
    case "${case_text}" in
        "1n_aws" | "2n_aws" | "3n_aws")
            export TF_VAR_testbed_name="${TEST_CODE}"
            TERRAFORM_MODULE_DIR="terraform-aws-${NODENESS}-${FLAVOR}-c5n"
            terraform_init || die "Failed to call terraform init."
            trap "terraform_destroy" ERR EXIT || {
                die "Trap attempt failed, please cleanup manually. Aborting!"
            }
            terraform_apply || die "Failed to call terraform apply."
            ;;
        "2n_c7gn" | "3n_c7gn")
            export TF_VAR_testbed_name="${TEST_CODE}"
            TERRAFORM_MODULE_DIR="terraform-aws-${NODENESS}-c7gn"
            terraform_init || die "Failed to call terraform init."
            trap "terraform_destroy" ERR EXIT || {
                die "Trap attempt failed, please cleanup manually. Aborting!"
            }
            terraform_apply || die "Failed to call terraform apply."
            ;;
        "1n_c6in" | "2n_c6in" | "3n_c6in")
            export TF_VAR_testbed_name="${TEST_CODE}"
            TERRAFORM_MODULE_DIR="terraform-aws-${NODENESS}-c6in"
            terraform_init || die "Failed to call terraform init."
            trap "terraform_destroy" ERR EXIT || {
                die "Trap attempt failed, please cleanup manually. Aborting!"
            }
            terraform_apply || die "Failed to call terraform apply."
            ;;
    esac
}


function reserve_and_cleanup_testbed () {

    # Reserve physical testbed, perform cleanup, register trap to unreserve.
    # When cleanup fails, remove from topologies and keep retrying
    # until all topologies are removed.
    #
    # Multiple other functions are called from here,
    # as they set variables that depend on reserved topology data.
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
                # Cleanup + calibration checks
                set +e
                ansible_playbook "cleanup,calibration"
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

    # Subfunctions to update data that may depend on topology reserved.
    set_environment_variables || die
    select_tags || die
    compose_robot_arguments || die
}


function run_robot () {

    # Run robot with options based on input variables.
    #
    # Testbed has to be reserved already,
    # as some data may have changed between reservations,
    # for example excluded NICs.
    #
    # Variables read:
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # - ARCHIVE_DIR - Path to store robot result files in.
    # - ROBOT_ARGS, EXPANDED_TAGS - See compose_robot_arguments.sh
    # - GENERATED_DIR - Tests are assumed to be generated under there.
    # - WORKING_TOPOLOGY - Path to topology yaml file of the reserved testbed.
    # - DUT - CSIT test/ subdirectory, set while processing tags.
    # - TAGS - Array variable holding selected tag boolean expressions.
    # - TEST_CODE - The test selection string from environment or argument.
    # Variables set:
    # - ROBOT_ARGS - String holding part of all arguments for robot.
    # - EXPANDED_TAGS - Array of string robot arguments compiled from tags.
    # - ROBOT_EXIT_STATUS - Exit status of most recent robot invocation.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    # Run ALL generated test suites:
    all_options=("--outputdir" "${ARCHIVE_DIR}" "${ROBOT_ARGS[@]}")
    # Run only tests defined by tag(s) out of generated tests:
    all_options+=("${EXPANDED_TAGS[@]}")

    pushd "${CSIT_DIR}" || die "Change directory operation failed."
    set +e
    robot "${all_options[@]}" "${GENERATED_DIR}/tests/"
    ROBOT_EXIT_STATUS="$?"
    set -e

    popd || die "Change directory operation failed."
}


function select_arch_os () {

    # Set variables affected by local CPU architecture and operating system.
    #
    # Variables set:
    # - IMAGE_VER_FILE - Name of file in CSIT dir containing the image name.
    # - VPP_COMMIT_FILE - Name of file in CSIT dir containing vpp commit
    #   version.
    # - VPP_VER_FILE - Name of file in CSIT dir containing vpp stable version.
    # - PKG_SUFFIX - Suffix of OS package file name, "rpm" or "deb."

    set -exuo pipefail

    source /etc/os-release || die "Get OS release failed."

    case "${ID}" in
        "ubuntu"*)
            case "${VERSION}" in
                *"LTS (Jammy Jellyfish)"*)
                    IMAGE_VER_FILE="VPP_DEVICE_IMAGE_UBUNTU_JAMMY"
                    VPP_COMMIT_FILE="VPP_STABLE_COMMIT"
                    VPP_VER_FILE="VPP_STABLE_VER_UBUNTU_JAMMY"
                    PKG_SUFFIX="deb"
                    ;;
                *"LTS (Noble Numbat)"*)
                    IMAGE_VER_FILE="VPP_DEVICE_IMAGE_UBUNTU_NOBLE"
                    VPP_COMMIT_FILE="VPP_STABLE_COMMIT"
                    VPP_VER_FILE="VPP_STABLE_VER_UBUNTU_NOBLE"
                    PKG_SUFFIX="deb"
                    ;;
                *)
                    die "Unsupported Ubuntu version!"
                    ;;
            esac
            ;;
        *)
            die "Unsupported distro or OS!"
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

    # Only to be called from the reservation function,
    # as resulting tags may change based on topology data.
    #
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
    # - SELECTION_MODE - Selection criteria [tags, undefined].

    set -exuo pipefail

    case "${TEST_CODE}" in
        # Select specific performance tests based on jenkins job type variable.
        *"device"* )
            ;;
        *"hoststack-daily"* )
            ;;
        *"ndrpdr-weekly"* )
            ;;
        *"mrr-daily"* )
            ;;
        *"mrr-weekly"* )
            ;;
        *"soak-weekly"* )
            ;;
        *"report-iterative"* )
            test_sets=(${TEST_TAG_STRING//:/ })
            ;;
        *"report-coverage"* )
            test_sets=(${TEST_TAG_STRING//:/ })
            ;;
        * )
            if [[ -z "${TEST_TAG_STRING-}" ]]; then
                # If nothing is specified, we will run pre-selected tests by
                # following tags.
                test_tag_array=("mrrAND1cAND64bANDethip4-ip4base")
            else
                # If trigger contains tags, split them into array.
                test_tag_array=(${TEST_TAG_STRING//:/ })
            fi
            SELECTION_MODE="tags"
            ;;
    esac

    TAGS=()
    prefix=""
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
    # - FLAVOR - Node flavor string, e.g. "clx" or "skx".
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # - TOPOLOGIES_DIR - Path to existing directory with available topologies.
    # Variables set:
    # - TOPOLOGIES - Array of paths to suitable topology yaml files.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    case "${TEST_CODE}" in
        *"1n-aws")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*1n-aws*.yaml )
            ;;
        *"1n-c6in")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*1n-c6in*.yaml )
            ;;
        *"1n-alt" | *"1n-spr")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*vpp_device*.template )
            ;;
        *"1n-vbox")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*vpp_device*.template )
            ;;
        *"2n-aws")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*2n-aws*.yaml )
            ;;
        *"2n-c7gn")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*2n-c7gn*.yaml )
            ;;
        *"2n-c6in")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*2n-c6in*.yaml )
            ;;
        *"2n-icx")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*2n_icx_*.yaml )
            ;;
        *"2n-spr")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*2n_spr_*.yaml )
            ;;
        *"2n-zn2")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*2n_zn2_*.yaml )
            ;;
        *"3n-alt")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*3n_alt_*.yaml )
            ;;
        *"2n-grc")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*2n_grc_*.yaml )
            ;;
        *"2n-emr")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*2n_emr_*.yaml )
            ;;
        *"3n-emr")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*3n_emr_*.yaml )
            ;;
        *"3n-oct")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*3n_oct_*.yaml )
            ;;
        *"3n-aws")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*3n-aws*.yaml )
            ;;
        *"3n-c7gn")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*3n-c7gn*.yaml )
            ;;
        *"3n-c6in")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*3n-c6in*.yaml )
            ;;
        *"3n-icx")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*3n_icx_*.yaml )
            ;;
        *"3n-icxd")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*3n_icxd_*.yaml )
            ;;
        *"3n-snr")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*3n_snr_*.yaml )
            ;;
        *"3na-spr")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*3na_spr_*.yaml )
            ;;
        *"3nb-spr")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*3nb_spr_*.yaml )
            ;;
        *"-x-2n"*)
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*_x_"${NODENESS}_${FLAVOR}"*.yaml )
            ;;
        *"-x-3n"*)
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*_x_"${NODENESS}_${FLAVOR}"*.yaml )
            ;;
        *)
            # No falling back to default, that should have been done
            # by the function which has set NODENESS and FLAVOR.
            die "Unknown specification: ${case_text}"
    esac

    if [[ -z "${TOPOLOGIES-}" ]]; then
        die "No applicable topology found!"
    fi
}


function set_environment_variables () {

    # Depending on testbed topology, overwrite defaults set in the
    # resources/libraries/python/Constants.py file
    #
    # Only to be called from the reservation function,
    # as resulting values may change based on topology data.
    #
    # Variables read:
    # - TEST_CODE - String affecting test selection, usually jenkins job name.
    # Variables set:
    # See specific cases

    set -exuo pipefail

    case "${TEST_CODE}" in
        *"1n-aws" | *"2n-aws" | *"3n-aws")
            export TREX_RX_DESCRIPTORS_COUNT=1024
            export TREX_EXTRA_CMDLINE="--mbuf-factor 19"
            export TREX_CORE_COUNT=6
            # Settings to prevent duration stretching.
            export PERF_TRIAL_STL_DELAY=0.1
            ;;
        *"2n-c7gn" | *"3n-c7gn")
            export TREX_RX_DESCRIPTORS_COUNT=1024
            export TREX_EXTRA_CMDLINE="--mbuf-factor 19"
            export TREX_CORE_COUNT=6
            # Settings to prevent duration stretching.
            export PERF_TRIAL_STL_DELAY=0.1
            ;;
        *"1n-c6in" | *"2n-c6in" | *"3n-c6in")
            export TREX_RX_DESCRIPTORS_COUNT=1024
            export TREX_EXTRA_CMDLINE="--mbuf-factor 19"
            export TREX_CORE_COUNT=6
            # Settings to prevent duration stretching.
            export PERF_TRIAL_STL_DELAY=0.1
            ;;
        *"2n-zn2")
            # Maciek's workaround for Zen2 with lower amount of cores.
            export TREX_CORE_COUNT=14
            ;;
        *"-x-2n"* | *"-x-3n"* )
            export TREX_CORE_COUNT=14
            export TREX_PORT_MTU=9000
            # Be gentle on infra.
            export INFRA_WARMUP_DURATION=5
            export INFRA_WARMUP_RATE=253
            # Settings to prevent duration stretching.
            export PERF_TRIAL_STL_DELAY=0.12
            ;;
    esac
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
    # Variables set:
    # - TERRAFORM_MODULE_DIR - Terraform module directory.
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
        case "${TEST_CODE}" in
            *"1n-aws" | *"2n-aws" | *"3n-aws")
                TERRAFORM_MODULE_DIR="terraform-aws-${NODENESS}-${FLAVOR}-c5n"
                terraform_destroy || die "Failed to call terraform destroy."
                ;;
            *"2n-c7gn" | *"3n-c7gn")
                TERRAFORM_MODULE_DIR="terraform-aws-${NODENESS}-${FLAVOR}"
                terraform_destroy || die "Failed to call terraform destroy."
                ;;
            *"1n-c6in" | *"2n-c6in" | *"3n-c6in")
                TERRAFORM_MODULE_DIR="terraform-aws-${NODENESS}-${FLAVOR}"
                terraform_destroy || die "Failed to call terraform destroy."
                ;;
            *)
                ;;
        esac
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
