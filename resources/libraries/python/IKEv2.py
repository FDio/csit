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

from resources.libraries.python.VatExecutor import VatExecutor, VatTerminal

def set_ipsec_if_up(node, sw_if_index, state):
    VatExecutor.cmd_from_template(node, 'set_if_state.vat',
                              sw_if_index=sw_if_index, state=state)


str_policy = 'strictcrlpolicy=yes\n\n'
ike_def = 'ike=aes256-sha1-modp2048!\n\t'
class StrongSwanConfig():

    def read_config(self,strict_policy=None,ike=None,esp=None,mobike=None,keyexchange=None,
                ikelifetime=None,lifetime=None,right=None,right_subnet=None,
                right_auth=None,right_id=None,left=None,left_subnet=None,left_auth=None,
                left_id=None,auto=None):
        tempFile = "config setup\n\t"
        tempFile += 'strictcrlpolicy={0}\n'.format(strict_policy) if strict_policy else str_policy
        tempFile += 'conn %default\n\t'
        tempFile += 'ike=\n\t' if ike else ike_def
        tempFile += 'esp=\n\t'
        tempFile += 'mobike=\n\t'
        tempFile += 'keyexchange=\n\t'
        tempFile += 'ikelifetime=\n\t'
        tempFile += 'lifetime=\n\n'
        tempFile += 'conn net-net\n\t'
        tempFile += 'right=\n\t'
        tempFile += 'rightsubnet=\n\t'
        tempFile += 'rightauth=\n\t'
        tempFile += 'rightid=\n\t'
        tempFile += 'left=\n\t'
        tempFile += 'leftsubnet=\n\t'
        tempFile += 'leftauth=\n\t'
        tempFile += 'leftid=\n\t'
        tempFile += 'auto=\n'
        print tempFile
        with open('/tmp/ipsec.tmp','w') as conf:
            for line in conf:
                if 'strictcrlpolicy=' in line:
                    tempFile += 'strictcrlpolicy=no\n\t'

                    print tempFile

# StrongSwanConfig().read_config(strict_policy='no')




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