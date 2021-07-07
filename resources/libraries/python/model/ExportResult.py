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
    data = get_export_data()
    data[u"sut_type"] = u"VPP"
    data[u"sut_version"] = str(version)


def append_mrr_value(mrr_value):
    """Store mrr value to proper place so it is dumped into json.

    The inner node "value" may or may not exist before calling this.
    Test type is not overwritten here, but when setting unit.

    :param mrr_value: Forwarding rate from MRR trial, unit specified elsewhere.
    :type mrr_value: float
    """
    data = get_export_data()
    results_node = data[u"results"]
    samples = descend(results_node, u"samples", list())
    samples.append(float(mrr_value))
    # TODO: Implement incremental udates.
    # That means storing starts somewhere json does not export.
    stats = AvgStdevStats.for_runs(samples)
    results_node[u"avg"] = stats.avg
    results_node[u"stdev"] = stats.stdev


def export_mrr_unit(unit):
    """Store MRR unit so it is dumped into json.

    If a previous value exists, it is overwritten silently.
    test type is set (overwritten) to MRR.

    :param unit: Unit of MRR forwarding rate, either cps or pps.
    :type unit: str
    """
    data = get_export_data()
    data[u"test_type"] = u"MRR"
    data[u"results"][u"unit"] = str(unit)


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
    data = get_export_data()
    text = str(text).lower()
    test_type = u"SOAK" if u"plrsearch" in text else u"NDRPDR"
    upper_or_lower = u"upper" if u"upper" in text else u"lower"
    ndr_or_pdr = u"ndr" if u"ndr" in text else u"pdr"
    data[u"test_type"] = test_type
    results_node = data[u"results"]
    rate_name = u"throughput" if test_type == u"NDRPDR" else u"critical_rate"
    rate_node = descend(results_node, rate_name)
    rate_node[u"unit"] = u"cps" if bandwidth is None else u"pps"
    if test_type == u"SOAK":
        rate_node[upper_or_lower] = float(value)
        # TODO: Support Gbps values for SOAK?
        return
    ndrpdr_node = descend(rate_node, ndr_or_pdr)
    value_node = descend(ndrpdr_node, u"value")
    value_node[upper_or_lower] = float(value)
    if bandwidth is None:
        return
    value_gbps_node = descend(ndrpdr_node, u"value_gbps")
    value_gbps_node[upper_or_lower] = float(bandwidth)


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
    data = get_export_data()
    results_node = data[u"results"]
    latency_node = descend(results_node, u"latency")
    percent = 0
    if u"90" in text:
        percent = 90
    elif u"50" in text:
        percent = 50
    elif u"10" in text:
        percent = 10
    node_name = f"pdr_{percent}"
    forward_node = descend(latency_node, u"forward")
    percent_node = descend(forward_node, node_name)
    l_min, l_avg, l_max, l_hdrh = latency[0].split(u"/", 3)
    percent_node[u"min"] = float(l_min)
    percent_node[u"avg"] = float(l_avg)
    percent_node[u"max"] = float(l_max)
    percent_node[u"hdrd"] = l_hdrh
    if len(latency) < 2:
        return
    reverse_node = descend(latency_node, u"reverse")
    percent_node = descend(reverse_node, node_name)
    l_min, l_avg, l_max, l_hdrh = latency[1].split(u"/", 3)
    percent_node[u"min"] = float(l_min)
    percent_node[u"avg"] = float(l_avg)
    percent_node[u"max"] = float(l_max)
    percent_node[u"hdrd"] = l_hdrh
