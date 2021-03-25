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


"""This module implements initialization and cleanup of NGINX framework."""

from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType


class NGINXTools:
    """This class implements:
    - Initialization of NGINX environment,
    - Cleanup of NGINX environment.
    """

    @staticmethod
    def cleanup_nginx_framework(node):
        """
        Cleanup the nginx framework on the DUT node.

        :param node: Will cleanup the nginx on this nodes.
        :type node: dict
        :raises RuntimeError: If it fails to cleanup the nginx.
        """
        command = f"rm -rf /usr/local/nginx"
        message = u"Cleanup the NGINX failed!"
        exec_cmd_no_error(node, command, sudo=True, timeout=1200,
                          message=message)

    @staticmethod
    def cleanup_nginx_framework_on_all_duts(nodes):
        """
        Cleanup the nginx framework on all DUT nodes.

        :param nodes: Will cleanup the nginx on this nodes.
        :type nodes: dict
        :raises RuntimeError: If it fails to cleanup the nginx.
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                command = f"rm -rf /usr/local/nginx"
                message = u"Cleanup the NGINX failed!"
                exec_cmd_no_error(node, command, sudo=True, timeout=1200,
                                  message=message)

    @staticmethod
    def install_original_nginx_framework(node):
        """
        Prepare the DPDK framework on the DUT node.

        :param node: Node from topology file.
        :type node: dict
        :raises RuntimeError: If command returns nonzero return code.
        """
        command = f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}" \
                  f"/entry/install_nginx.sh"
        message = u"Install the NGINX failed!"
        exec_cmd_no_error(node, command, sudo=True, timeout=600,
                          message=message)

        command = f"/usr/local/nginx/sbin/nginx -v"
        message = u"Get NGINX version failed!"
        stdout, _ = exec_cmd_no_error(node, command, sudo=True, message=message)

        logger.info(f"NGINX Version: {stdout}")

    @staticmethod
    def install_vsap_nginx_on_duts(nodes, pkg_dir):
        """
        Prepare the NGINX test environment

        :param nodes: DUT nodes.
        :param pkg_dir: Path to directory where packages are stored.
        :type nodes: dict
        :type pkg_dir: str
        :raises RuntimeError: If command returns nonzero return code.
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                command = u". /etc/lsb-release; echo \"${DISTRIB_ID}\""
                stdout, _ = exec_cmd_no_error(node, command)

                if stdout.strip() == u"Ubuntu":
                    logger.console(u"NGINX Nginx install on DUT... ")
                    exec_cmd_no_error(
                        node, u"apt-get purge -y 'vsap*' || true", timeout=120,
                        sudo=True
                    )
                    exec_cmd_no_error(
                        node, f"dpkg -i --force-all {pkg_dir}NGINX-NGINX*.deb",
                        timeout=120, sudo=True,
                        message=u"Installation of NGINX-NGINX failed!"
                    )

                    exec_cmd_no_error(node, f"dpkg -l | grep NGINX-NGINX",
                                      sudo=True)

                    logger.console(f"Completed!\n")
                else:
                    logger.console(u"Ubuntu need!\n")

    @staticmethod
    def install_nginx_framework_on_all_duts(nodes, pkg_dir=None):
        """
        Prepare the NGINX framework on all DUTs.

        :param nodes: Nodes from topology file.
        :param pkg_dir: Path to directory where packages are stored.
        :type nodes: dict
        """
        for node in list(nodes.values()):
            if node[u"type"] == NodeType.DUT:
                if pkg_dir:
                    NGINXTools.install_vsap_nginx_on_duts(node, pkg_dir)
                else:
                    NGINXTools.install_original_nginx_framework(node)
