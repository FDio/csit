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

import requests
import xml.etree.ElementTree as et
import re

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

BASEDN = "sys/rack-unit-1"

###
### Helper function - iterate through a list in pairs
###
def chunks(lst, chunksize):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(lst), chunksize):
        yield lst[i:i+chunksize]

###
### Helper function: Perform an XML request to CIMC
###
def xml_req(ip, xml, debug=False):
    if debug:
        print "DEBUG: XML-REQUEST:"
        et.dump(xml)
    headers = {'Content-Type': 'text/xml'}
    req = requests.post('https://' + ip + '/nuova', headers=headers,
                        verify=False, data=et.tostring(xml))
    resp = et.fromstring(req.content)
    if debug:
        print "DEBUG: XML-RESPONSE:"
        et.dump(resp)

    if resp.tag == 'error':
        if debug:
            print "XML response contains error:"
            et.dump(error)
        raise RuntimeError('XML response contains error')
    return resp

###
### Authenticate (Log-In) to CIMC and obtain a cookie
###
def login(ip, username, password):
    reqxml = et.Element('aaaLogin',
                        attrib={'inName':username, 'inPassword':password})
    respxml = xml_req(ip, reqxml)
    try:
        cookie = respxml.attrib['outCookie']
    except:
        print "Cannot find cookie in CIMC server response."
        print "CIMC server output:"
        et.dump(respxml)
        raise

    return cookie

###
### Log out from CIMC.
###
### Note: There is a maximum session limit in CIMC and sessions to take a long
### time (10 minutes) to time out. Therefore, calling this function during
### testing is essential, otherwise one will quickly exhaust all available
### sessions.
###
def logout(ip, cookie):
    reqxml = et.Element('aaaLogout', attrib={'cookie': cookie,
                                             'inCookie': cookie})
    xml_req(ip, reqxml)

###
### Power off the host
###
def powerOff(ip, cookie, debug=False):
    reqxml = et.Element('configConfMo',
                        attrib={'cookie': cookie, 'inHierarchical': 'false',
                                'dn': BASEDN})
    inconfig = et.SubElement(reqxml, 'inConfig')
    et.SubElement(inconfig, 'computeRackUnit',
                  attrib={'adminPower': 'down', 'dn': BASEDN})
    respxml = xml_req(ip, reqxml, debug)
    return respxml

###
### Power on the host
###
def powerOn(ip, cookie, debug=False):
    reqxml = et.Element('configConfMo',
                        attrib={'cookie': cookie, 'inHierarchical': 'false',
                                'dn': BASEDN})
    inconfig = et.SubElement(reqxml, 'inConfig')
    et.SubElement(inconfig, 'computeRackUnit',
                  attrib={'adminPower': 'up', 'dn': BASEDN})
    respxml = xml_req(ip, reqxml, debug)
    return respxml

###
### Restore BIOS to default settings
###
def restoreBiosDefaultSettings(ip, cookie, debug=False):
    reqxml = et.Element('configResolveClass',
                        attrib={'cookie': cookie, 'inHierarchical': 'true',
                                'classId': 'biosPlatformDefaults'})
    respxml = xml_req(ip, reqxml, debug)

    configs = respxml.find('outConfigs')
    defaults = configs.find('biosPlatformDefaults')

    reqxml = et.Element('configConfMo',
                        attrib={'cookie': cookie, 'inHierarchical': 'true',
                                'dn': "{}/bios/bios-settings".format(BASEDN)})
    inconfig = et.SubElement(reqxml, 'inConfig')
    biosset = et.SubElement(inconfig, 'biosSettings')
    biosset.extend(defaults)

    respxml = xml_req(ip, reqxml, debug)
    return respxml

