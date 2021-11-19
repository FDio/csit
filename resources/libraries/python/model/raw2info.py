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

import json

from resources.libraries.python.jumpavg.AvgStdevStats import AvgStdevStats
from resources.libraries.python.time_measurement import posix_from_iso


def _raw_to_info_path(raw_path):
    """Compute path for info output corresponding to given raw output.

    :param raw_path: Local filesystem path to read raw JSON data from.
    :type raw_path: str
    :returns: Local filesystem path to write info JSON content to.
    :rtype: str
    :raises RuntimeError: If the input path does not meet all expectations.
    """
    raw_dir = u"/output_raw/"
    path_parts = raw_path.split(raw_dir)
    if len(path_parts) != 2:
        raise RuntimeError(f"Not good {raw_dir}: {raw_path}")
    tmp_path = u"/output_info/".join(path_parts)
    raw_extension = u".raw.json"
    tmp_parts = tmp_path.split(raw_extension)
    if len(tmp_parts) != 2 or tmp_parts[1] != u"":
        raise RuntimeError(f"Not good {raw_extension}: {raw_path}")
    info_path = tmp_parts[0] + u".info.json"
    return info_path


def _convert_from_raw_to_info_in_memory(data):
    """Perform all changes needed for processing of data, in-place.

    Data is assumed to be valid for raw schema, so no exceptions are expected.

    :param data: The whole composite object to filter and enhance.
    :type data: dict
    """
    # Duration is computed for every file.
    start_time_float = posix_from_iso(data[u"start_time"])
    data[u"duration"] = posix_from_iso(data[u"end_time"]) - start_time_float

    # Suite name has to be in all file types, so does suite_id for info.
    suite_id = data[u"suite_name"].replace(u" ", u"_").lower()
    data[u"suite_id"] = suite_id
    # Suite_id variable is also used for test_id below.

    # Test ID is only in testcase files, but those have test_name.
    if u"test_name" in data:
        data[u"test_id"] = suite_id + u"." + data[u"test_name"].lower()

    # The rest is only relevant for test case outputs.
    if u"results" not in data:
        return
    results_node = data[u"results"]

    # Copy test type, detect tests by results.
    result_keys = list(results_node)
    if len(result_keys) <= 0:
        # Unsupported test type (e.g. device test).
        # Do not add test type, no more processing.
        return
    # TODO: Raise if results has multiple keys?
    test_type = result_keys[0]
    data[u"test_type"] = test_type

    # More processing depending on test type. TODO: Separate functions?

    # Compute avg and stdev for mrr.
    if test_type == u"mrr":
        mrr_node = results_node[u"mrr"]
        value_list = [item[u"rate"][u"value"] for item in mrr_node[u"samples"]]
        stats = AvgStdevStats.for_runs(value_list)
        mrr_node[u"avg"] = stats.avg
        mrr_node[u"stdev"] = stats.stdev

    # Multiple processing steps for ndrpdr
    if test_type != u"ndrpdr":
        return
    ndrpdr_node = results_node[u"ndrpdr"]
    # Add latency unit.
    ndrpdr_node[u"latency_unit"] = u"us"
    # Filter out invalid latencies.
    for which_key in (u"latency_forward", u"latency_reverse"):
        if which_key not in ndrpdr_node:
            # Probably just an unidir test.
            continue
        for load in (u"pdr_0", u"pdr_10", u"pdr_50", u"pdr_90"):
            if ndrpdr_node[which_key][load][u"max"] <= 0:
                # One invalid number is enough to remove all loads.
                break
        else:
            # No break means all numbers are ok, nothing to do here.
            continue
        # Break happened, something is invalid, remove all loads.
        del ndrpdr_node[which_key]


def process_content_to_info(from_raw_path):
    """Read raw output, perform filtering, add derivatves, write info output.

    :param from_raw_path: Local filesystem path to read raw JSON data from.
    :type from_raw_path: str
    :returns: Local filesystem path to written info JSON file.
    :rtype: str
    :raises RuntimeError: If path or content do not match expectations.
    """
    to_info_path = _raw_to_info_path(from_raw_path)
    with open(from_raw_path, u"rt") as file_in:
        data = json.load(file_in)

    _convert_from_raw_to_info_in_memory(data)

    with open(to_info_path, u"wt") as file_out:
        json.dump(data, file_out, indent=1)
    return to_info_path
