# Copyright (c) 2021 Cisco and/or its affiliates.
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

"""Module with keywords that publish metric and other log events.
"""

import datetime

from resources.libraries.python.model.util import get_export_data


def export_ssh_command(host, port, command):
    """Add a log item about SSH command execution starting.

    The log item is present only in raw output.
    Result arrives in a separate log item.
    Log level is always DEBUG.

    The command is stored as "data" (not "msg") as in some cases
    the command can be too long to act as a message.

    The host is added to the info set of hosts.

    :param host: Node "host" attribute, usually its IPv4 address.
    :param port: SSH port number to use when connecting to the host.
    :param command: Serialized bash command to execute.
    :type host: str
    :type port: int
    :type command: str
    """
    timestamp = datetime.datetime.utcnow().strftime(u"%Y-%m-%dT%H:%M:%S.%fZ")
    data = get_export_data()
    ssh_record = dict(
        source_type=u"host,port",
        source_id=dict(host=host, port=port),
        msg_type=u"ssh_command",
        log_level=u"DEBUG",
        timestamp=timestamp,
        msg="",
        data=str(command),
    )
    data[u"hosts"].add(host)
    data[u"log"].append(ssh_record)


def export_ssh_result(host, port, code, stdout, stderr, duration):
    """Add a log item about ssh execution result.

    Only for raw output log.

    There is no easy way to pair with the corresponding command,
    but usually there is only one SSH session for given host and port.
    The duration value may give a hint if that is not the case.

    Message is empty, data has fields "rc", "stdout", "stderr" and "duration".
    Log level is always DEBUG.

    The host is NOT added to the info set of hosts, as each result
    comes after a command.

    TODO: Do not require duration, find preceding ssh command in log.
    Reason: Pylint complains about too many arguments.
    Alternative: Define type for SSH endopoint (and use that instead host+port).

    :param host: Node "host" attribute, usually its IPv4 address.
    :param port: SSH port number to use when connecting to the host.
    :param code: Bash return code, e.g. 0 for success.
    :param stdout: Captured standard output of the command execution.
    :param stderr: Captured error output of the command execution.
    :param duration: How long has the command been executing, in seconds.
    :type host: str
    :type port: int
    :type code: int
    :type stdout: str
    :type stderr: str
    :type duration: float
    """
    timestamp = datetime.datetime.utcnow().strftime(u"%Y-%m-%dT%H:%M:%S.%fZ")
    data = get_export_data()
    ssh_record = dict(
        source_type=u"host,port",
        source_id=dict(host=host, port=port),
        msg_type=u"ssh_result",
        log_level=u"DEBUG",
        timestamp=timestamp,
        msg=u"",
        data=dict(
            rc=int(code),
            stdout=str(stdout),
            stderr=str(stderr),
            duration=float(duration),
        ),
    )
    data[u"log"].append(ssh_record)


def export_ssh_timeout(host, port, stdout, stderr, duration):
    """Add a log item about ssh execution timing out.

    Only for debug log.

    There is no easy way to pair with the corresponding command,
    but usually there is only one SSH session for given host and port.

    Message is empty, data has fields "stdout", "stderr" and "duration".
    The duration value may give a hint if that is not the case.
    Log level is always DEBUG.

    The host is NOT added to the info set of hosts, as each timeout
    comes after a command.

    :param host: Node "host" attribute, usually its IPv4 address.
    :param port: SSH port number to use when connecting to the host.
    :param stdout: Captured standard output of the command execution so far.
    :param stderr: Captured error output of the command execution so far.
    :param duration: How long has the command been executing, in seconds.
    :type host: str
    :type port: int
    :type stdout: str
    :type stderr: str
    :type duration: float
    """
    timestamp = datetime.datetime.utcnow().strftime(u"%Y-%m-%dT%H:%M:%S.%fZ")
    data = get_export_data()
    ssh_record = dict(
        source_type=u"host,port",
        source_id=dict(host=host, port=port),
        msg_type=u"ssh_timeout",
        log_level=u"DEBUG",
        timestamp=timestamp,
        msg=u"",
        data=dict(
            stdout=str(stdout),
            stderr=str(stderr),
            duration=float(duration),
        ),
    )
    data[u"log"].append(ssh_record)