###
### Apply specified BIOS settings.
###
### These must be a list of strings in XML format. Not currently very
### user friendly. Format can either be obtained from CIMC
### documention, or by setting them manually and then fetching
### BIOS settings via CIMC XML API.
###
def setBiosSettings(ip, cookie, settings, debug=False):
    reqxml = et.Element('configConfMo',
                        attrib={'cookie': cookie, 'inHierarchical': 'true',
                                'dn': "{}/bios/bios-settings".format(BASEDN)})
    inconfig = et.SubElement(reqxml, 'inConfig')
    biosset = et.SubElement(inconfig, 'biosSettings')
    print "Applying settings:"
    print settings
    for s in settings:
        x = et.fromstring(s)
        et.dump(x)
        biosset.append(et.fromstring(s))

    respxml = xml_req(ip, reqxml, debug)
    return respxml
###
### Delete any existing virtual drives
###
### WARNING: THIS WILL ERASE ALL DATA ON ALL DISKS, WITHOUT ANY CONFIRMATION
### QUESTION.
###
### The server must be POWERED ON for this to succeed.
###
def deleteAllVirtualDrives(ip, cookie, debug=False):
    reqxml = et.Element('configResolveClass',
                        attrib={'cookie': cookie, 'inHierarchical': 'true',
                                'classId': 'storageController'})
    respxml = xml_req(ip, reqxml, debug)

    configs = respxml.find('outConfigs')
    for sc in configs.iter('storageController'):
        if debug:
            print "DEBUG: SC DN {} ID {}".format(sc.attrib['dn'],
                                                 sc.attrib['id'])
        reqxml = et.Element('configConfMo',
                            attrib={'cookie': cookie, 'inHierarchical': 'true',
                                    'dn': sc.attrib['dn']})
        inconfig = et.SubElement(reqxml, 'inConfig')
        et.SubElement(inconfig, 'storageController',
                      attrib={'adminAction': 'delete-all-vds-reset-pds',
                              'dn': sc.attrib['dn']})
        xml_req(ip, reqxml, debug)

###
### Create a single RAID-10 across all drives.
###
### The server must be POWERED ON for this to succeed.
###
def createRaid10_all(ip, cookie, debug=False):
    reqxml = et.Element('configResolveClass',
                        attrib={'cookie': cookie, 'inHierarchical': 'true',
                                'classId': 'storageController'})
    respxml = xml_req(ip, reqxml, debug)

    configs = respxml.find('outConfigs')
    for sc in configs.iter('storageController'):
        if debug:
            print "DEBUG: SC DN {} ID {}".format(sc.attrib['dn'],
                                                 sc.attrib['id'])
        #
        # Find disk size and number of disks
        #
        disks = []
        total_size = 0
        for pd in sc.iter('storageLocalDisk'):
            if debug:
                print "DEBUG: PD {} size {}".format(pd.attrib['id'],
                                                    pd.attrib['coercedSize'])
            disks.append(pd.attrib['id'])
            total_size += int(pd.attrib['coercedSize'].split(' ')[0])

        #
        # Create a RAID10 array of all available disks, as in:
        # [1,2][3,4][5,6][7,8][9,10][11,12][13,14][15,16][17,18]
        #
        raid_size = total_size/2
        raid_span = ''
        for p in list(chunks(disks, 2)):
            raid_span += "[{},{}]".format(p[0], p[1])

        reqxml = et.Element('configConfMo',
                            attrib={'cookie': cookie, 'inHierarchical': 'true',
                                    'dn': sc.attrib['dn']})
        inconfig = et.SubElement(reqxml, 'inConfig')
        et.SubElement(inconfig,
                      'storageVirtualDriveCreatorUsingUnusedPhysicalDrive',
                      attrib={'virtualDriveName': 'raid10-all',
                              'size': str(raid_size)+' MB',
                              'raidLevel': '10', 'driveGroup': raid_span,
                              'adminState': 'trigger'})

        xml_req(ip, reqxml, debug)

