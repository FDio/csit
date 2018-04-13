# Copyright (c) 2018 Cisco and/or its affiliates.
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
            vat.vat_terminal_exec_cmd_from_template(
                "start_http_server.vat")

    @staticmethod
    def start_http_server_params(node, prealloc_fifos, fifo_size,
                                 private_segment_size):
        """Start HTTP server on the given node.

        test http server static prealloc-fifos <N> fifo-size <size in kB>
        private-segment-size <seg_size expressed as number + unit, e.g. 100m>

        Where N is the max number of connections you expect to handle at one
        time and <size> should be small if you test for CPS and exchange few
        bytes, say 4, if each connection just exchanges few packets. Or it
        should be much larger, up to 1024/4096 (i.e. 1-4MB) if you have only
        one connection and exchange a lot of packets, i.e., when you test for
        RPS. If you need to allocate lots of FIFOs, so you test for CPS, make
        private-segment-size something like 4g.

        Example:

        For CPS
        test http server static prealloc-fifos 10000 fifo-size 64
        private-segment-size 4000m

        For RPS
        test http server static prealloc-fifos 500000 fifo-size 4
        test http server static prealloc-fifos 500000 fifo-size 4
        private-segment-size 4000m

        :param node: Node to start HTTP server on.
        :param prealloc_fifos: Max number of connections you expect to handle at
            one time.
        :param fifo_size: FIFO size in kB.
        :param private_segment_size: Private segment size. Number + unit.
        :type node: dict
        :type prealloc_fifos: str
        :type fifo_size: str
        :type private_segment_size: str
        """

        with VatTerminal(node, json_param=False) as vat:
            vat.vat_terminal_exec_cmd_from_template(
                "start_http_server_params.vat",
                prealloc_fifos=prealloc_fifos,
                fifo_size=fifo_size,
                private_segment_size=private_segment_size)
