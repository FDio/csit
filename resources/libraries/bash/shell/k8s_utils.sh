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

function k8s_utils.destroy {
    # Destroy existing Kubernetes deployment
    kubectl drain $HOSTNAME --delete-local-data --force --ignore-daemonsets
    kubectl delete node $HOSTNAME

    # Revert any changes made to this host by 'kubeadm init' or 'kubeadm join'
    sudo kubeadm reset --force && sudo rm -rf $HOME/.kube || \
        { echo "Failed to reset kubeadm"; exit 1; }
}

function k8s_utils.prepare {
    # Sets up the Kubernetes master

    # Disable swap
    sudo swapoff --all

    # Set up the Kubernetes master
    sudo -E kubeadm init --token-ttl 0 ${1} || \
        { echo "Failed to init kubeadm"; exit 1; }

    # Make cgroup non-exclusive for CPU and MEM
    sudo cgset -r cpuset.cpu_exclusive=0 /kubepods
    sudo cgset -r cpuset.mem_exclusive=0 /kubepods

    rm -rf $HOME/.kube
    mkdir -p $HOME/.kube
    sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
    sudo chown $(id -u):$(id -g) $HOME/.kube/config
}

function k8s_utils.taint {
    # Updates the taints
    kubectl taint nodes --all node-role.kubernetes.io/master- || \
        { echo "Failed to taint nodes"; exit 1; }
}

function k8s_utils.calico_deploy {
    # Calico yaml URL or file
    k8s_calico=$1

    # Apply resources
    kubectl apply -f ${k8s_calico}  || \
        { echo "Failed to apply ${k8s_calico}"; exit 1; }

    # Update the taints
    k8s_utils.taint
}

function k8s_utils.contiv_vpp_deploy {
    # Contiv yaml URL or file
    k8s_contiv=$1
    k8s_contiv_patch="kubecon.contiv-vpp-yaml-patch.diff"

    # Pull the most recent Docker images
    bash <(curl -s https://raw.githubusercontent.com/contiv/vpp/master/k8s/pull-images.sh)

    # Apply resources
    wget ${k8s_contiv}
    patch contiv-vpp.yaml -i ${k8s_contiv_patch} -o - | kubectl apply -f - || \
        { echo "Failed to apply Contiv resources"; exit 1; }
    rm contiv-vpp.yaml

    # Update the taints
    k8s_utils.taint
}

function k8s_utils.cri_shim_install {
    # Install the CRI Shim on host
    sudo su root -c 'bash <(curl -s https://raw.githubusercontent.com/contiv/vpp/master/k8s/cri-install.sh)'
}

function k8s_utils.cri_shim_uninstall {
    # Uninstall the CRI Shim on host
    sudo su root -c 'bash <(curl -s https://raw.githubusercontent.com/contiv/vpp/master/k8s/cri-install.sh) --uninstall'
}

function k8s_utils.kube_proxy_install {
    # Installing custom version of Kube-Proxy to enable Kubernetes services
    bash <(curl -s https://raw.githubusercontent.com/contiv/vpp/master/k8s/proxy-install.sh)
}

function k8s_utils.apply {
    # Resource yaml URL or file
    k8s_resource=$1

    # Apply resources
    kubectl apply -f ${k8s_resource}  || \
        { echo "Failed to apply ${k8s_resource}"; exit 1; }
}

function k8s_utils.resource_delete {
    # Resource yaml URL or file
    k8s_resource=$1

    # Delete resources
    kubectl delete -f ${k8s_resource}  || \
        { echo "Failed to delete ${k8s_resource}"; exit 1; }
}

function k8s_utils.affinity_non_vpp {
    # Set affinity for all non VPP docker containers to CPU 0
    for i in `sudo docker ps --format "{{.ID}} {{.Names}}" | grep -v vpp | cut -d' ' -f1`; do
        sudo docker update --cpuset-cpus 0 ${i}
    done
}

function k8s_utils.dump_all {
    # Dumps the kubernetes objects
    kubectl get all --all-namespaces
    kubectl describe nodes
}
