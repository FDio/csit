# Copyright (c) 2019 Cisco and/or its affiliates.
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

"""Data store library."""

from pprint import pformat

from robot.api import logger

__all__ = ["DICT__DATASTORE", "DataStore"]


DICT__DATASTORE = dict()


class DataStore(object):
    """Contains methods to store data from test.
    """
    @staticmethod
    def add_item(datastore, value, path):
        """Add data item to data store.

        :param value: Value to insert.
        :param path: Path where to insert item.
        :type value: str
        :type path: list
        """
        if len(path) == 1:
            if path[0] not in datastore:
                datastore[path[0]] = value
            elif isinstance(datastore[path[0]], str):
                datastore[path[0]] = [datastore[path[0]], value]
            else:
                datastore[path[0]].append(value)
            return
        if path[0] not in datastore:
            datastore[path[0]] = {}
        elif isinstance(datastore[path[0]], str):
            if datastore[path[0]] == '':
                datastore[path[0]].update(dict())
            else:
                datastore[path[0]].update([datastore[path[0]], ''])
        DataStore.add_item(datastore[path[0]], value, path[1:])

    @staticmethod
    def add_papi_history_item(node, csit_papi_command):
        """Add command to PAPI command history on DUT node.

        :param node: DUT node to add command to PAPI command history for.
        :param csit_papi_command: Command to be added to PAPI command history.
        :type node: dict
        :type csit_papi_command: str
        """
        path = ['data', 'history', node['host']]
        DataStore.add_item(DICT__DATASTORE, csit_papi_command, path)

    @staticmethod
    def reset_datastore():
        """Reset datastore.
        """
        DICT__DATASTORE = dict()

    @staticmethod
    def dump_datastore():
        """Dump datastore into logger.
        """
        logger.info(pformat(DICT__DATASTORE))


DataStore.reset_datastore()
