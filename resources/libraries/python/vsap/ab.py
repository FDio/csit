# Copyright (c) 2020 Intel and/or its affiliates.
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

"""ab implementation into CSIT framework.
"""

from robot.api import logger

from resources.libraries.python.ssh import SSH
from resources.libraries.python.topology import NodeType
from resources.libraries.python.Constants import Constants
from resources.libraries.python.ssh import exec_cmd_no_error, exec_cmd


def check_ab(tg_node):
    """Check if ab is installed on the TG node.

    :param tg_node: generator node.
    :type tg_node: dict
    :raises: RuntimeError if the given node is not a TG node or if the
        command is not availble.
    """

    if tg_node['type'] != NodeType.TG:
        raise RuntimeError('Node type is not a TG.')

    ssh = SSH()
    ssh.connect(tg_node)

    ret, _, _ = ssh.exec_command(
        "command -v ab")
    if int(ret) != 0:
        install_ab(tg_node)

def install_ab(tg_node):
    """Installed ab on the TG node.

    :param tg_node: Traffic generator node.
    :type tg_node: dict
    """

    command = '. /etc/lsb-release; echo "${DISTRIB_ID}"'
    stdout, _ = exec_cmd_no_error(tg_node, command)

    if stdout.strip() == 'Ubuntu':
        exec_cmd_no_error(tg_node, 'apt-get install apache2-utils || true',\
                              timeout=120, sudo=True)
    else:
        exec_cmd_no_error(tg_node, 'yum -y install httpd-tools || true',\
                              timeout=120, sudo=True)

def run_ab(tg_node, ciphers, files_num):
    """ Run ab test.

    :param tg_node: Generator node.
    :param ciphers: Specify SSL/TLS cipher suite.
    :param files_num: Filename to be requested from the servers.
                      The file is named after the file size.
    :type tg_node: dict
    :type ciphers: str
    :type files_num: int
    :returns: Message with measured data.
    :rtype: str
    :raises: RuntimeError if node type is not a TG.
    """

    if tg_node['type'] != NodeType.TG:
        raise RuntimeError('Node type is not a TG.')

    files = str(files_num) + u"B.json"
    if files == u"0B.json":
        files = u"return"

    ip_address = u"192.168.10.1"
    cmd = f"{Constants.REMOTE_FW_DIR}/tests/vsap/vsap_scripts/abfork.py \
            --port 443 --clients 2000 --ip {ip_address}  --cipher {ciphers} \
            --files {files} --requests 40000 --protocol TLS1.2"

    ret, stdout, _ = exec_cmd(tg_node, cmd, timeout=600, sudo=True)

    if int(ret) != 0:
        raise RuntimeError('ab runtime error.')

    log_msg = _parse_ab_output(stdout)

    logger.info(log_msg)

    return log_msg


def _parse_ab_output(msg):
    """Parse the ab stdout with the results.

    :param msg: stdout of ab.
    :type msg: str
    :returns: Parsed results.
    :rtype: str
    """

    msg_lst = msg.splitlines(False)

    total_cps = u""
    latency = u""
    processing = u""
    complete_req = u""
    failed_req = u""
    total_bytes = u""
    rate = u""

    log_msg = u"\nMeasured values:\n"
    for line in msg_lst:
        if "Total cps:" in line:
            # rps (cps)
            total_cps = line + u"\n"
        elif "Rate:" in line:
            # Rate
            rate = line + u"\n"
        elif "Latency:" in line:
            # Latency
            latency = line + u"\n"
        elif "Processing:" in line:
            # processing
            processing = line + u"\n"
        elif u"Total transferred" in line:
            total_bytes = line + u"\n"
        elif u"Complete requests" in line:
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
