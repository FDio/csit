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

"""Module defining class for skipping certain suites based on environment.

If some part of target environment is not known (e.g. topology in tox checker),
no skipping is done (so all possible suites are generated).

If some part of target environment is detected but not covered by code here,
RuntimeError is raised.

Regenerator is calling methods early as it encounters more possibilities,
as early skip can avoid nested loops.

The tox job is special, as it generates all possible suites
so any bug in generator can be triggered.
In this case, skip_* methods return False early.
In all other situations, a suite needs to satisfy all checks to prevent skip.
Thus the skip_* methods generally return True early (immediate skip),
and False leads to subsequent skip_* call on next piece of info.

As the sequence of skip_* calls is known, the instance stores the info
so the latter calls do not need to repeat arguments of the former calls.

Typical causes for skipping include a mismatch in:
+ Number of DUTs.
+ Type of test (TREX, DPDK, VPP device, VPP perf).
+ NIC model (has to be available when topology is known).
+ Links (TG-TG for trex tests, two DUT-DUT for bonding tests).
+ Crypto device for ipsechw.
+ Test tags and functionality available on the testbed (e.g. no vhost on dnv).

When it comes to "number of topology nodes", the situation is complicated.
There are 3 sources of this "nodeness", detected from topology tag,
job name, or suite file name; but there can be subtle differences.
The current implementation handles the details by tracking "trex"
as a separate nodeness value, so trex tests can run both on 2n-clx and 1n-aws,
and additional checks to disallow unexpected combinations.

The current way for detecting ROBOT tags is quite brittle,
as in future the substrings may appear elsewhere in the suite prolog
(e.g. in documentation parts).
But it works and is fast, so good enough for now.
"""

from dataclasses import dataclass
from os import environ
from typing import Dict, List, Optional

from yaml import safe_load, YAMLError

from resources.libraries.python.Constants import Constants

