# Copyright (c) 2022 Intel and/or its affiliates.
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

"""ab implementation into CSIT framework."""

from robot.api import logger
from resources.libraries.python.topology import NodeType
from resources.libraries.python.Constants import Constants
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.OptionString import OptionString


class ABTools:
    """This class implements:
    - Get ab command.
    - Check ab version.
    """

    @staticmethod
    def get_cmd_options(**kwargs):
        """Create  parameters options.

        :param kwargs: Dict of cmd parameters.
        :type kwargs: dict
        :returns: Cmd parameters.
        :rtype: OptionString
        """
        cmd = OptionString()
        cmd.add(u"python3")
        dirname = f"{Constants.REMOTE_FW_DIR}/resources/tools/ab"
        cmd.add(f"{dirname}/ABFork.py")
        cmd_options = OptionString(prefix=u"-")
        # Number of requests to perform.
        cmd_options.add_with_value_from_dict(u"r", u"requests", kwargs)
        # Server port number to use.
        cmd_options.add_with_value_from_dict(u"p", u"port", kwargs)
        # Number of clients being processed at the same time.
        cmd_options.add_with_value_from_dict(u"c", u"clients", kwargs)
        # Filename to be requested from the servers.
        cmd_options.add_with_value_from_dict(u"f", u"files", kwargs)
        # Server ip address.
        cmd_options.add_with_value_from_dict(u"i", u"ip", kwargs)
        # tg ip address.
        cmd_options.add_with_value_from_dict(u"g", u"tip", kwargs)
        # Specify SSL/TLS cipher suite.
        cmd_options.add_with_value_from_dict(u"z", u"cipher", kwargs, default=0)
        # Specify SSL/TLS protocol.
        cmd_options.add_with_value_from_dict(u"t", u"protocol", kwargs,
                                             default=0)
        # Mode: RPS or CPS.
        cmd_options.add_with_value_from_dict(u"m", u"mode", kwargs)
        return cmd.extend(cmd_options)

    @staticmethod
    def check_ab(tg_node):
        """Check if ab is installed on the TG node.

        :param tg_node: Topology node.
        :type tg_node: dict
        :raises: RuntimeError if the given node is not a TG node or if the
            command is not available.
        """

        if tg_node[u"type"] != NodeType.TG:
            raise RuntimeError(u"Node type is not a TG!")

        cmd = u"command -v ab"
        message = u"ab not installed on TG node!"
        exec_cmd_no_error(tg_node, cmd, message=message)

    @staticmethod
    def get_ab_type(node):
        """Log and return the installed traffic generator type.

        :param node: Node from topology file.
        :type node: dict
        :returns: Traffic generator type string.
        :rtype: str
        """
        return "AB"

    @staticmethod
    def get_ab_version(node):
        """Log and return the installed traffic generator version.

        :param node: Node from topology file.
        :type node: dict
        :returns: Traffic generator version string.
        :rtype: str
        """
        command = f"ab -V | head -1 | cut -d',' -f2"
        message = u"Get AB version failed!"
        stdout, _ = exec_cmd_no_error(node, command, message=message)
        return stdout.strip()

    @staticmethod
    def run_ab(tg_node, ip_addr, tg_addr, tls_tcp, cipher, files_num, rps_cps,
               r_total, c_total, port, protocol=u"TLS1.3"):
        """ Run ab test.

        :param tg_node: Topology node.
        :param ip_addr: Sut ip address.
        :param tg_addr: Tg ip address.
        :param tls_tcp: TLS or TCP.
        :param cipher: Specify SSL/TLS cipher suite.
        :param files_num: Filename to be requested from the servers.
        The file is named after the file size.
        :param rps_cps: RPS or CPS.
        :param r_total: Requests total.
        :param r_total: Clients total.
        :param port: Server listen port.
        :param protocol: TLS Protocol.
        :type tg_node: dict
        :type ip_addr: str
        :type tg_addr: str
        :type tls_tcp: str
        :type cipher: str
        :type files_num: int
        :type rps_cps: str
        :type r_total: int
        :type c_total: int
        :type port: int
        :type protocol: str
        :returns: Message with measured data.
        :rtype: str
        :raises: RuntimeError if node type is not a TG.
        """
        if files_num == 0:
            files = u"return"
        elif files_num >= 1024:
            files = f"{int(files_num / 1024)}KB.json"
        else:
            files = f"{files_num}B.json"

        cmd = ABTools.get_cmd_options(
            requests=r_total,
            clients=c_total,
            ip=ip_addr,
            tip=tg_addr,
            files=files,
            cipher=cipher,
            protocol=protocol,
            port=port,
            mode=rps_cps,
        )
        stdout, _ = exec_cmd_no_error(tg_node, cmd, timeout=180, sudo=True,
                                      message=u"ab runtime error!")
        log_msg = ABTools._parse_ab_output(stdout, rps_cps, tls_tcp)

        logger.info(log_msg)

        return log_msg

    @staticmethod
    def _parse_ab_output(msg, rps_cps, tls_tcp):
        """Parse the ab stdout with the results.

        :param msg: Ab Stdout.
        :param rps_cps: RPS or CPS.
        :param tls_tcp: TLS or TCP.
        :type msg: str
        :type rps_cps: str
        :type tls_tcp: str
        :return: Message with measured data.
        :rtype: str
        """

        msg_lst = msg.splitlines(keepends=False)

        total_cps = u""
        latency = u""
        processing = u""
        complete_req = u""
        failed_req = u""
        total_bytes = u""
        rate = u""

        if tls_tcp == u"tls":
            log_msg = u"\nMeasured HTTPS values:\n"
        else:
            log_msg = u"\nMeasured HTTP values:\n"

        for line in msg_lst:
            if f"Connection {rps_cps} rate:" in line:
                # rps (cps)
                total_cps = line + u"\n"
            elif u"Transfer Rate:" in line:
                # Rate
                rate = line + u"\n"
            elif u"Latency:" in line:
                # Latency
                latency = line + u"\n"
            elif u"Total data transferred" in line:
                total_bytes = line + u"\n"
            elif u"Completed requests" in line:
                complete_req = line + u"\n"
            elif u"Failed requests" in line:
                failed_req = line + u"\n"

        log_msg += rate
        log_msg += latency
        log_msg += processing
        log_msg += complete_req
        log_msg += failed_req
        log_msg += total_bytes
        log_msg += total_cps

        return log_msg
