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

"""ab implementation into CSIT framework."""

from robot.api import logger
from resources.libraries.python.topology import NodeType
from resources.libraries.python.Constants import Constants
from resources.libraries.python.ssh import exec_cmd


def check_ab(tg_node):
    """Check if ab is installed on the TG node.

    :param tg_node: generator node.
    :type tg_node: dict
    :raises: RuntimeError if the given node is not a TG node or if the
        command is not availble.
    """

    if tg_node['type'] != NodeType.TG:
        raise RuntimeError('Node type is not a TG.')

    cmd = u"which ab"
    ret, _, stderr = exec_cmd(tg_node, cmd, timeout=180, sudo=True)

    if int(ret) != 0:
        raise RuntimeError(f"AB is not installed on TG node\nReason:{stderr}")


def run_ab(tg_node, tls_tcp, ciphers, files_num, rps_cps):
    """ Run ab test.

    :param tg_node: Generator node.
    :tls_tcp: TLS or TCP.
    :param ciphers: Specify SSL/TLS cipher suite.
    :param files_num: Filename to be requested from the servers.
                      The file is named after the file size.
    :param rps_cps: RPS or CPS.
    :type tg_node: dict
    :type tls_tcp: str
    :type ciphers: str
    :type files_num: int
    :type rps_cps: str
    :returns: Message with measured data.
    :rtype: str
    :raises: RuntimeError if node type is not a TG.
    """

    if tg_node['type'] != NodeType.TG:
        raise RuntimeError('Node type is not a TG.')

    if files_num == 0:
        files = 'return.json'
    elif files_num >= 1024:
        files = f'{int(files_num / 1024)}KB.json'
    else:
        files = f'{files_num}B.json'

    ip_address = u"192.168.10.1"
    python_dir = u"resources/libraries/python"
    port = u"443"
    qnum = u"40000"
    if tls_tcp == u"tcp":
        port = u"80"
        qnum = u"1000000"

    cmd = f"{Constants.REMOTE_FW_DIR}/{python_dir}/abfork.py" \
          f" --port {port} --clients 2000 --ip {ip_address}" \
          f" --cipher {ciphers}" \
          f" --files {files} --requests {qnum} --protocol TLS1.3"
    if rps_cps == u"rps":
        cmd = f"{cmd} --mode rps"
    else:
        cmd = f"{cmd} --mode cps"

    ret, stdout, _ = exec_cmd(tg_node, cmd, timeout=180, sudo=True)

    if int(ret) != 0:
        raise RuntimeError('ab runtime error.')

    log_msg = _parse_ab_output(stdout, rps_cps, tls_tcp)

    logger.info(log_msg)

    return log_msg


def _parse_ab_output(msg, rps_cps, tls_tcp):
    """Parse the ab stdout with the results.

    :param msg:
    :param rps_cps: RPS or CPS.
    :param tls_tcp: https or http
    :type rps_cps: str
    :type tls_tcp: str
    :return:
    """

    msg_lst = msg.splitlines(False)

    total_cps = u""
    latency = u""
    processing = u""
    complete_req = u""
    failed_req = u""
    total_bytes = u""
    rate = u""

    if tls_tcp == "tls":
        log_msg = u"\nMeasured HTTPS values:\n"
    else:
        log_msg = u"\nMeasured HTTP values:\n"

    for line in msg_lst:
        if f"Connection {rps_cps} rate:" in line:
            # rps (cps)
            total_cps = line + u"\n"
        elif "Transfer Rate:" in line:
            # Rate
            rate = line + u"\n"
        elif "Latency:" in line:
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
