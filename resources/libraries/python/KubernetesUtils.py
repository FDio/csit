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

"""Library to control Kubernetes kubectl."""

import time
import yaml

from resources.libraries.python.constants import Constants
from resources.libraries.python.topology import NodeType
from resources.libraries.python.ssh import SSH
from resources.libraries.python.CpuUtils import CpuUtils
from resources.libraries.python.VppConfigGenerator import VppConfigGenerator

__all__ = ["KubernetesUtils"]


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

        cmd = '{dir}/{lib}/k8s_setup.sh '.format(dir=Constants.REMOTE_FW_DIR,
                                                 lib=Constants.RESOURCES_LIB_SH)
        (ret_code, _, _) = ssh.exec_command(cmd, timeout=120)
        if int(ret_code) != 0:
            raise RuntimeError('Failed to setup Kubernetes on {node}.'
                               .format(node=node['host']))

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

        stream = file('{tpl}/{yaml}'.format(tpl=Constants.RESOURCES_TPL_K8S,
                                            yaml=yaml_file), 'r')

        for data in yaml.load_all(stream):
            data = reduce(lambda a, kv: a.replace(*kv), kwargs.iteritems(),
                          yaml.dump(data, default_flow_style=False))
            # Workaround to avoid using RAW string anotated with | in YAML as
            # library + bash is misinterpreting spaces.
            data = data.replace('.conf:\n', '.conf: |\n')
            cmd = 'cat <<EOF | kubectl apply -f - \n{data}\nEOF'.format(
                data=data)
            (ret_code, _, _) = ssh.exec_command_sudo(cmd, timeout=120)
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
    def create_kubernetes_cm_from_file_on_node(node, name, key, src_file):
        """Create Kubernetes ConfigMap from file on node.

        :param node: DUT node.
        :param name: ConfigMap name.
        :param key: Key (destination file).
        :param src_file: Source file.
        :type node: dict
        :type name: str
        :type key: str
        :type src_file: str
        :raises RuntimeError: If creating Kubernetes ConfigMap failed.
        """
        ssh = SSH()
        ssh.connect(node)

        cmd = 'kubectl create -n csit configmap {name} --from-file={key}='\
            '{src_file}'.format(name=name, key=key, src_file=src_file)
        (ret_code, _, _) = ssh.exec_command_sudo(cmd, timeout=120)
        if int(ret_code) != 0:
            raise RuntimeError('Failed to create Kubernetes ConfigMap {name} '
                               'on {node}.'.format(name=name,
                                                   node=node['host']))

    @staticmethod
    def create_kubernetes_cm_from_file_on_all_duts(nodes, name, key, src_file):
        """Create Kubernetes ConfigMap from file on all DUTs.

        :param nodes: Topology nodes.
        :param name: ConfigMap name.
        :param key: Key (destination file).
        :param src_file: Source file.
        :type nodes: dict
        :type name: str
        :type key: str
        :type src_file: str
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                KubernetesUtils.create_kubernetes_cm_from_file_on_node(node,
                                                                       name,
                                                                       key,
                                                                       src_file)

    @staticmethod
    def delete_kubernetes_resource_on_node(node, rtype='po,cm', name=None):
        """Delete Kubernetes resource on node.

        :param node: DUT node.
        :param rtype: Kubernetes resource type.
        :param name: Name of resource.
        :type node: dict
        :type rtype: str
        :type name: str
        :raises RuntimeError: If deleting Kubernetes resource failed.
        """
        ssh = SSH()
        ssh.connect(node)

        name = '{name}'.format(name=name) if name else '--all'

        cmd = 'kubectl delete -n csit {rtype} {name}'\
            .format(rtype=rtype, name=name)
        (ret_code, _, _) = ssh.exec_command_sudo(cmd, timeout=120)
        if int(ret_code) != 0:
            raise RuntimeError('Failed to delete Kubernetes resources in CSIT '
                               'namespace on {node}.'.format(node=node['host']))

        cmd = 'kubectl get -n csit pods --no-headers'
        for _ in range(24):
            (ret_code, stdout, _) = ssh.exec_command_sudo(cmd, timeout=120)
            if int(ret_code) == 0:
                ready = True
                for line in stdout.splitlines():
                    if 'No resources found.' not in line:
                        ready = False
                if ready:
                    break
            time.sleep(5)
        else:
            raise RuntimeError('Failed to delete Kubernetes resources in CSIT '
                               'namespace on {node}.'.format(node=node['host']))

    @staticmethod
    def delete_kubernetes_resource_on_all_duts(nodes, rtype='po,cm', name=None):
        """Delete all Kubernetes resource on all DUTs.

        :param nodes: Topology nodes.
        :param rtype: Kubernetes resource type.
        :param name: Name of resource.
        :type nodes: dict
        :type rtype: str
        :type name: str
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                KubernetesUtils.delete_kubernetes_resource_on_node(node, rtype,
                                                                   name)

    @staticmethod
    def describe_kubernetes_resource_on_node(node, rtype='po,cm'):
        """Describe Kubernetes resource on node.

        :param node: DUT node.
        :param rtype: Kubernetes resource type.
        :type node: dict
        :type rtype: str
        :raises RuntimeError: If describing Kubernetes resource failed.
        """
        ssh = SSH()
        ssh.connect(node)

        cmd = 'kubectl describe -n csit {rtype}'.format(rtype=rtype)
        (ret_code, _, _) = ssh.exec_command_sudo(cmd, timeout=120)
        if int(ret_code) != 0:
            raise RuntimeError('Failed to describe Kubernetes resource on '
                               '{node}.'.format(node=node['host']))

    @staticmethod
    def describe_kubernetes_resource_on_all_duts(nodes, rtype='po,cm'):
        """Describe Kubernetes resource on all DUTs.

        :param nodes: Topology nodes.
        :param rtype: Kubernetes resource type.
        :type nodes: dict
        :type rtype: str
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                KubernetesUtils.describe_kubernetes_resource_on_node(node,
                                                                     rtype)

    @staticmethod
    def get_kubernetes_logs_on_node(node, namespace='csit'):
        """Get Kubernetes logs on node.

        :param node: DUT node.
        :param namespace: Kubernetes namespace.
        :type node: dict
        :type namespace: str
        """
        ssh = SSH()
        ssh.connect(node)

        cmd = "for p in $(kubectl get pods -n {namespace} --no-headers"\
            " | cut -f 1 -d ' '); do echo $p; kubectl logs -n {namespace} $p; "\
            "done".format(namespace=namespace)
        ssh.exec_command(cmd, timeout=120)

    @staticmethod
    def get_kubernetes_logs_on_all_duts(nodes, namespace='csit'):
        """Get Kubernetes logs on all DUTs.

        :param nodes: Topology nodes.
        :param namespace: Kubernetes namespace.
        :type nodes: dict
        :type namespace: str
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                KubernetesUtils.get_kubernetes_logs_on_node(node, namespace)

    @staticmethod
    def reset_kubernetes_on_node(node):
        """Reset Kubernetes on node.

        :param node: DUT node.
        :type node: dict
        :raises RuntimeError: If resetting Kubernetes failed.
        """
        ssh = SSH()
        ssh.connect(node)

        cmd = 'kubeadm reset && rm -rf $HOME/.kube'
        (ret_code, _, _) = ssh.exec_command_sudo(cmd, timeout=120)
        if int(ret_code) != 0:
            raise RuntimeError('Failed to reset Kubernetes on {node}.'
                               .format(node=node['host']))

    @staticmethod
    def reset_kubernetes_on_all_duts(nodes):
        """Reset Kubernetes on all DUTs.

        :param nodes: Topology nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                KubernetesUtils.reset_kubernetes_on_node(node)

    @staticmethod
    def wait_for_kubernetes_pods_on_node(node):
        """Wait for Kubernetes PODs to become in 'Running' state on node.

        :param node: DUT node.
        :type node: dict
        :raises RuntimeError: If Kubernetes PODs are not ready.
        """
        ssh = SSH()
        ssh.connect(node)

        cmd = 'kubectl get -n csit pods --no-headers'
        for _ in range(48):
            (ret_code, stdout, _) = ssh.exec_command_sudo(cmd, timeout=120)
            if int(ret_code) == 0:
                ready = True
                for line in stdout.splitlines():
                    if 'Running' in line and '1/1' in line:
                        ready = True
                    else
                        ready = False
                if ready:
                    break
            time.sleep(5)
        else:
            raise RuntimeError('Kubernetes PODs are not ready on {node}.'
                               .format(node=node['host']))

    @staticmethod
    def wait_for_kubernetes_pods_on_all_duts(nodes):
        """Wait for Kubernetes PODs to become in Running state on all DUTs.

        :param nodes: Topology nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                KubernetesUtils.wait_for_kubernetes_pods_on_node(node)

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
        vpp_config.add_heapsize('3G')
        vpp_config.add_ip6_hash_buckets('2000000')
        vpp_config.add_ip6_heap_size('3G')
        if kwargs['framesize'] < 1522:
            vpp_config.add_dpdk_no_multi_seg()
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
        # We will pop first core from list to be main core
        vpp_config.add_cpu_main_core(str(cpuset_cpus.pop(0)))
        # if this is not only core in list, the rest will be used as workers.
        if cpuset_cpus:
            corelist_workers = ','.join(str(cpu) for cpu in cpuset_cpus)
            vpp_config.add_cpu_corelist_workers(corelist_workers)
        vpp_config.add_plugin_disable('dpdk_plugin.so')
        vpp_config.apply_config(filename=kwargs['filename'], restart_vpp=False)
