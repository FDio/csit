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

"""Module defining class for excluding certain suites based on environment."""

from dataclasses import dataclass
from os import environ
from typing import Dict, List, Optional

from yaml import safe_load

from resources.libraries.python.Constants import Constants

@dataclass
class Filt:
    """Class containing the parsed data, short for Filter.

    If some part of target environment is not known (e.g. in tox checker),
    no skipping is done (so all possible suites are generated).

    If some part of target environment is detected but not covered by code here,
    exception is raised.
    """

    test_code: Optional[str] = None
    """Name of jenkins job, its specific attributes are extracted elsewhere."""
    topology: Optional[dict] = None
    """Parsed YAML describing reserved testbed, if any."""
    ifaces: Optional[Dict[str, List[dict]]] = None
    """List of interfaces for each node. Present only when topology is."""
    in_filename: str = None
    """Current suite filename, used as a proxy for robot tags.
    The logic relies on skip_in_filename being called first for any suite."""
    nic_name: str = None
    """Currently processed nic name so skip_prolog_* does not need the argument.
    The logic relies on skip_nic_name_* being called before skip_prolog_*."""

    def __post_init__(self):
        """Detect and store environment information."""
        self.test_code = environ.get(u"TEST_CODE", None)
        print(f"Filt init debug: test_code='{self.test_code}'")
        topo_path = environ.get(u"WORKING_TOPOLOGY", None)
        print(f"Filt debug: topo_path='{topo_path}'")
        if not topo_path:
            return
        try:
            with open(topo_path, u"rt", encoding="utf8") as work_file:
                self.topology = safe_load(work_file)
        except RuntimeError:
            pass
        self.ifaces = dict()
        for node, ifaces in self.topology[u"nodes"].items():
            self.ifaces[node] = list(ifaces.values())
        print(f"Filt debug: ifaces='{self.ifaces}'")

    def skip_by_filename(self, in_filename):
        """FIXME!"""
        self.nic_name = None
        self.in_filename = in_filename
        twonode_prefixes = (u"2n-", u"2n1l-", u"1n1l-")
        if in_filename.endswith(u"-scapy.robot"):
            nodeness = 1
        elif any(in_filename.startswith(prefix) for prefix in twonode_prefixes):
            nodeness = 2
        elif in_filename.startswith(u"10ge2p1x710-"):
            nodeness = 3
        else:
            nodeness = 0
        if self.topology:
            # Ifs have to be two-line so elifs chain correctly.
            if u"dcr" in self.topology[u"metadata"][u"tags"]:
                if nodeness != 1:
                    return True
            elif u"2-node" in self.topology[u"metadata"][u"tags"]:
                if nodeness != 2:
                    return True
            elif u"3-node" in self.topology[u"metadata"][u"tags"]:
                # TODO: What if neither "dcr" nor "hw" in tags (e.g. "vagrant")?
                if nodeness != 3:
                    return True
            elif nodeness == 0:
                raise RuntimeError(f"Unknown nodeness: {in_filename}")
            # Not skipping due topology.
        if self.test_code:
            if u"-1n-" in self.test_code:
                if nodeness != 1:
                    return True
            elif u"-2n-" in self.test_code:
                if nodeness != 2:
                    return True
            elif u"-3n-" in self.test_code:
                if nodeness != 3:
                    return True
            elif u"csit-verify-tox-" not in self.test_code:
                raise RuntimeError(f"Unsupported code: {self.test_code}")
            # Not skipping due to test code.
        return False

    def skip_by_nic_name(self, nic_name, node=u"DUT1"):
        """FIXME!"""
        self.nic_name = nic_name
        if not self.topology:
            return False
        return not any(nic_name in ifc[u"model"] for ifc in self.ifaces[node])

    def skip_by_trex_nic_name(self, nic_name):
        """FIXME!"""
        if self.skip_by_nic_name(nic_name, u"TG"):
            return True
        if not self.topology:
            return False
        tg_links = [
            ifc[u"link"] for ifc in self.ifaces[u"TG"]
            if ifc[u"model"] == self.nic_name
        ]
        # Set eliminates duplicate, no duplicates mean no looping link.
        return len(tg_links) == len(set(tg_links))

    def get_crypto_hw(self):
        """FIXME!"""
        return Constants.NIC_NAME_TO_CRYPTO_HW.get(self.nic_name, None)

    def skip_by_crypto_hw(self):
        """FIXME!"""
        if self.test_code and u"ipsechw" not in self.test_code:
            return True
        return self.get_crypto_hw() is None

    def _skip_by_double_link(self, prolog):
        """FIXME!"""
        if not self.topology:
            return False
        if u"3_NODE_DOUBLE_LINK" not in prolog:
            return False
        dut1_links = set(
            ifc[u"link"] for ifc in self.ifaces[u"DUT1"]
            if ifc[u"model"] == self.nic_name
        )
        dut2_links = set(
            ifc[u"link"] for ifc in self.ifaces[u"DUT2"]
            if ifc[u"model"] == self.nic_name
        )
        return len(dut1_links.intersection(dut2_links)) < 2

    def skip_by_prolog(self, prolog):
        """FIXME!"""
        if self._skip_by_double_link(prolog):
            return True
        if not self.test_code:
            return False
        if u"1n-vbox" in self.test_code or u"n-dnv" in self.test_code:
            # Covers also VTS tests.
            if u"| VHOST" in prolog:
                return True
        if u"1n-vbox" in self.test_code or u"1n_tx2" in self.test_code:
            if u"FLOW" in prolog and u"_FLOW" not in prolog:
                return True
        if u"n-dnv" in self.test_code:
            # Covers also srv6-proxy tests.
            if u"MEMIF" in prolog:
                return True
        return False
