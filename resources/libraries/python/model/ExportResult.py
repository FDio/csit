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

"""Module with keywords that publish parts of result structure."""

from resources.libraries.python.jumpavg.AvgStdevStats import AvgStdevStats
from resources.libraries.python.model.util import descend, get_export_data


def export_vpp_version(version):
    """Export the argument as sut_version.

    Sets suit_type to "VPP".

    :param version: VPP version as returned by PAPI.
    :type version: str
    """
    debug_data, info_data = get_export_data()
    debug_data[u"sut_type"] = u"VPP"
    info_data[u"sut_type"] = u"VPP"
    version = str(version)
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
    debug_mrr_node = descend(debug_data[u"results"], u"mrr")
    debug_samples_list = descend(debug_mrr_node, u"samples", list)
    debug_samples_list.append(float(mrr_value))
    info_mrr_node = descend(info_data[u"results"], u"mrr")
    info_samples_list = descend(info_mrr_node, u"samples", list)
    info_samples_list.append(float(mrr_value))
    # Stats are derived quantity, so for info only.
    # TODO: Implement incremental udates.
    # That means storing stats somewhere json does not export.
    stats = AvgStdevStats.for_runs(info_samples_list)
    info_mrr_node[u"avg"] = stats.avg
    info_mrr_node[u"stdev"] = stats.stdev


def export_mrr_unit(unit):
    """Store MRR unit so it is dumped into json.

    If a previous value exists, it is overwritten silently.
    test type is set (overwritten) to MRR (info only).

    :param unit: Unit of MRR forwarding rate, either cps or pps.
    :type unit: str
    """
    debug_data, info_data = get_export_data()
    info_data[u"test_type"] = u"mrr"
    unit = str(unit)
    debug_data[u"results"][u"unit"] = unit
    info_data[u"results"][u"unit"] = unit


def export_search_bound(text, value, bandwidth=None):
    """Store bound value and unit.

    This function works for both NDRPDR and SOAK, decided by text.
    If bandwidth is not given, unit is assumed to be cps, otherwise pps.

    If a node does not exist, it is created.
    If a previous value exists, it is overwritten silently.
    Test type is set (overwritten) to ndrpdr (or soak), info only.

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
    test_type = u"soak" if u"plrsearch" in text else u"ndrpdr"
    upper_or_lower = u"upper" if u"upper" in text else u"lower"
    ndr_or_pdr = u"ndr" if u"ndr" in text else u"pdr"
    unit = u"cps" if bandwidth is None else u"pps"

    debug_data, info_data = get_export_data()
    info_data[u"test_type"] = test_type
    debug_type_node = descend(debug_data[u"results"], test_type)
    info_type_node = descend(info_data[u"results"], test_type)
    debug_type_node[u"unit"] = unit
    info_type_node[u"unit"] = unit
    if test_type == u"soak":
        debug_type_node[upper_or_lower] = value
        info_type_node[upper_or_lower] = value
        # TODO: Support Gbps values for SOAK?
        return
    descend(debug_type_node, ndr_or_pdr)[upper_or_lower] = value
    info_ndrpdr_node = descend(info_type_node, ndr_or_pdr)
    info_ndrpdr_node[upper_or_lower] = value
    if bandwidth is None:
        return
    bandwidth = float(bandwidth)
    info_ndrpdr_node[upper_or_lower + u"_gbps"] = bandwidth


def _add_latency(ndrpdr_node, percent, whichward, latency_string):
    """Descend to a corresponding node and add values from latency string.

    This is an internal block, moved out from export_ndrpdr_latency,
    as it can be called up to 4 times.

    :param ndrpdr_node: UTI tree node to descend from.
    :param percent: Percent value to use in node key (90, 50, 10, 0).
    :param whichward: "forward" or "reverse".
    :param latency_item: Unidir output from TRex utility, min/avg/max/hdrh.
    :type ndrpdr_node: dict
    :type percent: int
    :type whichward: str
    :latency_string: str
    :returns: True if the latency item is valid (min is not -1).
    :rtype: bool
    """
    l_min, l_avg, l_max, l_hdrh = latency_string.split(u"/", 3)
    whichward_node = descend(ndrpdr_node, f"latency_{whichward}")
    percent_node = descend(whichward_node, f"pdr_{percent}")
    percent_node[u"min"] = int(l_min)
    percent_node[u"avg"] = int(l_avg)
    percent_node[u"max"] = int(l_max)
    percent_node[u"hdrd"] = l_hdrh
    return int(l_min) > -1


def export_ndrpdr_latency(text, latency):
    """Store NDRPDR hdrh latency data.

    If "latency" node does not exist, it is created.
    If a previous value exists, it is overwritten silently.

    Text is used to determine what percentage of PDR is the load,
    as the Robot caller has the information only there.

    Reverse data may be missing, we assume the test was unidirectional.

    :param text: Info from Robot caller to determime load.
    :param latency: Output from TRex utility, min/avg/max/hdrh.
    :type text: str
    :type latency: 1-tuple or 2-tuple of str
    """
    debug_data, info_data = get_export_data()
    debug_ndrpdr_node = descend(debug_data[u"results"], u"ndrpdr")
    info_ndrpdr_node = descend(info_data[u"results"], u"ndrpdr")
    percent = 0
    if u"90" in text:
        percent = 90
    elif u"50" in text:
        percent = 50
    elif u"10" in text:
        percent = 10
    if _add_latency(debug_ndrpdr_node, percent, u"forward", latency[0]):
        _add_latency(info_ndrpdr_node, percent, u"forward", latency[0])
    # Else TRex does not support latency measurement for this traffic profile.
    if len(latency) < 2:
        return
    if _add_latency(debug_ndrpdr_node, percent, u"reverse", latency[1]):
        _add_latency(info_ndrpdr_node, percent, u"reverse", latency[1])
