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

from resources.libraries.python.model.metric_item import metric_item
from resources.libraries.python.model.util import get_export_data


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
    data = get_export_data()
    if data is None:
        return
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
    data[u"log"].append(metric_record)


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


def export_runtime_counters(host, socket, trial_type, runtime_nz, timestamp):
    """Add telemetry record for results of querying node counters in runtime.

    :param host: Node "host" attribute, usually its IPv4 address.
    :param socket: Socket path, VPPs in container will differ by this.
    :param runtime_nz: Object with non-zero-sum counters.
        See VPPCounters.vpp_show_runtime for the internal structure.
    :param trial_type: Description to distinguish from other runtime results.
    :param timestamp: UTC time just before the counter values were collected.
    :type host: str
    :type socket: str
    :type trial_type: str
    :type runtime_nz: List[Mapping[str, Union[str, Sequence[int]]]]
    :type timestamp: str
    """
    source_type = u"node,socket"
    source_id = f"{host},{socket}"
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
