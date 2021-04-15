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

"""Nginx Configuration File Generator library.
"""

from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType
from resources.libraries.python.NginxUtil import NginxUtil

__all__ = [u"NginxConfigGenerator"]


class NginxConfigGenerator:
    """VPP Configuration File Generator."""

    def __init__(self):
        """Initialize library."""
        # VPP Node to apply configuration on
        self._node = u""
        # NGINX Startup config location
        self._nginx_path = u"/usr/local/nginx/"
        # Serialized NGinx Configuration
        self._nginx_config = u""
        # VPP Configuration
        self._nodeconfig = dict()

    def set_node(self, node):
        """Set DUT node.

        :param node: Node to store configuration on.
        :type node: dict
        :raises RuntimeError: If Node type is not DUT.
        """
        if node[u"type"] != NodeType.DUT:
            raise RuntimeError(
                u"Startup config can only be applied to DUTnode."
            )
        self._node = node

    def set_nginx_path(self, packages_dir, nginx_version):
        """Set Nginx Conf Name.

        :param packages_dir: nginx install path.
        :param nginx_version: test nginx version.
        :type packages_dir: str
        :type nginx_version: str
        :raises RuntimeError: If Node type is not DUT.
        """
        self._nginx_path = f"{packages_dir}/nginx-" \
                           f"{nginx_version}"

    def add_http_server_listen(self, value):
        """Add Http Server listen port configuration."""
        path = ['http', 'server', 'listen']
        self.add_config_item(self._nodeconfig, value, path)

    def add_http_server_root(self, value='html'):
        """Add Http Server root configuration."""
        path = ['http', 'server', 'root']
        self.add_config_item(self._nodeconfig, value, path)

    def add_http_server_index(self, value='index.html index.htm'):
        """Add Http Server index configuration."""

        path = ['http', 'server', 'index']
        self.add_config_item(self._nodeconfig, value, path)

    def add_config_item(self, config, value, path):
        """Add nginx configuration item.

        :param config: Startup configuration of node.
        :param value: Value to insert.
        :param path: Path where to insert item.
        :type config: dict
        :type value: str
        :type path: list
        """
        if len(path) == 1:
            config[path[0]] = value
            return
        if path[0] not in config:
            config[path[0]] = dict()
        elif isinstance(config[path[0]], str):
            config[path[0]] = dict() if config[path[0]] == u"" \
                else {config[path[0]]: u""}
        self.add_config_item(config[path[0]], value, path[1:])

    def dump_config(self, obj, level=-1):
        """Dump the startup configuration in Nginx config format.

        :param obj: Python Object to print.
        :param level: Nested level for indentation.
        :type obj: Obj
        :type level: int
        :returns: nothing
        """
        indent = u"  "
        if level >= 0:
            self._nginx_config += f"{level * indent}{{\n"
        if isinstance(obj, dict):
            for key, val in obj.items():
                if hasattr(val, u"__iter__") and not isinstance(val, str):
                    self._nginx_config += f"{(level + 1) * indent}{key}\n"
                    self.dump_config(val, level + 1)
                else:
                    self._nginx_config += f"{(level + 1) * indent}" \
                                          f"{key} {val};\n"
        else:
            for val in obj:
                self._nginx_config += f"{(level + 1) * indent}{val};\n"
        if level >= 0:
            self._nginx_config += f"{level * indent}}}\n"

    def write_config(self, filename=None):
        """Generate and write Nginx startup configuration to file.

        :param filename: nginx configuration file name.
        :type filename: str
        """
        if filename is None:
            filename = f'{self._nginx_path}/conf/nginx.conf'
        self.dump_config(self._nodeconfig)
        cmd = f"echo \"{self._nginx_config}\" | sudo tee {filename}"
        exec_cmd_no_error(
            self._node, cmd, message=u"Writing config file failed!"
        )

    def add_http_server_location(self, size):
        """Add Http Server location configuration."""
        if size == 0:
            files = 'return'
        elif size >= 1024:
            files = f'{int(size / 1024)}KB.json'
        else:
            files = f'{size}B.json'
        key = f"{files}"
        size_str = size * 'x'
        value = "200 '%s'" % size_str
        path = ['http', 'server', f'location /{key}', 'return']
        self.add_config_item(self._nodeconfig, value, path)

    def add_http_access_log(self, value="off"):
        """Add Http access_log configuration."""
        path = ['http', 'access_log']
        self.add_config_item(self._nodeconfig, value, path)

    def add_http_include(self, value="mime.types"):
        """Add Http include configuration."""
        path = ['http', 'include']
        self.add_config_item(self._nodeconfig, value, path)

    def add_http_default_type(self, value="application/octet-stream"):
        """Add Http default_type configuration."""
        path = ['http', 'default_type']
        self.add_config_item(self._nodeconfig, value, path)

    def add_http_sendfile(self, value="on"):
        """Add Http sendfile configuration."""
        path = ['http', 'sendfile']
        self.add_config_item(self._nodeconfig, value, path)

    def add_http_keepalive_timeout(self, value):
        """Add Http keepalive alive timeout configuration."""
        path = ['http', 'keepalive_timeout']
        self.add_config_item(self._nodeconfig, value, path)

    def add_http_keepalive_requests(self, value):
        """Add Http keepalive alive requests configuration."""
        path = ['http', 'keepalive_requests']
        self.add_config_item(self._nodeconfig, value, path)

    def add_events_use(self, value='epoll'):
        """Add Events use configuration."""
        path = ['events', 'use']
        self.add_config_item(self._nodeconfig, value, path)

    def add_events_worker_connections(self, value=10240):
        """Add Events worker connections configuration."""
        path = ['events', 'worker_connections']
        self.add_config_item(self._nodeconfig, value, path)

    def add_events_accept_mutex(self, value='off'):
        """Add Events accept mutex configuration."""
        path = ['events', 'accept_mutex']
        self.add_config_item(self._nodeconfig, value, path)

    def add_events_multi_accept(self, value='off'):
        """Add Events multi accept configuration."""
        path = ['events', 'multi_accept']
        self.add_config_item(self._nodeconfig, value, path)

    def add_worker_rlimit_nofile(self, value=10240):
        """Add Events worker rlimit nofile configuration."""
        path = ['worker_rlimit_nofile']
        self.add_config_item(self._nodeconfig, value, path)

    def add_master_process(self, value='on'):
        """Add master process configuration."""
        path = ['master_process']
        self.add_config_item(self._nodeconfig, value, path)

    def add_daemon(self, value='off'):
        """Add daemon configuration."""
        path = ['daemon']
        self.add_config_item(self._nodeconfig, value, path)

    def add_worker_processes(self, value, smt_used):
        """Add worker processes configuration."""
        # nginx workers : vpp used phy workers = 2:1
        if smt_used:
            value = value * 4
        else:
            value = value * 2
        path = ['worker_processes']
        self.add_config_item(self._nodeconfig, value, path)

    def apply_config(self, filename=None, verify_nginx=True):
        """Generate and write Nginx configuration to file and
        verify configuration.

        :param filename: Nginx configuration file name.
        :param verify_nginx: Verify Nginx configuration.
        :type filename: str
        :type verify_nginx: bool
        """
        self.write_config(filename=filename)

        app_path = f'{self._nginx_path}/sbin/nginx'
        if verify_nginx:
            NginxUtil.nginx_config_verify(self._node, app_path)
