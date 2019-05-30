# Copyright (c) 2019 Cisco and/or its affiliates.
# Copyright (c) 2019 PANTHEON.tech and/or its affiliates.
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
    set -exuo pipefail

    # Create virtual vpp-device topology. Output of the function is topology
    # file describing created environment saved to a file.
    #
    # Variables read:
    # - BASH_FUNCTION_DIR - Path to existing directory this file is located in.
    # - TOPOLOGIES - Available topologies.
    # - NODENESS - Node multiplicity of desired testbed.
    # - FLAVOR - Node flavor string, usually describing the processor.
    # Variables set:
    # - WORKING_TOPOLOGY - Path to topology file.

    source "${BASH_FUNCTION_DIR}/device.sh" || {
        die "Source failed!"
    }

    device_image="$(< ${CSIT_DIR}/VPP_DEVICE_IMAGE)"
    case_text="${NODENESS}_${FLAVOR}"
    case "${case_text}" in
        "1n_skx")
            # We execute reservation over csit-shim-dcr (ssh) which runs sourced
            # script's functions. Env variables are read from ssh output
            # back to localhost for further processing.
            hostname=$(grep search /etc/resolv.conf | cut -d' ' -f3)
            ssh="ssh root@${hostname} -p 6022"
            run="activate_wrapper ${NODENESS} ${FLAVOR} ${device_image}"
            # backtics to avoid https://midnight-commander.org/ticket/2142
            env_vars=`${ssh} "$(declare -f); ${run}"` || {
                die "Topology reservation via shim-dcr failed!"
            }
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

    set -exuo pipefail

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

    # TODO: Do we want the callers to be able to set the env dir name?
    # TODO: + In that case, do we want to support env switching?
    # TODO:   + In that case we want to make env_dir global.
    # TODO: Do we want the callers to override PYTHONPATH loaction?

    root_path="${1-$CSIT_DIR}"
    env_dir="${root_path}/env"
    req_path=${2-$CSIT_DIR/requirements.txt}
    rm -rf "${env_dir}" || die "Failed to clean previous virtualenv."
    pip install --upgrade virtualenv || {
        die "Virtualenv package install failed."
    }
    virtualenv "${env_dir}" || {
        die "Virtualenv creation failed."
    }
    set +u
    source "${env_dir}/bin/activate" || die "Virtualenv activation failed."
    set -u
    pip install --upgrade -r "${req_path}" || {
        die "Requirements installation failed."
    }
    # Most CSIT Python scripts assume PYTHONPATH is set and exported.
    export PYTHONPATH="${CSIT_DIR}" || die "Export failed."
}


function archive_tests () {

    set -exuo pipefail

    # Create .tar.xz of generated/tests for archiving.
    # To be run after generate_tests, kept separate to offer more flexibility.

    # Directory read:
    # - ${GENERATED_DIR}/tests - Tree of executed suites to archive.
    # File rewriten:
    # - ${ARCHIVE_DIR}/tests.tar.xz - Archive of generated tests.

    tar c "${GENERATED_DIR}/tests" | xz -9e > "${ARCHIVE_DIR}/tests.tar.xz" || {
        die "Error creating archive of generated tests."
    }
}


function check_download_dir () {

    set -exuo pipefail

    # Fail if there are no files visible in ${DOWNLOAD_DIR}.
    # TODO: Do we need this as a function, if it is (almost) a one-liner?
    #
    # Variables read:
    # - DOWNLOAD_DIR - Path to directory pybot takes the build to test from.
    # Directories read:
    # - ${DOWNLOAD_DIR} - Has to be non-empty to proceed.
    # Functions called:
    # - die - Print to stderr and exit.

    if [[ ! "$(ls -A "${DOWNLOAD_DIR}")" ]]; then
        die "No artifacts downloaded!"
    fi
}


function cleanup_topo () {

    set -exuo pipefail

    # Variables read:
    # - WORKING_TOPOLOGY - Path to topology yaml file of the reserved testbed.
    # - PYTHON_SCRIPTS_DIR - Path to directory holding the reservation script.

    python "${PYTHON_SCRIPTS_DIR}/topo_cleanup.py" -t "${WORKING_TOPOLOGY}"
    # Not using "|| die" as some callers might want to ignore errors,
    # e.g. in teardowns, such as unreserve.
}


