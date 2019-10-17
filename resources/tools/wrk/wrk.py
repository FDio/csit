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

"""wrk implementation into CSIT framework.
"""

import re

from copy import deepcopy
from time import sleep

from robot.api import logger

from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType
from resources.libraries.python.CpuUtils import CpuUtils
from resources.libraries.python.Constants import Constants

from resources.tools.wrk.wrk_traffic_profile_parser import WrkTrafficProfile
from resources.tools.wrk.wrk_errors import WrkError


REGEX_LATENCY_STATS = \
    r"Latency\s*" \
    r"(\d*\.*\d*\S*)\s*" \
    r"(\d*\.*\d*\S*)\s*" \
    r"(\d*\.*\d*\S*)\s*" \
    r"(\d*\.*\d*\%)"
REGEX_RPS_STATS = \
    r"Req/Sec\s*" \
    r"(\d*\.*\d*\S*)\s*" \
    r"(\d*\.*\d*\S*)\s*" \
    r"(\d*\.*\d*\S*)\s*" \
    r"(\d*\.*\d*\%)"
REGEX_RPS = r"Requests/sec:\s*" \
            r"(\d*\.*\S*)"
REGEX_BW = r"Transfer/sec:\s*" \
           r"(\d*\.*\S*)"
REGEX_LATENCY_DIST = \
    r"Latency Distribution\n" \
    r"\s*50\%\s*(\d*\.*\d*\D*)\n" \
    r"\s*75\%\s*(\d*\.*\d*\D*)\n" \
    r"\s*90\%\s*(\d*\.*\d*\D*)\n" \
    r"\s*99\%\s*(\d*\.*\d*\D*)\n"

# Split number and multiplicand, e.g. 14.25k --> 14.25 and k
REGEX_NUM = r"(\d*\.*\d*)(\D*)"


def check_wrk(tg_node):
    """Check if wrk is installed on the TG node.

    :param tg_node: Traffic generator node.
    :type tg_node: dict
    :raises: RuntimeError if the given node is not a TG node or if the
        command is not availble.
    """

    if tg_node[u"type"] != NodeType.TG:
        raise RuntimeError(u"Node type is not a TG.")

    cmd = (
        f"{Constants.REMOTE_FW_DIR}/resources/tools/"
        u"wrk/wrk_utils.sh installed"
    )
    exec_cmd_no_error(tg_node, cmd, sudo=True,
                      message=u'WRK is not installed on TG node.')


