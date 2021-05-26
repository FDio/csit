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

"""Module string few utility functions.
"""

import datetime

from robot.libraries.BuiltIn import BuiltIn


builtin_instance = BuiltIn()
get_variable = builtin_instance.get_variable_value


def descend(parent_node, key, default=None):
    """Get sub-node, create it when it does not exist.

    Without this function:
        child_node = parent_node.get(key, dict())
        parent_node[key] = child_node

    With this function:
        child_node = descend(parent_node, key)

    New code is shorter and avoids the need to type key and parent_node twice.

    :param parent_node: Reference to inner node of a larger structure
        we want to descend from.
    :param key: Key of the maybe existing child node.
    :param default: What to insert if the key does not exist.
        None means dict(). The other option is list().
    :type parent_node: dict
    :type key: str
    :type default: object
    :returns: The reference to (maybe just created) child node.
    :rtype: object
    """
    default = dict() if default is None else default
    child_node = parent_node.get(key, default)
    parent_node[key] = child_node
    return child_node


def get_export_data():
    """Return data member of export_json library instance.

    This assumes the data has been initialized already.

    :returns: Current library instance's data member.
    :rtype: dict
    """
    lib = builtin_instance.get_library_instance(
        u"resources.libraries.python.model.export_json"
    )
    return lib.data


def now():
    """Return string formatted current datetime.

    One-liner, but saves line length in some call sites.

    :returns: Current UTC date and time.
    :rtype: str
    """
    return str(datetime.datetime.utcnow())
