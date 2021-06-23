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

from robot.api import logger

from resources.libraries.python.model.util import get_export_data
from resources.libraries.python.model.telemetry import split_telemetry_text
from resources.libraries.python.time_measurement import datetime_utc_str as now


# TODO: Split into ExportLogMetric and ExportLogPapi?

def export_papi_command_sent(
        host, port, socket, cmd_name, cmd_args, timestamp=None
    ):
    """Add a log item about PAPI command execution staring.

    No-op outside test case (e.g. in suite setup).

    Replies arrive in a separate log item.
    PAPI context number is not known before sending starts,
    and it may block.

    Timestamp marks time just before sending starts.
    Current time is used if timestamp is missing.
    Log level is always INFO.
    Args are deep-copied to make sure the values logged here
    are not affected by any further manipulation from the caller.

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
    data = get_export_data()
    if data is None:
        return
    papi_record = dict(
        source_type=u"host,port,socket",
        source_id=f"{host},{port},{socket}",
        msg_type=u"papi_command",
        log_level=u"INFO",
        timestamp=now() if timestamp is None else str(timestamp),
        msg=str(cmd_name),
        data=deepcopy(cmd_args),
    )
    data[u"log"].append(papi_record)


def export_papi_command_context(host, port, socket, context, timestamp=None):
    """Add a log item about PAPI command context number.

    No-op outside test case (e.g. in suite setup).

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
    data = get_export_data()
    if data is None:
        return
    papi_record = dict(
        source_type=u"host,port,socket",
        source_id=f"{host},{port},{socket}",
        msg_type=u"papi_context",
        log_level=u"DEBUG",
        timestamp=now() if timestamp is None else str(timestamp),
        msg=u"",
        data=context,
    )
    data[u"log"].append(papi_record)


def export_papi_replies(
        host, port, socket, context, replies, timestamp=None
    ):
    """Add a log item about PAPI replies.

    No-op outside test case (e.g. in suite setup).

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
    data = get_export_data()
    if data is None:
        return
    papi_record = dict(
        source_type=u"host,port,socket",
        source_id=f"{host},{port},{socket}",
        msg_type=u"papi_replies",
        log_level=u"DEBUG",
        timestamp=now() if timestamp is None else str(timestamp),
        msg=f"replies for context {context}",
        data=[deepcopy(item) for item in replies],
    )
    data[u"log"].append(papi_record)


def export_ssh_command(
        host, port, command, timestamp=None
    ):
    """Add a log item about SSH command execution staring.

    No-op outside test case (e.g. in suite setup).

    Result arrives in a separate log item.

    Timestamp marks time just before sending starts.
    Current time is used if timestamp is missing.
    Log level is always DEBUG.
    Command is converted to string to make sure the value logged here
    are not affected by any further manipulation from the caller.

    The command is stored as "data" (not "msg") as in some cases
    the command can be too long to act as a message.

    :param host: Node "host" attribute, usually its IPv4 address.
    :param port: SSH port number to use when connecting to the host.
    :param command: Serialized bash command to execute.
    :param timestamp: Local UTC time just before sending.
    :type host: str
    :type port: int
    :type command: str
    :type timestamp: Optional[str]
    """
    data = get_export_data()
    if data is None:
        return
    ssh_record = dict(
        source_type=u"host,port",
        source_id=f"{host},{port}",
        msg_type=u"ssh_command",
        log_level=u"DEBUG",
        timestamp=now() if timestamp is None else str(timestamp),
        msg="",
        data=str(command),
    )
    data[u"log"].append(ssh_record)


def export_ssh_result(
        host, port, code, stdout, stderr, duration, timestamp=None
    ):
    """Add a log item about ssh execution result.

    No-op outside test case (e.g. in suite setup).

    There is no easy way to pair with the corresponding command,
    but usually there is only one SSH session for given host and port.
    The duration value may give a hint if that is not the case.

    Message is empty, data has fields "rc", "stdout", "stderr" and "duration".

    Timestamp marks time just after command execution finished.
    Current time is used if timestamp is missing.
    Log level is always DEBUG.

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
    data = get_export_data()
    if data is None:
        return
    papi_record = dict(
        source_type=u"host,port",
        source_id=f"{host},{port}",
        msg_type=u"ssh_result",
        log_level=u"DEBUG",
        timestamp=now() if timestamp is None else str(timestamp),
        msg=u"",
        data=dict(
            rc=int(code),
            stdout=str(stdout),
            stderr=str(stderr),
            duration=float(duration),
        ),
    )
    data[u"log"].append(papi_record)


