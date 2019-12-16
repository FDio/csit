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

"""VPP Network Simulator Plugin util library."""

from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.InterfaceUtil import InterfaceUtil


class NsimUtil(object):
    """VPP NSIM Plugin Keywords."""

    @staticmethod
    def configure_vpp_nsim(node, vpp_nsim_attr, interface0, interface1=None):
        """Configure nsim on the specified VPP node.

        :param node: Topology node.
        :param interface0: Interface name.
        :type node: dict
        :type interface0: str or int
        """
        host = node[u"host"]
        if vpp_nsim_attr[u"output_feature_enable"] == False \
               and vpp_nsim_attr[u"cross_connect_feature_enable"] == False:
            logger.trace(f"No NSIM features enabled on host {host}")
            return

        logger.trace(f"vpp_nsim_attr: {vpp_nsim_attr}")
        cmd = u"nsim_configure"
        args = dict(
            delay_in_usec=vpp_nsim_attr[u"delay_in_usec"],
            average_packet_size=vpp_nsim_attr[u"average_packet_size"],
            bandwidth_in_bits_per_second=vpp_nsim_attr[
                u"bandwidth_in_bits_per_second"
            ],
            packets_per_drop=vpp_nsim_attr[u"packets_per_drop"],
        )
        err_msg = f"Failed to configure NSIM on host {host}"
        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)

        logger.trace(f"{cmd} reply : {reply}")
        if vpp_nsim_attr[u"output_feature_enable"] == True:
            cmd = u"nsim_output_feature_enable_disable"
            args = dict(
                enable_disable=vpp_nsim_attr[u"output_feature_enable"],
                sw_if_index=InterfaceUtil.get_interface_index(node, interface0),
            )
            err_msg = f"Failed to enable NSIM output feature on " \
                f"host {host} interface {interface0}"
            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(cmd, **args).get_reply(err_msg)

        elif vpp_nsim_attr[u"cross_connect_feature_enable"] == True:
            cmd = u"nsim_cross_connect_feature_enable_disable"
            args = dict(
                enable_disable=vpp_nsim_attr[u"cross_connect_feature_enable"],
                sw_if_index0=InterfaceUtil.get_interface_index(node,
                                                               interface0),
                sw_if_index1=InterfaceUtil.get_interface_index(node,
                                                               interface1),
            )
            err_msg = f"Failed to enable NSIM output feature on " \
                f"host {host} interface {interface0}"
            with PapiSocketExecutor(node) as papi_exec:
                reply = papi_exec.add(cmd, **args).get_reply(err_msg)

        logger.trace(f"{cmd} reply : {reply}")
        return reply
