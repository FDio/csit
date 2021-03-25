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

NGINX_PATH = f"{Constants.NGINX_INSTALL_DIR}"


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
        cmd_options.add(f"/{NGINX_PATH}/sbin/nginx")
        options = OptionString(prefix=u"-")
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
    def nginx_cmd_stop(node, **kwargs):
        """Stop NGINX cmd app on node.

        :param node: Topology node.
        :type node: dict
        :returns: nothing
        """
        kwargs['signal'] = 'stop'
        cmd_options = NginxUtil.get_cmd_options(**kwargs)

        exec_cmd_no_error(node, cmd_options, sudo=True, disconnect=True,
                          message="Nginx stop failed")

    @staticmethod
    def clear_nginx_on_nodes(nodes):
        """Remove NGINX app on node.

        :param nodes: Topology nodes.
        :type nodes: dict
        :returns: nothing
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                cmd = f'rm -rf {NGINX_PATH}'
                exec_cmd_no_error(node, cmd, sudo=True, disconnect=True,
                                  message="clear nginx framework failed")

    @staticmethod
    def copy_nginx_conf(nodes):
        """Copy NGINX-NGINX conf on node.

        :param nodes: Topology node.
        :type nodes: dict
        :returns: nothing
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                cmd = f'cp {Constants.REMOTE_FW_DIR}/' \
                      f'{Constants.RESOURCES_TPL}/vsap/nginx-vsap.conf' \
                      f' {NGINX_PATH}/conf/nginx-tmp.conf'
                exec_cmd_no_error(node, cmd, sudo=True, disconnect=True,
                                  message='Copy nginx conf failed')

    @staticmethod
    def get_nginx_conf_var(node, key):
        """Get NGINX conf var.

        :param node: Topology node.
        :param key: grep conf var key.
        :type node: dict
        :returns: string
        """
        message = f"Found {key} in Conf failed"
        get_config_var = f"cat {NGINX_PATH}/conf/nginx-tmp.conf " \
                         f"| grep {key}"
        stdout, _ = exec_cmd_no_error(node, get_config_var, sudo=True,
                                      disconnect=True, message=message)
        value = stdout.strip()
        if value == '':
            RuntimeError(message)
        return value

    @staticmethod
    def set_nginx_conf_value(node, original_string, new_string):
        """Set NGINX conf value on node.

        :param node: Topology node.
        :param original_string: original string.
        :param new_string: new string.
        :type node: dict
        :returns: nothing
        """
        sed_cmd = f'sed -i "s|{original_string}|{new_string}|"'
        sed_file = f"{NGINX_PATH}/conf/nginx-tmp.conf"
        cmd = f'{sed_cmd} {sed_file}'
        exec_cmd_no_error(node, cmd, sudo=True, disconnect=True,
                          message=f"Sed {new_string} failed")

    @staticmethod
    def set_nginx_worker_processes(node, workers, smt_used):
        """Set NGINX worker_processes on node.

        :param node: Node to stop cmd on.
        :param workers: vpp  workers.
        :param smt_used: Whether symmetric multithreading is used.
        :type smt_used: bool
        :type node: dict
        :returns: nothing
        """
        # nginx used workers : vpp used physics workers = 2:1
        if smt_used:
            nginx_workers = workers * 4
        else:
            nginx_workers = workers * 2
        current_wp = NginxUtil.get_nginx_conf_var(node, 'worker_processes')
        sed_str = f'worker_processes {nginx_workers};'
        NginxUtil.set_nginx_conf_value(node, current_wp, sed_str)

    @staticmethod
    def set_nginx_listen_port(node, tcp_tls):
        """Set NGINX worker_processes on node.

        :param node: Node to stop cmd on.
        :param tcp_tls: tcp or tls.
        :type node: dict
        :returns: nothing
        """
        listen_port = 80
        if tcp_tls == 'tls':
            listen_port = 443
        current_listen_port = NginxUtil.get_nginx_conf_var(node, 'listen')
        sed_str = f'listen {listen_port};'
        NginxUtil.set_nginx_conf_value(node, current_listen_port, sed_str)

    @staticmethod
    def set_nginx_keepalive_timeout(node, rps_cps):
        """Set NGINX keepalive_timeout on node.

        :param node: Node to stop cmd on.
        :param rps_cps: Performance tests which measure connections per second.
        :type node: dict
        :returns: nothing
        """
        keepalive_time_out = '300s'
        if rps_cps == 'cps':
            keepalive_time_out = '0s'
        get_kto = NginxUtil.get_nginx_conf_var(node, 'keepalive_timeout')
        sed_str = f'keepalive_timeout {keepalive_time_out};'
        NginxUtil.set_nginx_conf_value(node, get_kto, sed_str)

    @staticmethod
    def taskset_idle_cores_to_nginx_pid(node, cpu_idle_str):
        """Set NGINX keepalive_timeout on node.

        :param node: Node to stop cmd on.
        :param cpu_idle_str: Idle Cpus.
        :param pids: Nginx Pids.
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
