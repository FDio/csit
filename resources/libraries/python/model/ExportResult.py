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

import json

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
        # Documentation [0] looks like "children" is a keyword argument,
        # but code [1] lines 1458 and 1511-1512 show
        # it is just last stringy argument.
        # [0] http://robotframework.org/robotframework/
        #     3.1.2/libraries/BuiltIn.html#Set%20Suite%20Variable
        # [1] https://github.com/robotframework/robotframework/blob/
        #     v3.1.2/src/robot/libraries/BuiltIn.py
        BuiltIn().set_suite_variable(
            u"\\${DUT_TYPE}", dut_type, u"children=True"
        )
    if dut_version == u"unknown":
        dut_version = BuiltIn().get_variable_value(u"\\${DUT_VERSION}", u"unknown")
        if dut_type == u"unknown":
            raise RuntimeError(u"Dut version not provided.")
    else:
        BuiltIn().set_suite_variable(
            u"\\${DUT_VERSION}", dut_version, u"children=True"
        )
    data = get_export_data()
    data[u"dut_type"] = dut_type
    data[u"dut_version"] = dut_version


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
    result_node = get_export_data()[u"result"]
    result_node[u"type"] = u"mrr"
    rate_node = descend(descend(result_node, u"receive_rate"), "rate")
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

    result_node = get_export_data()[u"result"]
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
    result_node = get_export_data()[u"result"]
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


def export_reconf_result(packet_rate, packet_loss):
    """Export the results from a reconf test.

    Also, result type is set to RECONF.

    :param packet_rate: Aggregate rate sent in packets per second.
    :param packet_loss: How many of the packets were dropped or unsent.
    :type packet_rate: float
    :type packet_loss: int
    """
    result_node = get_export_data()[u"result"]
    result_node[u"type"] = u"reconf"
    rate_item = dict(rate=dict(value=float(packet_rate), unit=u"pps"))
    result_node[u"packet_rate"] = rate_item
    result_node[u"packet_loss"] = int(packet_loss)


def export_hoststack_ab_result(result):
    """Add test result coming from AB test tool.

    Test type is set to HOSTSTACK_AB.

    TODO: Do we need more checks for the exported values (as ABTools passed)?

    :param result: Resulting values as parsed by ABTools.
    :type result: Mapping[str, Union[str, float, int]]
    """
    result_node = get_export_data()[u"result"]
    result_node[u"type"] = u"hoststack_ab"
    result_node[u"object"] = result


def export_hoststack_iperf3_fail_result(output):
    """Add hoststack_iperf3 result mapping for failed program.

    Contrary to successful case, the output is not deserialized,
    as there is no guarantee it is a valid JSON.
    For info, the first line is extracted as failure reason,
    the full output is still included.

    Test type is set to a hoststack_iperf3.

    TODO: Add checks for known failure reasons?

    :param output: Arbitrary output, first line is assumed to be the reason.
    :type output: str
    """
    result_node = get_export_data()[u"result"]
    result_node[u"type"] = u"hoststack_iperf3"
    result_node[u"object"] = output


def export_hoststack_vpp_echo_fail_result(output):
    """Add hoststack_vpp_echo result item for failed program.

    Contrary to successful case, the output is not deserialized,
    as there is no guarantee it is a valid JSON.
    For info, the first line is extracted as failure reason,
    the full output is still included.
    The result item is added to the list of results,
    as client program can have results independent of server program.

    Test type is set to a hoststack_vpp_echo.

    TODO: Add checks for known failure reasons?

    :param output: Arbitrary output, first line is assumed to be the reason.
    :type output: str
    """
    result_node = get_export_data()[u"result"]
    result_node[u"type"] = u"hoststack_vpp_echo"
    output_list = descend(result_node, u"outputs", list)
    output_list.append(dict(success=False, object=dict(output_text=output)))


def _check_key_type(mapping, key, type_, do_raise=True):
    """If the key is missing, or value type is wrong, produce an error.

    Produce means either raise or return, controlled by do_raise argument.
    Numeric values additionally cannot be negative.
    If all is good, return None.

    This is heavily used for checking deserialized JSON data
    from hoststack client or server programs.
    Intended for string keys, but the implementation works also for other.

    Not raising is useful when the constraint is for one of two keys to work.

    :param mapping: Mapping to check.
    :param key: The key of the entry to check.
    :param type_: Type or list of types the value has to belong to.
    :param do_raise: Whether to raise or return whena check fails.
    :type mapping: Mapping[str, object]
    :type key: str
    :type type_: Union[type, Iterable[type]]
    :type do_raise: bool
    :returns: None or (if do_raise is false) exception to raise.
    :rtype: Optional[Union[KeyError, TypeError]]
    :raises KeyError: If key is missing and do_raise is true.
    :raises TypeError: If value is wrong type and do_raise is true.
    :raises ValueError: If a numeric value is negative.
    """
    if key not in mapping:
        error = KeyError(f"Key {key} missing in {mapping}")
        if do_raise:
            raise error
        return error
    value = mapping[key]
    if not isinstance(value, type_):
        error = TypeError("Value {value} not type {type_} in {mapping}")
        if do_raise:
            raise error
        return error
    if isinstance(value, (int, float)) and value < 0:
        error = ValueError("Value {value} negative in {mapping}")
        if do_raise:
            raise error
        return error
    return None


