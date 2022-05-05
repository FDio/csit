# Copyright (c) 2022 Cisco and/or its affiliates.
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

from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.model.util import descend, get_export_data


def export_dut_type_and_version(dut_type=u"unknown", dut_version=u"unknown"):
    """Export the arguments as dut type and version.

    Robot tends to convert "none" into None, hence the unusual default values.

    If either argument is missing, the value from robot variable is used.
    If argument is present, the value is also stored to robot suite variable.

    :param dut_type: DUT type, e.g. VPP or DPDK.
    :param dut_version: DUT version as determined by the caller.
    :type dut_type: Optional[str]
    :type dut_version: Optiona[str]
    :raises RuntimeError: If value is neither in argument not robot variable.
    """
    if dut_type == u"unknown":
        dut_type = BuiltIn().get_variable_value(u"\\${DUT_TYPE}", u"unknown")
        if dut_type == u"unknown":
            raise RuntimeError(u"Dut type not provided.")
    else:
        # We want to set a variable in higher level suite setup
        # to be available to test setup several levels lower.
        BuiltIn().set_suite_variable(
            u"\\${DUT_TYPE}", dut_type, u"children=True"
        )
    if dut_version == u"unknown":
        dut_version = BuiltIn().get_variable_value(
            u"\\${DUT_VERSION}", u"unknown"
        )
        if dut_type == u"unknown":
            raise RuntimeError(u"Dut version not provided.")
    else:
        BuiltIn().set_suite_variable(
            u"\\${DUT_VERSION}", dut_version, u"children=True"
        )
    data = get_export_data()
    data[u"dut_type"] = dut_type.lower()
    data[u"dut_version"] = dut_version


def export_tg_type_and_version(tg_type=u"unknown", tg_version=u"unknown"):
    """Export the arguments as tg type and version.

    Robot tends to convert "none" into None, hence the unusual default values.

    If either argument is missing, the value from robot variable is used.
    If argument is present, the value is also stored to robot suite variable.

    :param tg_type: TG type, e.g. TREX.
    :param tg_version: TG version as determined by the caller.
    :type tg_type: Optional[str]
    :type tg_version: Optiona[str]
    :raises RuntimeError: If value is neither in argument not robot variable.
    """
    if tg_type == u"unknown":
        tg_type = BuiltIn().get_variable_value(u"\\${TG_TYPE}", u"unknown")
        if tg_type == u"unknown":
            raise RuntimeError(u"TG type not provided.")
    else:
        # We want to set a variable in higher level suite setup
        # to be available to test setup several levels lower.
        BuiltIn().set_suite_variable(
            u"\\${TG_TYPE}", tg_type, u"children=True"
        )
    if tg_version == u"unknown":
        tg_version = BuiltIn().get_variable_value(
            u"\\${TG_VERSION}", u"unknown"
        )
        if tg_type == u"unknown":
            raise RuntimeError(u"TG version not provided.")
    else:
        BuiltIn().set_suite_variable(
            u"\\${TG_VERSION}", tg_version, u"children=True"
        )
    data = get_export_data()
    data[u"tg_type"] = tg_type.lower()
    data[u"tg_version"] = tg_version


def append_mrr_value(mrr_value, unit):
    """Store mrr value to proper place so it is dumped into json.

    The value is appended only when unit is not empty.

    :param mrr_value: Forwarding rate from MRR trial.
    :param unit: Unit of measurement for the rate.
    :type mrr_value: float
    :type unit: str
    """
    if not unit:
        return
    data = get_export_data()
    data[u"result"][u"type"] = u"mrr"
    rate_node = descend(descend(data[u"result"], u"receive_rate"), "rate")
    rate_node[u"unit"] = str(unit)
    values_list = descend(rate_node, u"values", list)
    values_list.append(float(mrr_value))
    # TODO: Fill in the bandwidth part for pps?


def export_search_bound(text, value, unit, bandwidth=None):
    """Store bound value and unit.

    This function works for both NDRPDR and SOAK, decided by text.

    If a node does not exist, it is created.
    If a previous value exists, it is overwritten silently.
    Result type is set (overwritten) to ndrpdr (or soak).

    Text is used to determine whether it is ndr or pdr, upper or lower bound,
    as the Robot caller has the information only there.

    :param text: Info from Robot caller to determime bound type.
    :param value: The bound value in packets (or connections) per second.
    :param unit: Rate unit the bound is measured (or estimated) in.
    :param bandwidth: The same value recomputed into L1 bits per second.
    :type text: str
    :type value: float
    :type unit: str
    :type bandwidth: Optional[float]
    """
    value = float(value)
    text = str(text).lower()
    result_type = u"soak" if u"plrsearch" in text else u"ndrpdr"
    upper_or_lower = u"upper" if u"upper" in text else u"lower"
    ndr_or_pdr = u"ndr" if u"ndr" in text else u"pdr"

    data = get_export_data()
    result_node = data[u"result"]
    result_node[u"type"] = result_type
    rate_item = dict(rate=dict(value=value, unit=unit))
    if bandwidth:
        rate_item[u"bandwidth"] = dict(value=float(bandwidth), unit=u"bps")
    if result_type == u"soak":
        descend(result_node, u"critical_rate")[upper_or_lower] = rate_item
        return
    descend(result_node, ndr_or_pdr)[upper_or_lower] = rate_item


def _add_latency(result_node, percent, whichward, latency_string):
    """Descend to a corresponding node and add values from latency string.

    This is an internal block, moved out from export_ndrpdr_latency,
    as it can be called up to 4 times.

    :param result_node: UTI tree node to descend from.
    :param percent: Percent value to use in node key (90, 50, 10, 0).
    :param whichward: "forward" or "reverse".
    :param latency_item: Unidir output from TRex utility, min/avg/max/hdrh.
    :type result_node: dict
    :type percent: int
    :type whichward: str
    :latency_string: str
    """
    l_min, l_avg, l_max, l_hdrh = latency_string.split(u"/", 3)
    whichward_node = descend(result_node, f"latency_{whichward}")
    percent_node = descend(whichward_node, f"pdr_{percent}")
    percent_node[u"min"] = int(l_min)
    percent_node[u"avg"] = int(l_avg)
    percent_node[u"max"] = int(l_max)
    percent_node[u"hdrh"] = l_hdrh
    percent_node[u"unit"] = u"us"


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
    data = get_export_data()
    result_node = data[u"result"]
    percent = 0
    if u"90" in text:
        percent = 90
    elif u"50" in text:
        percent = 50
    elif u"10" in text:
        percent = 10
    _add_latency(result_node, percent, u"forward", latency[0])
    # Else TRex does not support latency measurement for this traffic profile.
    if len(latency) < 2:
        return
    _add_latency(result_node, percent, u"reverse", latency[1])
