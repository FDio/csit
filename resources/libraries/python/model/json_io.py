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

"""Module aimed to simplify loading and dumping JSON from/to disk."""

import json
import os


def load_from(from_file_path):
    """Open file in text read mode, load JSON, return the loaded object.

    UTF-8 encoding is used, as Robot may generate non-ascii data.

    :param from_file_path: Local filesystem path including file name to load.
    :type from_file_path: str
    :raises RuntimeError: If file is not readable or JSON is malformed.
    """
    with open(from_file_path, u"rt", encoding="utf-8") as file_in:
        return json.load(file_in)


def dump_into(data, to_file_path):
    """Create ancestor directories and file, dump data.

    Dumped using default delimiters and indent=1.

    Write mode used is "xt", meaning this fails if the file
    is already created. This is the intended behavior,
    as we do not want to archive a mix of old and new results.
    Wiping the parget directory is the work for the higher level caller,
    e.g. the bootstrap script.

    :param data: Structured object to dump.
    :param to_file_path: Local filesystem path including file name to dump into.
    :type data: object
    :type to_file_path: str
    :raises RuntimeError: If file exists, not writable or data not serializable.
    """
    os.makedirs(os.path.dirname(to_file_path), exist_ok=True)
    with open(to_file_path, u"xt", encoding="utf-8") as file_out:
        json.dump(data, file_out, indent=1)
