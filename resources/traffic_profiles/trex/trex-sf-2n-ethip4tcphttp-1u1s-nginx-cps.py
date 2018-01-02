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

"""ASTF profile for TRex traffic generator.

ASTF profile:
 - Client side traffic in directions 0 --> 1.
 - Server side traffic disabled.
 - Packet: ETH / IP / TCP / HTTP1.1
 - Direction 0 --> 1:
   - Source IP address range:      172.16.130.2 - 172.16.130.2
   - Destination IP address range: 192.168.0.1
"""

from trex_astf_lib.api import *


class Prof1():
    def __init__(self):
        """Initialization and setting of streams' parameters."""

        # Response content length.
        self.content_len = 0
        # Number of requests per HTTP transaction.
        self.requests = 1
        # Number of transactions per HTTP connection.
        self.transaction_per_conn = 1
        # Use TCP RST instead of FIN+ACK.
        self.tcp_reset = False

        # IP used in packet headers.
        self.p1_src_start_ip = '172.16.130.2'
        self.p1_src_end_ip = '172.16.130.2'
        self.p1_dst_start_ip = '192.168.0.1'
        self.p1_dst_end_ip = '192.168.0.1'

        self.http_req = (b'GET /0KB.bin HTTP/1.1\r\n'
                          'Host: {host}\r\n'
                          'User-Agent: trex/astf\r\n'
                          'Accept: */*\r\n'
                          'Connection: keep-alive\r\n\r\n'
                          .format(host=self.p1_dst_start_ip))
        self.http_res = (b'HTTP/1.1 200 OK\r\n'
                          'Server: nginx/1.13.7\r\n'
                          'Date: Mon, 01 Jan 2018 00:00:00 GMT\r\n'
                          'Content-Type: application/octet-stream\r\n'
                          'Content-Length: {length}\r\n'
                          'Last-Modified: Mon, 01 Jan 2018 00:00:00 GMT\r\n'
                          'Connection: keep-alive\r\n'
                          'ETag: "5a027c14-0"\r\n'
                          'Accept-Ranges: bytes\r\n\r\n'
                          .format(length=self.content_len))

    def create_profile(self):
        # client operations
        prog_c = ASTFProgram()
        prog_c.connect()
        for i in range(self.transaction_per_conn):
            prog_c.send(self.http_req * self.requests)
            prog_c.recv((len(self.http_res) + self.content_len) * self.requests)
        if self.tcp_reset:
            prog_c.reset()

        # ip generator
        ip_gen_c = ASTFIPGenDist(ip_range=[self.p1_src_start_ip,
                                           self.p1_src_end_ip],
                                 distribution="seq")
        ip_gen_s = ASTFIPGenDist(ip_range=[self.p1_dst_start_ip,
                                           self.p1_dst_end_ip],
                                 distribution="seq")
        ip_gen = ASTFIPGen(glob=ASTFIPGenGlobal(ip_offset="0.0.0.1"),
                           dist_client=ip_gen_c,
                           dist_server=ip_gen_s)

        # TCP parameters
        tcp_params = ASTFTCPInfo(window=32768)
        # client tunables
        c_glob_info = ASTFGlobalInfo()

        # template
        client_template = ASTFTCPClientTemplate(program=prog_c,
                                                tcp_info=tcp_params,
                                                ip_gen=ip_gen)
        server_template = ASTFTCPServerTemplate(program=ASTFProgram(),
                                                tcp_info=tcp_params)
        template = ASTFTemplate(client_template=client_template,
                                server_template=server_template)

        # profile
        return ASTFProfile(default_ip_gen=ip_gen, templates=template,
                           default_c_glob_info=c_glob_info)

    def get_profile(self):
        return self.create_profile()


def register():
    return Prof1()

