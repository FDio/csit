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

"""Module facilitating conversion from raw outputs into info outputs."""

import copy
import json
import os

import dateutil.parser

from resources.libraries.python.Constants import Constants
from resources.libraries.python.jumpavg.AvgStdevStats import AvgStdevStats


def _raw_to_info_path(raw_path):
    """Compute path for info output corresponding to given raw output.

    :param raw_path: Local filesystem path to read raw JSON data from.
    :type raw_path: str
    :returns: Local filesystem path to write info JSON content to.
    :rtype: str
    :raises RuntimeError: If the input path does not meet all expectations.
    """
    raw_extension = u".raw.json"
    tmp_parts = raw_path.split(raw_extension)
    if len(tmp_parts) != 2 or tmp_parts[1] != u"":
        raise RuntimeError(f"Not good extension {raw_extension}: {raw_path}")
    info_path = tmp_parts[0] + u".info.json"
    return info_path


def _process_test_name(data):
    """Replace raw test name with short and long test name and set test_type.

    Perform in-place edits on the data dictionary.
    Remove raw suite_name and test_name, they are not part of info schema.
    Return early if the data is not for test case.
    Inserttest ID and long and short test name into the data.
    Besides suite_name and test_name, also test tags are read.

    Short test name is basically a suite tag, but with NIC driver prefix,
    if the NIC driver used is not the default one (drv_vfio_pci for VPP tests).

    Long test name has the following form:
    {nic_short_name}-{frame_size}-{threads_and_cores}-{suite_part}
    Lookup in test tags is needed to get the threads value.
    The threads_and_cores part may be empty, e.g. for TRex tests.

    Test ID has form {suite_name}.{test_name} where the two names come from
    Robot variables, converted to lower case and spaces replaces by undescores.

    Test type is set in an internal function.

    :param data: Raw data, perhaps some fields converted into info data already.
    :type data: dict
    :raises RuntimeError: If the raw data does not contain expected values.
    """
    suite_part = data.pop(u"suite_name").lower().replace(u" ", u"_")
    if u"test_name" not in data:
        # There will be no test_id, provide suite_id instead.
        data[u"suite_id"] = suite_part
        return
    test_part = data.pop(u"test_name").lower().replace(u" ", u"_")
    data[u"test_id"] = f"{suite_part}.{test_part}"
    tags = data[u"tags"]
    # Test name does not contain thread count.
    subparts = test_part.split(u"c-", 1)
    if len(subparts) < 2 or subparts[0][-2:-1] != u"-":
        # Physical core count not detected, assume it is a TRex test.
        if u"--" not in test_part:
            raise RuntimeError(f"Cores not found for {subparts}")
        short_name = test_part.split(u"--", 1)[1]
    else:
        short_name = subparts[1]
        # Add threads to test_part.
        core_part = subparts[0][-1] + u"c"
        for tag in tags:
            tag = tag.lower()
            if len(tag) == 4 and core_part == tag[2:] and tag[1] == u"t":
                test_part = test_part.replace(f"-{core_part}-", f"-{tag}-")
                break
        else:
            raise RuntimeError(f"Threads not found for {test_part} tags {tags}")
    # For long name we need NIC model, which is only in suite name.
    last_suite_part = suite_part.split(u".")[-1]
    # Short name happens to be the suffix we want to ignore.
    prefix_part = last_suite_part.split(short_name)[0]
    # Also remove the trailing dash.
    prefix_part = prefix_part[:-1]
    # Throw away possible link prefix such as "1n1l-".
    nic_code = prefix_part.split(u"-", 1)[-1]
    nic_short = Constants.NIC_CODE_TO_SHORT_NAME[nic_code]
    long_name = f"{nic_short}-{test_part}"
    # Set test type.
    test_type = _detect_test_type(data)
    data[u"test_type"] = test_type
    # Remove trailing test type from names (if present).
    short_name = short_name.split(f"-{test_type}")[0]
    long_name = long_name.split(f"-{test_type}")[0]
    # Store names.
    data[u"test_name_short"] = short_name
    data[u"test_name_long"] = long_name


def _detect_test_type(data):
    """Return test_type, as inferred from robot test tags.

    :param data: Raw data, perhaps some fields converted into info data already.
    :type data: dict
    :returns: The inferred test type value.
    :rtype: str
    :raises RuntimeError: If the test tags does not contain expected values.
    """
    tags = data[u"tags"]
    # First 5 options are specific for VPP tests.
    if u"DEVICETEST" in tags:
        test_type = u"device"
    elif u"LDP_NGINX" in tags:
        test_type = u"vsap"
    elif u"HOSTSTACK" in tags:
        test_type = u"hoststack"
    elif u"GSO_TRUE" in tags or u"GSO_FALSE" in tags:
        test_type = u"gso"
    elif u"RECONF" in tags:
        test_type = u"reconf"
    # The remaining 3 options could also apply to DPDK and TRex tests.
    elif u"SOAK" in tags:
        test_type = u"soak"
    elif u"NDRPDR" in tags:
        test_type = u"ndrpdr"
    elif u"MRR" in tags:
        test_type = u"mrr"
    else:
        raise RuntimeError(f"Unable to infer test type from tags: {tags}")
    return test_type


