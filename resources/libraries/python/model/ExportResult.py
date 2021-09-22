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

"""Module with keywords that publish parts of result structure.
"""

from resources.libraries.python.jumpavg.AvgStdevStats import AvgStdevStats
from resources.libraries.python.model.util import descend, get_export_data


def export_vpp_version(version):
    """Export the argument as sut_version.

    Sets suit_type to "VPP".

    :param version: VPP version as returned by PAPI.
    :type version: str
    """
    version = str(version)
    debug_data, info_data = get_export_data()
    debug_data[u"sut_type"] = u"VPP"
    info_data[u"sut_type"] = u"VPP"
    debug_data[u"sut_version"] = version
    info_data[u"sut_version"] = version


def append_mrr_value(mrr_value):
    """Store mrr value to proper place so it is dumped into json.

    The inner node "value" may or may not exist before calling this.
    Test type is not overwritten here, but when setting unit.

    :param mrr_value: Forwarding rate from MRR trial, unit specified elsewhere.
    :type mrr_value: float
    """
    debug_data, info_data = get_export_data()
    debug_results_node = debug_data[u"results"]
    samples = descend(debug_results_node, u"samples", list())
    samples.append(float(mrr_value))
    info_results_node = info_data[u"results"]
    samples = descend(info_results_node, u"samples", list())
    samples.append(float(mrr_value))
    # Stats are derived quantity, so for info only.
    # TODO: Implement incremental udates.
    # That means storing stats somewhere json does not export.
    stats = AvgStdevStats.for_runs(samples)
    info_results_node[u"avg"] = stats.avg
    info_results_node[u"stdev"] = stats.stdev


def export_mrr_unit(unit):
    """Store MRR unit so it is dumped into json.

    If a previous value exists, it is overwritten silently.
    test type is set (overwritten) to MRR.

    :param unit: Unit of MRR forwarding rate, either cps or pps.
    :type unit: str
    """
    unit = str(unit)
    debug_data, info_data = get_export_data()
    debug_data[u"test_type"] = u"MRR"
    info_data[u"test_type"] = u"MRR"
    debug_data[u"results"][u"unit"] = unit
    info_data[u"results"][u"unit"] = unit


def export_search_bound(text, value, bandwidth=None):
    """Store bound value and unit.

    This function works for both NDRPDR and SOAK, decided by text.
    If bandwidth is not given, unit is assumed to be cps, otherwise pps.

    If "throughput" (or "critical_rate") node does not exist, it is created.
    If a previous value exists, it is overwritten silently.
    Test type is set (overwritten) to NDRPDR (or SOAK).

    Text is used to determine whether it is ndr or pdr, upper or lower bound,
    as the Robot caller has the information only there.

    :param text: Info from Robot caller to determime bound type.
    :param value: The bound value in packets (or connections) per second.
    :param bandwidth: The same value recomputed into L1 gigabits per second.
        None means value is cps.
    :type text: str
    :type value: float
    :type bandwidth: Optional[float]
    """
    value = float(value)
    text = str(text).lower()
    test_type = u"SOAK" if u"plrsearch" in text else u"NDRPDR"
    upper_or_lower = u"upper" if u"upper" in text else u"lower"
    ndr_or_pdr = u"ndr" if u"ndr" in text else u"pdr"
    rate_name = u"throughput" if test_type == u"NDRPDR" else u"critical_rate"
    unit = u"cps" if bandwidth is None else u"pps"

    debug_data, info_data = get_export_data()
    debug_data[u"test_type"] = test_type
    info_data[u"test_type"] = test_type
    debug_results_node = debug_data[u"results"]
    info_results_node = info_data[u"results"]
    debug_rate_node = descend(debug_results_node, rate_name)
    info_rate_node = descend(info_results_node, rate_name)
    debug_rate_node[u"unit"] = unit
    info_rate_node[u"unit"] = unit
    if test_type == u"SOAK":
        debug_rate_node[upper_or_lower] = value
        info_rate_node[upper_or_lower] = value
        # TODO: Support Gbps values for SOAK?
        return
    debug_ndrpdr_node = descend(debug_rate_node, ndr_or_pdr)
    info_ndrpdr_node = descend(info_rate_node, ndr_or_pdr)
    debug_value_node = descend(debug_ndrpdr_node, u"value")
    info_value_node = descend(info_ndrpdr_node, u"value")
    debug_value_node[upper_or_lower] = value
    info_value_node[upper_or_lower] = value
    if bandwidth is None:
        return
    bandwidth = float(bandwidth)
    debug_value_gbps_node = descend(debug_ndrpdr_node, u"value_gbps")
    info_value_gbps_node = descend(info_ndrpdr_node, u"value_gbps")
    debug_value_gbps_node[upper_or_lower] = bandwidth
    info_value_gbps_node[upper_or_lower] = bandwidth


