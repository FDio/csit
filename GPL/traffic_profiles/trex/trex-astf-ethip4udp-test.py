# Copyright (c) 2020 Cisco and/or its affiliates.
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

"""ASTF profile for TRex traffic generator."""

from trex.astf.api import *
from profile_trex_astf_base_class import TrafficProfileBaseClass


class TrafficProfile(TrafficProfileBaseClass):
    """Stream profile."""

    def __init__(self):
        """Initialization and setting of streams' parameters."""

        # Response content length.
        self.content_len = 0

    def define_profiles(self, **kwargs):
        # Number of requests per HTTP transaction.
        self.requests = kwargs.get('req', 1)
        # Number of transactions per HTTP connection.
        self.transaction_per_conn = kwargs.get('tpc', 1)
        # Use TCP RST instead of FIN+ACK.
        self.tcp_reset = kwargs.get('rst', False)
        # HTTP connection.
        self.http_conn = kwargs.get('con', 'close')

        # IP used in packet headers.
        self.p1_src_start_ip = '172.16.0.2'
        self.p1_src_end_ip = '172.16.0.17'
        self.p2_src_start_ip = '172.16.10.2'
        self.p2_src_end_ip = '172.16.10.17'

        self.p1_dst_start_ip = '192.168.0.1'
        self.p1_dst_end_ip = '192.168.0.4'
        self.p2_dst_start_ip = '192.168.0.1'
        self.p2_dst_end_ip = '192.168.0.4'

        self.http_req = (b'GET /0KB.bin HTTP/1.1\r\n'
                          'Host: {host}\r\n'
                          'User-Agent: trex/astf\r\n'
                          'Accept: */*\r\n'
                          'Connection: {connection}\r\n\r\n'
                          .format(host=self.p1_dst_start_ip,
                                  connection=self.http_conn))
        self.http_res = (b'HTTP/1.1 200 OK\r\n'
                          'Server: nginx/1.13.7\r\n'
                          'Date: Mon, 01 Jan 2018 00:00:00 GMT\r\n'
                          'Content-Type: application/octet-stream\r\n'
                          'Content-Length: {length}\r\n'
                          'Last-Modified: Mon, 01 Jan 2018 00:00:00 GMT\r\n'
                          'Connection: {connection}\r\n'
                          'ETag: "5a027c14-0"\r\n'
                          'Accept-Ranges: bytes\r\n\r\n'
                          .format(length=self.content_len,
                                  connection=self.http_conn))

        # client operations
        prog_c = ASTFProgram()
        prog_c.set_var("i", self.transaction_per_conn)
        prog_c.set_label("a:")
        prog_c.send(self.http_req * self.requests)
        prog_c.recv((len(self.http_res) + self.content_len) * self.requests,
                     True)
        prog_c.jmp_nz("i", "a:")
        if self.tcp_reset:
            prog_c.reset()

        # server operations
        prog_s = ASTFProgram()

        # ip generator
        ip_gen_c1 = ASTFIPGenDist(ip_range=[self.p1_src_start_ip,
                                            self.p1_src_end_ip],
                                  distribution="seq")
        ip_gen_c2 = ASTFIPGenDist(ip_range=[self.p2_src_start_ip,
                                            self.p2_src_end_ip],
                                  distribution="seq")
        ip_gen_s1 = ASTFIPGenDist(ip_range=[self.p1_dst_start_ip,
                                            self.p1_dst_end_ip],
                                  distribution="seq")
        ip_gen_s2 = ASTFIPGenDist(ip_range=[self.p2_dst_start_ip,
                                            self.p2_dst_end_ip],
                                  distribution="seq")
        ip_gen1 = ASTFIPGen(glob=ASTFIPGenGlobal(ip_offset="0.0.0.1"),
                            dist_client=ip_gen_c1,
                            dist_server=ip_gen_s1)
        ip_gen2 = ASTFIPGen(glob=ASTFIPGenGlobal(ip_offset="0.0.0.1"),
                            dist_client=ip_gen_c2,
                            dist_server=ip_gen_s2)

        # template
        client1_template = ASTFTCPClientTemplate(program=prog_c,
                                                ip_gen=ip_gen1)
        client2_template = ASTFTCPClientTemplate(program=prog_c,
                                                ip_gen=ip_gen2)
        server_template = ASTFTCPServerTemplate(program=prog_s)
        template1 = ASTFTemplate(client_template=client1_template,
                                 server_template=server_template)
        template2 = ASTFTemplate(client_template=client2_template,
                                 server_template=server_template)

        return ip_gen1, [template1, template2]


def register():
    """Register this traffic profile to T-Rex.

    Do not change this function.

    :return: Traffic Profiles.
    :rtype: Object
    """
    return TrafficProfile()
