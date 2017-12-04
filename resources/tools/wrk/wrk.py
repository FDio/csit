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

"""wrk implementation into CSIT framework.
"""

import re

from robot.api import logger

from resources.libraries.python.ssh import SSH
from resources.libraries.python.topology import NodeType
from resources.libraries.python.constants import Constants

from wrk_traffic_profile_parser import WrkTrafficProfile
from wrk_errors import WrkError

REGEX_LATENCY_STATS = \
    r"Latency\s*(\d*.\d*\S*)\s*(\d*.\d*\S*)\s*(\d*.\d*\S*)\s*(\d*.\d*\%)"
REGEX_RPS_STATS = \
    r"Req/Sec\s*(\d*.\d*\S*)\s*(\d*.\d*\S*)\s*(\d*.\d*\S*)\s*(\d*.\d*\%)"
REGEX_RPS = r"Requests/sec:\s*(\d*.\d*)"
REGEX_BW = r"Transfer/sec:\s*(\d*.\d*)"
REGEX_LATENCY_DIST = \
    r"Latency Distribution\n" \
    r"\s*50\%\s*(\d*.\d*\D*)\n" \
    r"\s*75\%\s*(\d*.\d*\D*)\n" \
    r"\s*90\%\s*(\d*.\d*\D*)\n" \
    r"\s*99\%\s*(\d*.\d*\D*)\n"


def install_wrk(tg_node):
    """Install wrk on the TG node.

    :param tg_node: Traffic generator node.
    :type tg_node: dict
    :raises: RuntimeError if the given node is not a TG node or if the
    installation fails.
    """

    if tg_node['type'] != NodeType.TG:
        raise RuntimeError('Node type is not a TG.')

    ssh = SSH()
    ssh.connect(tg_node)

    ret, stdout, stderr = ssh.exec_command(
        "sudo -E "
        "sh -c '{0}/resources/tools/wrk/wrk_utils.sh install {1} force'".
        format(Constants.REMOTE_FW_DIR, Constants.WRK_PATH), timeout=1800)
    if int(ret) != 0:
        logger.error('wrk installation failed: {0}'.format(stdout + stderr))
        raise RuntimeError('Installation of wrk on TG node failed.')
    else:
        logger.debug(stdout)


def destroy_wrk(tg_node):
    """Destroy wrk on the TG node.

    :param tg_node: Traffic generator node.
    :type tg_node: dict
    :raises: RuntimeError if the given node is not a TG node.
    """

    if tg_node['type'] != NodeType.TG:
        raise RuntimeError('Node type is not a TG.')

    ssh = SSH()
    ssh.connect(tg_node)

    ret, stdout, stderr = ssh.exec_command(
        "sudo -E "
        "sh -c '{0}/resources/tools/wrk/wrk_utils.sh destroy {1}'".
        format(Constants.REMOTE_FW_DIR, Constants.WRK_PATH), timeout=1800)
    if int(ret) != 0:
        logger.error('wrk removal failed: {0}'.format(stdout + stderr))
        raise RuntimeError('Removal of wrk from the TG node failed.')
    else:
        logger.debug(stdout)


def run_wrk(tg_node, profile_name):
    """Send the traffic as defined in the profile.

    :param tg_node: Traffic generator node.
    :param profile_name: The name of wrk traffic profile.
    :type profile_name: str
    :type tg_node: dict
    """

    if tg_node['type'] != NodeType.TG:
        raise RuntimeError('Node type is not a TG.')

    # Parse and validate the profile
    profile_path = ("resources/traffic_profiles/wrk/{0}.yaml".
                    format(profile_name))
    profile = WrkTrafficProfile(profile_path).traffic_profile

    if len(profile["urls"]) == profile["cpus"]:
        params = [
            "traffic_n_urls_n_cores",
            str(profile["first-cpu"]),
            str(profile["nr-of-threads"]),
            str(profile["nr-of-connections"]),
            "{0}s".format(profile["duration"]),
            "'{0}'".format(profile["header"]),
            str(profile["timeout"]),
            str(profile["script"]),
            str(profile["latency"]),
            "'{0}'".format(" ".join(profile["urls"]))
        ]
    else:
        params = [
            "traffic_n_urls_m_cores",
            str(profile["first-cpu"]),
            str(profile["cpus"] / len(profile["urls"])),
            str(profile["nr-of-threads"]),
            str(profile["nr-of-connections"]),
            "{0}s".format(profile["duration"]),
            "'{0}'".format(profile["header"]),
            str(profile["timeout"]),
            str(profile["script"]),
            str(profile["latency"]),
            "'{0}'".format(" ".join(profile["urls"]))
        ]
    args = " ".join(params)

    print(args)

    ssh = SSH()
    ssh.connect(tg_node)

    ret, stdout, stderr = ssh.exec_command(
        "{0}/resources/tools/wrk/wrk_utils.sh {1}".
        format(Constants.REMOTE_FW_DIR, args), timeout=1800)
    if int(ret) != 0:
        logger.error('wrk runtime error.')
        logger.error(stdout)
        logger.error(stderr)
        raise RuntimeError('wrk runtime error.')
    else:
        logger.debug(stdout)
        logger.debug(stderr)


def _parse_wrk_output(msg):
    """Parse the wrk stdout with the results.

    :param msg: stdout of wrk.
    :type msg: str
    :returns: Parsed results.
    :rtype: dict
    """

    if "Thread Stats" not in msg:
        raise WrkError("The output of wrk does not include the results.")

    msg_lst = msg.splitlines(keepends=False)

    stats = {
        "latency-dist-lst": list(),
        "latency-stats-lst": list(),
        "rps-stats-lst": list(),
        "rps-lst": list(),
        "bw-lst": list(),
        "rps-sum": float(),
        "bw-sum": float()
    }

    for line in msg_lst:
        if "Latency Distribution" in line:
            # Latency distribution - 50%, 75%, 90%, 99%
            pass
        elif "Latency" in line:
            # Latency statistics - Avg, Stdev, Max, +/- Stdev
            pass
        elif "Req/Sec" in line:
            # rps statistics - Avg, Stdev, Max, +/- Stdev
            pass
        elif "Requests/sec:" in line:
            # rps (cps)
            groups = re.search(REGEX_RPS, line)
        elif "Transfer/sec:" in line:
            # BW
            pass