function common_dirs () {

    set -exuo pipefail

    # Set global variables, create some directories (without touching content).

    # Variables set:
    # - BASH_FUNCTION_DIR - Path to existing directory this file is located in.
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # - TOPOLOGIES_DIR - Path to existing directory with available tpologies.
    # - RESOURCES_DIR - Path to existing CSIT subdirectory "resources".
    # - TOOLS_DIR - Path to existing resources subdirectory "tools".
    # - PYTHON_SCRIPTS_DIR - Path to existing tools subdirectory "scripts".
    # - ARCHIVE_DIR - Path to created CSIT subdirectory "archive".
    # - DOWNLOAD_DIR - Path to created CSIT subdirectory "download_dir".
    # - GENERATED_DIR - Path to created CSIT subdirectory "generated".
    # Directories created if not present:
    # ARCHIVE_DIR, DOWNLOAD_DIR, GENERATED_DIR.
    # Functions called:
    # - die - Print to stderr and exit.

    BASH_FUNCTION_DIR="$(dirname "$(readlink -e "${BASH_SOURCE[0]}")")" || {
        die "Some error during localizing this source directory."
    }
    # Current working directory could be in a different repo, e.g. VPP.
    pushd "${BASH_FUNCTION_DIR}" || die "Pushd failed"
    CSIT_DIR="$(readlink -e "$(git rev-parse --show-toplevel)")" || {
        die "Readlink or git rev-parse failed."
    }
    popd || die "Popd failed."
    TOPOLOGIES_DIR="$(readlink -e "${CSIT_DIR}/topologies/available")" || {
        die "Readlink failed."
    }
    RESOURCES_DIR="$(readlink -e "${CSIT_DIR}/resources")" || {
        die "Readlink failed."
    }
    TOOLS_DIR="$(readlink -e "${RESOURCES_DIR}/tools")" || {
        die "Readlink failed."
    }
    PYTHON_SCRIPTS_DIR="$(readlink -e "${TOOLS_DIR}/scripts")" || {
        die "Readlink failed."
    }

    ARCHIVE_DIR="$(readlink -f "${CSIT_DIR}/archive")" || {
        die "Readlink failed."
    }
    mkdir -p "${ARCHIVE_DIR}" || die "Mkdir failed."
    DOWNLOAD_DIR="$(readlink -f "${CSIT_DIR}/download_dir")" || {
        die "Readlink failed."
    }
    mkdir -p "${DOWNLOAD_DIR}" || die "Mkdir failed."
    GENERATED_DIR="$(readlink -f "${CSIT_DIR}/generated")" || {
        die "Readlink failed."
    }
    mkdir -p "${GENERATED_DIR}" || die "Mkdir failed."
}


function compose_pybot_arguments () {

    set -exuo pipefail

    # Variables read:
    # - WORKING_TOPOLOGY - Path to topology yaml file of the reserved testbed.
    # - DUT - CSIT test/ subdirectory, set while processing tags.
    # - TAGS - Array variable holding selected tag boolean expressions.
    # - TOPOLOGIES_TAGS - Tag boolean expression filtering tests for topology.
    # - TEST_CODE - The test selection string from environment or argument.
    # Variables set:
    # - PYBOT_ARGS - String holding part of all arguments for pybot.
    # - EXPANDED_TAGS - Array of strings pybot arguments compiled from tags.

    # No explicit check needed with "set -u".
    PYBOT_ARGS=("--loglevel" "TRACE")
    PYBOT_ARGS+=("--variable" "TOPOLOGY_PATH:${WORKING_TOPOLOGY}")

    case "${TEST_CODE}" in
        *"device"*)
            PYBOT_ARGS+=("--suite" "tests.${DUT}.device")
            ;;
        *"func"*)
            PYBOT_ARGS+=("--suite" "tests.${DUT}.func")
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
            EXPANDED_TAGS+=("--include" "${TOPOLOGIES_TAGS}AND${tag}")
        fi
    done
}


