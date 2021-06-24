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

"""Module hosting conversion functions for telemetry."""


def split_telemetry_text(text):
    """Ignore leading garbage and group openmetric blocks.

    This is a generator function yielding blocks of text.
    Empty (or too short) lines are skipped.

    For the imput format, see resources/tools/telemetry/serializer.py

    :param text: Textual form of telemetry, leading garbage is ignored.
    :type text: str
    :returns: Generator yielding blocks of text
    :rtype: Generator[str, None, None]
    """
    multi_lines = list()
    garbage = True
    for line in text.splitlines():
        if line.startswith(u"# HELP"):
            garbage = False
            if multi_lines:
                yield u"\n".join(multi_lines)
            multi_lines = list()
        if garbage or len(line) <= 2:
            continue
        multi_lines.append(line)
    # Flush the last block
    if multi_lines:
        yield u"\n".join(multi_lines)
