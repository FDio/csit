#!/usr/bin/env bash

set -euo pipefail

function die () {
    # Print the message to standard error end exit with error code specified
    # by the second argument.
    #
    # Hardcoded values:
    # - The default error message.
    # Arguments:
    # - ${1} - The whole error message, be sure to quote. Optional
    # - ${2} - the code to exit with, default: 1.

    set +eu
    warn "${1:-Unspecified run-time error occurred!}"
    exit "${2:-1}"
}


function set_eligibility_off {
    # Set Nomad eligibility to ineligible for scheduling. Fail otherwise.

    set -euo pipefail

    node_id="$(nomad node status | grep $(hostname) | cut -d ' ' -f 1)" || die
    node_status="$(nomad node status | grep $(hostname))" || die

    if [[ "${node_status}" != *"ineligible"* ]]; then
        nomad node eligibility -disable "${node_id}" || die
        node_status="$(nomad node status | grep $(hostname))" || die
        if [[ "${node_status}" != *"ineligible"* ]]; then
            die "Set eligibility off failed!"
        fi
    fi
}


function set_eligibility_on {
    # Set Nomad eligibility to eligible for scheduling. Fail otherwise.

    set -euo pipefail

    node_id="$(nomad node status | grep $(hostname) | cut -d ' ' -f 1)" || die
    node_status="$(nomad node status | grep $(hostname))" || die

    if [[ "${node_status}" == *"ineligible"* ]]; then
        nomad node eligibility -enable "${node_id}" || die
        node_status="$(nomad node status | grep $(hostname))" || die
        if [[ "${node_status}" == *"ineligible"* ]]; then
            die "Set eligibility on failed!"
        fi
    fi
}


function restart_vfs_service {
    # Stop and start VF serice. This will reinitialize VFs and driver mappings.

    set -euo pipefail

    warn "Restarting VFs service (this may take few minutes)..."
    sudo service csit-initialize-vfs stop || die "Failed to stop VFs service!"
    sudo service csit-initialize-vfs start || die "Failed to start VFs service!"
}


function wait_for_pending_containers {
    # Wait in loop for defined amount of time for pending containers to
    # gracefully quit them. If parameter force is specified. Force kill them.

    # Arguments:
    # - ${@} - Script parameters.

    set -euo pipefail

    retries=60
    wait_time=60
    containers=(docker ps --quiet --filter name=csit*)

    for i in $(seq 1 ${retries}); do
        mapfile -t pending_containers < <( ${containers[@]} ) || die
        warn "Waiting for pending containers [${pending_containers[@]}] ..."
        if [ ${#pending_containers[@]} -eq 0 ]; then
            break
        fi
        sleep "${wait_time}" || die
    done
    if [ ${#pending_containers[@]} -ne 0 ]; then
        if [[ "${1-}" == "force" ]]; then
            warn "Force killing [${pending_containers[@]}] ..."
            docker rm --force ${pending_containers[@]} || die
        else
            die "Still few containers running!"
        fi
    fi
}


function warn () {
    # Print the message to standard error.
    #
    # Arguments:
    # - ${@} - The text of the message.

    echo "$@" >&2
}


set_eligibility_off || die
wait_for_pending_containers "${@}" || die
restart_vfs_service || die
set_eligibility_on || die
