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

"""Implementation of HTTP requests GET, PUT, POST and DELETE used in
communication with Honeycomb.

The HTTP requests are implemented in the class HTTPRequest which uses
requests.request.
"""
import os

from resources.libraries.python.VatExecutor import VatExecutor, VatTerminal
from resources.libraries.python.ssh import  exec_cmd_no_error



str_policy = 'strictcrlpolicy=yes\n\n'
ike_def = 'ike=aes256-sha1-modp2048!\n\t'
esp_def = 'esp=aes192-sha1-noesn!\n\t'
mobike_def = 'mobike=no\n\t'
keyexchange_def='keyexchange=ikev2\n\t'
ikelifetime_def='ikelifetime=24h\n\t'
lifetime_def = 'lifetime=24h\n'
right_def='right=192.168.100.3\n\t'
rightsubnet_def='rightsubnet=192.168.124.0/24\n\t'
rightauth_def='rightauth=psk\n\t'
rightid_def='rightid=@vpp.home\n\t'
left_def='left=192.168.100.2\n\t'
leftsubnet_def='leftsubnet=192.168.255.0/24\n\t'
leftauth_def='leftauth=psk\n\t'
leftid_def='leftid=@roadwarrior.vpn.example.com\n\t'
auto_def='auto=start\n\t'

def set_strongswan_config(node, strict_policy=None, ike=None, esp=None, mobike=None, keyexchange=None,
            ikelifetime=None, lifetime=None, right=None, right_subnet=None,
            right_auth=None, right_id=None, left=None, left_subnet=None, left_auth=None,
            left_id=None, auto=None):
    tempFile = "config setup\n\t"
    tempFile += 'strictcrlpolicy={0}\n'.format(strict_policy) if strict_policy else str_policy
    tempFile += 'conn %default\n\t'
    tempFile += 'ike={}\n\t'.format(ike) if ike else ike_def
    tempFile += 'esp={}\n\t'.format(esp) if esp else esp_def
    tempFile += 'mobike={}\n\t'.format(mobike_def) if mobike else mobike_def
    tempFile += 'keyexchange={}\n\t'.format(keyexchange) if keyexchange else keyexchange_def
    tempFile += 'ikelifetime={}\n\t'.format(ikelifetime) if ikelifetime else ikelifetime_def
    tempFile += 'lifetime={}\n'.format(lifetime) if lifetime else lifetime_def
    tempFile += 'conn net-net\n\t'
    tempFile += 'right={}\n\t'.format(right) if right else right_def
    tempFile += 'rightsubnet={}\n\t'.format(right_subnet) if right_subnet else rightsubnet_def
    tempFile += 'rightauth={}\n\t'.format(right_auth) if right_auth else rightauth_def
    tempFile += 'rightid={}\n\t'.format(right_id) if right_id else rightid_def
    tempFile += 'left={}\n\t'.format(left) if left else left_def
    tempFile += 'leftsubnet={}\n\t'.format(left_subnet) if left_subnet else leftsubnet_def
    tempFile += 'leftauth={}\n\t'.format(left_auth) if left_auth else leftauth_def
    tempFile += 'leftid={}\n\t'.format(left_id) if left_id else leftid_def
    tempFile += 'auto={}\n'.format(auto) if auto else auto_def

    write_file = 'echo "{}" > /tmp/ipsec.tmp'.format(tempFile)
    exec_cmd_no_error(node,write_file)
    exec_cmd_no_error(node,'mv /tmp/ipsec.tmp /etc/ipsec.conf',sudo=True)




def set_ipsec_if_up(node, sw_if_index, state):
    VatExecutor.cmd_from_template(node, 'set_if_state.vat', state=state,
                                  sw_if_index=sw_if_index)

def set_ipsec_route(node, ip, ipsec_if):
    VatExecutor.cmd_from_template(node, 'ikev_ipsec_route.vat',
                              address=ip, ipsec=ipsec_if)
def set_ikev2_profile(node, name):
    VatExecutor.cmd_from_template(node, 'ikev2_profile.vat',
                              name=name)
def set_ikev2_auth(node, name, auth_method, auth_data):
    VatExecutor.cmd_from_template(node, 'ikev2_profile_auth.vat',
                              name=name,
                              auth_method=auth_method,
                              auth_data=auth_data)
def set_ikev2_id(node, name, id_type, id_data, place):
    VatExecutor.cmd_from_template(node, 'ikev2_profile_id.vat',
                              name=name,
                              id_type=id_type,
                              id_data=id_data,
                              place=place)

def set_ikev2_ts(node, name, protocol, sport, eport, saddr, eaddr, place):
    VatExecutor.cmd_from_template(node, 'ikev2_profile_ts.vat',
                              name=name,
                              protocol_number=protocol,
                              start_port=sport,
                              end_port=eport,
                              start_addr=saddr,
                              end_addr=eaddr,
                              place=place)

def strongswan_ipsec(node,cmd):
    cmd = 'ipsec {}'.format(cmd)
    (out,err) = exec_cmd_no_error(node,cmd,sudo=True)


def get_vpp_ipsec_keys(node,side):
    cmd = 'vppctl sh ipsec'
    (out,err) = exec_cmd_no_error(node,cmd,sudo=True)

    if not err:
        for line in out.splitlines():
            if '{}-spi'.format(side) in line:
                spi = line.split(' ')[-3]
                continue
            if '{}-crypto'.format(side) in line:
                enc_key = line.split(' ')[-1]
                continue
            if '{}-integrity'.format(side) in line:
                auth_key = line.split()[-1]
    else:
        raise RuntimeError("Could not get keys for IKEv2")
    if not spi or not enc_key or not auth_key:
        raise ValueError('Could not retrieve SPI or ipsec keys.')
    print "SPI {}: {}".format(side,spi)
    print "Encryption key - {}: {}".format(side,enc_key)
    print "Authentication key - {}: {}".format(side,auth_key)
    return (spi,enc_key,auth_key)

