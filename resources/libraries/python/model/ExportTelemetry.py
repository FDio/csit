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

"""Module with keywords that publish telemetry events.
"""

import datetime

from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.model.telemetry_item import telemetry_item


def add_telemetry_items(tel_id, tel_type, items, timestamp=None):
    """Add a telemetry record with given items in it.

    User probably needs to interact with telemetry_item class.
    If timestamp is missing, local UTC time is used.

    :param tel_id: Identifier for this telemetry record according to model.
    :param tel_type: Type of this telemetry record according to model.
    :param items: List of data items for this record.
    :param timestamp: Use this time if given.
    :type tel_id: str
    :type tel_type: str
    :type items: Sequence[telemetry_item]
    :type timestamp: Optional[str]
    """
    data = BuiltIn().get_library_instance(
        u"resources.libraries.python.model.export_json"
    )
    telemetry_node = data.get_subdata([u"test", u"telemetry"])
    item_list = [
        {
            u"name": item.name,
            u"value": item.value,
            u"labels": item.labels,
        }
        for item in items
    ]
    if timestamp is None:
        timestamp = str(datetime.datetime.utcnow())
    telemetry_record = {
        u"telemetry-id": str(telemetry_id),
        u"telemetry-type": str(telemetry_type),
        u"timestamp": timestamp,
        u"data": item_list,
    }
    telemetry_node.append(telemetry_record)


def add_single_telemetry_item(
        tel_id, tel_type, name, value, labels, timestamp=None
    ):
    """Add a telemetry record with single value in it.

    Caller does not need to interact with telemetry_item class.
    If timestamp is missing, local UTC time is used.

    :param tel_id: Identifier for this telemetry record according to model.
    :param tel_type: Type of this telemetry recond according to model.
    :param name: Telemetry item quantity name, e.g. "rx_packets".
    :param value: The value of the telemetry item.
    :param labels: Attributes to distinguish from similar items.
    :param timestamp: Use this time if given.
    :type tel_id: str
    :type tel_type: str
    :type name: str
    :type value: Union[str, int, float]
    :type labels: Mapping[str, str]
    :type timestamp: Optional[str]
    """
    item = telemetry_item(name=name, value=value, labels=labels)
    add_telemetry_items(tel_id, tel_type, [item], timestamp)


def export_runtime_counters(host, socket, runtime_nz, timestamp):
    """Add telemetry record for results of querying node counters in runtime.

    :param host: Node "host" attribute, usually its Ipv4 address.
    :param socket: Socket path, VPPs in container will differ by this.
    :param runtime_nz: Object with non-zero-sum counters.
        See VPPCounters.vpp_show_runtime for the internal structure.
    :param timestamp: UTC time just before the counter values were collected.
    :type host: str
    :type socket: str
    :type runtime_nz: List[Mapping[str, Union[str, Sequence[int]]]]
    :type timestamp: str
    """
    tel_id = u"TODO: Distinguish NDR sh run from PDR here."
    tel_type = u"vpp_show_runtime"
    tel_name = u"show_runtime"
    labels = dict(
        host=host,
        socket=socket,
    )
    items = list()
    for node_item in runtime_nz:
        labels[u"graph_node"] = node_item[u"name"]
        for metric in (u"calls", u"clocks", u"suspends", u"vectors"):
            labels[u"metric"] = metric
            value_list = node_item[metric]
            for thread_index, value in value_list:
                labels[u"thread_id"] = thread_index
                # TODO: Detect and add thread name, e.g. vpp_main or vpp_wk_0.
                # TODO: Also detect and add lcore?
                # TODO: Detect and add state ("active", "polling", "any wait").
                items.append(telemetry_item(tel_name, value, labels))
    add_telemetry_items(tel_id, tel_type, items, timestamp)
