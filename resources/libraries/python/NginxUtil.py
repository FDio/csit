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
from resources.libraries.python.Constants import Constants
from resources.libraries.python.topology import NodeType
from resources.libraries.python.DUTSetup import DUTSetup


class NginxManage:
    def __init__(self, node, version, nginx_conf_name, pkg_dir):
        """
        :param node: Topology node.
        :param version: nginx version
        :param nginx_conf_name: nginx conf name
        :param pkg_dir: download dir
        """
        self.node = node
        self.version = version
        self.path = f'{pkg_dir}/nginx-{self.version}'
        self.conf = f'{self.path}/conf/{nginx_conf_name}'

    def nginx_cmd_stop(self):
        """Stop NGINX cmd app on node.

        :returns: nothing
        """
        cmd_options = NginxUtil.get_cmd_options(path=self.path, signal='stop')

        exec_cmd_no_error(self.node, cmd_options, sudo=True, disconnect=True,
                          message="Nginx stop failed")

    def nginx_cmd_start(self):
        """Start NGINX cmd app on node.

        :returns: nothing
        """
        cmd_options = NginxUtil.get_cmd_options(path=self.path,
                                                filename=self.conf)

        exec_cmd_no_error(self.node, cmd_options, sudo=True, disconnect=True,
                          message="Nginx start failed")

    def get_nginx_conf_var(self, key):
        """Get NGINX conf var.

        :param key: grep conf var key.
        :returns: string
        """
        message = f"Found {key} in Conf failed"
        get_config_var = f"cat {self.conf} " \
                         f"| grep {key}"
        stdout, _ = exec_cmd_no_error(self.node, get_config_var, sudo=True,
                                      disconnect=True, message=message)
        value = stdout.strip()
        if value == '':
            RuntimeError(message)
        return value

    def set_nginx_conf_value(self, original_string, new_string):
        """Set NGINX conf value on node.

        :param original_string: original string.
        :param new_string: new string.
        :returns: nothing
        """
        sed_cmd = f'sed -i "s|{original_string}|{new_string}|"'
        cmd = f'{sed_cmd} {self.conf}'
        exec_cmd_no_error(self.node, cmd, sudo=True, disconnect=True,
                          message=f"Sed {new_string} failed")

    def set_nginx_worker_processes(self, workers, smt_used):
        """Set NGINX worker_processes on node.
.
        :param workers: vpp  workers.
        :param smt_used: Whether symmetric multithreading is used.
        :type smt_used: bool
        :returns: nothing
        """
        # nginx used workers : vpp used  workers = 2:1
        if smt_used:
            nginx_workers = workers * 4
        else:
            nginx_workers = workers * 2
        current_wp = self.get_nginx_conf_var('worker_processes')
        sed_str = f'worker_processes {nginx_workers};'
        self.set_nginx_conf_value(current_wp, sed_str)

    def set_nginx_listen_port(self, tcp_tls):
        """Set NGINX listen port on node.

        :param tcp_tls: tcp or tls.
        :returns: nothing
        """
        listen_port = 80
        if tcp_tls == 'tls':
            listen_port = 443
        current_listen_port = self.get_nginx_conf_var('listen')
        sed_str = f'listen {listen_port};'
        self.set_nginx_conf_value(current_listen_port, sed_str)

    def set_nginx_keepalive_timeout(self, rps_cps):
        """Set NGINX keepalive_timeout on node.

        :param rps_cps: Performance tests which measure connections per second.
        :returns: nothing
        """
        keepalive_time_out = '300s'
        if rps_cps == 'cps':
            keepalive_time_out = '0s'
        get_kto = self.get_nginx_conf_var('keepalive_timeout')
        sed_str = f'keepalive_timeout {keepalive_time_out};'
        self.set_nginx_conf_value(get_kto, sed_str)


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
        cmd_options.add(f"/{nginx_path}/sbin/nginx")
        options = OptionString(prefix=u"-")
        options.add(u"v")
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
        options.add_with_value_from_dict(
            u"v", u"version", kwargs
        )
        cmd_options.extend(options)
        return cmd_options

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
    def copy_nginx_tpl_conf(nodes, nginx_version, conf_name, pkg_dir):
        """Copy NGINX-Template conf on node.

        :param nodes: Topology node.
        :param nginx_version: Nginx Version.
        :param conf_name: Nginx conf name.
        :param pkg_dir: downloads dir.
        :type nodes: dict
        :returns: nothing
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                cmd = f'cp {Constants.REMOTE_FW_DIR}/' \
                      f'{Constants.RESOURCES_TPL}/vsap/nginx-vsap.conf' \
                      f' {pkg_dir}/nginx-{nginx_version}' \
                      f'/conf/{conf_name}'
                exec_cmd_no_error(node, cmd, sudo=True, disconnect=True,
                                  message='Copy nginx conf failed')

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
        cpu_idle_list = [int(i) for i in cpu_idle_str.split(',')]
        pids = DUTSetup.get_pid(node, 'nginx')
        for index, pid in enumerate(pids):
            cmd = f"taskset -pc {cpu_idle_list[index]} {pid}"
            exec_cmd_no_error(
                node, cmd, sudo=True, timeout=180,
                message=u"taskset cores to nginx pid failed"
            )
