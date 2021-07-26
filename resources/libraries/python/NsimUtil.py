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

"""VPP Network Simulator Plugin util library."""

from resources.libraries.python.InterfaceUtil import InterfaceUtil
from resources.libraries.python.PapiSocketExecutor import PapiSocketExecutor


class NsimUtil():
    """VPP NSIM Plugin Keywords."""

    @staticmethod
    def configure_vpp_nsim(node, vpp_nsim_attr, interface0, interface1=None):
        """Configure nsim on the specified VPP node.

        :param node: Topology node.
        :param vpp_nsim_attr: VPP NSIM configuration attributes
        :param interface0: Interface name.
        :param interface1: 2nd Interface name for cross-connect feature
        :type node: dict
        :type vpp_nsim_attr: dict
        :type interface0: str or int
        :type interface1: str or int
        :raises RuntimeError: if no NSIM features are enabled or
                vpp papi command fails.
        """
        host = node[u"host"]
        if not vpp_nsim_attr[u"output_nsim_enable"] \
                and not vpp_nsim_attr[u"xc_nsim_enable"]:
            raise RuntimeError(f"No NSIM features enabled on host {host}:\n"
                               f"vpp_nsim_attr = {vpp_nsim_attr}")
        cmd = u"nsim_configure2"
        args = dict(
            delay_in_usec=vpp_nsim_attr[u"delay_in_usec"],
            average_packet_size=vpp_nsim_attr[u"average_packet_size"],
            bandwidth_in_bits_per_second=vpp_nsim_attr[
                u"bw_in_bits_per_second"
            ],
            packets_per_drop=vpp_nsim_attr[u"packets_per_drop"],
            packets_per_reorder=vpp_nsim_attr.get(u"packets_per_reorder", 0)
        )
        err_msg = f"Failed to configure NSIM on host {host}"
        try:
            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(cmd, **args).get_reply(err_msg)
        except AssertionError:
            # Perhaps VPP is an older version
            old_cmd = u"nsim_configure"
            args.pop(u"packets_per_reorder")
            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(old_cmd, **args).get_reply(err_msg)

        if vpp_nsim_attr[u"output_nsim_enable"]:
            cmd = u"nsim_output_feature_enable_disable"
            args = dict(
                enable_disable=vpp_nsim_attr[u"output_nsim_enable"],
                sw_if_index=InterfaceUtil.get_interface_index(node, interface0),
            )
            err_msg = f"Failed to enable NSIM output feature on " \
                f"host {host} interface {interface0}"
            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(cmd, **args).get_reply(err_msg)

        elif vpp_nsim_attr[u"xc_nsim_enable"]:
            cmd = u"nsim_cross_connect_feature_enable_disable"
            args = dict(
                enable_disable=vpp_nsim_attr[u"xc_nsim_enable"],
                sw_if_index0=InterfaceUtil.get_interface_index(node,
                                                               interface0),
                sw_if_index1=InterfaceUtil.get_interface_index(node,
                                                               interface1),
            )
            err_msg = f"Failed to enable NSIM output feature on " \
                f"host {host} interface {interface0}"
            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(cmd, **args).get_reply(err_msg)
