# Copyright (c) 2025 Cisco and/or its affiliates.
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

"""Module for canitizing JSON instances found invalid against schema.

Short module currently, as we validate only testcase info outputs,
and the only supporterd form of sanitization is to replace result
with "unknown" type and mark as failed.
"""

from resources.libraries.python.model.MemDump import write_output


def sanitize(file_path, data, error):
    """If error, edit data in-place, write edited data to disk again.

    There might have been multiple schema violations.
    In practice, the only part likely to cause an error is "result",
    so it should be enough to replace it with the "unknown" type.
    The old invalid result is forgotten to save space,
    as any serious investigation will look at log.html instead.

    Mark the test as failed, so the results do not affect anomaly detection.
    Use the validation error as failure message, as it is short,
    and corresponds to Robot console output.

    :param file_path: Local filesystem path including the file name to load.
    :param data: Previously exported data that was found invalid.
    :param error: Validation error as returned by validator.
    :type file_path: str
    :type data: dict
    :type error: Optional[ValidationError]
    """
    if not error:
        return
    data["passed"] = False
    data["message"] = str(error)
    data["result"] = dict(type="unknown")
    write_output(file_path, data)
