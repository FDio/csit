# Copyright (c) 2016 Cisco and/or its affiliates.
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

"""SPAN setup library"""

from resources.libraries.python.topology import Topology
from resources.libraries.python.VatExecutor import VatTerminal


# pylint: disable=too-few-public-methods
class SPAN(object):
    """Class contains methods for setting up SPAN mirroring on DUTs."""

    def __init__(self):
        """Initializer."""
        pass

    @staticmethod
    def set_span_mirroring(node, src_if, dst_if):
        """Set Span mirroring on the specified node.

        :param node: DUT node.
        :param src_if: Interface to mirror traffic from.
        :param dst_if: Interface to mirror trafic to.
        :type node: dict
        :type src_if: str
        :type dst_if: str
        """

        src_if = Topology.get_interface_name(node, src_if)
        dst_if = Topology.get_interface_name(node, dst_if)

        with VatTerminal(node, json_param=False) as vat:
            vat.vat_terminal_exec_cmd_from_template('span_create.vat',
                                                    src_if=src_if,
                                                    dst_if=dst_if,
                                                    )
