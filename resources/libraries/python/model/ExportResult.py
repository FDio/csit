# Copyright (c) 2023 Cisco and/or its affiliates.
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


def export_dut_type_and_version(dut_type="unknown", dut_version="unknown"):
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
    if dut_type == "unknown":
        dut_type = BuiltIn().get_variable_value("\\${DUT_TYPE}", "unknown")
        if dut_type == "unknown":
            raise RuntimeError("Dut type not provided.")
    else:
        # We want to set a variable in higher level suite setup
        # to be available to test setup several levels lower.
        BuiltIn().set_suite_variable(
            "\\${DUT_TYPE}", dut_type, "children=True"
        )
    if dut_version == "unknown":
        dut_version = BuiltIn().get_variable_value(
            "\\${DUT_VERSION}", "unknown"
        )
        if dut_type == "unknown":
            raise RuntimeError("Dut version not provided.")
    else:
        BuiltIn().set_suite_variable(
            "\\${DUT_VERSION}", dut_version, "children=True"
        )
    data = get_export_data()
    data["dut_type"] = dut_type.lower()
    data["dut_version"] = dut_version


def export_tg_type_and_version(tg_type="unknown", tg_version="unknown"):
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
    if tg_type == "unknown":
        tg_type = BuiltIn().get_variable_value("\\${TG_TYPE}", "unknown")
        if tg_type == "unknown":
            raise RuntimeError("TG type not provided!")
    else:
        # We want to set a variable in higher level suite setup
        # to be available to test setup several levels lower.
        BuiltIn().set_suite_variable(
            "\\${TG_TYPE}", tg_type, "children=True"
        )
    if tg_version == "unknown":
        tg_version = BuiltIn().get_variable_value(
            "\\${TG_VERSION}", "unknown"
        )
        if tg_type == "unknown":
            raise RuntimeError("TG version not provided!")
    else:
        BuiltIn().set_suite_variable(
            "\\${TG_VERSION}", tg_version, "children=True"
        )
    data = get_export_data()
    data["tg_type"] = tg_type.lower()
    data["tg_version"] = tg_version


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
    data["result"]["type"] = "mrr"
    rate_node = descend(descend(data["result"], "receive_rate"), "rate")
    rate_node["unit"] = str(unit)
    values_list = descend(rate_node, "values", list)
    values_list.append(float(mrr_value))


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
    result_type = "soak" if "plrsearch" in text else "ndrpdr"
    upper_or_lower = "upper" if "upper" in text else "lower"
    ndr_or_pdr = "ndr" if "ndr" in text else "pdr"

    result_node = get_export_data()["result"]
    result_node["type"] = result_type
    rate_item = dict(rate=dict(value=value, unit=unit))
    if bandwidth:
        rate_item["bandwidth"] = dict(value=float(bandwidth), unit="bps")
    if result_type == "soak":
        descend(result_node, "critical_rate")[upper_or_lower] = rate_item
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
    l_min, l_avg, l_max, l_hdrh = latency_string.split("/", 3)
    whichward_node = descend(result_node, f"latency_{whichward}")
    percent_node = descend(whichward_node, f"pdr_{percent}")
    percent_node["min"] = int(l_min)
    percent_node["avg"] = int(l_avg)
    percent_node["max"] = int(l_max)
    percent_node["hdrh"] = l_hdrh
    percent_node["unit"] = "us"


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
    result_node = get_export_data()["result"]
    percent = 0
    if "90" in text:
        percent = 90
    elif "50" in text:
        percent = 50
    elif "10" in text:
        percent = 10
    _add_latency(result_node, percent, "forward", latency[0])
    # Else TRex does not support latency measurement for this traffic profile.
    if len(latency) < 2:
        return
    _add_latency(result_node, percent, "reverse", latency[1])


def export_reconf_result(packet_rate, packet_loss, bandwidth):
    """Export the RECONF type results.

    Result type is set to reconf.

    :param packet_rate: Aggregate offered load in packets per second.
    :param packet_loss: How many of the packets were dropped or unsent.
    :param bandwidth: The offered load recomputed into L1 bits per second.
    :type packet_rate: float
    :type packet_loss: int
    :type bandwidth: float
    """
    result_node = get_export_data()["result"]
    result_node["type"] = "reconf"

    time_loss = int(packet_loss) / float(packet_rate)
    result_node["aggregate_rate"] = dict(
        bandwidth=dict(
            unit="bps",
            value=float(bandwidth)
        ),
        rate=dict(
            unit="pps",
            value=float(packet_rate)
        )
    )
    result_node["loss"] = dict(
        packet=dict(
            unit="packets",
            value=int(packet_loss)
        ),
        time=dict(
            unit="s",
            value=time_loss
        )
    )


def export_hoststack_results(
        bandwidth, rate=None, rate_unit=None, latency=None,
        failed_requests=None, completed_requests=None, retransmits=None,
        duration=None
):
    """Export the HOSTSTACK type results.

    Result type is set to hoststack.

    :param bandwidth: Measured transfer rate using bps as a unit.
    :param rate: Resulting rate measured by the test. [Optional]
    :param rate_unit: CPS or RPS. [Optional]
    :param latency: Measure latency. [Optional]
    :param failed_requests: Number of failed requests. [Optional]
    :param completed_requests: Number of completed requests. [Optional]
    :param retransmits: Retransmitted TCP packets. [Optional]
    :param duration: Measurment duration. [Optional]
    :type bandwidth: float
    :type rate: float
    :type rate_unit: str
    :type latency: float
    :type failed_requests: int
    :type completed_requests: int
    :type retransmits: int
    :type duration: float
    """
    result_node = get_export_data()["result"]
    result_node["type"] = "hoststack"

    result_node["bandwidth"] = dict(unit="bps", value=bandwidth)
    if rate is not None:
        result_node["rate"] = \
            dict(unit=rate_unit, value=rate)
    if latency is not None:
        result_node["latency"] = \
            dict(unit="ms", value=latency)
    if failed_requests is not None:
        result_node["failed_requests"] = \
            dict(unit="requests", value=failed_requests)
    if completed_requests is not None:
        result_node["completed_requests"] = \
            dict(unit="requests", value=completed_requests)
    if retransmits is not None:
        result_node["retransmits"] = \
            dict(unit="packets", value=retransmits)
    if duration is not None:
        result_node["duration"] = \
            dict(unit="s", value=duration)


def append_telemetry(telemetry_item):
    """Append telemetry entry to proper place so it is dumped into json.

    :param telemetry_item: Telemetry entry.
    :type telemetry_item: str
    """
    data = get_export_data()
    data["telemetry"].append(telemetry_item)
