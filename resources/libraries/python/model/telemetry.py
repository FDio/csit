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
    garbage = True
    for line in text.splitlines():
        if line.startswith(u"# HELP"):
            garbage = False
        if garbage or len(line) <= 2 or line.startswith(u"#"):
            continue
        name, rest = line.split(u"{", 1)
        s_labels, rest = rest.split(u"} ", 1)
        s_labels = s_labels.replace(u'\"', u'"').split(u",")
        o_labels = dict()
        for label in s_labels:
            key, value = label.split(u"=", 1)
            if len(value) >= 2 and value[0] == value[-1] == u'"':
                value = value[1:-1]
            # TODO: Else convert to float or int or bool or whatever.
            o_labels[key] = value
        values = rest.split(u" ")
        if len(values) not in (1, 2):
            raise RuntimeError(f"Wrong number of values: {line}")
        data_item = dict(
            name=name,
            labels=o_labels,
            value=values[0],
        )
        if len(values) == 2:
            data_item[u"timestamp"] = values[1]
        parsed_items.append(data_item)
    return parsed_items
