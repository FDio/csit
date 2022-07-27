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

import glob
import sys
import tempfile

from dataclasses import dataclass, field
from tempfile import TemporaryDirectory

from robot.api import logger

from resources.libraries.python.FilteredLogger import FilteredLogger
from resources.libraries.python.LocalExecution import run
from resources.libraries.python.VppApiCrc import VppApiCrcChecker
from resources.libraries.python.ssh import (exec_cmd_no_error, scp_node)


@dataclass
class Clients:
    """FIXME."""

    node: dict
    """Topology node to connect to and forward unix domain socket from."""
    api_root_dir: TemporaryDirectory = field(init=False)
    """We copy .api json files and PAPI code from DUT to robot machine.
    This field  holds temporary directory once created.
    When python exits, the directory is deleted, so no downloaded file leaks.
    The value will be set to TemporaryDirectory class instance
    (not string path) to ensure deletion at exit."""
    api_json_path: str = field(init=False)
    """String path to .api.json files.
    A directory somewhere in api_root_dir."""
    api_package_path: str = field(init=False)
    """String path to PAPI code, a different directory in api_root_dir."""
    crc_checker: VppApiCrcChecker = field(init=False)
    """Crc checker accesses .api.json files at creation,
    caching speeds up accessing it."""
    reusable_vpp_client_list: u"vpp_api.VPPApiClient" = field(init=False)
    """Each connection needs a separate client instance,
    and each client instance creation needs to parse all .api files,
    which takes time. If a client instance disconnects, it is put here,
    so on next connect we can reuse intead of creating new."""

    def __post_init__(self):
        """Copy files from DUT to local temporary directory.

        If the directory is still there, do not copy again.
        If copying, also initialize CRC checker (this also performs
        static checks), and remember PAPI package path.
        Do not add that to PATH yet.
        """
        self.reusable_vpp_client_list = list()
        self.api_root_dir = tempfile.TemporaryDirectory(dir=u"/tmp")
        root_path = self.api_root_dir.name
        # Pack, copy and unpack Python part of VPP installation from _node.
        # TODO: Use rsync or recursive version of ssh.scp_node instead?
        exec_cmd_no_error(self.node, [u"rm", u"-rf", u"/tmp/papi.txz"])
        # Papi python version depends on OS (and time).
        installed_papi_glob = u"/usr/lib/python3*/*-packages/vpp_papi"
        # We need to wrap this command in bash, in order to expand globs,
        # and as ssh does join, the inner command has to be quoted.
        inner_cmd = u" ".join([
            u"tar", u"cJf", u"/tmp/papi.txz", u"--exclude=*.pyc",
            installed_papi_glob, u"/usr/share/vpp/api"
        ])
        exec_cmd_no_error(self.node, [u"bash", u"-c", u"'" + inner_cmd + u"'"])
        scp_node(
            self.node, root_path + u"/papi.txz", u"/tmp/papi.txz", get=True
        )
        run([u"tar", u"xf", root_path + u"/papi.txz", u"-C", root_path])
        self.api_json_path = root_path + u"/usr/share/vpp/api"
        # Perform initial checks before .api.json files are gone,
        # by creating the checker instance.
        self.crc_checker = VppApiCrcChecker(self.api_json_path)
        # When present locally, we finally can find the installation path.
        self.api_package_path = glob.glob(root_path + installed_papi_glob)[0]
        # Package path has to be one level above the vpp_papi directory.
        self.api_package_path = self.api_package_path.rsplit(u"/", 1)[0]

    def get_client(self):
        """Create or reuse a closed client instance, return it.

        The instance is initialized for unix domain socket access,
        it has initialized all the bindings, it is removed from the internal
        list of disconnected clients, but it is not connected
        (to a local socket) yet.

        :returns: VPP client instance ready for connect.
        :rtype: vpp_papi.VPPApiClient
        """
        if self.reusable_vpp_client_list:
            # Reuse in LIFO fashion.
            *self.reusable_vpp_client_list, ret = self.reusable_vpp_client_list
            return ret
        # Creating an instance leads to dynamic imports from VPP PAPI code,
        # so the package directory has to be present until the instance.
        # But it is simpler to keep the package dir around.
        try:
            sys.path.append(self.api_package_path)
            # TODO: Pylint says import-outside-toplevel and import-error.
            # It is right, we should refactor the code and move initialization
            # of package outside.
            from vpp_papi.vpp_papi import VPPApiClient as vpp_class
            vpp_class.apidir = self.api_json_path
            # We need to create instance before removing from sys.path.
            vpp_client = vpp_class(
                use_socket=True, server_address=u"TBD", async_thread=False,
                read_timeout=14, logger=FilteredLogger(logger, u"INFO")
            )
            # Cannot use loglevel parameter, robot.api.logger lacks support.
            # TODO: Stop overriding read_timeout when VPP-1722 is fixed.
        finally:
            if sys.path[-1] == self.api_package_path:
                sys.path.pop()
        return vpp_client

    def recycle_client(self, vpp_client):
        """Put disconnected client instance back to the reusable list.

        :param vpp_client: Client instance no longer actively used.
        :type vpp_client: vpp_papi.VPPApiClient
        """
        self.reusable_vpp_client_list.append(vpp_client)
