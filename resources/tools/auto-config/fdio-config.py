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

"""Script Configures FDIO for optimal performance."""

import argparse
import logging

from resources.libraries.python.AutoConfig import AutoConfig
from resources.libraries.python.VPPUtil import VPPUtil

FDIO_DEFAULT_FILE = './fdio-config.yaml'

'''
fdio_not_implemented:

This function is not implemented yet.
'''


def fdio_not_implemented(cdargs):
    print cdargs
    print("This function is not impemented yet")


'''
fdio_cpu:

Configure cpu parameters for FDIO.

'''


def fdio_cpu(cdargs):
    logging.basicConfig(level=logging.DEBUG)
    filename = FDIO_DEFAULT_FILE
    if cdargs.file is not None:
        filename = cdargs.file

    ac = AutoConfig(filename)

    ac.apply_cpu()

'''
fdio_grub:

Configure grub for FDIO.

'''


def fdio_grub(cdargs):
    logging.basicConfig(level=logging.DEBUG)
    filename = FDIO_DEFAULT_FILE
    if cdargs.file is not None:
        filename = cdargs.file

    ac = AutoConfig(filename)

    ac.apply_grub()

'''
fdio_hugepages:

Configure huge pages for FDIO.

'''


def fdio_hugepages(cdargs):
    logging.basicConfig(level=logging.DEBUG)
    filename = FDIO_DEFAULT_FILE
    if cdargs.file is not None:
        filename = cdargs.file

    ac = AutoConfig(filename)

    ac.apply_hugepages()

'''
fdio_qemu:

Configure the correct QEMU version.

'''


def fdio_qemu(cdargs):
    logging.basicConfig(level=logging.DEBUG)
    filename = FDIO_DEFAULT_FILE
    if cdargs.file is not None:
        filename = cdargs.file

    ac = AutoConfig(filename)

    ac.patch_qemu()

'''
fdio_devices:

Configure the FDIO devices.

'''


def fdio_devices(cdargs):
    logging.basicConfig(level=logging.DEBUG)
    filename = FDIO_DEFAULT_FILE
    if cdargs.file is not None:
        filename = cdargs.file

    ac = AutoConfig(filename)
    ac.devices_interactive()

    ac.apply_devices()

'''
fdio_uninstall:

Uninstall FDIO.

'''


def fdio_uninstall(cdargs):
    logging.basicConfig(level=logging.DEBUG)
    filename = FDIO_DEFAULT_FILE
    if cdargs.file is not None:
        filename = cdargs.file

    ac = AutoConfig(filename)
    vu = VPPUtil()

    nodes = ac.get_nodes()
    for i in nodes.items():
        node = i[1]
        vu.uninstall_vpp_ubuntu(node)


'''
fdio_install:

Install FDIO.

'''


def fdio_install(cdargs):
    logging.basicConfig(level=logging.DEBUG)
    filename = FDIO_DEFAULT_FILE
    if cdargs.file is not None:
        filename = cdargs.file

    ac = AutoConfig(filename)
    vu = VPPUtil()

    nodes = ac.get_nodes()
    for i in nodes.items():
        node = i[1]
        vu.install_vpp_ubuntu(node)


'''
fdio_show_system:

Show the current system configuration.
'''


def fdio_show_system(cdargs):
    filename = FDIO_DEFAULT_FILE
    if cdargs.file is not None:
        filename = cdargs.file

    ac = AutoConfig(filename)

    ac.discover()

    ac.sys_info()

'''
fdio_all:

Configure cpu parameters for FDIO.

'''


def fdio_all(cdargs):
    logging.basicConfig(level=logging.DEBUG)
    filename = FDIO_DEFAULT_FILE
    if cdargs.file is not None:
        filename = cdargs.file

    ac = AutoConfig(filename)
    vu = VPPUtil()

    # Install VPP
    nodes = ac.get_nodes()
    for i in nodes.items():
        node = i[1]
        vu.install_vpp_ubuntu(node)

    # Huge Pages
    ac.apply_hugepages()

    # Patch qemu
    ac.patch_qemu()

    # Devices
    ac.devices_interactive()
    ac.apply_devices()

    # Grub
    ac.apply_grub()

    # CPU Config
    ac.apply_cpu()

if __name__ == '__main__':
    main_parser = argparse.ArgumentParser(prog='fdio-config',
                                          description="Configuration utility for FDIO")
    main_parser.add_argument('-file', help='FDIO Configuration file, ./fdio-configuration.yaml if none is specified')
    subparsers = main_parser.add_subparsers()

    fdall = subparsers.add_parser('all', help='Do complete FDIO system configuration')
    fdall.set_defaults(func=fdio_not_implemented)

    fdshs = subparsers.add_parser('show-system', help='Show Important System information')
    fdshs.add_argument('-verbose', action='store_true', help='Show Detailed System information')
    fdshs.set_defaults(func=fdio_show_system)

    fdins = subparsers.add_parser('install', help='Install FDIO')
    fdins.set_defaults(func=fdio_install)

    fduns = subparsers.add_parser('uninstall', help='Uninstall FDIO')
    fduns.set_defaults(func=fdio_uninstall)

    fddvc = subparsers.add_parser('devices', help='Configure the FDIO Devices')
    fddvc.set_defaults(func=fdio_devices)

    fdqmu = subparsers.add_parser('qemu', help='Build the correct QEMU version for FDIO')
    fdqmu.set_defaults(func=fdio_qemu)

    fdqmu = subparsers.add_parser('huge-pages', help='Configure Huge Pages for FDIO')
    fdqmu.set_defaults(func=fdio_hugepages)

    fdqmu = subparsers.add_parser('grub', help='Configure grub for FDIO')
    fdqmu.set_defaults(func=fdio_grub)

    fdqmu = subparsers.add_parser('cpu', help='Configure cpu parameters for FDIO')
    fdqmu.set_defaults(func=fdio_cpu)

    fdqmu = subparsers.add_parser('all', help='Configure cpu parameters for FDIO')
    fdqmu.set_defaults(func=fdio_all)

    args = main_parser.parse_args()

    args.func(args)