def run_wrk(tg_node, profile_name, tg_numa, test_type, warm_up=False):
    """Send the traffic as defined in the profile.

    :param tg_node: Traffic generator node.
    :param profile_name: The name of wrk traffic profile.
    :param tg_numa: Numa node on which wrk will run.
    :param test_type: The type of the tests: cps, rps, bw
    :param warm_up: If True, warm-up traffic is generated before test traffic.
    :type profile_name: str
    :type tg_node: dict
    :type tg_numa: int
    :type test_type: str
    :type warm_up: bool
    :returns: Message with measured data.
    :rtype: str
    :raises: RuntimeError if node type is not a TG.
    """

    if tg_node[u"type"] != NodeType.TG:
        raise RuntimeError(u"Node type is not a TG.")

    # Parse and validate the profile
    profile_path = f"resources/traffic_profiles/wrk/{profile_name}.yaml"
    profile = WrkTrafficProfile(profile_path).traffic_profile

    cores = CpuUtils.cpu_list_per_node(tg_node, tg_numa)
    first_cpu = cores[profile[u"first-cpu"]]

    if len(profile[u"urls"]) == 1 and profile[u"cpus"] == 1:
        params = [
            u"traffic_1_url_1_core",
            str(first_cpu),
            str(profile[u"nr-of-threads"]),
            str(profile[u"nr-of-connections"]),
            f"{profile[u'duration']}s",
            f"'{profile[u'header']}'",
            str(profile[u"timeout"]),
            str(profile[u"script"]),
            str(profile[u"latency"]),
            f"'{u' '.join(profile[u'urls'])}'"
        ]
        if warm_up:
            warm_up_params = deepcopy(params)
            warm_up_params[4] = u"10s"
    elif len(profile[u"urls"]) == profile[u"cpus"]:
        params = [
            u"traffic_n_urls_n_cores",
            str(first_cpu),
            str(profile[u"nr-of-threads"]),
            str(profile[u"nr-of-connections"]),
            f"{profile[u'duration']}s",
            f"'{profile[u'header']}'",
            str(profile[u"timeout"]),
            str(profile[u"script"]),
            str(profile[u"latency"]),
            f"'{u' '.join(profile[u'urls'])}'"
        ]
        if warm_up:
            warm_up_params = deepcopy(params)
            warm_up_params[4] = u"10s"
    else:
        params = [
            u"traffic_n_urls_m_cores",
            str(first_cpu),
            str(profile[u"cpus"] // len(profile[u"urls"])),
            str(profile[u"nr-of-threads"]),
            str(profile[u"nr-of-connections"]),
            f"{profile[u'duration']}s",
            f"'{profile[u'header']}'",
            str(profile[u"timeout"]),
            str(profile[u"script"]),
            str(profile[u"latency"]),
            f"'{u' '.join(profile[u'urls'])}'"
        ]
        if warm_up:
            warm_up_params = deepcopy(params)
            warm_up_params[5] = u"10s"

    if warm_up:
        warm_up_params = u" ".join(warm_up_params)
        cmd = (
            f"{Constants.REMOTE_FW_DIR}/resources/tools/wrk/wrk_utils.sh "
            f"{warm_up_params}"
        )
        exec_cmd_no_error(tg_node, cmd, timeout=1800,
                          message=u'wrk runtime error.')
        sleep(60)

    params = u" ".join(params)
    cmd = (
        f"{Constants.REMOTE_FW_DIR}/resources/tools/wrk/wrk_utils.sh {params}"
    )
    stdout, _ = exec_cmd_no_error(tg_node, cmd, timeout=1800,
                                  message=u'wrk runtime error.')

    stats = _parse_wrk_output(stdout)

    log_msg = u"\nMeasured values:\n"
    if test_type == u"cps":
        log_msg += u"Connections/sec: Avg / Stdev / Max  / +/- Stdev\n"
        for item in stats[u"rps-stats-lst"]:
            log_msg += u" / ".join(map(str, item)) + u"\n"
        log_msg += f"Total cps: {stats[u'rps-sum']}cps\n"
    elif test_type == u"rps":
        log_msg += u"Requests/sec: Avg / Stdev / Max  / +/- Stdev\n"
        for item in stats[u"rps-stats-lst"]:
            log_msg += u" / ".join(map(str, item)) + u"\n"
        log_msg += f"Total rps: {stats[u'rps-sum']}rps\n"
    elif test_type == u"bw":
        log_msg += f"Transfer/sec: {stats[u'bw-sum']}Bps"

    logger.info(log_msg)

    return log_msg


def _parse_wrk_output(msg):
    """Parse the wrk stdout with the results.

    :param msg: stdout of wrk.
    :type msg: str
    :returns: Parsed results.
    :rtype: dict
    :raises: WrkError if the message does not include the results.
    """

    if u"Thread Stats" not in msg:
        raise WrkError(u"The output of wrk does not include the results.")

    msg_lst = msg.splitlines(False)

    stats = {
        u"latency-dist-lst": list(),
        u"latency-stats-lst": list(),
        u"rps-stats-lst": list(),
        u"rps-lst": list(),
        u"bw-lst": list(),
        u"rps-sum": 0,
        u"bw-sum": None
    }

    for line in msg_lst:
        if u"Latency Distribution" in line:
            # Latency distribution - 50%, 75%, 90%, 99%
            pass
        elif u"Latency" in line:
            # Latency statistics - Avg, Stdev, Max, +/- Stdev
            pass
        elif u"Req/Sec" in line:
            # rps statistics - Avg, Stdev, Max, +/- Stdev
            stats[u"rps-stats-lst"].append(
                (
                    _evaluate_number(re.search(REGEX_RPS_STATS, line).group(1)),
                    _evaluate_number(re.search(REGEX_RPS_STATS, line).group(2)),
                    _evaluate_number(re.search(REGEX_RPS_STATS, line).group(3)),
                    _evaluate_number(re.search(REGEX_RPS_STATS, line).group(4))
                )
            )
        elif u"Requests/sec:" in line:
            # rps (cps)
            stats[u"rps-lst"].append(
                _evaluate_number(re.search(REGEX_RPS, line).group(1))
            )
        elif u"Transfer/sec:" in line:
            # BW
            stats[u"bw-lst"].append(
                _evaluate_number(re.search(REGEX_BW, line).group(1))
            )

    for item in stats[u"rps-stats-lst"]:
        stats[u"rps-sum"] += item[0]
    stats[u"bw-sum"] = sum(stats[u"bw-lst"])

    return stats


def _evaluate_number(num):
    """Evaluate the numeric value of the number with multiplicands, e.g.:
    12.25k --> 12250

    :param num: Number to evaluate.
    :type num: str
    :returns: Evaluated number.
    :rtype: float
    :raises: WrkError if it is not possible to evaluate the given number.
    """

    val = re.search(REGEX_NUM, num)
    try:
        val_num = float(val.group(1))
    except ValueError:
        raise WrkError(
            u"The output of wrk does not include the results or the format "
            u"of results has changed."
        )
    val_mul = val.group(2).lower()
    if val_mul:
        if u"k" in val_mul:
            val_num *= 1000
        elif u"m" in val_mul:
            val_num *= 1000000
        elif u"g" in val_mul:
            val_num *= 1000000000
        elif u"b" in val_mul:
            pass
        elif u"%" in val_mul:
            pass
        elif u"" in val_mul:
            pass
        else:
            raise WrkError(f"The multiplicand {val_mul} is not defined.")
    return val_num