# Series of small blocks, too many to fit into a single function.
def _process_mrr_result(result_node):
    """Compute avg and stdev for mrr.

    :param result_node: Result part of Python data to edit in-place.
    :type result_node: dict
    """
    rate_node = result_node[u"receive_rate"][u"rate"]
    stats = AvgStdevStats.for_runs(rate_node[u"values"])
    rate_node[u"avg"] = stats.avg
    rate_node[u"stdev"] = stats.stdev


def _process_reconf_result(result_node):
    """Compute time loss for reconf and add missing units.

    :param result_node: Result part of Python data to edit in-place.
    :type result_node: dict
    """
    packet_rate = result_node[u"packet_rate"][u"rate"][u"value"]
    time_loss = result_node[u"packet_loss"][u"value"] / packet_rate
    result_node[u"time_loss"] = dict(value=time_loss, unit=u"s")
    result_node[u"packet_rate"][u"rate"][u"unit"] = u"pps"
    result_node[u"packet_loss"][u"unit"] = u"packets"
    if u"bandwidth" in result_node[u"packet_rate"]:
        result_node[u"packet_rate"][u"bandwidth"][u"unit"] = u"bps"


def _process_ab_result(result_node):
    """Add missing units to AB result.

    :param result_node: Result part of Python data to edit in-place.
    :type result_node: dict
    """
    result_node[u"completed_requests"][u"unit"] = u"requests"
    result_node[u"failed_requests"][u"unit"] = u"requests"
    result_node[u"total_bytes"][u"unit"] = u"bytes"
    # Convert transfer rate to bps.
    rate_node = result_node[u"transfer_rate"]
    unit = rate_node[u"unit"]
    if unit == u"Kbytes/sec":
        rate_node[u"value"] = 1000 * rate_node[u"value"]
    else:
        raise RuntimeError(f"Unexpected rate unit: {unit}")
    rate_node[u"unit"] = u"bps"


def _process_iperf_result(result_node):
    """Add missing units to iperf hoststack results.

    :param result_node: Result part of Python data to edit in-place.
    :type result_node: dict
    """
    for endpoint in (result_node[u"client"], result_node[u"server"]):
        for interval in endpoint[u"intervals"]:
            for item in interval[u"streams"] + [interval[u"sum"]]:
                item[u"duration"][u"unit"] = u"s"
                item[u"total_bytes"][u"unit"] = u"bytes"
                item[u"transfer_rate"][u"unit"] = u"bps"
                if u"packets" in item:
                    item[u"packets"][u"unit"] = u"packets"
                if u"retransmits" in item:
                    item[u"retransmits"][u"unit"] = u"packets"


def _process_vpp_echo_result(result_node):
    """Add missing units to vpp_echo result.

    :param result_node: Result part of Python data to edit in-place.
    :type result_node: dict
    """
    for program in (u"client", u"server"):
        program_node = result_node[program]
        program_node[u"duration"][u"unit"] = u"s"
        program_node[u"rx_data"][u"unit"] = u"bytes"
        program_node[u"tx_data"][u"unit"] = u"bytes"
        program_node[u"rx_rate"][u"unit"] = u"bps"
        program_node[u"tx_rate"][u"unit"] = u"bps"


def _process_ndrpdr_result(result_node):
    """Filter out invalid latencies.

    :param result_node: Result part of Python data to edit in-place.
    :type result_node: dict
    """
    for which_key in (u"latency_forward", u"latency_reverse"):
        if which_key not in result_node:
            # Probably just an unidir test.
            continue
        for load in (u"pdr_0", u"pdr_10", u"pdr_50", u"pdr_90"):
            if result_node[which_key][load][u"max"] <= 0:
                # One invalid number is enough to remove all loads.
                break
        else:
            # No break means all numbers are ok, nothing to do here.
            continue
        # Break happened, something is invalid, remove all loads.
        result_node.pop(which_key)