@dataclass
class Filt:
    """Class containing the parsed data, short for Filter.

    In general, filtering based on nic driver could also be added,
    but currently no (additional) logic would be there.
    """

    test_code: Optional[str] = None
    """Name of jenkins job, decisions are based on presence of substrings."""
    topology: Optional[dict] = None
    """Parsed YAML describing reserved testbed, if any."""
    ifaces: Optional[Dict[str, List[dict]]] = None
    """List of interfaces for each node. Present only when topology is.
    Slightly flattened to shorten access to link name or nic model."""
    filename: str = None
    """File name of the currently processed suite template.
    This acts as a crude proxy for robot tags.
    The logic relies on skip_in_filename being called first for any suite."""
    nic_name: str = None
    """Currently processed nic name so skip_prolog_* does not need the argument.
    The logic relies on skip_nic_name_* being called before skip_prolog_*."""

    def __post_init__(self):
        """Detect, process and store environment information."""
        self.test_code = environ.get(u"TEST_CODE", None)
        topo_path = environ.get(u"WORKING_TOPOLOGY", None)
        if not topo_path:
            return
        try:
            with open(topo_path, u"rt", encoding="utf8") as topo_file:
                self.topology = safe_load(topo_file)
        except (OSError, YAMLError):
            return
        self.ifaces = dict()
        for node, ifs in self.topology[u"nodes"].items():
            self.ifaces[node] = list(ifs[u"interfaces"].values())

    def skip_by_filename(self, filename):
        """Store filename, apply several filters.

        Reset nic name possibly set by previous checks.

        Nodeness is determined from the file name and basic checks are done.
        They are refined by test type determined from test code.

        :param filename: File name (without path) of the current suite template.
        :type filename: str
        :returns: True if suites should be skipped.
        :rtype: bool
        """
        self.nic_name = None
        self.filename = filename
        if self.test_code and u"csit-verify-tox-" in self.test_code:
            return False
        twonode_prefixes = (u"2n-", u"2n1l-")
        dpdk_substrs = (u"-l2xcbase-testpmd-", u"-ip4base-l3fwd-")
        non_vpp_substrs = dpdk_substrs + (u"-tg-", u"-scapy.")
        if filename.startswith(u"1n1l-"):
            nodeness = u"trex"
        elif filename.endswith(u"-scapy.robot"):
            nodeness = 1
        elif any(filename.startswith(prefix) for prefix in twonode_prefixes):
            nodeness = 2
        elif filename.startswith(u"10ge2p1x710-"):
            nodeness = 3
        else:
            raise RuntimeError(f"Unknown nodeness: {filename}")
        if self._skip_by_nodeness(nodeness):
            return True
        if self.test_code:
            if u"-trex-" in self.test_code:
                if u"-tg-" not in filename or nodeness != u"trex":
                    return True
            elif u"-dpdk-" in self.test_code:
                if not any(substr in filename for substr in dpdk_substrs):
                    return True
            elif u"-device-" in self.test_code:
                if nodeness != 1:
                    return True
            else:
                # Assuming to be VPP perf test.
                if any(substr in filename for substr in non_vpp_substrs):
                    return True
            # Not skipping due to dpdk/trex/device/perf.
        return False

    def _skip_by_nodeness(self, nodeness):
        """The basic checks mentioned in skip_by_filename.

        Number of nodes in topology (if present) has to match.
        The value in test code has to match.
        Trex works with both 1n and 2n.

        :param nodeness: Value determined from file name.
        :type nodeness: 0, 1, 2, 3, or "trex".
        :returns: True if suites should be skipped.
        :rtype: bool
        """
        if self.topology:
            topo_tags = self.topology[u"metadata"][u"tags"]
            # Ifs have to be two-line, otherwise elifs do not chain correctly.
            if u"dcr" in topo_tags:
                if nodeness != 1:
                    return True
            elif u"1-node" in topo_tags:
                if nodeness != u"trex":
                    return True
            elif u"2-node" in topo_tags:
                if nodeness not in (2, u"trex"):
                    return True
            elif u"3-node" in topo_tags:
                # TODO: What if neither "dcr" nor "hw" in tags (e.g. "vagrant")?
                if nodeness != 3:
                    return True
            elif nodeness == 0:
                raise RuntimeError(f"Unknown nodeness: {topo_tags}")
            # Not skipping due to topology.
        if self.test_code:
            if u"-1n-" in self.test_code:
                if nodeness not in (1, u"trex"):
                    return True
            elif u"-2n-" in self.test_code:
                if nodeness not in (2, u"trex"):
                    return True
            elif u"-3n-" in self.test_code:
                if nodeness != 3:
                    return True
            else:
                raise RuntimeError(f"Unknown nodeness: {self.test_code}")
            # Not skipping due to test code.
        return False

    def skip_by_nic_name(self, nic_name, node=u"DUT1"):
        """Store nic name, check the nic model is in topology if available.

        :param nic_name: Possible NIC model name to check.
        :param node: Which topology node (e.g. DUT1 or TG) has to have the NIC.
        :type nic_name: str
        :type node: str
        :returns: True if suites should be skipped.
        :rtype: bool
        """
        self.nic_name = nic_name
        if not self.topology:
            return False
        return not any(nic_name in ifc[u"model"] for ifc in self.ifaces[node])

    def skip_by_trex_nic_name(self, nic_name):
        """Call skip_by_nic_name for TG, check the NIC has a TG-TG link.

        :param nic_name: Possible NIC model name to check.
        :type nic_name: str
        :returns: True if suites should be skipped.
        :rtype: bool
        """
        if self.skip_by_nic_name(nic_name, u"TG"):
            return True
        if not self.topology:
            return False
        tg_links = [
            ifc[u"link"] for ifc in self.ifaces[u"TG"]
            if ifc[u"model"] == self.nic_name
        ]
        # Set eliminates duplicates, no duplicates mean no looping link.
        return len(tg_links) == len(set(tg_links))

    def get_crypto_hw(self):
        """Return suitable crypto dev model name, or None if not available.

        One-liner to make call sites shorter and more readable.

        :returns: What NIC_NAME_TO_CRYPTO_HW says.
        :rtype: Optional[str]
        """
        return Constants.NIC_NAME_TO_CRYPTO_HW.get(self.nic_name, None)

    def skip_by_crypto_hw(self):
        """Skip an ipsechw suite if testbed without QAT or not matching NIC.

        This is called after skip_by_nic_name.
        The topology only contains the PCI address,
        so we assume the model does match.

        :returns: True if suites should be skipped.
        :rtype: bool
        """
        if self.test_code:
            if u"csit-verify-tox-" in self.test_code:
                return False
            if u"ipsechw" not in self.test_code:
                return True
        if self.topology:
            if u"cryptodev" not in self.topology[u"nodes"][u"DUT1"]:
                return True
        return self.get_crypto_hw() is None

    def _skip_by_double_link(self, prolog):
        """If suite needs double link (and topology is known) check it is there.

        This could be a block in skip_by_prolog,
        but having it as a separate method makes it more easy
        to use "return False" for control flow.

        :param prolog: The (partially edited) part of suite without tests.
        :type prolog: str
        :returns: True if suites should be skipped.
        :rtype: bool
        """
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
        """Apply various checks that depend on Robot tags.

        Checks requirements for double link, flow, vhost and memif.

        :param prolog: The (partially edited) part of suite without tests.
        :type prolog: str
        :returns: True if suites should be skipped.
        :rtype: bool
        """
        if self._skip_by_double_link(prolog):
            return True
        if not self.test_code or u"csit-verify-tox-" in self.test_code:
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
