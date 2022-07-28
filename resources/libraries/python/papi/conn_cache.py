# Copyright (c) 2022 Cisco and/or its affiliates.
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

"""FIXME."""

from robot.api import logger


class ConnectionCache:
    """FIXME."""

    def __init__(self):
        """Initialize empty cache of connections."""
        self.cache = dict()

    def set_client_connected(self, client, key):
        """Add a connected client instance into cache.

        If there already is a client for the computed key,
        fail, as it is a sign of resource leakage.

        :param client: VPP client instance in connected state.
        :param key: Arbitrary identifier to distinguish connections.
        :type client: vpp_papi.VPPApiClient
        :type key: collections.abc.Hashable
        :raises RuntimeError: If related key already has a cached client.
        """
        if key in self.cache:
            raise RuntimeError(f"Caching client with existing key: {key}")
        self.cache[key] = client

    def set_client_disconnected(self, key):
        """Add a remove client instance from cache.

        If there is no client for the key, fail,
        as it is a sign of resource leakage.

        :param client: VPP client instance in connected state.
        :param key: Arbitrary identifier to distinguish connections.
        :type client: vpp_papi.VPPApiClient
        :type key: collections.abc.Hashable
        :raises RuntimeError: If related key already has a cached client.
        """
        if key not in self.cache:
            raise RuntimeError(f"Uncaching client without existing key: {key}")
        del self.cache[key]

    def get_connected_client(self, key):
        """Return None or cached connected client.

        If check_connected, RuntimeError is raised when the client is
        not in cache. None is returned if client is not in cache
        (and the check is disabled).

        :param key: Arbitrary identifier to distinguish connections.
        :param check_connected: Whether cache miss raises.
        :type check_connected: bool
        :type key: collections.abc.Hashable
        :returns: Connected client instance, or None if uncached and no check.
        :rtype: Optional[vpp_papi.VPPApiClient]
        :raises RuntimeError: If cache miss and check enabled.
        """
        ret = self.cache.get(key, None)
        if ret is None:
            logger.debug(f"Client not cached for key: {key}")
        else:
            # When reading logs, it is good to see which VPP is accessed.
            logger.debug(f"Activated cached PAPI client for key: {key}")
        return ret
