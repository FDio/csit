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


def dump_into(data, to_file_path, overwrite=False):
    """Create ancestor directories and file, dump data.

    Dumped using default delimiters and indent=1.

    :param data: Structured object to dump.
    :param to_file_path: Local filesystem path including file name to dump into.
    :param overwrite: If true, tolerate when the file already exists.
    :type data: object
    :type to_file_path: str
    :type overwrite: bool
    :raises RuntimeError: If file exists, not writable or data not serializable.
    """
    mode = u"wt" if overwrite else u"xt"
    os.makedirs(os.path.dirname(to_file_path), exist_ok=True)
    with open(to_file_path, mode, encoding="utf-8") as file_out:
        json.dump(data, file_out, indent=1)
