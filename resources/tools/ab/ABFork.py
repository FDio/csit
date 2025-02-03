#!/usr/bin/env python3
# Copyright (c) 2023 Intel and/or its affiliates.
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

"""ab fork library."""

from multiprocessing import Pool
import subprocess
import argparse
import re

REGEX_RPS = r"Requests per second:\s*" \
            r"(\d*\.*\S*)"
REGEX_LATENCY = r"Time per request:\s*" \
                r"(\d*\.*\S*)"
REGEX_PROCESS = r"Time per request:\s*" \
                r"(\d*\.*\S*)"
REGEX_TR = r"Transfer rate:\s*" \
           r"(\d*\.*\S*)"
REGEX_TT = r"Total transferred:\s*" \
           r"(\d*)"
REGEX_OK_NUM = r"Complete requests:\s*" \
               r"(\d*)"
REGEX_FAILED_NUM = r"Failed requests:\s*" \
                   r"(\d*)"
REGEX_NUM = r"(\d*\.*\d*)(\D*)"


def main():
    """ main function. get option and run ab test.

    :returns: Nothing.
    """

    # Get option.
    parser = argparse.ArgumentParser(description=u"Get option and run ab test")

    # Number of requests to perform.
    parser.add_argument(u"-r", u"--requests", type=int,
                        required=True, help=u"Number of requests to perform.")

    # Server port number to use.
    parser.add_argument(u"-p", u"--port", type=int, required=True,
                        help=u"Server port number to use.")

    # Number of clients being processed at the same time.
    parser.add_argument(u"-c", u"--clients", type=int, required=True,
                        help=u"Number of clients being processed at "
                             u"the same time.")

    # Filename to be requested from the servers.
    parser.add_argument(u"-f", u"--files", type=str, required=True,
                        help="Filename to be requested from the servers.")

    # Server ip address.
    parser.add_argument(u"-i", u"--ip", type=str, required=True,
                        help=u"Server bind IP address.")

    # Tg ip address.
    parser.add_argument(u"-g", u"--tip", type=str, required=True,
                        help=u"TG bind IP address.")

    # Specify SSL/TLS cipher suite.
    parser.add_argument(u"-z", u"--cipher", type=str, default=u"0",
                        help=u"Specify SSL/TLS cipher.")

    # Specify SSL/TLS protocol.
    parser.add_argument(u"-t", u"--protocol", type=str, default=u"0",
                        help=u"Specify SSL/TLS protocol.")

    # Mode: RPS or CPS.
    parser.add_argument(u"-m", u"--mode", type=str, required=True,
                        help=u"Send requests mode:RPS/CPS.")

    args = parser.parse_args()

    req_num = args.requests
    port = args.port
    cli_num = args.clients
    files = args.files
    ip_address = args.ip
    tg_address = args.tip
    cipher = args.cipher
    protocol = args.protocol
    mode = args.mode

    if req_num == 0:
        print(u"Failed number of req_num!")
        return 1

    # The number of processing units available to the current process.
    _, cpu_num = subprocess.getstatusoutput(u"nproc --all")
    cpu_num = int(cpu_num)
    if cpu_num > 32:
        cpu_num = 32

    # Requests and Clients are evenly distributed on each CPU.
    per_req = round(req_num / cpu_num)
    per_cli = round(cli_num / cpu_num)

    # Revise rounding request, This will be in the first ab request
    all_total = per_req * cpu_num
    per_req_1st = per_req + (req_num - all_total)

    results = []
    # Start process pool.
    pool = Pool(processes=cpu_num)

    for i in range(1, cpu_num + 1):
        results.append(
            pool.apply_async(one, (
                i, per_req_1st if i == 1 else per_req, per_cli, cipher,
                protocol, ip_address, tg_address, files, port, mode)))

    pool.close()
    pool.join()

    info_list = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    # Statistical test results.
    for res in results:
        stats = res.get()
        if stats:
            info_list = [a + b for a, b in zip(info_list, stats)]

    # Output results.
    print(f"Transfer Rate: {round(info_list[6], 2)} [Kbytes/sec]")
    print(f"Latency: {round(info_list[4] / 8, 2)} ms")
    print(f"Connection {mode} rate: {round(info_list[3], 2)} per sec")
    print(f"Total data transferred: {round(info_list[2])} bytes")
    print(f"Completed requests: {round(info_list[0])} ")
    print(f"Failed requests: {round(info_list[1])} ")


def one(cpu, requests, clients, cipher, protocol, ip_addr, tg_addr, files, port,
        mode):
    """Run one test.

    :param cpu: Core number id.
    :param requests: Request number.
    :param clients: Clients number.
    :param cipher: Specify SSL/TLS cipher suite.
    :param protocol: Specify SSL/TLS protocol.
    :param ip_addr: Server ip address.
    :param tg_addr: Tg ip address.
    :param files: Filename to be requested from the servers.
    :param port: Server port.
    :type cpu: int
    :type requests: int
    :type clients: int
    :type cipher: str
    :type protocol: str
    :type ip_addr: str
    :type tg_addr: str
    :type files: str
    :type port: int
    :type mode: str
    :returns: Test results.
    :rtype: list
    """

    cmd = f"sudo -E -S taskset --cpu-list {cpu} ab -n {requests} -c {clients}"
    cmd = f"{cmd} -B {tg_addr} -r "
    if mode == u"rps":
        cmd = f"{cmd} -k"

    if port == 80:
        cmd = f"{cmd} http://{ip_addr}:{port}/{files}"
    else:
        cmd = f"{cmd} -Z {cipher} -f {protocol}"
        cmd = f"{cmd} https://{ip_addr}:{port}/{files}"

    _, output = subprocess.getstatusoutput(cmd)
    ret = _parse_output(output)

    return ret


def _parse_output(msg):
    """Parse the stdout with the results.

    :param msg: stdout of ab.
    :type msg: str
    :returns: Parsed results.
    :rtype: list
    """

    msg_lst = msg.splitlines(False)

    stats = []
    for line in msg_lst:
        if u"Requests per second" in line:
            stats.append(
                _float_number(re.search(REGEX_RPS, line).group(1))
            )
        elif u"Time per request" in line:
            stats.append(
                _float_number(re.search(REGEX_LATENCY, line).group(1))
            )
        elif u"Transfer rate" in line:
            stats.append(
                _float_number(re.search(REGEX_TR, line).group(1))
            )
        elif u"Total transferred" in line:
            stats.append(
                _float_number(re.search(REGEX_TT, line).group(1))
            )
        elif u"Complete requests" in line:
            stats.append(
                _float_number(re.search(REGEX_OK_NUM, line).group(1))
            )
        elif u"Failed requests" in line:
            stats.append(
                _float_number(re.search(REGEX_FAILED_NUM, line).group(1))
            )

    return stats


def _float_number(num):
    """float value of the number.

    :param num: Number to evaluate.
    :type num: str
    :returns: float number.
    :rtype: float
    """

    val = re.search(REGEX_NUM, num)
    try:
        val_num = float(val.group(1))
    except ValueError:
        raise RuntimeError(u"The output of ab does not include the results.")
    return val_num


if __name__ == "__main__":
    main()
