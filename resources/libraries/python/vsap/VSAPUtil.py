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

"""VSAP util library."""

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
