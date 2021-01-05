# Copyright (c) 2020 Intel and/or its affiliates.
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

"""VSAP util library."""

from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.DUTSetup import DUTSetup
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType


class VSAPUtil:
    """General class for any VSAP related methods/functions."""

    @staticmethod
    def stop_qat_service(node, qat):
        """Stop QAT service on DUT node.

        :param node: DUT node.
        :param qat: Whether to use qat engine.
        :type node: dict
        :type qat: int
        """
        if qat == 1:
            if node[u"type"] == NodeType.DUT:
                DUTSetup.stop_service(node, "qat_service")

    @staticmethod
    def restart_qat_service(node, qat):
        """Restart VPP service on DUT node.

        :param node: DUT node.
        :para qat: Whether to use qat engine.
        :type node: dict
        :type qat: int
        """
        if qat == 1:
            if node[u"type"] == NodeType.DUT:
                DUTSetup.restart_service(node, "qat_service")

    @staticmethod
    def vpp_tls_openssl_set_engine(node, qat):
        """Set qat engine.

        :param node: DUT node.
        :param qat: Whether to use qat engine.
        :type node: dict
        :type qat: int
        """
        if qat == 1:
            if node[u"type"] == NodeType.DUT:
                cmd = u"vppctl tls openssl set engine qat alg \
                        rsa,pkey_crypto ciphers rsa async"
                exec_cmd_no_error(
                    node, cmd, sudo=True, message=u"VPP failed \
                        to set qat engine!", retries=120
                )

    @staticmethod
    def install_vsap_on_duts(nodes, pkg_dir):
        """
        Prepare the VSAP test environment

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

                    logger.console(u"VSAP install on DUT... ")

                    exec_cmd_no_error(
                        node, u"apt-get purge -y 'vsap*' || true",
                        timeout=120, sudo=True
                    )

                    exec_cmd_no_error(
                        node, f"dpkg -i --force-all {pkg_dir}vsap*.deb",
                        timeout=120, sudo=True,
                        message=u"Installation of VSAP failed!"
                    )

                    exec_cmd_no_error(node, f"dpkg -l | grep vsap", sudo=True)

                    logger.console(f"Completed!\n")
                else:
                    logger.console(u"Ubuntu need!\n")

    @staticmethod
    def install_openssl3_on_duts(nodes, pkg_dir):
        """
        Prepare the openssl3 test environment

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

                    logger.console(u"Openssl3.0.0 install on DUT... ")

                    exec_cmd_no_error(
                        node, u"apt-get purge -y 'openssl3' || true",
                        timeout=120, sudo=True
                    )

                    exec_cmd_no_error(
                        node, f"dpkg -i --force-all {pkg_dir}openssl*.deb",
                        timeout=120, sudo=True,
                        message=u"Installation of Openssl3 failed!"
                    )

                    exec_cmd_no_error(node, u"dpkg -l|grep openssl3",
                                      sudo=True)

                    cmd = f"{Constants.REMOTE_FW_DIR}" \
                          f"/{Constants.RESOURCES_LIB_ENTRY}" \
                          f"/nginx_utils.sh export"

                    exec_cmd_no_error(
                        node, cmd, sudo=True,
                        message=u"Configure the openssl3 library failed!"
                    )
                    logger.console(f"Completed!\n")
                else:
                    logger.console(u"Ubuntu need!\n")
