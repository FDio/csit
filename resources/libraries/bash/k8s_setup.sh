#!/bin/bash
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

set -xo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Include
source ${SCRIPT_DIR}/config/defaults
source ${SCRIPT_DIR}/shell/dpdk_utils.sh
source ${SCRIPT_DIR}/shell/k8s_utils.sh

# Read configuration
while read line
do
    if echo $line | grep -F = &>/dev/null
    then
        varname=$(echo "$line" | cut -d '=' -f 1)
        cfg[$varname]=$(echo "$line" | cut -d '=' -f 2-)
    fi
done < ${script_dir}/../config/config

trap "k8s_utils.destroy" ERR

case "$1" in
    prepare)
        # Revert any changes made to this host by 'kubeadm init'
        k8s_utils.destroy
        # Sets up the Kubernetes master
        k8s_utils.prepare
        ;;
    deploy_calico)
        # Load kernel modules uio/uio_pci_generic
        dpdk_utils.load_modules
        # Revert any changes made to this host by 'kubeadm init'
        k8s_utils.destroy
        # Sets up the Kubernetes master
        k8s_utils.prepare "--pod-network-cidr=192.168.0.0/16"
        # Apply resources
        k8s_utils.calico_deploy ${cfg[K8S_CALICO]}
        # Dump Kubernetes objects ...
        k8s_utils.dump_all
        ;;
    destroy)
        # Revert any changes made to this host by 'kubeadm init'
        k8s_utils.destroy
        ;;
    *)
        echo "usage: $0 function"
        echo "function:"
        echo "    prepare_k8s"
        echo "    deploy_calico"
        echo "    destroy_k8s"
        exit 1
esac
shift

echo Kubernetes setup finished
