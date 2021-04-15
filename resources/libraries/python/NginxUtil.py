# Copyright (c) 2021 Intel and/or its affiliates.
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

"""NGINX Utilities Library."""

from resources.libraries.python.OptionString import OptionString
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType
from resources.libraries.python.DUTSetup import DUTSetup


class NginxUtil:
    """Utilities for NGINX."""

    @staticmethod
    def get_cmd_options(**kwargs):
        """Create  parameters options.

        :param kwargs: Dict of cmd parameters.
        :type kwargs: dict
        :returns: cmd parameters.
        :rtype: OptionString
        """
        cmd_options = OptionString()
        nginx_path = kwargs.get('path', '/usr/local/nginx')
        cmd_options.add(nginx_path)
        options = OptionString(prefix=u"-")
        # Show Nginx Version
        options.add("v")
        # Verify Configuration
        options.add("t")
        # Send signal to a master process: stop, quit, reopen.
        options.add_with_value_from_dict(
            u"s", u"signal", kwargs
        )
        # Set prefix path (default: /usr/local/nginx/).
        options.add_with_value_from_dict(
            u"p", u"prefix", kwargs
        )
        # Set configuration file (default: conf/nginx.conf).
        options.add_with_value_from_dict(
            u"c", u"filename", kwargs
        )
        # Set global directives out of configuration file
        options.add_with_value_from_dict(
            u"g", u"directives", kwargs
        )
        cmd_options.extend(options)
        return cmd_options

    @staticmethod
    def nginx_cmd_stop(node, path):
        """Stop NGINX cmd app on node.

        :returns: nothing
        """
        cmd_options = NginxUtil.get_cmd_options(path=path, signal='stop')

        exec_cmd_no_error(node, cmd_options, sudo=True, disconnect=True,
                          message="Nginx stop failed")

    @staticmethod
    def nginx_cmd_start(node, path, filename):
        """Start NGINX cmd app on node.

        :returns: nothing
        """
        cmd_options = NginxUtil.get_cmd_options(path=path,
                                                filename=filename)

        exec_cmd_no_error(node, cmd_options, sudo=True, disconnect=True,
                          message="Nginx start failed")

    @staticmethod
    def nginx_config_verify(node, path):
        """Start NGINX cmd app on node.

        :returns: nothing
        """
        cmd_options = NginxUtil.get_cmd_options(path=path)
        exec_cmd_no_error(node, cmd_options, sudo=True, disconnect=True,
                          message="Nginx Config failed")

    @staticmethod
    def clear_nginx_on_nodes(nodes, nginx_path):
        """Remove NGINX  install path  on node.

        :returns: nothing
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                cmd = f'rm -rf {nginx_path}'
                exec_cmd_no_error(node, cmd, sudo=True, disconnect=True,
                                  message="clear nginx framework failed")

    @staticmethod
    def taskset_idle_cores_to_nginx_pid(node, cpu_idle_str):
        """Set NGINX keepalive_timeout on node.

        :param node: Topology node.
        :param cpu_idle_str: Idle Cpus.
        :type node: dict
        :returns: nothing
        """
        if node['type'] != NodeType.DUT:
            raise RuntimeError('Node type is not a DUT.')

        cpu_idle_list = [int(i) for i in cpu_idle_str.split(',')][2:]
        pids = DUTSetup.get_pid(node, 'nginx')
        for index, pid in enumerate(pids):
            cmd = f"taskset -pc {cpu_idle_list[index]} {pid}"
            exec_cmd_no_error(
                node, cmd, sudo=True, timeout=180,
                message=u"taskset cores to nginx pid failed"
            )
