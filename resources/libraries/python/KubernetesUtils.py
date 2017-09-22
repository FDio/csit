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

"""Library to manipulate Kubernetes."""

import yaml

from resources.libraries.python.constants import Constants
from resources.libraries.python.topology import NodeType
from resources.libraries.python.ssh import SSH
from resources.libraries.python.VppConfigGenerator import VppConfigGenerator


__all__ = ["KubernetesUtils"]

class KubernetesUtils(object):
    """Kubernetes utilities class."""

    def __init__(self):
        """Initialize KubernetesUtils class."""
        pass

    @staticmethod
    def setup_kubernetes_on_node(node):
        """Setup Kubernetes on node.

        :param node: DUT node.
        :type node: dict
        """

        ssh = SSH()
        ssh.connect(node)

        cmd = '{dir}/{lib}/k8s_setup.sh --version={version} '\
              '--bin={bin}'.format(dir=Constants.REMOTE_FW_DIR,
                                   lib=Constants.RESOURCES_LIB_SH,
                                   version=Constants.K8S_KUBECTL_VERSION,
                                   bin=Constants.K8S_KUBECTL_BIN)
        (ret_code, _, _) = ssh.exec_command(cmd, timeout=120)
        if int(ret_code) != 0:
            raise Exception('Failed to setup Kubernetes on {node}.'
                            .format(node=node['host']))

    @staticmethod
    def setup_kubernetes_on_all_duts(nodes):
        """Setup Kubernetes on all DUTs.

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
        :type node: dict
        :type yaml_file: str
        """

        ssh = SSH()
        ssh.connect(node)

        stream = file('{tpl}/{yaml}'.format(tpl=Constants.RESOURCES_TPL_K8S,
                                            yaml=yaml_file), 'r')

        for data in yaml.load_all(stream):
            data = reduce(lambda a, kv: a.replace(*kv), kwargs.iteritems(),
                          yaml.dump(data))
            print data
            cmd = 'cat <<EOF | kubectl apply -f -\n{data}\nEOF'.format(
                data=data)
            (ret_code, _, _) = ssh.exec_command_sudo(cmd, timeout=120)
            if int(ret_code) != 0:
                raise Exception('Failed to apply Kubernetes template {yaml} on '
                                '{node}.'.format(yaml=yaml_file,
                                                 node=node['host']))

    @staticmethod
    def apply_kubernetes_resource_on_all_duts(nodes, yaml_file, **kwargs):
        """Apply Kubernetes resource on all DUTs.

        :param nodes: Topology nodes.
        :param yaml_file: YAML configuration file.
        :type nodes: dict
        :type yaml_file: str
        """

        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                KubernetesUtils.apply_kubernetes_resource_on_node(node,
                                                                  yaml_file,
                                                                  **kwargs)

    @staticmethod
    def delete_kubernetes_resource_on_node(node, name=None):
        """Delete Kubernetes resource on node.

        :param node: DUT node.
        :name name: Name of resource.
        :type node: dict
        :type name: str
        """

        ssh = SSH()
        ssh.connect(node)

        name = '{name}'.format(name=name) if name else '--all'

        cmd = 'kubectl -n csit delete pods,services {name}'\
            .format(name=name)
        (ret_code, _, _) = ssh.exec_command_sudo(cmd, timeout=120)
        if int(ret_code) != 0:
            raise Exception('Failed to delete Kubernetes resources in CSIT '
                            'namespace on {node}.'.format(node=node['host']))

    @staticmethod
    def delete_kubernetes_resource_on_all_duts(nodes, name=None):
        """Delete all Kubernetes resource on all DUTs.

        :param nodes: Topology nodes.
        :name name: Name of resource.
        :type nodes: dict
        :type name: str
        """

        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                KubernetesUtils.delete_kubernetes_resource_on_node(node, name)

    @staticmethod
    def reset_kubernetes_on_node(node):
        """Reset Kubernetes on node.

        :param node: DUT node.
        :type node: dict
        """

        ssh = SSH()
        ssh.connect(node)

        cmd = 'kubeadm reset'
        (ret_code, _, _) = ssh.exec_command_sudo(cmd, timeout=120)
        if int(ret_code) != 0:
            raise Exception('Failed to reset Kubernetes on {node}.'
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
