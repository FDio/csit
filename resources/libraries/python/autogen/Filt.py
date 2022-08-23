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
from typing import Optional

from yaml import safe_load

@dataclass
class Filt:
    """Class containing the parsed data, short for Filter.

    If some part of target environment is not known (e.g. in tox checker),
    no skipping is done (so all possible suites are generated).

    If some part of target environment is detected but not covered by code here,
    exception is raised.
    """

    topology: Optional[dict] = None
    """Parsed YAML describing reserved testbed, if any."""
    test_code: Optional[str] = None
    """Name of jenkins job, its specific attributes are extracted elsewhere."""

    def __post_init__(self):
        """Detect and store environment information."""
        self.test_code = environ.get(u"TEST_CODE", None)
        topo_path = environ.get(u"WORKING_TOPOLOGY", None)
        if topo_path:
            try:
                with open(topo_path) as work_file:
                    self.topology = safe_load(work_file)
            except RuntimeError:
                pass

    def skip_in_filename(self, in_filename):
        """FIXME!"""
        twonode_prefixes = (u"2n-", u"2n1l-", u"1n1l-")
        if in_filename.endswith(u"-scapy.robot"):
            nodeness = 1
        elif any(in_filename.startswith(prefix) for prefix in twonode_prefixes):
            nodeness = 2
        elif in_filename.startswith(u"10ge2p1x710-"):
            nodeness = 3
        else:
            nodeness = 0
        print(f"nodeness {nodeness}")
        if self.topology:
            # Ifs have to be two-line so elifs chain correctly.
            if u"dcr" in self.topology[u"metadata"][u"tags"]:
                if nodeness != 1:
                    return True
            elif u"2-node" in self.topology[u"metadata"][u"tags"]:
                if nodeness != 2:
                    return True
            elif u"3-node" in self.topology[u"metadata"][u"tags"]:
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

    def _skip_nic_name_common(self, nic_name, node_name):
        """FIXME!"""
        if self.topology:
            ifaces = self.topology[u"nodes"][node_name][u"interfaces"]
            if not any(nic_name in ifc[u"model"] for ifc in ifaces.values()):
                return True
        return False

    def skip_nic_name_for_default(self, nic_name):
        """FIXME!"""
        return self._skip_nic_name_common(nic_name, u"DUT1")

    def skip_nic_name_for_default_hw(self, nic_name):
        """FIXME!"""
        return self._skip_nic_name_common(nic_name, u"DUT1")

    def skip_nic_name_for_dpdk(self, nic_name):
        """FIXME!"""
        return self._skip_nic_name_common(nic_name, u"DUT1")

    def skip_nic_name_for_reconf(self, nic_name):
        """FIXME!"""
        return self._skip_nic_name_common(nic_name, u"DUT1")

    def skip_nic_name_for_tcp(self, nic_name):
        """FIXME!"""
        return self._skip_nic_name_common(nic_name, u"DUT1")

    def skip_nic_name_for_iperf3(self, nic_name):
        """FIXME!"""
        return self._skip_nic_name_common(nic_name, u"DUT1")

    def skip_nic_name_for_trex(self, nic_name):
        """FIXME!"""
        return self._skip_nic_name_common(nic_name, u"TG")

    def skip_nic_name_for_device(self, nic_name):
        """FIXME!"""
        return self._skip_nic_name_common(nic_name, u"DUT1")

    def _skip_driver_common(self, driver):
        """FIXME!"""
        # FIXME: Copy from bootstrap exclusions.
        return False

    def skip_driver_for_vpp(self, driver):
        """FIXME!"""
        return self._skip_driver_common(driver)

    def skip_driver_for_dpdk(self, driver):
        """FIXME!"""
        return self._skip_driver_common(driver)

    def skip_driver_for_reconf(self, driver):
        """FIXME!"""
        return self._skip_driver_common(driver)

    def skip_driver_for_tcp(self, driver):
        """FIXME!"""
        return self._skip_driver_common(driver)

    def skip_driver_for_device(self, driver):
        """FIXME!"""
        return self._skip_driver_common(driver)

    def _skip_suite_tag_common(self, suite_tag):
        """FIXME!"""
        # FIXME: Copy from bootstrap exclusions.
        return False

    def skip_suite_tag_for_vpp(self, suite_tag):
        """FIXME!"""
        return self._skip_suite_tag_common(suite_tag)

    def skip_suite_tag_for_dpdk(self, suite_tag):
        """FIXME!"""
        return self._skip_suite_tag_common(suite_tag)

    def skip_suite_tag_for_reconf(self, suite_tag):
        """FIXME!"""
        return self._skip_suite_tag_common(suite_tag)

    def skip_suite_tag_for_tcp(self, suite_tag):
        """FIXME!"""
        return self._skip_suite_tag_common(suite_tag)

    def skip_suite_tag_for_iperf3(self, suite_tag):
        """FIXME!"""
        return self._skip_suite_tag_common(suite_tag)

    def skip_suite_tag_for_trex(self, suite_tag):
        """FIXME!"""
        return self._skip_suite_tag_common(suite_tag)

    def skip_suite_tag_for_device(self, suite_tag):
        """FIXME!"""
        return self._skip_suite_tag_common(suite_tag)
