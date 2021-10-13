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

import json

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
    debug_samples_list = descend(debug_data[u"results"], u"samples", list)
    debug_samples_list.append(float(mrr_value))
    info_results_node = info_data[u"results"]
    info_samples_list = descend(info_results_node, u"samples", list)
    info_samples_list.append(float(mrr_value))
    # Stats are derived quantity, so for info only.
    # TODO: Implement incremental udates.
    # That means storing stats somewhere json does not export.
    stats = AvgStdevStats.for_runs(info_samples_list)
    info_results_node[u"avg"] = stats.avg
    info_results_node[u"stdev"] = stats.stdev


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
    info_data[u"test_type"] = u"reconf"
    debug_reconf_node = descend(debug_data[u"results"], u"reconf")
    debug_reconf_node[u"packet_rate"] = packet_rate
    debug_reconf_node[u"packet_loss"] = packet_loss
    # Time loss is derived, so not needed in debug.
    info_reconf_node = descend(info_data[u"results"], u"reconf")
    info_reconf_node[u"packet_rate"] = packet_rate
    info_reconf_node[u"packet_loss"] = packet_loss
    info_reconf_node[u"time_loss"] = time_loss


def export_hoststack_ab_result(result):
    """Add test result coming from AB test tool.

    Test type is set to HOSTSTACK_AB.

    TODO: Do we need more checks for the exported values (as ABTools passed)?

    :param result: Resulting values as parsed by ABTools.
    :type result: Mapping[str, Union[str, float, int]]
    """
    debug_data, info_data = get_export_data()
    info_data[u"test_type"] = u"hoststack_ab"
    debug_data[u"results"][u"hoststack_ab"] = result
    info_data[u"results"][u"hoststack_ab"] = result


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
    debug_data, info_data = get_export_data()
    test_type = u"hoststack_iperf3"
    info_data[u"test_type"] = test_type
    debug_item = dict(success=False, output_text=output)
    debug_data[u"results"][test_type] = debug_item
    info_item = debug_item.copy()
    info_item[u"reason"] = output.split(u"\n", 1)[0]
    info_data[u"results"][test_type] = info_item


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
    debug_data, info_data = get_export_data()
    test_type = u"hoststack_vpp_echo"
    info_data[u"test_type"] = test_type
    debug_item = dict(success=False, output_text=output)
    debug_hoststack_list = descend(debug_data[u"results"], test_type, list)
    debug_hoststack_list.append(debug_item)
    info_item = debug_item.copy()
    info_item[u"reason"] = output.split(u"\n", 1)[0]
    info_hoststack_list = descend(info_data[u"results"], test_type, list)
    info_hoststack_list.append(info_item)


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
    if tcp_error is not None and udp_error is not None:
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
    _check_key_type(output, u"time", str)
    output[u"time"] = float(output[u"time"])
    _check_key_type(output, u"time", float)
    _check_key_type(output, u"start_evt", str)
    _check_key_type(output, u"start_evt_missing", str)
    output[u"start_evt_missing"] = bool(output[u"start_evt_missing"])
    _check_key_type(output, u"start_evt_missing", bool)
    _check_key_type(output, u"end_evt", str)
    _check_key_type(output, u"end_evt_missing", str)
    output[u"end_evt_missing"] = bool(output[u"end_evt_missing"])
    _check_key_type(output, u"end_evt_missing", bool)
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

    :param output: JSON-serializable output, as processed by HoststackUtil.
    :type output: str
    :raises ValueError: If the parse output does not conform to UTI model.
    """
    debug_data, info_data = get_export_data()
    test_type = f"hoststack_iperf3"
    info_data[u"test_type"] = test_type
    parsed_output = json.loads(output)
    _check_hoststack_iperf3_output(parsed_output)
    item = dict(success=True, output=parsed_output)
    debug_data[u"results"][test_type] = item
    info_data[u"results"][test_type] = item


def export_hoststack_vpp_echo_pass_result(output):
    """Add hoststack_vpp_echo result item for successful program.

    The output is deserialized, mosly without checking of the entries present.
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

    :param output: JSON-serializable output, otherwise arbitrary.
    :type output: str
    :raises ValueError: If no key contains "bits_per_second".
    """
    debug_data, info_data = get_export_data()
    test_type = u"hoststack_vpp_echo"
    info_data[u"test_type"] = test_type
    parsed_output = json.loads(output)
    _check_hoststack_vpp_echo_output(parsed_output)
    item = dict(success=True, output=parsed_output)
    debug_hoststack_list = descend(debug_data[u"results"], test_type, list)
    debug_hoststack_list.append(item)
    info_hoststack_list = descend(info_data[u"results"], test_type, list)
    info_hoststack_list.append(item)
