# Copyright (c) 2019 Cisco and/or its affiliates.
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

"""TCP util library."""

from resources.libraries.python.Constants import Constants
from resources.libraries.python.PapiExecutor import PapiSocketExecutor


class TCPUtils(object):
    """Implementation of the TCP utilities."""

    www_root_dir = f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_TP_WRK_WWW}"

    def __init__(self):
        pass

    @classmethod
    def start_vpp_http_server_params(
            cls, node, http_static_plugin, prealloc_fifos, fifo_size,
            private_segment_size):
        """Start the test HTTP server internal application or
           the HTTP static server plugin internal applicatoin on the given node.

        http static server www-root <www-root-dir> prealloc-fifos <N>
        fifo-size <size in kB>
        private-segment-size <seg_size expressed as number + unit, e.g. 100m>
                                -- or --
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
        http static server www-root <www-root-dir> prealloc-fifos 10000
        fifo-size 64 private-segment-size 4000m

        For RPS
        test http server static prealloc-fifos 500000 fifo-size 4
        private-segment-size 4000m

        :param node: Node to start HTTP server on.
        :param http_static_plugin: Run HTTP static server plugin
        :param prealloc_fifos: Max number of connections you expect to handle at
            one time.
        :param fifo_size: FIFO size in kB.
        :param private_segment_size: Private segment size. Number + unit.
        :type node: dict
        :type http_static_plugin: boolean
        :type prealloc_fifos: str
        :type fifo_size: str
        :type private_segment_size: str
        """
        cmd = f"http static server www-root {cls.www_root_dir} " \
            f"prealloc-fifos {prealloc_fifos} fifo-size {fifo_size} " \
            f"private-segment-size {private_segment_size}" \
            if http_static_plugin \
            else f"test http server static prealloc-fifos {prealloc_fifos} " \
            f"fifo-size {fifo_size} private-segment-size {private_segment_size}"

        PapiSocketExecutor.run_cli_cmd(node, cmd)