function copy_archives () {

    set -exuo pipefail

    # Variables read:
    # - WORKSPACE - Jenkins workspace, copy only if the value is not empty.
    #   Can be unset, then it speeds up manual testing.
    # - ARCHIVE_DIR - Path to directory with content to be copied.
    # Directories updated:
    # - ${WORKSPACE}/archives/ - Created if does not exist.
    #   Content of ${ARCHIVE_DIR}/ is copied here.
    # Functions called:
    # - die - Print to stderr and exit.

    # We will create additional archive if workspace variable is set.
    # This way if script is running in jenkins all will be
    # automatically archived to logs.fd.io.
    if [[ -n "${WORKSPACE-}" ]]; then
        mkdir -p "${WORKSPACE}/archives/" || die "Archives dir create failed."
        cp -rf "${ARCHIVE_DIR}"/* "${WORKSPACE}/archives" || die "Copy failed."
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
        "1n_skx")
            hostname=$(grep search /etc/resolv.conf | cut -d' ' -f3)
            ssh="ssh root@${hostname} -p 6022"
            env_vars="$(env | grep CSIT_ | tr '\n' ' ' )"
            ${ssh} "$(declare -f); deactivate_wrapper ${env_vars}" || {
                die "Topology cleanup via shim-dcr failed!"
            }
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

    set -exuo pipefail

    # Source this fragment if you want to abort on any failed test case.
    #
    # Variables read:
    # - PYBOT_EXIT_STATUS - Set by a pybot running fragment.
    # Functions called:
    # - die - Print to stderr and exit.

    if [[ "${PYBOT_EXIT_STATUS}" != "0" ]]; then
        die "Test failures are present!" "${PYBOT_EXIT_STATUS}"
    fi
}


function generate_tests () {

    set -exuo pipefail

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

    rm -rf "${GENERATED_DIR}/tests"
    cp -r "${CSIT_DIR}/tests" "${GENERATED_DIR}/tests"
    cmd_line=("find" "${GENERATED_DIR}/tests" "-type" "f")
    cmd_line+=("-executable" "-name" "*.py")
    file_list=$("${cmd_line[@]}") || die

    for gen in ${file_list}; do
        directory="$(dirname "${gen}")" || die
        filename="$(basename "${gen}")" || die
        pushd "${directory}" || die
        ./"${filename}" || die
        popd || die
    done
}


function get_test_code () {

    set -exuo pipefail

    # Arguments:
    # - ${1} - Optional, argument of entry script (or empty as unset).
    #   Test code value to override job name from environment.
    # Variables read:
    # - JOB_NAME - String affecting test selection, default if not argument.
    # Variables set:
    # - TEST_CODE - The test selection string from environment or argument.
    # - NODENESS - Node multiplicity of desired testbed.
    # - FLAVOR - Node flavor string, usually describing the processor.

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
        *"2n-skx"*)
            NODENESS="2n"
            FLAVOR="skx"
            ;;
        *"3n-skx"*)
            NODENESS="3n"
            FLAVOR="skx"
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

    set -exuo pipefail

    # Variables read:
    # - GERRIT_EVENT_TYPE - Event type set by gerrit, can be unset.
    # - GERRIT_EVENT_COMMENT_TEXT - Comment text, read for "comment-added" type.
    # - TEST_CODE - The test selection string from environment or argument.
    # Variables set:
    # - TEST_TAG_STRING - The string following "perftest" in gerrit comment,
    #   or empty.

    # TODO: ci-management scripts no longer need to perform this.

    trigger=""
    if [[ "${GERRIT_EVENT_TYPE-}" == "comment-added" ]]; then
        case "${TEST_CODE}" in
            *"device"*)
                # On parsing error, ${trigger} stays empty.
                trigger="$(echo "${GERRIT_EVENT_COMMENT_TEXT}" \
                    | grep -oE '(devicetest$|devicetest[[:space:]].+$)')" \
                    || true
                # Set test tags as string.
                TEST_TAG_STRING="${trigger#$"devicetest"}"
                ;;
            *"perf"*)
                # On parsing error, ${trigger} stays empty.
                comment="${GERRIT_EVENT_COMMENT_TEXT}"
                # As "perftest" can be followed by something, we substitute it.
                comment="${comment/perftest-2n/perftest}"
                comment="${comment/perftest-3n/perftest}"
                comment="${comment/perftest-hsw/perftest}"
                comment="${comment/perftest-skx/perftest}"
                comment="${comment/perftest-tsh/perftest}"
                tag_string="$(echo "${comment}" \
                    | grep -oE '(perftest$|perftest[[:space:]].+$)' || true)"
                # Set test tags as string.
                TEST_TAG_STRING="${tag_string#$"perftest"}"
                ;;
            *)
                die "Unknown specification: ${TEST_CODE}"
        esac
    fi
}


function reserve_testbed () {

    set -exuo pipefail

    # Reserve physical testbed, perform cleanup, register trap to unreserve.
    #
    # Variables read:
    # - TOPOLOGIES - Array of paths to topology yaml to attempt reservation on.
    # - PYTHON_SCRIPTS_DIR - Path to directory holding the reservation script.
    # Variables set:
    # - WORKING_TOPOLOGY - Path to topology yaml file of the reserved testbed.
    # Functions called:
    # - die - Print to stderr and exit.
    # Traps registered:
    # - EXIT - Calls cancel_all for ${WORKING_TOPOLOGY}.

    while true; do
        for topo in "${TOPOLOGIES[@]}"; do
            set +e
            python "${PYTHON_SCRIPTS_DIR}/topo_reservation.py" -t "${topo}"
            result="$?"
            set -e
            if [[ "${result}" == "0" ]]; then
                WORKING_TOPOLOGY="${topo}"
                echo "Reserved: ${WORKING_TOPOLOGY}"
                trap "untrap_and_unreserve_testbed" EXIT || {
                    message="TRAP ATTEMPT AND UNRESERVE FAILED, FIX MANUALLY."
                    untrap_and_unreserve_testbed "${message}" || {
                        die "Teardown should have died, not failed."
                    }
                    die "Trap attempt failed, unreserve succeeded. Aborting."
                }
                cleanup_topo || {
                    die "Testbed cleanup failed."
                }
                break
            fi
        done

        if [[ -n "${WORKING_TOPOLOGY-}" ]]; then
            # Exit the infinite while loop if we made a reservation.
            break
        fi

        # Wait ~3minutes before next try.
        sleep_time="$[ ( $RANDOM % 20 ) + 180 ]s" || {
            die "Sleep time calculation failed."
        }
        echo "Sleeping ${sleep_time}"
        sleep "${sleep_time}" || die "Sleep failed."
    done
}


function run_pybot () {

    set -exuo pipefail

    # Variables read:
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # - ARCHIVE_DIR - Path to store robot result files in.
    # - PYBOT_ARGS, EXPANDED_TAGS - See compose_pybot_arguments.sh
    # - GENERATED_DIR - Tests are assumed to be generated under there.
    # Variables set:
    # - PYBOT_EXIT_STATUS - Exit status of most recent pybot invocation.
    # Functions called:
    # - die - Print to stderr and exit.

    all_options=("--outputdir" "${ARCHIVE_DIR}" "${PYBOT_ARGS[@]}")
    all_options+=("${EXPANDED_TAGS[@]}")

    pushd "${CSIT_DIR}" || die "Change directory operation failed."
    set +e
    # TODO: Make robot tests not require "$(pwd)" == "${CSIT_DIR}".
    pybot "${all_options[@]}" "${GENERATED_DIR}/tests/"
    PYBOT_EXIT_STATUS="$?"
    set -e

    # Generate INFO level output_info.xml for post-processing.
    all_options=("--loglevel" "INFO")
    all_options+=("--log" "none")
    all_options+=("--report" "none")
    all_options+=("--output" "${ARCHIVE_DIR}/output_info.xml")
    all_options+=("${ARCHIVE_DIR}/output.xml")
    rebot "${all_options[@]}"
    popd || die "Change directory operation failed."
}


function select_tags () {

    set -exuo pipefail

    # Variables read:
    # - WORKING_TOPOLOGY - Path to topology yaml file of the reserved testbed.
    # - TEST_CODE - String affecting test selection, usually jenkins job name.
    # - TEST_TAG_STRING - String selecting tags, from gerrit comment.
    #   Can be unset.
    # - TOPOLOGIES_DIR - Path to existing directory with available tpologies.
    # Variables set:
    # - TAGS - Array of processed tag boolean expressions.

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
    exclude_nics=($(comm -13 <(echo "${reserved}") <(echo "${available}")))

    # Select default NIC
    case "${TEST_CODE}" in
        *"3n-tsh"*)
            DEFAULT_NIC='nic_intel-x520-da2'
            ;;
        *)
            DEFAULT_NIC='nic_intel-x710'
            ;;
    esac

    case "${TEST_CODE}" in
        # Select specific performance tests based on jenkins job type variable.
        *"ndrpdr-weekly"* )
            readarray -t test_tag_array < "${BASH_FUNCTION_DIR}/mlr-weekly.txt"
            ;;
        *"mrr-daily"* )
            readarray -t test_tag_array < "${BASH_FUNCTION_DIR}/mrr-daily.txt"
            ;;
        *"mrr-weekly"* )
            readarray -t test_tag_array < "${BASH_FUNCTION_DIR}/mrr-weekly.txt"
            ;;
        * )
            if [[ -z "${TEST_TAG_STRING-}" ]]; then
                # If nothing is specified, we will run pre-selected tests by
                # following tags.
                test_tag_array=("mrrAND${DEFAULT_NIC}AND1cAND64bANDip4base"
                                "mrrAND${DEFAULT_NIC}AND1cAND78bANDip6base"
                                "mrrAND${DEFAULT_NIC}AND1cAND64bANDl2bdbase"
                                "mrrAND${DEFAULT_NIC}AND1cAND64bANDl2xcbase"
                                "!dot1q" "!drv_avf")
            else
                # If trigger contains tags, split them into array.
                test_tag_array=(${TEST_TAG_STRING//:/ })
            fi
            ;;
    esac

    # Blacklisting certain tags per topology.
    case "${TEST_CODE}" in
        *"3n-hsw"*)
            test_tag_array+=("!drv_avf")
            test_tag_array+=("!ipsechwNOTnic_intel-xl710")
            ;;
        *"2n-skx"*)
            test_tag_array+=("!ipsechw")
            ;;
        *"3n-skx"*)
            test_tag_array+=("!ipsechw")
            # Not enough nic_intel-xxv710 to support double link tests.
            test_tag_array+=("!3_node_double_link_topoANDnic_intel-xxv710")
            ;;
        *"3n-tsh"*)
            test_tag_array+=("!ipsechw")
            test_tag_array+=("!memif")
            test_tag_array+=("!srv6_proxy")
            test_tag_array+=("!vhost")
            test_tag_array+=("!vts")
            ;;
        *)
            # Default to 3n-hsw due to compatibility.
            test_tag_array+=("!drv_avf")
            ;;
    esac

    # We will add excluded NICs.
    test_tag_array+=("${exclude_nics[@]/#/!NIC_}")

    TAGS=()

    # We will prefix with perftest to prevent running other tests
    # (e.g. Functional).
    prefix="perftestAND"
    if [[ "${TEST_CODE}" == "vpp-"* ]]; then
        # Automatic prefixing for VPP jobs to limit the NIC used and
        # traffic evaluation to MRR.
        if [[ "${TEST_TAG_STRING-}" == *"nic_"* ]]; then
            prefix="${prefix}mrrAND"
        else
            prefix="${prefix}mrrAND${DEFAULT_NIC}AND"
        fi
    fi
    for tag in "${test_tag_array[@]}"; do
        if [[ "${tag}" == "!"* ]]; then
            # Exclude tags are not prefixed.
            TAGS+=("${tag}")
        elif [[ "${tag}" != "" && "${tag}" != "#"* ]]; then
            # Empty and comment lines are skipped.
            # Other lines are normal tags, they are to be prefixed.
            TAGS+=("${prefix}${tag}")
        fi
    done
}


function select_vpp_device_tags () {

    set -exuo pipefail

    # Variables read:
    # - TEST_CODE - String affecting test selection, usually jenkins job name.
    # - TEST_TAG_STRING - String selecting tags, from gerrit comment.
    #   Can be unset.
    # Variables set:
    # - TAGS - Array of processed tag boolean expressions.

    case "${TEST_CODE}" in
        # Select specific performance tests based on jenkins job type variable.
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
            ;;
    esac

    TAGS=()

    # We will prefix with perftest to prevent running other tests
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


function select_topology () {

    set -exuo pipefail

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

    case_text="${NODENESS}_${FLAVOR}"
    case "${case_text}" in
        "1n_vbox")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*vpp_device*.template )
            TOPOLOGIES_TAGS="2_node_single_link_topo"
            ;;
        "1n_skx")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*vpp_device*.template )
            TOPOLOGIES_TAGS="2_node_single_link_topo"
            ;;
        "2n_skx")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*2n_skx*.yaml )
            TOPOLOGIES_TAGS="2_node_*_link_topo"
            ;;
        "3n_skx")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*3n_skx*.yaml )
            TOPOLOGIES_TAGS="3_node_*_link_topo"
            ;;
        "3n_hsw")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*3n_hsw*.yaml )
            TOPOLOGIES_TAGS="3_node_single_link_topo"
            ;;
        "3n_tsh")
            TOPOLOGIES=( "${TOPOLOGIES_DIR}"/*3n_tsh*.yaml )
            TOPOLOGIES_TAGS="3_node_*_link_topo"
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

    set -xo pipefail
    set +eu  # We do not want to exit early in a "teardown" function.
    trap - EXIT || echo "Trap deactivation failed, continuing anyway."
    wt="${WORKING_TOPOLOGY}"  # Just to avoid too long lines.
    if [[ -z "${wt-}" ]]; then
        set -eu
        warn "Testbed looks unreserved already. Trap removal failed before?"
    else
        cleanup_topo || true
        python "${PYTHON_SCRIPTS_DIR}/topo_reservation.py" -c -t "${wt}" || {
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

    echo "$@" >&2
}
