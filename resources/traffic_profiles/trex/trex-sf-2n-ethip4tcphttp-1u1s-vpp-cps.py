from trex_astf_lib.api import *


class Prof1():
    def __init__(self):
        """Initialization and setting of streams' parameters."""

        # Response content length.
        self.content_len = 115
        # Number of requests per HTTP transaction.
        self.requests = 1
        # Number of transactions per HTTP connection.
        self.transaction_per_conn = 1
        # Use TCP RST instead of FIN+ACK.
        self.tcp_reset = False

        # IP used in packet headers.
        self.p1_src_start_ip = '172.16.130.2'
        self.p1_src_end_ip = '172.16.130.2'
        self.p1_dst_start_ip = '172.16.130.1'
        self.p1_dst_end_ip = '172.16.130.1'

        self.http_req = (b'GET / HTTP/1.1\r\n'
                          'Host: {host}\r\n'
                          'User-Agent: trex/astf\r\n'
                          'Accept: */*\r\n\r\n'
                          .format(host=self.p1_dst_start_ip))
        self.http_res = (b'HTTP/1.1 200 OK\r\n'
                          'Content-Type: text/html\r\n'
                          'Expires: Mon, 11 Jan 1970 10:10:10 GMT\r\n'
                          'Connection: close\r\n'
                          'Pragma: no-cache\r\n'
                          'Content-Length: {length}\r\n\r\n'
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

