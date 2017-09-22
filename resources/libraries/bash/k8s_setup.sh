#!/bin/bash
# Copyright (c) 2017 Cisco and/or its affiliates.
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

K8S_URL="https://storage.googleapis.com/kubernetes-release"
K8S_VERSION="v1.7.7"
K8S_KUBECTL_BIN="/usr/local/bin/kubectl"
K8S_KUBECTL_URL="${K8S_URL}/release/${K8S_VERSION}/bin/linux/amd64/kubectl"
K8S_CALICO="${SCRIPT_DIR}/../../templates/kubernetes/calico_v2.4.1.yaml"
K8S_CSIT="${SCRIPT_DIR}/../../templates/kubernetes/csit.yaml"

for i in "$@"; do
    case $i in
        --version=*)
            K8S_VERSION="${i#*=}"
            shift ;;
        --bin=*)
            K8S_KUBECTL_BIN="${i#*=}"
            shift ;;
        *)
            ;;
    esac
done

trap "sudo kubeadm reset && rm -rf $HOME/.kube" ERR

# If kubectl version does not match download it
sudo /usr/local/bin/kubectl version | grep ${K8S_VERSION}
if [[ $? != 0 ]]
then
    wget -O kubectl -q ${K8S_KUBECTL_URL} || \
        { echo "Failed to download Kubernetes ${K8S_VERSION}"; exit 1; }
    chmod +x ./kubectl
    sudo mv ./kubectl ${K8S_KUBECTL_BIN}
fi

# Revert any changes made to this host by 'kubeadm init' or 'kubeadm join'
sudo kubeadm reset || \
    { echo "Failed to reset kubeadm"; exit 1; }

# Ret up the Kubernetes master
sudo -E kubeadm init --token-ttl 0 --pod-network-cidr=192.168.0.0/16 || \
    { echo "Failed to init kubeadm"; exit 1; }

rm -rf $HOME/.kube
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Apply resources
${K8S_KUBECTL_BIN} apply -f ${K8S_CALICO}  || \
    { echo "Failed to apply Calico resources"; exit 1; }
${K8S_KUBECTL_BIN} apply -f ${K8S_CSIT}  || \
    { echo "Failed to apply CSIT resource"; exit 1; }

# Update the taints
${K8S_KUBECTL_BIN} taint nodes --all node-role.kubernetes.io/master- || \
    { echo "Failed to taint nodes"; exit 1; }

# Dump Kubernetes objects ...
${K8S_KUBECTL_BIN} get services

echo Kubernetes is ready