PROCESS_BY_RESULT_TYPE = dict(
    # Using lambda to avoid pylint complaints about unused argument.
    unknown=lambda result_node: None,
    mrr=_process_mrr_result,
    ndrpdr=_process_ndrpdr_result,
    reconf=_process_reconf_result,
    ab_cps=_process_ab_result,
    ab_rps=_process_ab_result,
    iperf_udp=_process_iperf_result,
    iperf_tcp=_process_iperf_result,
    vpp_echo=_process_vpp_echo_result,
)


def _convert_to_info_in_memory(data):
    """Perform all changes needed for processing of data, return new data.

    Data is assumed to be valid for raw schema, so no exceptions are expected.
    The original argument object is not edited,
    a new copy is created for edits and returned,
    because there is no easy way to sort keys in-place.

    Common processing directly, result_type specific by calling functions.

    :param data: The whole composite object to filter and enhance.
    :type data: dict
    :returns: New object with the edited content.
    :rtype: dict
    """
    data = copy.deepcopy(data)

    # Drop any SSH log items.
    data[u"log"] = list()

    # Duration is computed for every file.
    start_float = dateutil.parser.parse(data[u"start_time"]).timestamp()
    end_float = dateutil.parser.parse(data[u"end_time"]).timestamp()
    data[u"duration"] = end_float - start_float

    # Reorder impotant fields to the top.
    sorted_data = dict(version=data.pop(u"version"))
    sorted_data[u"duration"] = data.pop(u"duration")
    sorted_data[u"start_time"] = data.pop(u"start_time")
    sorted_data[u"end_time"] = data.pop(u"end_time")
    sorted_data.update(data)
    data = sorted_data
    # TODO: Do we care about the order of subsequently added fields?

    # Convert status into a boolean.
    status = data.pop(u"status", None)
    if status is not None:
        data[u"passed"] = (status == u"PASS")
        if data[u"passed"]:
            # Also truncate success test messages.
            data[u"message"] = u""

    # Replace raw names with processed ones, set test_id and test_type.
    _process_test_name(data)

    # The rest is only relevant for test case outputs.
    if u"result" not in data:
        return data
    result_node = data[u"result"]
    result_type = result_node[u"type"]
    PROCESS_BY_RESULT_TYPE[result_type](result_node)

    return data


def _merge_into_suite_info_file(teardown_info_path):
    """Move setup and teardown data into a singe file, remove old files.

    The caller has to confirm the argument is correct, e.g. ending in
    "/teardown.info.json".

    :param teardown_info_path: Local filesystem path to teardown info file.
    :type teardown_info_path: str
    :returns: Local filesystem path to newly created suite info file.
    :rtype: str
    """
    # Manual right replace: https://stackoverflow.com/a/9943875
    setup_info_path = u"setup".join(teardown_info_path.rsplit(u"teardown", 1))
    with open(teardown_info_path, u"rt", encoding="utf-8") as file_in:
        teardown_data = json.load(file_in)
    # Transforming setup data into suite data.
    with open(setup_info_path, u"rt", encoding="utf-8") as file_in:
        suite_data = json.load(file_in)

    end_time = teardown_data[u"end_time"]
    suite_data[u"end_time"] = end_time
    start_float = dateutil.parser.parse(suite_data[u"start_time"]).timestamp()
    end_float = dateutil.parser.parse(suite_data[u"end_time"]).timestamp()
    suite_data[u"duration"] = end_float - start_float
    setup_log = suite_data.pop(u"log")
    suite_data[u"setup_log"] = setup_log
    suite_data[u"teardown_log"] = teardown_data[u"log"]

    suite_info_path = u"suite".join(teardown_info_path.rsplit(u"teardown", 1))
    with open(suite_info_path, u"wt", encoding="utf-8") as file_out:
        json.dump(suite_data, file_out, indent=1)
    # We moved everything useful from temporary setup/teardown info files.
    os.remove(setup_info_path)
    os.remove(teardown_info_path)

    return suite_info_path


def convert_content_to_info(from_raw_path):
    """Read raw output, perform filtering, add derivatves, write info output.

    Directory path is created if missing.

    When processing teardown, create also suite output using setup info.

    :param from_raw_path: Local filesystem path to read raw JSON data from.
    :type from_raw_path: str
    :returns: Local filesystem path to written info JSON file.
    :rtype: str
    :raises RuntimeError: If path or content do not match expectations.
    """
    to_info_path = _raw_to_info_path(from_raw_path)
    with open(from_raw_path, u"rt", encoding="utf-8") as file_in:
        data = json.load(file_in)

    data = _convert_to_info_in_memory(data)

    with open(to_info_path, u"wt", encoding="utf-8") as file_out:
        json.dump(data, file_out, indent=1)
    if to_info_path.endswith(u"/teardown.info.json"):
        to_info_path = _merge_into_suite_info_file(to_info_path)
        # TODO: Return both paths for validation?

    return to_info_path
