#!/usr/bin/env bash

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

# CSIT SRIOV VF initialization and isolation.

set -euo pipefail

case "${1:-start}" in
    "start" )
        # Run TG
        for cnt in $(seq 1 ${2:-1}); do
            docker network create --driver bridge csit-nw-tg${cnt} || true
            # If the IMAGE is not already loaded then docker run will pull the
            # IMAGE, and all image dependencies, before it starts the container.
            dcr_image="csit_sut-ubuntu2004:local"
            # Run the container in the background and print the new container
            # ID.
            dcr_stc_params="--detach=true "
            # Give extended privileges to this container. A "privileged"
            # container is given access to all devices and able to run nested
            # containers.
            dcr_stc_params+="--privileged "
            # Publish all exposed ports to random ports on the host interfaces.
            dcr_stc_params+="--publish 600${cnt}:2222 "
            # Automatically remove the container when it exits.
            dcr_stc_params+="--rm "
            # Size of /dev/shm.
            dcr_stc_params+="--shm-size 4G "
            # Mount vfio to be able to bind to see binded interfaces. We cannot
            # use --device=/dev/vfio as this does not see newly binded
            # interfaces.
            dcr_stc_params+="--volume /dev:/dev "
            # Mount /opt/boot/ where VM kernel and initrd are located.
            dcr_stc_params+="--volume /opt:/opt "
            # Mount host hugepages for VMs.
            dcr_stc_params+="--volume /dev/hugepages:/dev/hugepages "

            params=(${dcr_stc_params} --name csit-tg-"${cnt}" "${dcr_image}")
            docker run --network=csit-nw-tg${cnt} "${params[@]}"
        done
        ;;
    "stop" )
        docker rm --force $(docker ps --all --quiet --filter name=csit)
        docker network rm $(docker network ls --filter name=csit --quiet)
        ;;
esac
