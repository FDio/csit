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

"""Library for parsing results from JSON back to python objects.

This is useful for vpp-csit jobs like per-patch performance verify.
Such jobs invoke robot multiple times, each time on a different build.
Each robot invocation may execute several test cases.
How exactly are the results compared depends on the job type,
but extracting just the main results from jsons (file trees) is a common task,
so it is placed into this library.

As such, the code in this file does not directly interact
with the code in other files in this directory
(result comparison is done outside robot invocation),
but all files share common assumptions about json structure.

The function here expects a particular tree created on a filesystem by
a bootstrap script, including test results
exported as json files according to a current model schema.
This script extracts the results (according to result type)
and joins them mapping from test IDs to lists of floats.
Also, the result is cached into a results.json file,
so each tree is parsed only once.

The cached result does not depend on tree placement,
so the bootstrap script may move and copy trees around
before or after parsing.
"""

import json
import os
import pathlib

from typing import Dict, List


def parse(dirpath: str, fake_value: float = 1.0) -> Dict[str, List[float]]:
    """Look for test jsons, extract scalar results.

    Files other than .json are skipped, jsons without test_id are skipped.
    If the test failed, four fake values are used as a fake result.

    Units are ignored, as both parent and current are tested
    with the same CSIT code so the unit should be identical.

    The test results are sorted by test_id,
    as the filesystem order is not deterministic enough.

    The result is also cached as results.json file.

    :param dirpath: Path to the directory tree to examine.
    :param fail_value: Fake value to use for test cases that failed.
    :type dirpath: str
    :type fail_falue: float
    :returns: Mapping from test IDs to list of measured values.
    :rtype: Dict[str, List[float]]
    :raises RuntimeError: On duplicate test ID or unknown test type.
    """
    if not pathlib.Path(dirpath).is_dir():
        # This happens when per-patch runs out of iterations.
        return {}
    resultpath = pathlib.Path(f"{dirpath}/results.json")
    if resultpath.is_file():
        with open(resultpath, "rt", encoding="utf8") as file_in:
            return json.load(file_in)
    results = {}
    for root, _, files in os.walk(dirpath):
        for filename in files:
            if not filename.endswith(".json"):
                continue
            filepath = os.path.join(root, filename)
            with open(filepath, "rt", encoding="utf8") as file_in:
                data = json.load(file_in)
            if "test_id" not in data:
                continue
            name = data["test_id"]
            if name in results:
                raise RuntimeError(f"Duplicate: {name}")
            if not data["passed"]:
                results[name] = [fake_value] * 4
                continue
            result_object = data["result"]
            result_type = result_object["type"]
            if result_type == "mrr":
                results[name] = result_object["receive_rate"]["rate"]["values"]
            elif result_type == "ndrpdr":
                results[name] = [result_object["pdr"]["lower"]["rate"]["value"]]
            elif result_type == "soak":
                results[name] = [
                    result_object["critical_rate"]["lower"]["rate"]["value"]
                ]
            elif result_type == "reconf":
                results[name] = [result_object["loss"]["time"]["value"]]
            elif result_type == "hoststack":
                results[name] = [result_object["bandwidth"]["value"]]
            else:
                raise RuntimeError(f"Unknown result type: {result_type}")
    results = {test_id: results[test_id] for test_id in sorted(results)}
    with open(resultpath, "wt", encoding="utf8") as file_out:
        json.dump(results, file_out, indent=1, separators=(", ", ": "))
    return results