###
### Create a single RAID across from empty drives as provided.
###
### The server must be POWERED ON for this to succeed.
###
def createRaid(ip, cookie, name, raidlevel, size, drives, debug=False):
    reqxml = et.Element('configResolveClass',
                        attrib={'cookie': cookie, 'inHierarchical': 'true',
                                'classId': 'storageController'})
    respxml = xml_req(ip, reqxml, debug)

    configs = respxml.find('outConfigs')
    for sc in configs.iter('storageController'):
        if debug:
            print "DEBUG: SC DN {} ID {}".format(sc.attrib['dn'],
                                                 sc.attrib['id'])

        reqxml = et.Element('configConfMo',
                            attrib={'cookie': cookie, 'inHierarchical': 'true',
                                    'dn': sc.attrib['dn']})
        inconfig = et.SubElement(reqxml, 'inConfig')
        et.SubElement(inconfig,
                      'storageVirtualDriveCreatorUsingUnusedPhysicalDrive',
                      attrib={'virtualDriveName': name,
                              'size': str(size)+' MB',
                              'raidLevel': raidlevel,
                              'driveGroup': drives,
                              'adminState': 'trigger'})

        xml_req(ip, reqxml, debug)

###
### Enable Serial-Over-LAN (SOL) console and redirect BIOS output to
### serial console
###
def enableConsoleRedir(ip, cookie, debug=False):
    reqxml = et.Element('configConfMo',
                        attrib={'cookie': cookie, 'inHierarchical': 'false',
                                'dn': "{}/bios/bios-settings".format(BASEDN)})
    inconfig = et.SubElement(reqxml, 'inConfig')
    bs = et.SubElement(inconfig, 'biosSettings',
                       attrib={'dn': "{}/bios/bios-settings".format(BASEDN)})
    et.SubElement(bs,
                  'biosVfConsoleRedirection',
                  attrib={'vpConsoleRedirection': 'com-0',
                          'vpBaudRate': '115200'})
    respxml = xml_req(ip, reqxml, debug)
    reqxml = et.Element('configConfMo',
                        attrib={'cookie': cookie, 'inHierarchical': 'false',
                                'dn': BASEDN+'/sol-if'})
    inconfig = et.SubElement(reqxml, 'inConfig')
    et.SubElement(inconfig, 'solIf',
                  attrib={'dn': BASEDN+'/sol-if', 'adminState': 'enable',
                          'speed': '115200', 'comport': 'com0'})
    respxml = xml_req(ip, reqxml, debug)
    return respxml

###
### Boot into UEFI bootloader (we may use this to "park" the host in
### powered-on state)
###
def bootIntoUefi(ip, cookie, debug=False):
    reqxml = et.Element('configConfMo',
                        attrib={'cookie': cookie, 'inHierarchical': 'false',
                                'dn': BASEDN+'/boot-policy'})
    inconfig = et.SubElement(reqxml, 'inConfig')
    bootDef = et.SubElement(inconfig, 'lsbootDef',
                            attrib={'dn': BASEDN+'/boot-policy',
                                    'rebootOnUpdate': 'yes'})
    et.SubElement(bootDef, 'lsbootEfi',
                  attrib={'rn': 'efi-read-only', 'order': '1',
                          'type': 'efi'})

    respxml = xml_req(ip, reqxml, debug)
    return respxml

###
### Boot via PXE. Reboot immediately.
###
def bootPXE(ip, cookie, debug=False):
    reqxml = et.Element('configConfMo',
                        attrib={'cookie': cookie, 'inHierarchical': 'false',
                                'dn': BASEDN+'/boot-policy'})
    inconfig = et.SubElement(reqxml, 'inConfig')
    bootDef = et.SubElement(inconfig, 'lsbootDef',
                            attrib={'dn': BASEDN+'/boot-policy',
                                    'rebootOnUpdate': 'yes'})
    et.SubElement(bootDef, 'lsbootLan',
                  attrib={'rn': 'lan-read-only', 'order': '1',
                          'type': 'lan', 'prot': 'pxe'})

    respxml = xml_req(ip, reqxml, debug)
    return respxml


