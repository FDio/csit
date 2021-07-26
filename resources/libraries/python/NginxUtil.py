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

from resources.libraries.python.DUTSetup import DUTSetup
from resources.libraries.python.OptionString import OptionString
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType


class NginxUtil:
    """Utilities for NGINX."""

    @staticmethod
    def get_cmd_options(**kwargs):
        """Create parameters options.

        :param kwargs: Dict of cmd parameters.
        :type kwargs: dict
        :returns: cmd parameters.
        :rtype: OptionString
        """
        cmd_options = OptionString()
        nginx_path = kwargs.get(u"path", u"/usr/local/nginx")
        cmd_options.add(nginx_path)
        options = OptionString(prefix=u"-")
        # Show Nginx Version
        options.add(u"v")
        # Verify Configuration
        options.add(u"t")
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
        :param node: Topology node.
        :param path: Nginx install path.
        :type node: dict
        :type path: str
        :returns: nothing
        """
        cmd_options = NginxUtil.get_cmd_options(path=path, signal=u"stop")

        exec_cmd_no_error(node, cmd_options, sudo=True, disconnect=True,
                          message=u"Nginx stop failed!")

    @staticmethod
    def nginx_cmd_start(node, path, filename):
        """Start NGINX cmd app on node.
        :param node: Topology node.
        :param path: Nginx install path.
        :param filename: Nginx conf name.
        :type node: dict
        :type path: str
        :type filename: str

        :returns: nothing
        """
        cmd_options = NginxUtil.get_cmd_options(path=path,
                                                filename=filename)

        exec_cmd_no_error(node, cmd_options, sudo=True, disconnect=True,
                          message=u"Nginx start failed!")

    @staticmethod
    def nginx_config_verify(node, path):
        """Start NGINX cmd app on node.
        :param node: Topology node.
        :param path: Nginx install path.
        :type node: dict
        :type path: str
        :returns: nothing
        """
        cmd_options = NginxUtil.get_cmd_options(path=path)
        exec_cmd_no_error(node, cmd_options, sudo=True, disconnect=True,
                          message=u"Nginx Config failed!")

    @staticmethod
    def taskset_nginx_pid_to_idle_cores(node, cpu_idle_list):
        """Set idle cpus to NGINX pid on node.

        :param node: Topology node.
        :param cpu_idle_list: Idle Cpus.
        :type node: dict
        :type cpu_idle_list: list
        :returns: nothing
        """
        if node[u"type"] != NodeType.DUT:
            raise RuntimeError(u'Node type is not a DUT!')
        pids = DUTSetup.get_pid(node, u"nginx")
        for index, pid in enumerate(pids):
            cmd = f"taskset -pc {cpu_idle_list[index]} {pid}"
            exec_cmd_no_error(
                node, cmd, sudo=True, timeout=180,
                message=u"taskset cores to nginx pid failed!"
            )