def export_ndrpdr_latency(text, latency):
    """Store NDRPDR hdrh latency data.

    If "latency" node does not exist, it is created.
    If a previous value exists, it is overwritten silently.

    Text is used to determine what percentage of PDR is the load,
    as the Robot caller has the information only there.

    Reverse data may be missing, we assume the test was unidirectional.

    TODO: Do not export -1/-1/-1/ value?

    :param text: Info from Robot caller to determime load.
    :param latency: Output from TRex utility, min/avg/max/hdrh.
    :type text: str
    :type latency: 1-tuple or 2-tuple of str
    """
    debug_data, info_data = get_export_data()
    debug_results_node = debug_data[u"results"]
    info_results_node = info_data[u"results"]
    debug_latency_node = descend(debug_results_node, u"latency")
    info_latency_node = descend(info_results_node, u"latency")
    percent = 0
    if u"90" in text:
        percent = 90
    elif u"50" in text:
        percent = 50
    elif u"10" in text:
        percent = 10
    node_name = f"pdr_{percent}"
    debug_forward_node = descend(debug_latency_node, u"forward")
    info_forward_node = descend(info_latency_node, u"forward")
    debug_percent_node = descend(debug_forward_node, node_name)
    info_percent_node = descend(info_forward_node, node_name)
    l_min, l_avg, l_max, l_hdrh = latency[0].split(u"/", 3)
    l_min, l_avg, l_max = float(l_min), float(l_avg), float(l_max)
    debug_percent_node[u"min"] = l_min
    info_percent_node[u"min"] = l_min
    debug_percent_node[u"avg"] = l_avg
    info_percent_node[u"avg"] = l_avg
    debug_percent_node[u"max"] = l_max
    info_percent_node[u"max"] = l_max
    debug_percent_node[u"hdrd"] = l_hdrh
    info_percent_node[u"hdrd"] = l_hdrh
    if len(latency) < 2:
        return
    debug_reverse_node = descend(debug_latency_node, u"reverse")
    info_reverse_node = descend(info_latency_node, u"reverse")
    debug_percent_node = descend(debug_reverse_node, node_name)
    info_percent_node = descend(info_reverse_node, node_name)
    l_min, l_avg, l_max, l_hdrh = latency[1].split(u"/", 3)
    l_min, l_avg, l_max = float(l_min), float(l_avg), float(l_max)
    debug_percent_node[u"min"] = l_min
    info_percent_node[u"min"] = l_min
    debug_percent_node[u"avg"] = l_avg
    info_percent_node[u"avg"] = l_avg
    debug_percent_node[u"max"] = l_max
    info_percent_node[u"max"] = l_max
    debug_percent_node[u"hdrd"] = l_hdrh
    info_percent_node[u"hdrd"] = l_hdrh


def export_reconf_result(packet_rate, packet_loss, time_loss):
    """Export the results from a reconf packet test.

    Also, test type is set to RECONF.

    :param packet_rate: Aggregate rate sent in packets per second.
    :param packet_loss: How many of the packets were dropped or unsent.
    :param time_loss: Time in seconds (loss divided by rate).
    :type packet_rate: float
    :type packet_loss: int
    :type time_loss: float
    """
    debug_data, info_data = get_export_data()
    debug_data[u"test_type"] = u"RECONF"
    info_data[u"test_type"] = u"RECONF"
    debug_results_node = debug_data[u"results"]
    debug_results_node[u"packet_rate"] = packet_rate
    debug_results_node[u"packet_loss"] = packet_loss
    # Time loss is derived, so not needed in debug.
    info_results_node = info_data[u"results"]
    info_results_node[u"packet_rate"] = packet_rate
    info_results_node[u"packet_loss"] = packet_loss
    info_results_node[u"time_loss"] = time_loss
