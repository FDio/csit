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

"""Module facilitating conversion from raw outputs into info outputs."""

import copy
import os

from resources.libraries.python.jumpavg.AvgStdevStats import AvgStdevStats
from resources.libraries.python.model.json_io import load_from, dump_into
from resources.libraries.python.model.util import normalize
from resources.libraries.python.time_measurement import posix_from_iso


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


def _convert_from_raw_to_info_in_memory(data):
    """Perform all changes needed for processing of data, return new data.

    Data is assumed to be valid for raw schema, so no exceptions are expected.
    The original argument object is not edited,
    a new copy is created for edits and returned,
    because there is no easy way to sort keys in-place.

    :param data: The whole composite object to filter and enhance.
    :type data: dict
    :returns: New object with the edited content.
    :rtype: dict
    """
    data = copy.deepcopy(data)

    # Truncate success test messages:
    if u"robot" in data and data[u"robot"][u"status"] == u"PASS":
        data[u"robot"][u"message"] = u""

    # Duration is computed for every file.
    start_time_float = posix_from_iso(data[u"start_time"])
    data[u"duration"] = posix_from_iso(data[u"end_time"]) - start_time_float

    # Reorder impotant fields to the top.
    sorted_data = dict(version=data.pop(u"version"))
    sorted_data[u"duration"] = data.pop(u"duration")
    sorted_data[u"start_time"] = data.pop(u"start_time")
    sorted_data[u"end_time"] = data.pop(u"end_time")
    sorted_data.update(data)
    data = sorted_data
    # TODO: Do we care about the order of subsequently added fields?

    # Suite name has to be in all file types, so does suite_id for info.
    suite_id = normalize(data[u"suite_name"])
    data[u"suite_id"] = suite_id
    # Suite_id variable is also used for test_id below.

    # Test ID is only in testcase files, but those have test_name.
    if u"test_name" in data:
        data[u"test_id"] = suite_id + u"." + normalize(data[u"test_name"])

    # The rest is only relevant for test case outputs.
    if u"result" not in data:
        return data
    result_node = data[u"result"]
    result_type = result_node[u"type"]
    if result_type == u"unknown":
        # Device or something else not supported.
        return data

    # More processing depending on result type. TODO: Separate functions?

    # Compute avg and stdev for mrr.
    if result_type == u"mrr":
        rate_node = result_node[u"receive_rate"][u"rate"]
        stats = AvgStdevStats.for_runs(rate_node[u"values"])
        rate_node[u"avg"] = stats.avg
        rate_node[u"stdev"] = stats.stdev

    # Multiple processing steps for ndrpdr
    if result_type != u"ndrpdr":
        return data
    # Filter out invalid latencies.
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
    teardown_data = load_from(teardown_info_path)
    # Transforming setup data into suite data.
    suite_data = load_from(setup_info_path)

    end_time = teardown_data[u"end_time"]
    suite_data[u"end_time"] = end_time
    start_time_float = posix_from_iso(suite_data[u"start_time"])
    suite_data[u"duration"] = posix_from_iso(end_time) - start_time_float
    setup_log = suite_data.pop(u"log")
    suite_data[u"setup_log"] = setup_log
    suite_data[u"teardown_log"] = teardown_data[u"log"]

    suite_info_path = u"suite".join(teardown_info_path.rsplit(u"teardown", 1))
    dump_into(suite_data, suite_info_path)
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
    data = load_from(from_raw_path)

    data = _convert_from_raw_to_info_in_memory(data)

    dump_into(data, to_info_path)
    if to_info_path.endswith(u"/teardown.info.json"):
        to_info_path = _merge_into_suite_info_file(to_info_path)
        # TODO: Return both paths for validation?

    return to_info_path
