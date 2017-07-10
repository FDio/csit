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
import subprocess

from resources.libraries.python.AutoConfig import AutoConfig
from resources.libraries.python.VppHugePageUtil import VppHugePageUtil
from resources.libraries.python.VppPCIUtil import VppPCIUtil

'''
autoconfig_sys_info:

Show the current system configuration.
'''


def autoconfig_sys_info(cdargs):
    ac = AutoConfig(cdargs.filename)

    ac.discover()

    ac.sys_info()

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
autoconfig_qemu_patch:

Build qemu with correct patches.
'''


def autoconfig_qemu_patch(cdargs):
    logging.basicConfig(level=logging.DEBUG)
    ac = AutoConfig(cdargs.filename)

    ac.patch_qemu()


'''
autoconfig_setup:

Setup the Auto Config utility.
'''


def autoconfig_setup():
    logging.basicConfig(level=logging.DEBUG)
    ac = AutoConfig(args.filename)

    cmd = 'mkdir /tmp/openvpp-testing'
    print("CMD: {}".format(cmd))
    p = subprocess.Popen(cmd, shell=True,
                         bufsize=1,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    ret = p.wait()
    print("RET: {}".format(ret))
    print("OUT: {}".format(stdout))
    print("ERR: {}".format(stderr))

    cmd = 'cp -r ../../../resources /tmp/openvpp-testing'
    print("CMD: {}".format(cmd))
    p = subprocess.Popen(cmd, shell=True,
                         bufsize=1,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    ret = p.wait()
    print("RET: {}".format(ret))
    print("OUT: {}".format(stdout))
    print("ERR: {}".format(stderr))

    cmd = 'service vpp stop'
    print("CMD: {}".format(cmd))
    p = subprocess.Popen(cmd, shell=True,
                         bufsize=1,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    ret = p.wait()
    print("RET: {}".format(ret))
    print("OUT: {}".format(stdout))
    print("ERR: {}".format(stderr))

    cmd = 'cp ./startup.conf.basic /etc/vpp/startup.conf'
    print("CMD: {}".format(cmd))
    p = subprocess.Popen(cmd, shell=True,
                         bufsize=1,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    ret = p.wait()
    print("RET: {}".format(ret))
    print("OUT: {}".format(stdout))
    print("ERR: {}".format(stderr))

    cmd = 'service vpp start'
    print("CMD: {}".format(cmd))
    p = subprocess.Popen(cmd, shell=True,
                         bufsize=1,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    ret = p.wait()
    print("RET: {}".format(ret))
    print("OUT: {}".format(stdout))
    print("ERR: {}".format(stderr))

'''
autoconfig_all:

Does the complete autoconfig.

'''


def autoconfig_all(cdargs):
    # logging.basicConfig(level=logging.DEBUG)
    ac = AutoConfig(cdargs.filename)

    # Get the devices
    ac.devices_interactive()

    # Apply the post boot functions
    ac = AutoConfig(cdargs.filename)
    ac.discover()
    ac.apply_postboot()

'''
autoconfig_main:

Handles the argument and call the corect functions.
'''


def autoconfig_main(cdargs):
    if cdargs.sys_info:
        autoconfig_sys_info(cdargs)
        return
    if cdargs.sys_analyze:
        print("Sys Analyze not implemented yet.")
        return
    if cdargs.setup:
        autoconfig_setup()
        return
    if cdargs.qemu_patch:
        autoconfig_qemu_patch(cdargs)
        return
    if cdargs.pre_boot:
        autoconfig_preboot(cdargs)
        return
    if cdargs.post_boot:
        autoconfig_postboot(cdargs)
        return

    # If there are no arguments specified, do the complete auto config
    autoconfig_all(cdargs)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='auto-config',
                                     description='Auto configuration tool.',
                                     epilog='See "%(prog)s help COMMAND" for help on a specific command.')
    parser.add_argument('filename', help='The file to be used for the autoconfig data')
    parser.add_argument('-sys-info', action='store_true', help='Show the current system Information')
    parser.add_argument('-sys-analyze', action='store_true', help='Analyze the current system.')
    parser.add_argument('-pre-boot', action='store_true', help='Execute the pre boot configuration')
    parser.add_argument('-post-boot', action='store_true', help='Execute the post boot configuration')
    parser.add_argument('-qemu-patch', action='store_true', help='Build and install a correctly patched qemu')
    parser.add_argument('-setup', action='store_true', help='Bui')

    args = parser.parse_args()
    autoconfig_main(args)
