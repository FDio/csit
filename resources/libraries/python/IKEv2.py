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
from resources.libraries.python.ssh import exec_cmd_no_error

def set_ipsec_if_up(node, sw_if_index, state):
    VatExecutor.cmd_from_template(node, 'set_if_state.vat',
                              sw_if_index=sw_if_index, state=state)
def get_vpp_keys(node):
    cmd = 'vppctl sh ikev2 sa'
    child_occured = False
    take_next_e = False
    take_next_a = False
    (out,err) = exec_cmd_no_error(node,cmd,sudo=True)

    if not err:
        for line in out.splitlines():
            if 'child sa' in line:
                child_occured = True
            if child_occured:
                if 'spi' in line:
                    line = line.split(' ')
                    responderSpi = line[-1]
                if 'SK_e' in line:
                    line = line.split(':')
                    enc_key_I = line[1]
                    take_next_e = True
                    continue
                if 'SK_a' in line:
                    line = line.split(':')
                    auth_key_I = line[1]
                    take_next_a = True
                    continue
                if take_next_e:
                    enc_key_R = line.split(':')[1]
                    take_next_e = False
                if take_next_a:
                    auth_key_R = line.split(':')[1]
                    take_next_a = False
    else:
        raise RuntimeError("Could not get keys for IKEv2")
    print "SPI Right: {}".format(responderSpi)
    print "Encryption key - Right: {}".format(enc_key_R)
    print "Encryption key - Left: {}".format(enc_key_I)
    print "Authentication key - Right: {}".format(auth_key_R)
    print "Authentication key - Left: {}".format(auth_key_I)
    return (responderSpi,enc_key_I,auth_key_I)

str_policy = 'strictcrlpolicy=yes\n\n'
ike_def = 'ike=aes256-sha1-modp2048!\n\t'
esp_def = 'esp=aes192-sha1-esn!\n\t'
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

class StrongSwanConfig():

    def read_config(self,strict_policy=None,ike=None,esp=None,mobike=None,keyexchange=None,
                ikelifetime=None,lifetime=None,right=None,right_subnet=None,
                right_auth=None,right_id=None,left=None,left_subnet=None,left_auth=None,
                left_id=None,auto=None):
        tempFile = "config setup\n\t"
        tempFile += 'strictcrlpolicy={0}\n'.format(strict_policy) if strict_policy else str_policy
        tempFile += 'conn %default\n\t'
        tempFile += 'ike={}\n\t' if ike else ike_def
        tempFile += 'esp={}\n\t' if esp else esp_def
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
        print tempFile
        with open('/tmp/ipsec.tmp','w+') as conf:
            for line in conf:
                if 'strictcrlpolicy=' in line:
                    tempFile += 'strictcrlpolicy=no\n\t'

                    print tempFile
            conf.write(tempFile)
            conf.close()
        os.system('sudo mv /tmp/ipsec.tmp /etc/ipsec.conf')

StrongSwanConfig().read_config()


# config setup
#         strictcrlpolicy=no
#
# conn %default
#         ike=aes256-sha1-modp2048!
#         esp=aes192-sha1-esn!
#         mobike=no
#         keyexchange=ikev2
#         ikelifetime=24h
#         lifetime=24h
#
# conn net-net
#         right=192.168.100.3
#         rightsubnet=192.168.124.0/24
#         rightauth=psk
#         rightid=@vpp.home
#         left=192.168.100.2
#         leftsubnet=192.168.255.0/24
#         leftauth=psk
#         leftid=@roadwarrior.vpn.example.com
#         auto=start