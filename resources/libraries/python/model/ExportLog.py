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

from copy import deepcopy

from resources.libraries.python.model.util import get_export_data, descend
from resources.libraries.python.time_measurement import timestamp_or_now


# TODO: Split into ExportLogMetric and ExportLogPapi?

def export_papi_command_sent(
        host, port, socket, cmd_name, cmd_args, timestamp=None
    ):
    """Add a log item about PAPI command execution staring.

    Replies arrive in a separate log item.
    PAPI context number is not known before sending starts,
    and it may block.

    Timestamp marks time just before sending starts.
    Current time is used if timestamp is missing.
    Log level is always INFO.
    Args are deep-copied to make sure the values logged here
    are not affected by any further manipulation from the caller.

    The host is added to the info set of hosts.

    :param host: Node "host" attribute, usually its IPv4 address.
    :param port: SSH port number to use when connecting to the host.
    :param socket: Socket path, VPPs in container will differ by this.
    :param cmd_name: Name of the command message being sent.
    :param cmd_args: Arguments of the command message.
    :param timestamp: Local UTC time just before sending.
    :type host: str
    :type port: int
    :type socket: str
    :type cmd_name: str
    :type cmd_args: Mapping[str, object]
    :type timestamp: Optional[str]
    """
    debug_data, info_data = get_export_data()
    papi_record = dict(
        source_type=u"host,port,socket",
        source_id=dict(host=host, port=port, socket=socket),
        msg_type=u"papi_command",
        log_level=u"INFO",
        timestamp=timestamp_or_now(timestamp),
        msg=str(cmd_name),
        data=deepcopy(cmd_args),
    )
    debug_data[u"log"].append(papi_record)
    info_data[u"log"].append(papi_record)
    hosts_node = descend(info_data, u"hosts", set())
    hosts_node.add(host)


def export_papi_command_context(host, port, socket, context, timestamp=None):
    """Add a log item about PAPI command context number.

    Only for debug log.

    For sync calls, this event happens just before reply event.
    For async calls, this event happens just after command sent event.
    In either case, the context number is related to the command sent,
    appearing in the log immediately before this event,
    regardless of timestamp.

    The context number may be needed to identify which async replies
    are caused by the last command.
    Also, a big jump in the context number signifies
    we stopped PAPI logging for a while, e.g. for large scale tests
    where the data is repetitious and the number of events is huge.

    Timestamp marks time just after sending unblocked.
    Current time is used if timestamp is missing.
    Log level is always DEBUG.

    The host is NOT added to the info set of hosts, as each context
    comes after a command.

    :param host: Node "host" attribute, usually its IPv4 address.
    :param port: SSH port number to use when connecting to the host.
    :param socket: Socket path, VPPs in container will differ by this.
    :param context: A number identifier assigned by PAPI library.
    :param timestamp: Local UTC time just after sending.
    :type host: str
    :type port: int
    :type socket: str
    :type context: int
    :type timestamp: Optional[str]
    """
    debug_data, _ = get_export_data()
    papi_record = dict(
        source_type=u"host,port,socket",
        source_id=dict(host=host, port=port, socket=socket),
        msg_type=u"papi_context",
        log_level=u"DEBUG",
        timestamp=timestamp_or_now(timestamp),
        msg=u"",
        data=context,
    )
    debug_data[u"log"].append(papi_record)


def export_papi_replies(
        host, port, socket, context, replies, timestamp=None
    ):
    """Add a log item about PAPI replies.

    Only for debug log.

    This is intended for sync calls, which unblock after receiving
    all the replies needed.
    For async calls, separate event will be added.

    The context number is refers to the corresponding command sent,
    appearing in the log somewhere before this event.

    Timestamp marks time just after all replies are gathered.
    Current time is used if timestamp is missing.
    Log level is always DEBUG.
    Replies are deep-copied to make sure the values logged here
    are not affected by any further processing in the caller.

    The host is NOT added to the info set of hosts, as each reply
    comes after a command.

    :param host: Node "host" attribute, usually its IPv4 address.
    :param port: SSH port number to use when connecting to the host.
    :param socket: Socket path, VPPs in container will differ by this.
    :param context: A number identifier assigned by PAPI library.
    :param replies: Unprocessed response objects as returned by PAPI library.
    :param timestamp: Local UTC time just before sending.
    :type host: str
    :type port: int
    :type socket: str
    :type context: int
    :type replies: Sequence[Mapping[str, object]]
    :type timestamp: Optional[str]
    """
    debug_data, _ = get_export_data()
    papi_record = dict(
        source_type=u"host,port,socket",
        source_id=dict(host=host, port=port, socket=socket),
        msg_type=u"papi_replies",
        log_level=u"DEBUG",
        timestamp=timestamp_or_now(timestamp),
        msg=f"replies for context {context}",
        data=[deepcopy(item) for item in replies],
    )
    debug_data[u"log"].append(papi_record)


