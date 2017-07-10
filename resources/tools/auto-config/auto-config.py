#!/usr/bin/python

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

"""Script Automatically configures vpp testbeds for optimal performance."""

import argparse
import logging

from resources.libraries.python.AutoConfig import AutoConfig
from resources.libraries.python.VppHugePageUtil import VppHugePageUtil
from resources.libraries.python.VppPCIUtil import VppPCIUtil

'''
autoconfig_show:

Show the current system configuration.
'''


def autoconfig_show(cdargs):
    logging.basicConfig(level=logging.INFO)
    ac = AutoConfig(cdargs.filename)

    for n in ac.get_nodes().values():
        # Show the huge page configuration
        hgp = VppHugePageUtil(n)
        print("\n")
        hgp.show_huge_pages()

        # Show the VPP Device configuration
        vpp = VppPCIUtil(n)
        devices_used = vpp.get_dpdk_devices()
        devices_not_used = vpp.get_kernel_devices()
        devices_not_used += vpp.get_other_devices()
        devices_link_up = vpp.get_link_up_devices()

        print("\nPCI Device Information on {}:".format(n['host']))
        print("These devices are currently being used by the DPDK:\n")
        vpp.show_vpp_devices(devices_used)

        print("\nThese device(s) are being used (link up) by the kernel and can NOT be used by FDIO:\n")
        vpp.show_vpp_devices(devices_link_up)

        print("\nThese device(s) are NOT currently being used by FDIO:\n")
        vpp.show_vpp_devices(devices_not_used)

'''
autoconfig_postboot:

Run all the configuration that is needed after rebooting.
'''


def autoconfig_postboot(cdargs):
    logging.basicConfig(level=logging.DEBUG)
    ac = AutoConfig(cdargs.filename)

    ac.discover()

    ac.apply_postboot()

'''
autoconfig_preboot:

Run all the configuration that is needed before rebooting.
'''


def autoconfig_preboot(cdargs):
    logging.basicConfig(level=logging.DEBUG)
    ac = AutoConfig(cdargs.filename)

    ac.discover()

    ac.apply_preboot()

'''
discover:

Discover the autoconfiguration.
'''


def autoconfig_discover(cdargs):
    logging.basicConfig(level=logging.DEBUG)
    ac = AutoConfig(cdargs.filename)

    ac.discover()

if __name__ == '__main__':
    main_parser = argparse.ArgumentParser(prog='auto-config',
                                          description='Auto configuration tool.',
                                          epilog='See "%(prog)s help COMMAND" for help on a specific command.')
    subparsers = main_parser.add_subparsers()

    itr_parser = subparsers.add_parser('show', help='Show the current system configuration')
    itr_parser.add_argument('filename', help='The file name that contains the autoconfig data')
    itr_parser.set_defaults(func=autoconfig_show)

    itr_parser = subparsers.add_parser('discover', help='Discover system configuration using the autoconfg.yaml file')
    itr_parser.add_argument('filename', help='The file name that contains the autoconfig data')
    itr_parser.set_defaults(func=autoconfig_discover)

    itr_parser = subparsers.add_parser('pre-boot', help='Execute the auto config directly from the autoconfg.yaml file')
    itr_parser.add_argument('filename', help='The file name that contains the autoconfig data')
    itr_parser.set_defaults(func=autoconfig_preboot)

    itr_parser = subparsers.add_parser('post-boot',
                                       help='Execute the auto config directly from the autoconfg.yaml file')
    itr_parser.add_argument('filename', help='The file name that contains the autoconfig data')
    itr_parser.set_defaults(func=autoconfig_postboot)

    args = main_parser.parse_args()

    args.func(args)
