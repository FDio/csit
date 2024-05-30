# Copyright (c) 2024 Cisco and/or its affiliates.
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

"""Library to control Kubernetes kubectl."""

from functools import reduce
from io import open
from time import sleep

from resources.libraries.python.Constants import Constants
from resources.libraries.python.CpuUtils import CpuUtils
from resources.libraries.python.ssh import SSH, exec_cmd_no_error
from resources.libraries.python.topology import NodeType
from resources.libraries.python.VppConfigGenerator import VppConfigGenerator

__all__ = [u"KubernetesUtils"]

# Maximum number of retries to check if PODs are running or deleted.
MAX_RETRY = 48


class KubernetesUtils:
    """Kubernetes utilities class."""

    def __init__(self):
        """Initialize KubernetesUtils class."""

    @staticmethod
    def load_docker_image_on_node(node, image_path):
        """Load Docker container image from file on node.

        :param node: DUT node.
        :param image_path: Container image path.
        :type node: dict
        :type image_path: str
        :raises RuntimeError: If loading image failed on node.
        """
        command = f"docker load -i {image_path}"
        message = f"Failed to load Docker image on {node[u'host']}."
        exec_cmd_no_error(
            node, command, timeout=240, sudo=True, message=message
        )

        command = u"docker rmi $(sudo docker images -f 'dangling=true' -q)"
        message = f"Failed to clean Docker images on {node[u'host']}."
        try:
            exec_cmd_no_error(
                node, command, timeout=240, sudo=True, message=message
            )
        except RuntimeError:
            pass

    @staticmethod
    def load_docker_image_on_all_duts(nodes, image_path):
        """Load Docker container image from file on all DUTs.

        :param nodes: Topology nodes.
        :param image_path: Container image path.
        :type nodes: dict
        :type image_path: str
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                KubernetesUtils.load_docker_image_on_node(node, image_path)

    @staticmethod
    def setup_kubernetes_on_node(node):
        """Set up Kubernetes on node.

        :param node: DUT node.
        :type node: dict
        :raises RuntimeError: If Kubernetes setup failed on node.
        """
        ssh = SSH()
        ssh.connect(node)

        cmd = f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}/" \
            f"k8s_setup.sh deploy_calico"
        ret_code, _, _ = ssh.exec_command(cmd, timeout=240)
        if int(ret_code) != 0:
            raise RuntimeError(
                "Failed to setup Kubernetes on {node[u'host']}."
            )

        KubernetesUtils.wait_for_kubernetes_pods_on_node(
            node, nspace=u"kube-system"
        )

    @staticmethod
    def setup_kubernetes_on_all_duts(nodes):
        """Set up Kubernetes on all DUTs.

        :param nodes: Topology nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                KubernetesUtils.setup_kubernetes_on_node(node)

    @staticmethod
    def destroy_kubernetes_on_node(node):
        """Destroy Kubernetes on node.

        :param node: DUT node.
        :type node: dict
        :raises RuntimeError: If destroying Kubernetes failed.
        """
        ssh = SSH()
        ssh.connect(node)

        cmd = f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}/" \
            f"k8s_setup.sh destroy"

        ret_code, _, _ = ssh.exec_command(cmd, timeout=120)
        if int(ret_code) != 0:
            raise RuntimeError(
                f"Failed to destroy Kubernetes on {node[u'host']}."
            )

    @staticmethod
    def destroy_kubernetes_on_all_duts(nodes):
        """Destroy Kubernetes on all DUTs.

        :param nodes: Topology nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                KubernetesUtils.destroy_kubernetes_on_node(node)

    @staticmethod
    def apply_kubernetes_resource_on_node(node, yaml_file, **kwargs):
        """Apply Kubernetes resource on node.

        :param node: DUT node.
        :param yaml_file: YAML configuration file.
        :param kwargs: Key-value pairs to replace in YAML template.
        :type node: dict
        :type yaml_file: str
        :type kwargs: dict
        :raises RuntimeError: If applying Kubernetes template failed.
        """
        ssh = SSH()
        ssh.connect(node)

        fqn_file = f"{Constants.RESOURCES_TPL_K8S}/{yaml_file}"
        with open(fqn_file, 'r') as src_file:
            stream = src_file.read()
            data = reduce(
                lambda a, kv: a.replace(*kv), list(kwargs.items()), stream
            )
            cmd = f"cat <<EOF | kubectl apply -f - \n{data}\nEOF"

            ret_code, _, _ = ssh.exec_command_sudo(cmd)
            if int(ret_code) != 0:
                raise RuntimeError(
                    f"Failed to apply Kubernetes template {yaml_file} "
                    f"on {node[u'host']}."
                )

    @staticmethod
    def apply_kubernetes_resource_on_all_duts(nodes, yaml_file, **kwargs):
        """Apply Kubernetes resource on all DUTs.

        :param nodes: Topology nodes.
        :param yaml_file: YAML configuration file.
        :param kwargs: Key-value pairs to replace in YAML template.
        :type nodes: dict
        :type yaml_file: str
        :type kwargs: dict
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                KubernetesUtils.apply_kubernetes_resource_on_node(
                    node, yaml_file, **kwargs
                )

    @staticmethod
    def create_kubernetes_cm_from_file_on_node(node, nspace, name, **kwargs):
        """Create Kubernetes ConfigMap from file on node.

        :param node: DUT node.
        :param nspace: Kubernetes namespace.
        :param name: ConfigMap name.
        :param kwargs: Named parameters.
        :type node: dict
        :type nspace: str
        :type name: str
        :param kwargs: dict
        :raises RuntimeError: If creating Kubernetes ConfigMap failed.
        """
        ssh = SSH()
        ssh.connect(node)

        nspace = f"-n {nspace}" if nspace else u""
        from_file = u" ".join(
            f"--from-file={key}={kwargs[key]} " for key in kwargs
        )
        cmd = f"kubectl create {nspace} configmap {name} {from_file}"

        ret_code, _, _ = ssh.exec_command_sudo(cmd)
        if int(ret_code) != 0:
            raise RuntimeError(
                f"Failed to create Kubernetes ConfigMap on {node[u'host']}."
            )

    @staticmethod
    def create_kubernetes_cm_from_file_on_all_duts(
            nodes, nspace, name, **kwargs):
        """Create Kubernetes ConfigMap from file on all DUTs.

        :param nodes: Topology nodes.
        :param nspace: Kubernetes namespace.
        :param name: ConfigMap name.
        :param kwargs: Named parameters.
        :type nodes: dict
        :type nspace: str
        :type name: str
        :param kwargs: dict
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                KubernetesUtils.create_kubernetes_cm_from_file_on_node(
                    node, nspace, name, **kwargs
                )

    @staticmethod
    def delete_kubernetes_resource_on_node(
            node, nspace, name=None, rtype=u"po,cm,deploy,rs,rc,svc"):
        """Delete Kubernetes resource on node.

        :param node: DUT node.
        :param nspace: Kubernetes namespace.
        :param rtype: Kubernetes resource type.
        :param name: Name of resource (Default: all).
        :type node: dict
        :type nspace: str
        :type rtype: str
        :type name: str
        :raises RuntimeError: If retrieving or deleting Kubernetes resource
            failed.
        """
        ssh = SSH()
        ssh.connect(node)

        name = f"{name}" if name else u"--all"
        nspace = f"-n {nspace}" if nspace else u""
        cmd = f"kubectl delete {nspace} {rtype} {name}"

        ret_code, _, _ = ssh.exec_command_sudo(cmd, timeout=120)
        if int(ret_code) != 0:
            raise RuntimeError(
                f"Failed to delete Kubernetes resources on {node[u'host']}."
            )

        cmd = f"kubectl get {nspace} pods --no-headers"
        for _ in range(MAX_RETRY):
            ret_code, stdout, stderr = ssh.exec_command_sudo(cmd)
            if int(ret_code) != 0:
                raise RuntimeError(
                    f"Failed to retrieve Kubernetes resources "
                    f"on {node[u'host']}."
                )
            if name == u"--all":
                ready = False
                for line in stderr.splitlines():
                    if u"No resources found." in line:
                        ready = True
                if ready:
                    break
            else:
                ready = False
                for line in stdout.splitlines():
                    try:
                        state = line.split()[1].split(u"/")
                        ready = bool(
                            u"Running" in line and state == state[::-1]
                        )
                        if not ready:
                            break
                    except (ValueError, IndexError):
                        ready = False
                if ready:
                    break
            sleep(5)
        else:
            raise RuntimeError(
                f"Failed to delete Kubernetes resources on {node[u'host']}."
            )

    @staticmethod
    def delete_kubernetes_resource_on_all_duts(
            nodes, nspace, name=None, rtype=u"po,cm,deploy,rs,rc,svc"):
        """Delete all Kubernetes resource on all DUTs.

        :param nodes: Topology nodes.
        :param nspace: Kubernetes namespace.
        :param rtype: Kubernetes resource type.
        :param name: Name of resource.
        :type nodes: dict
        :type nspace: str
        :type rtype: str
        :type name: str
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                KubernetesUtils.delete_kubernetes_resource_on_node(
                    node, nspace, name, rtype
                )

    @staticmethod
    def describe_kubernetes_resource_on_node(node, nspace):
        """Describe all Kubernetes PODs in namespace on node.

        :param node: DUT node.
        :param nspace: Kubernetes namespace.
        :type node: dict
        :type nspace: str
        """
        ssh = SSH()
        ssh.connect(node)

        nspace = f"-n {nspace}" if nspace else u""
        cmd = f"kubectl describe {nspace} all"

        ssh.exec_command_sudo(cmd)

    @staticmethod
    def describe_kubernetes_resource_on_all_duts(nodes, nspace):
        """Describe all Kubernetes PODs in namespace on all DUTs.

        :param nodes: Topology nodes.
        :param nspace: Kubernetes namespace.
        :type nodes: dict
        :type nspace: str
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                KubernetesUtils.describe_kubernetes_resource_on_node(
                    node, nspace
                )

    @staticmethod
    def get_kubernetes_logs_on_node(node, nspace):
        """Get Kubernetes logs from all PODs in namespace on node.

        :param node: DUT node.
        :param nspace: Kubernetes namespace.
        :type node: dict
        :type nspace: str
        """
        ssh = SSH()
        ssh.connect(node)

        nspace = f"-n {nspace}" if nspace else u""
        cmd = f"for p in $(kubectl get pods {nspace} " \
            f"-o jsonpath='{{.items[*].metadata.name}}'); do echo $p; " \
            f"kubectl logs {nspace} $p; done"

        ssh.exec_command(cmd)

        cmd = f"kubectl exec {nspace} etcdv3 -- etcdctl " \
            f"--endpoints \"localhost:22379\" get \"/\" --prefix=true"

        ssh.exec_command(cmd)

    @staticmethod
    def get_kubernetes_logs_on_all_duts(nodes, nspace):
        """Get Kubernetes logs from all PODs in namespace on all DUTs.

        :param nodes: Topology nodes.
        :param nspace: Kubernetes namespace.
        :type nodes: dict
        :type nspace: str
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                KubernetesUtils.get_kubernetes_logs_on_node(node, nspace)

    @staticmethod
    def wait_for_kubernetes_pods_on_node(node, nspace):
        """Wait for Kubernetes PODs to become ready on node.

        :param node: DUT node.
        :param nspace: Kubernetes namespace.
        :type node: dict
        :type nspace: str
        :raises RuntimeError: If Kubernetes PODs are not in Running state.
        """
        ssh = SSH()
        ssh.connect(node)

        nspace = f"-n {nspace}" if nspace else u"--all-namespaces"
        cmd = f"kubectl get {nspace} pods --no-headers"

        for _ in range(MAX_RETRY):
            ret_code, stdout, _ = ssh.exec_command_sudo(cmd)
            if int(ret_code) == 0:
                ready = False
                for line in stdout.splitlines():
                    try:
                        state = line.split()[1].split(u"/")
                        ready = bool(
                            u"Running" in line and state == state[::-1]
                        )
                        if not ready:
                            break
                    except (ValueError, IndexError):
                        ready = False
                if ready:
                    break
            sleep(5)
        else:
            raise RuntimeError(
                f"Kubernetes PODs are not running on {node[u'host']}."
            )

    @staticmethod
    def wait_for_kubernetes_pods_on_all_duts(nodes, nspace):
        """Wait for Kubernetes to become ready on all DUTs.

        :param nodes: Topology nodes.
        :param nspace: Kubernetes namespace.
        :type nodes: dict
        :type nspace: str
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                KubernetesUtils.wait_for_kubernetes_pods_on_node(node, nspace)

    @staticmethod
    def set_kubernetes_pods_affinity_on_node(node):
        """Set affinity for all Kubernetes PODs except VPP on node.

        :param node: DUT node.
        :type node: dict
        """
        ssh = SSH()
        ssh.connect(node)

        cmd = f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}/" \
            f"k8s_setup.sh affinity_non_vpp"

        ssh.exec_command(cmd)

    @staticmethod
    def set_kubernetes_pods_affinity_on_all_duts(nodes):
        """Set affinity for all Kubernetes PODs except VPP on all DUTs.

        :param nodes: Topology nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                KubernetesUtils.set_kubernetes_pods_affinity_on_node(node)

    @staticmethod
    def create_kubernetes_vswitch_startup_config(**kwargs):
        """Create Kubernetes VSWITCH startup configuration.

        :param kwargs: Key-value pairs used to create configuration.
        :param kwargs: dict
        """
        smt_used = CpuUtils.is_smt_enabled(kwargs[u"node"][u"cpuinfo"])

        cpuset_cpus = CpuUtils.cpu_slice_of_list_per_node(
            node=kwargs[u"node"], cpu_node=kwargs[u"cpu_node"], skip_cnt=2,
            cpu_cnt=kwargs[u"phy_cores"], smt_used=smt_used
        )
        cpuset_main = CpuUtils.cpu_slice_of_list_per_node(
            node=kwargs[u"node"], cpu_node=kwargs[u"cpu_node"], skip_cnt=1,
            cpu_cnt=1, smt_used=smt_used
        )

        # Create config instance
        vpp_config = VppConfigGenerator()
        vpp_config.set_node(kwargs[u"node"])
        vpp_config.add_unix_cli_listen(value=u"0.0.0.0:5002")
        vpp_config.add_unix_nodaemon()
        vpp_config.add_socksvr()
        vpp_config.add_ip6_heap_size(u"4G")
        vpp_config.add_ip6_hash_buckets(u"2000000")
        if not kwargs[u"jumbo"]:
            vpp_config.add_dpdk_no_multi_seg()
        vpp_config.add_dpdk_enable_tcp_udp_checksum()
        vpp_config.add_dpdk_no_tx_checksum_offload()
        vpp_config.add_dpdk_dev_default_rxq(kwargs[u"rxq_count_int"])
        vpp_config.add_dpdk_dev(kwargs[u"if1"], kwargs[u"if2"])
        vpp_config.add_buffers_per_numa(kwargs[u"buffers_per_numa"])
        # We will pop first core from list to be main core
        vpp_config.add_cpu_main_core(str(cpuset_main.pop(0)))
        # if this is not only core in list, the rest will be used as workers.
        if cpuset_cpus:
            corelist_workers = u",".join(str(cpu) for cpu in cpuset_cpus)
            vpp_config.add_cpu_corelist_workers(corelist_workers)
        vpp_config.write_config(filename=kwargs[u"filename"])

    @staticmethod
    def create_kubernetes_vnf_startup_config(**kwargs):
        """Create Kubernetes VNF startup configuration.

        :param kwargs: Key-value pairs used to create configuration.
        :param kwargs: dict
        """
        smt_used = CpuUtils.is_smt_enabled(kwargs[u"node"][u"cpuinfo"])
        skip_cnt = kwargs[u"cpu_skip"] + (kwargs[u"i"] - 1) * \
            (kwargs[u"phy_cores"] - 1)
        cpuset_cpus = CpuUtils.cpu_slice_of_list_per_node(
            node=kwargs[u"node"], cpu_node=kwargs[u"cpu_node"],
            skip_cnt=skip_cnt, cpu_cnt=kwargs[u"phy_cores"]-1, smt_used=smt_used
        )
        cpuset_main = CpuUtils.cpu_slice_of_list_per_node(
            node=kwargs[u"node"], cpu_node=kwargs[u"cpu_node"], skip_cnt=1,
            cpu_cnt=1, smt_used=smt_used
        )
        # Create config instance
        vpp_config = VppConfigGenerator()
        vpp_config.set_node(kwargs[u"node"])
        vpp_config.add_unix_cli_listen(value=u"0.0.0.0:5002")
        vpp_config.add_unix_nodaemon()
        vpp_config.add_socksvr()
        # We will pop first core from list to be main core
        vpp_config.add_cpu_main_core(str(cpuset_main.pop(0)))
        # if this is not only core in list, the rest will be used as workers.
        if cpuset_cpus:
            corelist_workers = u",".join(str(cpu) for cpu in cpuset_cpus)
            vpp_config.add_cpu_corelist_workers(corelist_workers)
        vpp_config.add_plugin(u"disable", [u"dpdk_plugin.so"])
        vpp_config.write_config(filename=kwargs[u"filename"])
