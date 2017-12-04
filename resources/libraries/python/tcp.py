# Copyright (c) 2017 Cisco and/or its affiliates.
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

"""TCP util library.
"""

from resources.libraries.python.VatExecutor import VatTerminal


class TCPUtils(object):
    """Implementation of the TCP utilities.
    """

    def __init__(self):
        pass

    @staticmethod
    def start_http_server(node):
        """Start HTTP server on the given node.

        :param node: Node to start HTTP server on.
        :type node: dict
        """

        with VatTerminal(node) as vat:
            vat.vat_terminal_exec_cmd_from_template("start_http_server.vat")
