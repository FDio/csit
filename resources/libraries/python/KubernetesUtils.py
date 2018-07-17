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

"""Library to control Kubernetes kubectl."""

from time import sleep

from resources.libraries.python.constants import Constants
from resources.libraries.python.topology import NodeType
from resources.libraries.python.ssh import SSH
from resources.libraries.python.CpuUtils import CpuUtils
from resources.libraries.python.VppConfigGenerator import VppConfigGenerator

__all__ = ["KubernetesUtils"]

# Maximum number of retries to check if PODs are running or deleted.
MAX_RETRY = 48

class KubernetesUtils(object):
    """Kubernetes utilities class."""

    def __init__(self):
        """Initialize KubernetesUtils class."""
        pass

    @staticmethod
    def setup_kubernetes_on_node(node):
        """Set up Kubernetes on node.

        :param node: DUT node.
        :type node: dict
        :raises RuntimeError: If Kubernetes setup failed on node.
        """
        ssh = SSH()
        ssh.connect(node)

        cmd = '{dir}/{lib}/k8s_setup.sh deploy_calico'\
            .format(dir=Constants.REMOTE_FW_DIR,
                    lib=Constants.RESOURCES_LIB_SH)
        (ret_code, _, _) = ssh.exec_command(cmd, timeout=240)
        if int(ret_code) != 0:
            raise RuntimeError('Failed to setup Kubernetes on {node}.'
                               .format(node=node['host']))

        KubernetesUtils.wait_for_kubernetes_pods_on_node(node,
                                                         nspace='kube-system')

    @staticmethod
    def setup_kubernetes_on_all_duts(nodes):
        """Set up Kubernetes on all DUTs.

        :param nodes: Topology nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
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

        cmd = '{dir}/{lib}/k8s_setup.sh destroy'\
            .format(dir=Constants.REMOTE_FW_DIR,
                    lib=Constants.RESOURCES_LIB_SH)
        (ret_code, _, _) = ssh.exec_command(cmd, timeout=120)
        if int(ret_code) != 0:
            raise RuntimeError('Failed to destroy Kubernetes on {node}.'
                               .format(node=node['host']))

    @staticmethod
    def destroy_kubernetes_on_all_duts(nodes):
        """Destroy Kubernetes on all DUTs.

        :param nodes: Topology nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
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

        fqn_file = '{tpl}/{yaml}'.format(tpl=Constants.RESOURCES_TPL_K8S,
                                         yaml=yaml_file)
        with open(fqn_file, 'r') as src_file:
            stream = src_file.read()
            data = reduce(lambda a, kv: a.replace(*kv), kwargs.iteritems(),
                          stream)
            cmd = 'cat <<EOF | kubectl apply -f - \n{data}\nEOF'.format(
                data=data)
            (ret_code, _, _) = ssh.exec_command_sudo(cmd)
            if int(ret_code) != 0:
                raise RuntimeError('Failed to apply Kubernetes template {yaml} '
                                   'on {node}.'.format(yaml=yaml_file,
                                                       node=node['host']))

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
            if node['type'] == NodeType.DUT:
                KubernetesUtils.apply_kubernetes_resource_on_node(node,
                                                                  yaml_file,
                                                                  **kwargs)

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

        nspace = '-n {nspace}'.format(nspace=nspace) if nspace else ''

        from_file = '{0}'.format(' '.join('--from-file={0}={1} '\
            .format(key, kwargs[key]) for key in kwargs))

        cmd = 'kubectl create {nspace} configmap {name} {from_file}'\
            .format(nspace=nspace, name=name, from_file=from_file)
        (ret_code, _, _) = ssh.exec_command_sudo(cmd)
        if int(ret_code) != 0:
            raise RuntimeError('Failed to create Kubernetes ConfigMap '
                               'on {node}.'.format(node=node['host']))

    @staticmethod
    def create_kubernetes_cm_from_file_on_all_duts(nodes, nspace, name,
                                                   **kwargs):
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
            if node['type'] == NodeType.DUT:
                KubernetesUtils.create_kubernetes_cm_from_file_on_node(node,
                                                                       nspace,
                                                                       name,
                                                                       **kwargs)

    @staticmethod
    def delete_kubernetes_resource_on_node(node, nspace, name=None,
                                           rtype='po,cm,deploy,rs,rc,svc'):
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

        name = '{name}'.format(name=name) if name else '--all'
        nspace = '-n {nspace}'.format(nspace=nspace) if nspace else ''

        cmd = 'kubectl delete {nspace} {rtype} {name}'\
            .format(nspace=nspace, rtype=rtype, name=name)
        (ret_code, _, _) = ssh.exec_command_sudo(cmd)
        if int(ret_code) != 0:
            raise RuntimeError('Failed to delete Kubernetes resources '
                               'on {node}.'.format(node=node['host']))

        cmd = 'kubectl get {nspace} pods -a --no-headers'\
            .format(nspace=nspace)
        for _ in range(MAX_RETRY):
            (ret_code, stdout, stderr) = ssh.exec_command_sudo(cmd)
            if int(ret_code) != 0:
                raise RuntimeError('Failed to retrieve Kubernetes resources on '
                                   '{node}.'.format(node=node['host']))
            if name == '--all':
                ready = False
                for line in stderr.splitlines():
                    if 'No resources found.' in line:
                        ready = True
                if ready:
                    break
            else:
                ready = False
                for line in stdout.splitlines():
                    try:
                        state = line.split()[1].split('/')
                        ready = True if 'Running' in line and\
                            state == state[::-1] else False
                        if not ready:
                            break
                    except (ValueError, IndexError):
                        ready = False
                if ready:
                    break
            sleep(5)
        else:
            raise RuntimeError('Failed to delete Kubernetes resources on '
                               '{node}.'.format(node=node['host']))

    @staticmethod
    def delete_kubernetes_resource_on_all_duts(nodes, nspace, name=None,
                                               rtype='po,cm,deploy,rs,rc,svc'):
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
            if node['type'] == NodeType.DUT:
                KubernetesUtils.delete_kubernetes_resource_on_node(node, nspace,
                                                                   name, rtype)

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

        nspace = '-n {nspace}'.format(nspace=nspace) if nspace else ''

        cmd = 'kubectl describe {nspace} all'.format(nspace=nspace)
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
            if node['type'] == NodeType.DUT:
                KubernetesUtils.describe_kubernetes_resource_on_node(node,
                                                                     nspace)

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

        nspace = '-n {nspace}'.format(nspace=nspace) if nspace else ''

        cmd = "for p in $(kubectl get pods {nspace} -o jsonpath="\
            "'{{.items[*].metadata.name}}'); do echo $p; kubectl logs "\
            "{nspace} $p; done".format(nspace=nspace)
        ssh.exec_command(cmd)

        cmd = "kubectl exec {nspace} etcdv3 -- etcdctl --endpoints "\
            "\"localhost:22379\" get \"/\" --prefix=true".format(nspace=nspace)
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
            if node['type'] == NodeType.DUT:
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

        nspace = '-n {nspace}'.format(nspace=nspace) if nspace \
            else '--all-namespaces'

        cmd = 'kubectl get {nspace} pods -a --no-headers' \
            .format(nspace=nspace)
        for _ in range(MAX_RETRY):
            (ret_code, stdout, _) = ssh.exec_command_sudo(cmd)
            if int(ret_code) == 0:
                ready = False
                for line in stdout.splitlines():
                    try:
                        state = line.split()[1].split('/')
                        ready = True if 'Running' in line and \
                            state == state[::-1] else False
                        if not ready:
                            break
                    except (ValueError, IndexError):
                        ready = False
                if ready:
                    break
            sleep(5)
        else:
            raise RuntimeError('Kubernetes PODs are not running on {node}.'
                               .format(node=node['host']))

    @staticmethod
    def wait_for_kubernetes_pods_on_all_duts(nodes, nspace):
        """Wait for Kubernetes to become ready on all DUTs.

        :param nodes: Topology nodes.
        :param nspace: Kubernetes namespace.
        :type nodes: dict
        :type nspace: str
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                KubernetesUtils.wait_for_kubernetes_pods_on_node(node, nspace)

    @staticmethod
    def set_kubernetes_pods_affinity_on_node(node):
        """Set affinity for all Kubernetes PODs except VPP on node.

        :param node: DUT node.
        :type node: dict
        """
        ssh = SSH()
        ssh.connect(node)

        cmd = '{dir}/{lib}/k8s_setup.sh affinity_non_vpp'\
            .format(dir=Constants.REMOTE_FW_DIR,
                    lib=Constants.RESOURCES_LIB_SH)
        ssh.exec_command(cmd)

    @staticmethod
    def set_kubernetes_pods_affinity_on_all_duts(nodes):
        """Set affinity for all Kubernetes PODs except VPP on all DUTs.

        :param nodes: Topology nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                KubernetesUtils.set_kubernetes_pods_affinity_on_node(node)

    @staticmethod
    def create_kubernetes_vswitch_startup_config(**kwargs):
        """Create Kubernetes VSWITCH startup configuration.

        :param kwargs: Key-value pairs used to create configuration.
        :param kwargs: dict
        """
        cpuset_cpus = \
            CpuUtils.cpu_slice_of_list_per_node(node=kwargs['node'],
                                                cpu_node=kwargs['cpu_node'],
                                                skip_cnt=kwargs['cpu_skip'],
                                                cpu_cnt=kwargs['cpu_cnt'],
                                                smt_used=kwargs['smt_used'])

        # Create config instance
        vpp_config = VppConfigGenerator()
        vpp_config.set_node(kwargs['node'])
        vpp_config.add_unix_cli_listen(value='0.0.0.0:5002')
        vpp_config.add_unix_nodaemon()
        vpp_config.add_dpdk_socketmem('1024,1024')
        vpp_config.add_heapsize('4G')
        vpp_config.add_ip_heap_size('4G')
        vpp_config.add_ip6_heap_size('4G')
        vpp_config.add_ip6_hash_buckets('2000000')
        if kwargs['framesize'] < 1522:
            vpp_config.add_dpdk_no_multi_seg()
        vpp_config.add_dpdk_no_tx_checksum_offload
        vpp_config.add_dpdk_dev_default_rxq(kwargs['rxq'])
        vpp_config.add_dpdk_dev(kwargs['if1'], kwargs['if2'])
        # We will pop first core from list to be main core
        vpp_config.add_cpu_main_core(str(cpuset_cpus.pop(0)))
        # if this is not only core in list, the rest will be used as workers.
        if cpuset_cpus:
            corelist_workers = ','.join(str(cpu) for cpu in cpuset_cpus)
            vpp_config.add_cpu_corelist_workers(corelist_workers)
        vpp_config.apply_config(filename=kwargs['filename'], restart_vpp=False)

    @staticmethod
    def create_kubernetes_vnf_startup_config(**kwargs):
        """Create Kubernetes VNF startup configuration.

        :param kwargs: Key-value pairs used to create configuration.
        :param kwargs: dict
        """
        skip_cnt = kwargs['cpu_skip'] + (kwargs['i'] - 1) * \
            (kwargs['cpu_cnt'] - 1)
        cpuset_cpus = \
            CpuUtils.cpu_slice_of_list_per_node(node=kwargs['node'],
                                                cpu_node=kwargs['cpu_node'],
                                                skip_cnt=skip_cnt,
                                                cpu_cnt=kwargs['cpu_cnt']-1,
                                                smt_used=kwargs['smt_used'])
        cpuset_main = \
            CpuUtils.cpu_slice_of_list_per_node(node=kwargs['node'],
                                                cpu_node=kwargs['cpu_node'],
                                                skip_cnt=1,
                                                cpu_cnt=1,
                                                smt_used=kwargs['smt_used'])
        # Create config instance
        vpp_config = VppConfigGenerator()
        vpp_config.set_node(kwargs['node'])
        vpp_config.add_unix_cli_listen(value='0.0.0.0:5002')
        vpp_config.add_unix_nodaemon()
        # We will pop first core from list to be main core
        vpp_config.add_cpu_main_core(str(cpuset_main.pop(0)))
        # if this is not only core in list, the rest will be used as workers.
        if cpuset_cpus:
            corelist_workers = ','.join(str(cpu) for cpu in cpuset_cpus)
            vpp_config.add_cpu_corelist_workers(corelist_workers)
        vpp_config.add_plugin('disable', 'dpdk_plugin.so')
        vpp_config.apply_config(filename=kwargs['filename'], restart_vpp=False)