###
### Boot via Local HDD first, then via PXE. Do not reboot immediately.
###
def bootHDDPXE(ip, cookie, debug=False):
    reqxml = et.Element('configConfMo',
                        attrib={'cookie': cookie, 'inHierarchical': 'false',
                                'dn': BASEDN+'/boot-policy'})
    inconfig = et.SubElement(reqxml, 'inConfig')
    bootDef = et.SubElement(inconfig, 'lsbootDef',
                            attrib={'dn': BASEDN+'/boot-policy',
                                    'rebootOnUpdate': 'no'})
    storage = et.SubElement(bootDef, 'lsbootStorage',
                            attrib={'rn': 'storage-read-write',
                                    'access': 'read-write',
                                    'order': '1', 'type': 'storage'})
    et.SubElement(storage, 'lsbootLocalStorage',
                  attrib={'rn': 'local-storage'})
    et.SubElement(bootDef, 'lsbootLan',
                  attrib={'rn': 'lan-read-only', 'order': '2',
                          'type': 'lan', 'prot': 'pxe'})

    respxml = xml_req(ip, reqxml, debug)
    return respxml

###
### Return LOM port 1 MAC address
###
def getLOMMacAddress(ip, cookie, debug=False):
    reqxml = et.Element('configResolveClass',
                        attrib={'cookie': cookie, 'inHierarchical': 'true',
                                'classId': 'networkAdapterUnit'})
    respxml = xml_req(ip, reqxml, debug)
    reqxml = et.Element('configResolveDn',
                        attrib={'cookie': cookie, 'inHierarchical': 'true',
                                'dn': BASEDN+'/network-adapter-L/eth-1'})
    respxml = xml_req(ip, reqxml, debug)

    oc = respxml.find('outConfig')
    netw = oc.find('networkAdapterEthIf')
    if debug:
        print "DEBUG: MAC address is {}".format(netw.get('mac'))
    return netw.get('mac')

###
### Return all port MAC addresses
###
def getMacAddresses(ip, cookie, debug=False):
    maclist = {}
    reqxml = et.Element('configResolveClass',
                        attrib={'cookie': cookie, 'inHierarchical': 'true',
                                'classId': 'networkAdapterUnit'})
    respxml = xml_req(ip, reqxml, debug)
    oc = respxml.find('outConfigs')
    for adapter in oc.iter('networkAdapterUnit'):
        if debug:
            print "DEBUG: ADAPTER SLOT {} MODEL {}".format(adapter.attrib['slot'],
                                                           adapter.attrib['model'])
        slot = adapter.attrib['slot']
        maclist[slot] = {}
        for port in adapter.iter('networkAdapterEthIf'):
            if debug:
                print "DEBUG:    SLOT {} PORT {} MAC {}".format(slot,
                                                                port.attrib['id'],
                                                                port.attrib['mac'])
            maclist[slot][port.attrib['id']] = port.attrib['mac'].lower()

    reqxml = et.Element('configResolveClass',
                        attrib={'cookie': cookie, 'inHierarchical': 'true',
                                'classId': 'adaptorUnit'})
    respxml = xml_req(ip, reqxml, debug)
    oc = respxml.find('outConfigs')
    for adapter in oc.iter('adaptorUnit'):
        if debug:
            print "DEBUG: VIC ADAPTER SLOT {} MODEL {}".format(adapter.attrib['pciSlot'],
                                                               adapter.attrib['model'])
        slot = adapter.attrib['pciSlot']
        maclist[slot] = {}
        for port in adapter.iter('adaptorHostEthIf'):
            portnum = int(re.sub('eth([0-9]+)', '\\1', port.attrib['name']))+1
            if debug:
                print "DEBUG:    VIC SLOT {} PORT {} MAC {}".format(slot,
                                                                    portnum,
                                                                    port.attrib['mac'])
            maclist[slot][portnum] = port.attrib['mac'].lower()

    return maclist
