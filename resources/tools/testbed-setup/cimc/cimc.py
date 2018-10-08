#!/usr/bin/python
#
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

import cimclib
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("ip", help="CIMC IP address")
parser.add_argument("-u", "--username", help="CIMC username (admin)",
                    default="admin")
parser.add_argument("-p", "--password", help="CIMC password (cisco123)",
                    default="cisco123")
parser.add_argument("-d", "--debug", help="Enable debugging", action="count",
                    default=0)

parser.add_argument("-i", "--initialize",
                    help="Initialize args.ip: Power-Off, reset BIOS defaults, Enable console redir, get LOM MAC addr",
                    action='store_true')
parser.add_argument("-s", "--set",
                    help="Set specific BIOS settings", action='append')
parser.add_argument("--wipe", help="Delete all virtual drives",
                    action='store_true')
parser.add_argument("-r", "--raid", help="Create RAID array",
                    action='store_true')
parser.add_argument("-rl", "--raid-level", help="RAID level", default='10')
parser.add_argument("-rs", "--raid-size", help="RAID size", default=3*571250)
parser.add_argument("-rd", "--raid-disks",
                    help="RAID disks ('[1,2][3,4][5,6]')",
                    default='[1,2][3,4][5,6]')
parser.add_argument("-pxe", "--boot-pxe", help="Reboot using PXE",
                    action='store_true')
parser.add_argument("-hdd", "--boot-hdd", help="Boot using HDD on next boot",
                    action='store_true')
parser.add_argument("-poff", "--power-off", help="Power Off",
                    action='store_true')
parser.add_argument("-pon", "--power-on", help="Power On", action='store_true')
parser.add_argument("-m", "--mac-table",
                    help="Show interface MAC address table",
                    action='store_true')

args = parser.parse_args()

cookie = cimclib.login(args.ip, args.username, args.password)

if args.wipe:
    cimclib.deleteAllVirtualDrives(args.ip, cookie, args.debug)

if args.raid:
    cimclib.createRaid(args.ip, cookie, "raid-virl", args.raid_level, args.raid_size, args.raid_disks, args.debug)

if args.initialize:
    cimclib.powerOff(args.ip, cookie)
    cimclib.restoreBiosDefaultSettings(args.ip, cookie, args.debug)
    cimclib.enableConsoleRedir(args.ip, cookie, args.debug)
    cimclib.powerOn(args.ip, cookie, args.debug)
    cimclib.bootIntoUefi(args.ip, cookie, args.debug)
    lom_mac = cimclib.getLOMMacAddress(args.ip, cookie, args.debug)
    print "Host {} LOM MAC address: {}".format(args.ip, lom_mac)

if args.set:
    cimclib.setBiosSettings(args.ip, cookie, args.set, args.debug)

if args.boot_pxe:
    cimclib.bootPXE(args.ip, cookie, args.debug)

if args.boot_hdd:
    cimclib.bootHDDPXE(args.ip, cookie, args.debug)

if args.power_off:
    cimclib.powerOff(args.ip, cookie, args.debug)

if args.power_on:
    cimclib.powerOn(args.ip, cookie, args.debug)

if args.mac_table:
    maclist = cimclib.getMacAddresses(args.ip, cookie, args.debug)

    for k in sorted(maclist.keys()):
        print "{}:".format(k)
        for p in sorted(maclist[k].keys()):
            print "  {} - {}".format(p, maclist[k][p])

cimclib.logout(args.ip, cookie)