def export_ssh_command(
        host, port, command, timestamp=None
    ):
    """Add a log item about SSH command execution staring.

    Only for debug log.
    Result arrives in a separate log item.

    Timestamp marks time just before sending starts.
    Current time is used if timestamp is missing.
    Log level is always DEBUG.
    Command is converted to string to make sure the value logged here
    are not affected by any further manipulation from the caller.

    The command is stored as "data" (not "msg") as in some cases
    the command can be too long to act as a message.

    The host is added to the info set of hosts.

    :param host: Node "host" attribute, usually its IPv4 address.
    :param port: SSH port number to use when connecting to the host.
    :param command: Serialized bash command to execute.
    :param timestamp: Local UTC time just before sending.
    :type host: str
    :type port: int
    :type command: str
    :type timestamp: Optional[str]
    """
    debug_data, info_data = get_export_data()
    ssh_record = dict(
        source_type=u"host,port",
        source_id=dict(host=host, port=port),
        msg_type=u"ssh_command",
        log_level=u"DEBUG",
        timestamp=timestamp_or_now(timestamp),
        msg="",
        data=str(command),
    )
    debug_data[u"log"].append(ssh_record)
    hosts_node = descend(info_data, u"hosts", set())
    hosts_node.add(host)


def export_ssh_result(
        host, port, code, stdout, stderr, duration, timestamp=None
    ):
    """Add a log item about ssh execution result.

    Only for debug log.

    There is no easy way to pair with the corresponding command,
    but usually there is only one SSH session for given host and port.
    The duration value may give a hint if that is not the case.

    Message is empty, data has fields "rc", "stdout", "stderr" and "duration".

    Timestamp marks time just after command execution finished.
    Current time is used if timestamp is missing.
    Log level is always DEBUG.

    The host is NOT added to the info set of hosts, as each result
    comes after a command.

    :param host: Node "host" attribute, usually its IPv4 address.
    :param port: SSH port number to use when connecting to the host.
    :param code: Bash return code, e.g. 0 for success.
    :param stdout: Captured standard output of the command execution.
    :param stderr: Captured error output of the command execution.
    :param duration: How long has the command been executing, in seconds.
    :param timestamp: Local UTC time just after command returned.
    :type host: str
    :type port: int
    :type code: int
    :type stdout: str
    :type stderr: str
    :type duration: float
    :type timestamp: Optional[str]
    """
    debug_data, _ = get_export_data()
    papi_record = dict(
        source_type=u"host,port",
        source_id=dict(host=host, port=port),
        msg_type=u"ssh_result",
        log_level=u"DEBUG",
        timestamp=timestamp_or_now(timestamp),
        msg=u"",
        data=dict(
            rc=int(code),
            stdout=str(stdout),
            stderr=str(stderr),
            duration=float(duration),
        ),
    )
    debug_data[u"log"].append(papi_record)


def export_ssh_timeout(
        host, port, stdout, stderr, duration, timestamp=None
    ):
    """Add a log item about ssh execution timing out.

    Only for debug log.

    There is no easy way to pair with the corresponding command,
    but usually there is only one SSH session for given host and port.

    Message is empty, data has fields "stdout", "stderr" and "duration".
    The duration value may give a hint if that is not the case.

    Timestamp marks time just after command execution overstepped its timeout.
    Current time is used if timestamp is missing.
    Log level is always DEBUG.

    The host is NOT added to the info set of hosts, as each timeout
    comes after a command.

    :param host: Node "host" attribute, usually its IPv4 address.
    :param port: SSH port number to use when connecting to the host.
    :param stdout: Captured standard output of the command execution so far.
    :param stderr: Captured error output of the command execution so far.
    :param duration: How long has the command been executing, in seconds.
    :param timestamp: Local UTC time just before sending.
    :type host: str
    :type port: int
    :type stdout: str
    :type stderr: str
    :type duration: float
    :type timestamp: Optional[str]
    """
    debug_data, _ = get_export_data()
    papi_record = dict(
        source_type=u"host,port",
        source_id=dict(host=host, port=port),
        msg_type=u"ssh_timeout",
        log_level=u"DEBUG",
        timestamp=timestamp_or_now(timestamp),
        msg=u"",
        data=dict(
            stdout=str(stdout),
            stderr=str(stderr),
            duration=float(duration),
        ),
    )
    debug_data[u"log"].append(papi_record)
