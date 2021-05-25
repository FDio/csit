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

from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.jumpavg.AvgStdevStats import AvgStdevStats
from .util import descend


def append_mrr_value(mrr_value):
    """Store mrr value to proper place so it is dumped into json.

    The inner node "value" may or may not exist before calling this.
    Test type is not overwritten here, but when setting unit.

    :param mrr_value: Forwarding rate from MRR trial, unit specified elsewhere.
    :type mrr_value: float
    """
    lib = BuiltIn().get_library_instance(
        u"resources.libraries.python.model.export_json"
    )
    results_node = lib.data[u"test"][u"results"]
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
    lib = BuiltIn().get_library_instance(
        u"resources.libraries.python.model.export_json"
    )
    lib.data[u"test"][u"test-type"] = u"MRR"
    lib.data[u"test"][u"results"][u"unit"] = str(unit)

def export_ndrpdr_pps_bound(text, pps, bandwidth):
    """Store NDRPDR pps values and unit.

    If "throughput" node does not exist, it is created.
    If a previous values exist, they are overwritten silently.
    Test type is set (overwritten) to NDRPDR.

    Text is used to determine whether it is ndr or pdr, upper or lower bound,
    as the Robot caller has the information only there.

    :param text: Info from Robot caller to determime bound type.
    :param pps: The bound value in packets per second.
    :param bandwidth: The same value recomputed into L1 gigabits per second.
    :type text: str
    :type pps: float
    :type bandwidth: float
    """
    lib = BuiltIn().get_library_instance(
        u"resources.libraries.python.model.export_json"
    )
    lib.data[u"test"][u"test-type"] = u"NDRPDR"
    results_node = lib.data[u"test"][u"results"]
    throughput_node = descend(results_node, u"throughput")
    throughput_node[u"unit"] = u"pps"
    text = str(text).lower()
    ndr_or_pdr = u"ndr" if u"ndr" in text else u"pdr"
    upper_or_lower = u"upper" if u"upper" in text else u"lower"
    ndrpdr_node = descend(throughput_node, ndr_or_pdr)
    value_node = descend(ndrpdr_node, u"value")
    value_node[upper_or_lower] = float(pps)
    value_gbps_node = descend(ndrpdr_node, u"value_gbps")
    value_gbps_node[upper_or_lower] = float(bandwidth)

def export_ndrpdr_cps_bound(text, cps):
    """Store NDRPDR cps value and unit.

    If "throughput" node does not exist, it is created.
    If a previous values exist, they are overwritten silently.
    Test type is set (overwritten) to NDRPDR.

    Text is used to determine whether it is ndr or pdr, upper or lower bound,
    as the Robot caller has the information only there.

    :param text: Info from Robot caller to determime bound type.
    :param pps: The bound value in packets per second.
    :type text: str
    :type pps: float
    """
    lib = BuiltIn().get_library_instance(
        u"resources.libraries.python.model.export_json"
    )
    lib.data[u"test"][u"test-type"] = u"NDRPDR"
    results_node = lib.data[u"test"][u"results"]
    throughput_node = descend(results_node, u"throughput")
    throughput_node[u"unit"] = u"cps"
    text = str(text).lower()
    ndr_or_pdr = u"ndr" if u"ndr" in text else u"pdr"
    upper_or_lower = u"upper" if u"upper" in text else u"lower"
    ndrpdr_node = descend(throughput_node, ndr_or_pdr)
    value_node = descend(ndrpdr_node, u"value")
    value_node[upper_or_lower] = float(cps)

def export_ndrpdr_latency(text, latency):
    """Store NDRPDR hdrh latency data.

    If "throughput" node does not exist, it is created.
    If a previous values exist, they are overwritten silently.
    Test type is set (overwritten) to NDRPDR.

    Text is used to determine whether it is ndr or pdr, upper or lower bound,
    as the Robot caller has the information only there.

    :param text: Info from Robot caller to determime bound type.
    :param pps: The bound value in packets per second.
    :type text: str
    :type pps: float
    """
    lib = BuiltIn().get_library_instance(
        u"resources.libraries.python.model.export_json"
    )
    results_node = lib.data[u"test"][u"results"]
    latency_node = descend(results_node, u"latency")
    percent = 0
    if u"90" in text:
        percent = 90
    elif u"50" in text:
        percent = 50
    elif u"10" in text:
        percent = 10
    node_name = f"pdr-{percent}"
    forward_node = descend(latency_node, u"forward")
    percent_node = descend(forward_node, node_name)
    l_min, l_avg, l_max, l_hdrh = latency[0].split(u"/", 3)
    percent_node[u"min"] = l_min
    percent_node[u"avg"] = l_avg
    percent_node[u"max"] = l_max
    percent_node[u"hdrd"] = l_hdrh
    if len(latency) < 2:
        return
    reverse_node = descend(latency_node, u"reverse")
    percent_node = descend(reverse_node, node_name)
    l_min, l_avg, l_max, l_hdrh = latency[1].split(u"/", 3)
    percent_node[u"min"] = l_min
    percent_node[u"avg"] = l_avg
    percent_node[u"max"] = l_max
    percent_node[u"hdrd"] = l_hdrh
