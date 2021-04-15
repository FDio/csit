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
from resources.libraries.python.ssh import exec_cmd_no_error, exec_cmd
from resources.libraries.python.topology import NodeType
from resources.libraries.python.NginxUtil import NginxUtil


class NGINXTools:
    """This class implements:
    - Initialization of NGINX environment,
    - Cleanup of NGINX environment.
    """

    @staticmethod
    def cleanup_nginx_framework(node, nginx_ins_path):
        """
        Cleanup the nginx framework on the DUT node.

        :param node: Will cleanup the nginx on this nodes.
        :param nginx_ins_path: nginx install path.
        :type node: dict
        :raises RuntimeError: If it fails to cleanup the nginx.
        """
        command = f"rm -rf {nginx_ins_path}"
        message = u"Cleanup the NGINX failed!"
        exec_cmd_no_error(node, command, sudo=True, timeout=1200,
                          message=message)

    @staticmethod
    def cleanup_nginx_framework_on_all_duts(nodes, nginx_ins_path):
        """
        Cleanup the nginx framework on all DUT nodes.

        :param nodes: Will cleanup the nginx on this nodes.
        :param nginx_ins_path: nginx install path.
        :type nodes: dict
        :raises RuntimeError: If it fails to cleanup the nginx.
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                NGINXTools.cleanup_nginx_framework(node, nginx_ins_path)

    @staticmethod
    def install_original_nginx_framework(node, pkg_dir, nginx_version):
        """
        Prepare the nginx framework on the DUT node.

        :param node: Node from topology file.
        :param pkg_dir: ldp nginx install dir.
        :param nginx_version: Vpp Version.
        :type node: dict
        :raises RuntimeError: If command returns nonzero return code.
        """
        nginx_path = f'{pkg_dir}/nginx-{nginx_version}'
        cmd_options = NginxUtil.get_cmd_options(path=nginx_path)
        ret_code, _, stderr = exec_cmd(node, cmd_options, sudo=True)
        if nginx_version in stderr and ret_code == 0:
            logger.info(f"NGINX Version: {stderr}")
            return
        command = f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_SH}" \
                  f"/entry/install_nginx.sh nginx-{nginx_version}"
        message = u"Install the NGINX failed!"
        exec_cmd_no_error(node, command, sudo=True, timeout=600,
                          message=message)
        _, stderr = exec_cmd_no_error(node, cmd_options, sudo=True,
                                      message=message)

        logger.info(f"NGINX Version: {stderr}")

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
                        node, f"dpkg -i --force-all {pkg_dir}vsap-nginx*.deb",
                        timeout=120, sudo=True,
                        message=u"Installation of vsap-nginx failed!"
                    )

                    exec_cmd_no_error(node, f"dpkg -l | grep vsap",
                                      sudo=True)

                    logger.console(f"Completed!\n")
                else:
                    logger.console(u"Ubuntu need!\n")

    @staticmethod
    def install_nginx_framework_on_all_duts(nodes, pkg_dir,
                                            nginx_version=None):
        """
        Prepare the NGINX framework on all DUTs.

        :param nodes: Nodes from topology file.
        :param pkg_dir: Path to directory where packages are stored.
        :param nginx_version: nginx version.
        :type nodes: dict
        """

        for node in list(nodes.values()):
            if node[u"type"] == NodeType.DUT:
                if nginx_version:
                    NGINXTools.install_original_nginx_framework(node, pkg_dir,
                                                                nginx_version)
                else:
                    NGINXTools.install_vsap_nginx_on_duts(node, pkg_dir)