def export_ssh_timeout(
        host, port, stdout, stderr, duration, timestamp=None
    ):
    """Add a log item about ssh execution timing out.

    No-op outside test case (e.g. in suite setup).

    There is no easy way to pair with the corresponding command,
    but usually there is only one SSH session for given host and port.

    Message is empty, data has fields "stdout", "stderr" and "duration".
    The duration value may give a hint if that is not the case.

    Timestamp marks time just after command execution overstepped its timeout.
    Current time is used if timestamp is missing.
    Log level is always DEBUG.

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
    data = get_export_data()
    if data is None:
        return
    papi_record = dict(
        source_type=u"host,port",
        source_id=f"{host},{port}",
        msg_type=u"ssh_timeout",
        log_level=u"DEBUG",
        timestamp=now() if timestamp is None else str(timestamp),
        msg=u"",
        data=dict(
            stdout=str(stdout),
            stderr=str(stderr),
            duration=float(duration),
        ),
    )
    data[u"log"].append(papi_record)


def export_mlrsearch_debug(message, timestamp=None):
    """Add a log item with debug messages from MLRsearch.

    No-op outside test case (e.g. in suite setup).
    Message is put as message, data is an empty string.

    Timestamp marks time when MLRsearch thinks the message applies.
    Current time is used if timestamp is missing.
    Log level is always DEBUG.

    :param message: Text to log.
    :param timestamp: Local UTC time just before sending.
    :type message: str
    :type timestamp: Optional[str]
    """
    data = get_export_data()
    if data is None:
        return
    mlrsearch_record = dict(
        source_type=u"search_algorithm",
        source_id=u"mlrsearch",
        msg_type=u"mlrsearch_debug",
        log_level=u"DEBUG",
        timestamp=now() if timestamp is None else str(timestamp),
        msg=str(message),
        data=u"",
    )
    data[u"log"].append(mlrsearch_record)


def export_plrsearch_by_level(level, message, timestamp=None):
    """Add a log item with a message from PLRsearch.

    No-op outside test case (e.g. in suite setup).
    Message is put as message, data is an empty string.

    Timestamp marks time when PLRsearch thinks the message applies.
    Current time is used if timestamp is missing.
    Log level is transormed to smaller range.

    The record puts the original level value into "message" field,
    and the actual message into "data" field,
    as on some levels the messages are quite long.

    :param level: Text to indicate PLRsearch logging level.
    :param message: Text to log.
    :param timestamp: Local UTC time just before sending.
    :type level: str
    :type message: str
    :type timestamp: Optional[str]
    """
    data = get_export_data()
    if data is None:
        return
    plr_level = level.lower()
    log_level = u"INFO" if plr_level in (u"error", u"info") else u"DEBUG"
    mlrsearch_record = dict(
        source_type=u"search_algorithm",
        source_id=u"plrsearch",
        msg_type=f"plrsearch_{plr_level}",
        log_level=log_level,
        timestamp=now() if timestamp is None else str(timestamp),
        msg=f"original level: {level}",
        data=str(message),
    )
    data[u"log"].append(mlrsearch_record)


def export_telemetry(host, port, socket, message, text, timestamp=None):
    """Add a log item with collection of metrics.

    No-op outside test case (e.g. in suite setup).
    Message is put as message, data is an empty string.

    Timestamp marks time when all metrics were done gathering.
    Current time is used if timestamp is missing.
    Log level is always DEBUG.

    Argument "message" can be used to distinguish metric when
    they are gathered multiple times within a test case, e.g. "teardown".

    Multiple log events are exported, one for each openmetric block.

    :param host: Node "host" attribute, usually its IPv4 address.
    :param port: SSH port number to use when connecting to the host.
    :param socket: Socket path, VPPs in container will differ by this.
    :param message: Additional info on circumstances of the metric.
    :param text: Textual form of the metric data to export.
    :param timestamp: Local UTC time just before sending.
    :type host: str
    :type port: int
    :type socket: str
    :type message: str
    :type text: str
    :type timestamp: Optional[str]
    """
    data = get_export_data()
    if data is None:
        return
    timestamp = now() if timestamp is None else str(timestamp)
    for block in split_telemetry_text(text):
        name = block.split(u" ", 3)[2]
        telemetry_record = dict(
            source_type=u"host,port,socket",
            source_id=f"{host},{port},{socket}",
            msg_type=u"metric",
            log_level=u"INFO",
            timestamp=timestamp,
            msg=f"{message} {name}",
            data=block,
        )
        data[u"log"].append(telemetry_record)
