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

K8S_CALICO="${SCRIPT_DIR}/../../templates/kubernetes/calico_v2.4.1.yaml"
K8S_CSIT="${SCRIPT_DIR}/../../templates/kubernetes/csit.yaml"

trap "sudo kubeadm reset && sudo rm -rf $HOME/.kube" ERR

# Revert any changes made to this host by 'kubeadm init' or 'kubeadm join'
sudo kubeadm reset && sudo rm -rf $HOME/.kube || \
    { echo "Failed to reset kubeadm"; exit 1; }

# Ret up the Kubernetes master
sudo -E kubeadm init --token-ttl 0 --pod-network-cidr=192.168.0.0/16 || \
    { echo "Failed to init kubeadm"; exit 1; }

# Make cgroup non-exclusive for CPU and MEM
sudo cgset -r cpuset.cpu_exclusive=0 /kubepods
sudo cgset -r cpuset.mem_exclusive=0 /kubepods

rm -rf $HOME/.kube
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Apply resources
kubectl apply -f ${K8S_CALICO}  || \
    { echo "Failed to apply Calico resources"; exit 1; }
kubectl apply -f ${K8S_CSIT}  || \
    { echo "Failed to apply CSIT resource"; exit 1; }

# Update the taints
kubectl taint nodes --all node-role.kubernetes.io/master- || \
    { echo "Failed to taint nodes"; exit 1; }

# Dump Kubernetes objects ...
kubectl get all --all-namespaces

echo Kubernetes is ready
