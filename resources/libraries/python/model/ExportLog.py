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

from resources.libraries.python.model.metric_item import metric_item
from resources.libraries.python.model.util import get_export_data
from resources.libraries.python.time_measurement import datetime_utc_str as now


# TODO: Split into ExportLogMetric and ExportLogPapi?


def add_metric_items(
        source_type, source_id, msg, items, timestamp, log_level=u"INFO"
    ):
    """Add a metric record with given items in it.

    User probably needs to interact with metric_item class
    to create metric items.

    :param source_type: Identifier for metric source type, e.g. "node".
    :param source_id: Identifier for instanse of the given type, e.g. "dut1".
    :param msg: Further identifier, e.g. "show-runtime".
    :param items: List of metric items for this log record.
    :param timestamp: Use this time. Required.
        TODO: If it has to be sequential, use current now() instead.
    :param log_level: Level of importance, as in robot.api.logger.
    :type source_type: str
    :type source_id: str
    :type msg: str
    :type items: Sequence[metric_item]
    :type timestamp: str
    :type log_level: str
    """
    item_list = [
        {
            u"name": item.name,
            u"value": item.value,
            u"labels": item.labels,
        }
        for item in items
    ]
    metric_record = {
        u"source": {
            u"source-type": str(source_type),
            u"source-id": str(source_id),
        },
        u"msg-type": u"metric",
        u"log-level": str(log_level),
        u"timestamp": str(timestamp),
        u"msg": str(msg),
        u"data": item_list,
    }
    get_export_data()[u"log"].append(metric_record)


def add_single_metric_item(
        source_type, source_id, msg, name, value, labels, timestamp,
        log_level=u"INFO"
    ):
    """Add a telemetry record with a single value in it.

    Caller does not need to interact with telemetry_item class.
    If timestamp is missing, local UTC time is used.

    :param source_type: Identifier for metric source type, e.g. "node".
    :param source_id: Identifier for instanse of the given type, e.g. "dut1".
    :param msg: Further identifier, e.g. "show-runtime".
    :param name: Telemetry item quantity name, e.g. "rx_packets".
    :param value: The value of the telemetry item.
    :param labels: Attributes to distinguish from similar items.
    :param timestamp: Use this time. Required.
        TODO: If it has to be sequential, use current now() instead.
    :param log_level: Level of importance, as in robot.api.logger.
    :type source_type: str
    :type source_id: str
    :type msg: str
    :type name: str
    :type value: Union[int, float]
    :type labels: Mapping[str, str]
    :type timestamp: str
    :type log_level: str
    """
    item = metric_item(name=name, value=value, labels=labels)
    add_metric_items(source_type, source_id, msg, [item], timestamp, log_level)


def export_runtime_counters(
        host, port, socket, trial_type, runtime_nz, timestamp
    ):
    """Add telemetry record for results of querying node counters in runtime.

    :param host: Node "host" attribute, usually its IPv4 address.
    :param port: SSH port number to use when connecting to the host.
    :param socket: Socket path, VPPs in container will differ by this.
    :param runtime_nz: Object with non-zero-sum counters.
        See VPPCounters.vpp_show_runtime for the internal structure.
    :param trial_type: Description to distinguish from other runtime results.
    :param timestamp: UTC time just before the counter values were collected.
    :type host: str
    :type port: int
    :type socket: str
    :type trial_type: str
    :type runtime_nz: List[Mapping[str, Union[str, Sequence[int]]]]
    :type timestamp: str
    """
    source_type = u"host,port,socket"
    source_id = f"{host},{port},{socket}"
    msg = f"show-running for {trial_type}"
    labels = dict(
        host=host,
        socket=socket,
    )
    items = list()
    for node_item in runtime_nz:
        labels[u"graph_node"] = node_item[u"name"]
        for name in (u"calls", u"clocks", u"suspends", u"vectors"):
            value_list = node_item[name]
            for thread_index, value in enumerate(value_list):
                labels[u"thread_id"] = str(thread_index)
                # TODO: Detect and add thread name, e.g. vpp_main or vpp_wk_0.
                # TODO: Also detect and add lcore?
                # TODO: Detect and add state ("active", "polling", "any wait").
                items.append(metric_item(name, value, labels))
    add_metric_items(source_type, source_id, msg, items, timestamp)


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
    papi_record = {
        u"source": {
            u"source-type": u"host,port,socket",
            u"source-id": f"{host},{port},{socket}",
        },
        u"msg-type": u"papi-command",
        u"log-level": u"INFO",
        u"timestamp": now() if timestamp is None else str(timestamp),
        u"msg": str(cmd_name),
        u"data": deepcopy(cmd_args),
    }
    get_export_data()[u"log"].append(papi_record)


def export_papi_command_context(host, port, socket, context, timestamp=None):
    """Add a log item about PAPI command context number.

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
    papi_record = {
        u"source": {
            u"source-type": u"host,port,socket",
            u"source-id": f"{host},{port},{socket}",
        },
        u"msg-type": u"papi-context",
        u"log-level": u"DEBUG",
        u"timestamp": now() if timestamp is None else str(timestamp),
        u"msg": str(context),
    }
    get_export_data()[u"log"].append(papi_record)


def export_papi_replies(
        host, port, socket, context, replies, timestamp=None
    ):
    """Add a log item about PAPI replies.

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
    papi_record = {
        u"source": {
            u"source-type": u"host,port,socket",
            u"source-id": f"{host},{port},{socket}",
        },
        u"msg-type": u"papi-replies",
        u"log-level": u"DEBUG",
        u"timestamp": now() if timestamp is None else str(timestamp),
        u"msg": f"replies for context {context}",
        u"data": [deepcopy(item) for item in replies],
    }
    get_export_data()[u"log"].append(papi_record)