def _check_hoststack_iperf3_output(output):
    """Raise if incompatibility with model documentation is detected.

    :param output: Output from iperf3 tool, deserialized.
    :type output: Mapping[str, object]
    :raises KeyError: If the output is missing a required key.
    :raises TypeError: If a value is not of (one of) the expected type(s).
    :raises ValueError: If a numeric value is negative.
    """
    _check_key_type(output, u"start", (int, float))
    _check_key_type(output, u"end", float)
    _check_key_type(output, u"seconds", float)
    _check_key_type(output, u"bytes", int)
    _check_key_type(output, u"bits_per_second", float)
    _check_key_type(output, u"omitted", bool)
    _check_key_type(output, u"sender", bool)
    tcp_error = _check_key_type(output, u"retransmits", int, do_raise=False)
    udp_error = _check_key_type(output, u"packets", int, do_raise=False)
    # Pylint gets confused if we use "is None" checks instead.
    if isinstance(tcp_error, Exception) and isinstance(udp_error, Excption):
        # Assume it was TCP.
        raise tcp_error


def _check_hoststack_vpp_echo_output(output):
    """Raise if incompatibility with model documentation is detected.

    As callers do not convert some values from string, it is done here,
    which means the output is modified in-place.

    :param output: Output from vpp_echo tool, deserialized.
    :type output: MutableMapping[str, object]
    :raises KeyError: If the output is missing a required key.
    :raises TypeError: If a value is not of (one of) the expected type(s).
    :raises ValueError: If a numeric value is negative.
    """
    _check_key_type(output, u"role", str)
    _check_key_type(output, u"time", (str, float))
    output[u"time"] = float(output[u"time"])
    _check_key_type(output, u"time", float)
    _check_key_type(output, u"start_evt", str)
    _check_key_type(output, u"start_evt_missing", (str, bool))
    output[u"start_evt_missing"] = bool(output[u"start_evt_missing"])
    _check_key_type(output, u"end_evt", str)
    _check_key_type(output, u"end_evt_missing", (str, bool))
    output[u"end_evt_missing"] = bool(output[u"end_evt_missing"])
    _check_key_type(output, u"rx_data", int)
    _check_key_type(output, u"tx_data", int)
    _check_key_type(output, u"rx_bits_per_second", float)
    _check_key_type(output, u"tx_bits_per_second", float)
    # TODO: Add checks for string and bool values.


def export_hoststack_iperf3_pass_result(output):
    """Add hoststack_iperf3 result for successful program.

    The output is deserialized and checked.

    Test type is set to a hoststack_iperf3.

    TODO: Check nsim tests also work (they already fail on master).

    :param output: JSON-serializable output, as parsed by HoststackUtil.
    :type output: dict
    :raises ValueError: If the parse output does not conform to UTI model.
    """
    result_node = get_export_data()[u"result"]
    result_node[u"type"] = u"hoststack_iperf3"
    result_node[u"object"] = output


def export_hoststack_vpp_echo_pass_result(parsed_output):
    """Add hoststack_vpp_echo result item for successful program.

    We export parsed_output, mostly without checking of the entries present.
    This is intentional, as we support multiple client and server programs,
    with slightly different entries in their output.
    The only requirement is at least one of entry keys has to contain
    "bits_per_second", as that is what PAL looks for.

    The result item is added to the list of results,
    as client program can have results independent of server program.

    Test type is set to a hoststack subtype depending on program name.

    TODO: Split into several hoststack subtypes if PAL looks at
    different entries based on the subtype.
    (Currently hard to do, as nsim tests are failing for some time.)

    TODO: Turn into fail result if a required key is missing?

    :param parsed_output: JSON-serializable output, otherwise arbitrary.
    :type parsed_output: dict
    :raises ValueError: If no key contains "bits_per_second".
    """
    result_node = get_export_data()[u"result"]
    result_node[u"type"] = u"hoststack_vpp_echo"
    output_list = descend(result_node, u"outputs", list)
    _check_hoststack_vpp_echo_output(parsed_output)
    output_list.append(dict(success=True, object=parsed_output))
