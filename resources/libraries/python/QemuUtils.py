# Copyright (c) 2016 Cisco and/or its affiliates.
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

"""QEMU utilities library."""

from resources.libraries.python.QemuNode import QemuNode


class QemuUtils(object):
    """QEMU utilities."""

    def __init__(self):
        self._nodes = {}
        self._nodes_id = {}
        self._nodes_max_id = 0
        self._selected_node = None

    def qemu_get_selected_node(self):
        if self._selected_node is not None:
            return self._nodes[self._selected_node]
        else:
            return None

    def qemu_set_node(self, node):
        self._selected_node = '{}:{}'.format(node['host'], node['port'])
        if not self._nodes.has_key(self._selected_node):
            self._nodes[self._selected_node] = QemuNode()
            self._nodes_id[self._selected_node] = self._nodes_max_id
            self[self._selected_node].qemu_set_node(node)
            self[self._selected_node].qemu_set_id(self._nodes_max_id)
            self._nodes_max_id += 1

    def qemu_add_vhost_user_if(self, *args, **kwargs):
        self[self._selected_node].qemu_add_vhost_user_if(*args, **kwargs)

    def qemu_start(self):
        return self[self._selected_node].qemu_start()

    def qemu_kill(self):
        self[self._selected_node].qemu_kill()

    def qemu_system_status(self):
        return self[self._selected_node].qemu_system_status()

    def qemu_system_powerdown(self):
        self[self._selected_node].qemu_system_powerdown()

    def qemu_quit(self):
        self[self._selected_node].qemu_quit()

    def qemu_clear_socks(self):
        self[self._selected_node].qemu_clear_socks()

    def qemu_system_reset(self):
        self[self._selected_node].qemu_system_reset()
