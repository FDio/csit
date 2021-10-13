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

"""Module hosting few functions useful when dealing with modelled data."""

from robot.libraries.BuiltIn import BuiltIn


def descend(parent_node, key, default_factory=None):
    """Return a sub-node, create and insert it when it does not exist.

    Without this function:
        child_node = parent_node.get(key, dict())
        parent_node[key] = child_node

    With this function:
        child_node = descend(parent_node, key)

    New code is shorter and avoids the need to type key and parent_node twice.

    :param parent_node: Reference to inner node of a larger structure
        we want to descend from.
    :param key: Key of the maybe existing child node.
    :param default_factory: If the key does not exist, call this
        to create a new value to be inserted under the key.
        None means dict. The other popular option is list.
    :type parent_node: dict
    :type key: str
    :type default_factory: Optional[Callable[[], object]]
    :returns: The reference to (maybe just created) child node.
    :rtype: object
    """
    if key not in parent_node:
        factory = dict if default_factory is None else default_factory
        parent_node[key] = factory()
    return parent_node[key]


def get_export_data():
    """Return data members of export_json library instance.

    This assumes the data has been initialized already.
    Return None if Robot is not running.

    :returns: Current library instance's debug data and info data members.
    :rtype: Optional[Tuple[dict, dict]]
    :raises AttributeError: If library is not imported yet.
    """
    name = u"resources.libraries.python.model.export_json"
    instance = BuiltIn().get_library_instance(name)
    if instance is None:
        return None
    return instance.debug_data, instance.info_data
