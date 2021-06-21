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

import json


def process_telemetry_lines(lines):
    """Return list of parsed data items for the given list of input lines.

    If the input list is empty, return empty list.

    :param lines: Text lines belonging to a common metric type.
    :type lines: Iterable[str]
    :returns: Parsed data items.
    :rtype: List[dict]
    :raises RuntimeError: If input does not conform to the expected format.
    """
    if not lines:
        return list()
    l_help, l_type, *l_others = lines
    name = l_help[7:].split(u" ", 1)[0]
    names = [name]
    if name.endswith(u"_totals"):
        names.append(name[:-7])
    elif name.endswith(u"_info"):
        names.append(name[:-5])
    if l_type[7:].split(u" ", 1)[0] != name:
        raise RuntimeError(f"Mismatching metric type: {l_type}")
    data_items = list()
    for line in l_others:
        l_name, labels_and_rest = line.split(u"{", 1)
        if l_name not in names:
            raise RuntimeError(f"Mismatching metric line name: {line}")
        s_labels, rest = labels_and_rest.split(u"}", 1)
        o_labels = json.loads(f"{{{s_labels}}}".replace(u'\"', u'"'))
        data_item[u"labels"] = o_labels
        values = rest.split(u" ")
        if len(values) not in (1, 2):
            raise RuntimeError(f"Wrong number of values: {line}")
        data_item = dict(
            name=l_name,
            labels=o_labels,
            value=values[0],
        )
        if len(values) == 2:
            data_item[u"timestamp"] = values[1]
    data_items.append(data_item)
    return data_items


def parse_telemetry_text(text):
    """Create structured object based on serialized telemetry data.

    The goal is the object to be serialized to json via dumps().

    For the imput format, see resources/tools/telemetry/serializer.py

    :param text: Textual form of telemetry, leading garbage is ignored.
    :type text: str
    :returns: Strustured metric items according to model.
    :rtype: List[dict]
    """
    parsed_items = list()
    same_type_lines = list()
    garbage = True
    for line in text.splitlines():
        if not line.startswith(u"# HELP"):
            if garbage:
                continue
            same_type_lines.append(line)
            continue
        garbage = False
        # New line type starts, flush the previous type.
        parsed_items.extend(process_telemetry_lines(same_type_lines))
        same_type_lines = list()
        same_type_lines.append(line)
    # Flush the last type.
    parsed_items.extend(process_telemetry_lines(same_type_lines))
    return parsed_items
