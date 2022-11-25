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


def export_reconf_result(packet_rate, packet_loss, bandwidth=None):
    """Export the results from a reconf test.

    Also, result type is set to RECONF.
    Raw results do not contain units, they are added for info output later.

    :param packet_rate: Aggregate offered load in packets per second.
    :param packet_loss: How many of the packets were dropped or unsent.
    :param bandwidth: The offered load recomputed into L1 bits per second.
    :type packet_rate: float
    :type packet_loss: int
    :type bandwidth: Optional[float]
    """
    result_node = get_export_data()[u"result"]
    result_node[u"type"] = u"reconf"
    result_node[u"packet_rate"] = dict(rate=dict(value=float(packet_rate)))
    result_node[u"packet_loss"] = dict(value=int(packet_loss))
    if bandwidth:
        result_node[u"packet_rate"][u"bandwidth"] = dict(value=float(bandwidth))


def export_hoststack_ab_result(orig_result):
    """Add test result coming from AB test tool.

    Test type is set to HOSTSTACK_AB.
    This function supports both CPS and RPS results.

    TODO: Do we need more checks for the exported values (as ABTools passed)?

    :param orig_result: Resulting values as parsed by ABTools.
    :type orig_result: Mapping[str, Union[str, float, int]]
    """
    result_node = get_export_data()[u"result"]
    result_node.update(dict(latency=dict(), transfer_rate=dict(), rate=dict()))
    for key, value in orig_result.items():
        if key == u"latency_unit":
            result_node[u"latency"][u"unit"] = value
        elif key == u"latency_value":
            result_node[u"latency"][u"value"] = value
        elif key == u"transfer_unit":
            result_node[u"transfer_rate"][u"unit"] = value
            # To be converted when creating .info.
        elif key == u"transfer_rate":
            result_node[u"transfer_rate"][u"value"] = value
        elif key == u"quantity":
            result_node[u"rate"][u"unit"] = value
            result_node[u"type"] = f"ab_{value}"
        elif key == u"rate":
            result_node[u"rate"][u"value"] = value
        elif key == u"protocol":
            result_node[key] = value
        else:
            # The rest are values, units will be added to .info.
            result_node[key] = dict(value=value)


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


IPERF_KEYS = set((
    u"duration", u"omitted", u"packets", u"retransmits", u"sender",
    u"total_bytes", u"transfer_rate"
))


def _process_iperf_item(item):
    """Perform edits in-place as required by model.

    Common for both UDP and TCP items.
    Units will be added when converting to .info.

    :param item: Part of output from iperf tool, deserialized.
    :type output: Mapping[str, object]
    """
    item[u"duration"] = dict(value=item.pop(u"seconds"))
    item[u"total_bytes"] = dict(value=item.pop(u"bytes"))
    item[u"transfer_rate"] = dict(value=item.pop(u"bits_per_second"))
    if u"packets" in item:
        item[u"packets"] = dict(value=item.pop(u"packets"))
    if u"retransmits" in item:
        item[u"retransmits"] = dict(value=item.pop(u"retransmits"))
    for key in set(item) - IPERF_KEYS:
        del item[key]


def export_hoststack_iperf_result(parsed_output):
    """Add hoststack_iperf result for successful program.

    The parsed output is processed as needed, without explicit checking.

    Test type is set to an iperf variant (udp or tcp).

    TODO: Check nsim tests also work (they already fail on master).

    :param parsed_output: JSON-deserialized output, as parsed in HoststackUtil.
    :type parsed_output: dict
    :raises ValueError: If the parse output does not conform to UTI model.
    """
    client_object = parsed_output.pop(u"intervals")
    server_object = parsed_output.pop(u"server_output_json").pop(u"intervals")
    for endpoint_object in (client_object, server_object):
        for interval in endpoint_object:
            for stream in interval[u"streams"]:
                _process_iperf_item(stream)
            _process_iperf_item(interval[u"sum"])
    result_node = get_export_data()[u"result"]
    result_node[u"client"] = dict(intervals=client_object)
    result_node[u"server"] = dict(intervals=server_object)
    item = client_object[0][u"sum"]
    proto = u"udp" if u"packets" in item else u"tcp"
    result_node[u"type"] = f"iperf_{proto}"


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


VPP_ECHO_KEYS = set((
    u"duration", u"end_evt", u"end_evt_missing", u"role", u"rx_rate",
    u"rx_data", u"start_evt", u"start_evt_missing", u"tx_rate", u"tx_data",
))


def export_hoststack_vpp_echo_result(parsed_output):
    """Add vpp_echo_result item for successful program.

    We export parsed_output, mostly without checking of the entries present.
    This is intentional, as we support multiple client and server programs,
    with slightly different entries in their output.
    The only requirement is at least one of entry keys has to contain
    "bits_per_second", as that is (converted to) what PAL looks for.

    Call this function twice, separately for client and resrver results.

    TODO: Turn into fail result if a required key is missing?

    :param parsed_output: JSON-serializable output, otherwise arbitrary.
    :type parsed_output: dict
    :raises ValueError: If no key contains "bits_per_second".
    """
    _check_hoststack_vpp_echo_output(parsed_output)
    # Rename and restructure according to model.
    # Units will be added when converting into .info.
    parsed_output[u"rx_data"] = dict(value=parsed_output.pop(u"rx_data"))
    parsed_output[u"tx_data"] = dict(value=parsed_output.pop(u"tx_data"))
    parsed_output[u"rx_rate"] = dict(
        value=parsed_output.pop(u"rx_bits_per_second")
    )
    parsed_output[u"tx_rate"] = dict(
        value=parsed_output.pop(u"tx_bits_per_second")
    )
    parsed_output[u"duration"] = dict(value=parsed_output.pop(u"time"))
    # Prune unneeded fields.
    for key in set(parsed_output) - VPP_ECHO_KEYS:
        del parsed_output[key]
    # Put to results.
    result_node = get_export_data()[u"result"]
    result_node[u"type"] = u"vpp_echo"
    result_node[parsed_output[u"role"]] = parsed_output
