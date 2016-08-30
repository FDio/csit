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
from resources.libraries.python.ssh import  exec_cmd_no_error, exec_cmd



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

def set_strongswan_config(node, strict_policy=None, ike=None, esp=None,
                          mobike=None, keyexchange=None, ikelifetime=None,
                          lifetime=None, right=None, right_subnet=None,
                          right_auth=None, right_id=None, left=None,
                          left_subnet=None, left_auth=None, left_id=None,
                          auto=None, cacert=None, authby=None, leftcert=None, rightcert=None):
    """
    Upon call, can set default strongswan config file if no parameters are
    provided, or any could be specified and ipsec.secrets file is subsequently
    updated.

    :param node: The node to connect.
    :param strict_policy: Defines if a fresh CRL must be available in order for
    the peer authentication based on RSA.
    :param ike: Comma-separated list of IKE/ISAKMP SA encryption/authentication
    algorithms to be used.
    :param esp: Comma-separated list of ESP encryption/authentication algorithms
    to be used for the connection.
    :param mobike: Enables the IKEv2 MOBIKE protocol defined by RFC 4555.
    :param keyexchange: Method of key exchange (IKE,IKEv1,IKEv2).
    :param ikelifetime: How long the keying channel of a connection should last.
    :param lifetime: How long a particular instance of a connection should last.
    :param right: Destination interface IP.
    :param right_subnet: Destination IP range for TS (Traffic Selector).
    :param right_auth: Type of authentication for destination.
    :param right_id: Destination ID.
    :param left: Source interface IP.
    :param left_subnet: Source IP range for TS (Traffic Selector).
    :param left_auth: Type of authentication for source.
    :param left_id: Source ID
    :param auto: What operation, if any, should be done automatically at
    IPsec startup.
    :param cacert: CA certificate if needed (OPTIONAL).
    :param authby: How the two security gateways should authenticate each other
    (OPTIONAL).
    :param leftcert: Server certificate name (OPTIONAL).
    :param rightcert: Client certificate name (OPTIONAL).

    :type node: dict
    :type strict_policy: str
    :type ike: str
    :type esp: str
    :type mobike: str
    :type keyexchange: str
    :type ikelifetime: str
    :type lifetime: str
    :type right: str
    :type right_subnet: str
    :type right_auth: str
    :type right_id: str
    :type left: str
    :type left_subnet: str
    :type left_auth: str
    :type left_id: str
    :type cacert: str
    :type authby: str
    :type leftcert: str
    :type rightcert: str
    :type auto: str
    """
    tempFile = "config setup\n\t"
    tempFile += 'strictcrlpolicy={0}\n'.format(strict_policy) if strict_policy \
        else str_policy
    if cacert:
        tempFile += 'ca roadwarrior\n\t'
        tempFile += 'cacert={}\n'.format(cacert)
    tempFile += 'conn %default\n\t'
    tempFile += 'ike={}\n\t'.format(ike) if ike else ike_def
    tempFile += 'esp={}\n\t'.format(esp) if esp else esp_def
    tempFile += 'mobike={}\n\t'.format(mobike) if mobike else mobike_def
    tempFile += 'keyexchange={}\n\t'.format(keyexchange) if keyexchange \
        else keyexchange_def
    tempFile += 'ikelifetime={}\n\t'.format(ikelifetime) if ikelifetime \
        else ikelifetime_def
    tempFile += 'lifetime={}\n'.format(lifetime) if lifetime else lifetime_def
    if authby:
        tempFile += '\tauthby={}\n'.format(authby)
    tempFile += 'conn net-net\n\t'
    tempFile += 'right={}\n\t'.format(right) if right else right_def
    tempFile += 'rightsubnet={}\n\t'.format(right_subnet) if right_subnet \
        else rightsubnet_def
    if rightcert:
        tempFile += 'rightcert={}\n\t'.format(rightcert)
    tempFile += 'rightauth={}\n\t'.format(right_auth) if right_auth \
        else rightauth_def
    tempFile += 'rightid={}\n\t'.format(right_id) if right_id else rightid_def
    tempFile += 'left={}\n\t'.format(left) if left else left_def
    tempFile += 'leftsubnet={}\n\t'.format(left_subnet) if left_subnet \
        else leftsubnet_def
    if leftcert:
        tempFile += 'leftcert={}\n\t'.format(leftcert)
    tempFile += 'leftauth={}\n\t'.format(left_auth) if left_auth \
        else leftauth_def
    tempFile += 'leftid={}\n\t'.format(left_id) if left_id else leftid_def
    tempFile += 'auto={}\n'.format(auto) if auto else auto_def

    write_file = 'echo "{}" > /tmp/ipsec.tmp'.format(tempFile)
    exec_cmd_no_error(node,write_file)
    exec_cmd_no_error(node,'mv /tmp/ipsec.tmp /etc/ipsec.conf',sudo=True)

def set_secrets_strongswan(node, secret):
    """
    Update ipsec.secrets file with RSA secret key or PSK key.

    :param node: The node to connect.
    :param secret: Either PSK key or RSA file.
    :type node: dict
    :type secret: str
    """
    write_file = 'echo "{}" > /tmp/ipsec.secrets'.format(secret)
    exec_cmd_no_error(node,write_file)
    exec_cmd_no_error(node,'mv /tmp/ipsec.secrets /etc/ipsec.secrets',sudo=True)

def set_ipsec_if_state(node, sw_if_index, state):
    """
    Sets IPSEC interface up/down.

    :param node: The node to connect.
    :param sw_if_index: Ipsec index.
    :param state: up/down.
    :type node: dict
    :type sw_if_index: int
    :type state: str
    """
    VatExecutor.cmd_from_template(node, 'set_if_state.vat', state=state,
                                  sw_if_index=sw_if_index)

def set_ipsec_route(node, ip, ipsec_if):
    """
    Set route for ipsec. Temporary because of vat command problem.

    :param node: The node to connect.
    :param ip: Source IP.
    :param ipsec_if: Ipsec interface.
    :type node: dict
    :type ip: str
    :type ipsec_if: int
    """
    VatExecutor.cmd_from_template(node, 'ikev_ipsec_route.vat',
                              address=ip, ipsec=ipsec_if)
def set_ikev2_profile(node, name):
    """
    Set IKEv2 profile for IKE connection.

    :param node: The node to connect.
    :param name: Profile name.
    :type node: dict
    :type name: str
    """
    VatExecutor.cmd_from_template(node, 'ikev2_profile.vat',
                              name=name)
def set_ikev2_auth(node, name, auth_method, auth_data):
    """
    Set IKEv2 authentication method and data.

    :param node: The node to connect.
    :param name: Profile name.
    :param auth_method: Method of authentication.
    :param auth_data: Data for authentication.
    :type node: dict
    :type name: str
    :type auth_method: str
    :type auth_data: str
    """
    VatExecutor.cmd_from_template(node, 'ikev2_profile_auth.vat',
                              name=name,
                              auth_method=auth_method,
                              auth_data=auth_data)
def set_ikev2_id(node, name, id_type, id_data, place):
    """
    Set IKEv2 ID. Both local and remote should be set.

    :param node: The node to connect.
    :param name: Profile name.
    :param id_type: ID type.
    :param id_data: ID data.
    :param place: Local/remote.
    :type node: dict
    :type name: str
    :type id_type: str
    :type id_data: str
    :type place: str
    """
    VatExecutor.cmd_from_template(node, 'ikev2_profile_id.vat',
                              name=name,
                              id_type=id_type,
                              id_data=id_data,
                              place=place)
def set_ikev2_key(node,key):
    """
    Set IKEv2 RSA key location

    :param node: The node to connect.
    :param key: Path to key.
    :type node: dict
    :type key: str
    """
    VatExecutor.cmd_from_template(node, 'ikev2_set_key.vat',
                      file=key)

def set_ikev2_ts(node, name, protocol, sport, eport, saddr, eaddr, place):
    """
    Set IKEv2 traffic selector for local/remote.

    :param node: The node to connect.
    :param name: Profile name.
    :param protocol: Protocol number.
    :param sport: Start port.
    :param eport: End port.
    :param saddr: Start address.
    :param eaddr: End address.
    :param place: Local/remote
    :type node: dict
    :type name: str
    :type protocol: int
    :type sport: int
    :type eport: int
    :type saddr: str
    :type eaddr: str
    :type place: str
    """
    VatExecutor.cmd_from_template(node, 'ikev2_profile_ts.vat',
                              name=name,
                              protocol_number=protocol,
                              start_port=sport,
                              end_port=eport,
                              start_addr=saddr,
                              end_addr=eaddr,
                              place=place)

def strongswan_ipsec(node,cmd):
    """
    Start or stop ipsec.

    :param node: The node to connect.
    :param cmd: Start or stop ipsec
    :type node: dict
    :type cmd: str
    """
    cmd = 'ipsec {}'.format(cmd)
    exec_cmd_no_error(node,cmd,sudo=True)


def get_vpp_ipsec_keys(node,side):
    """
    Gets the sh ipsec output and retrieves the SPI, crypto and integrity keys.

    :param node: Vpp node.
    :param side: You can specify local or remote.
    :type node:dict
    :type side:str
    :return: SPI, crypto and integrity keys.
    :rtype: tuple
    """
    cmd = 'vppctl sh ipsec'
    (out,err) = exec_cmd_no_error(node,cmd,sudo=True)
    spi = None
    enc_key = None
    auth_key = None
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

def transfer_rsa_file(node, file, dst):
    """
    Takes file and writes it to temp file. Then it is moved to destination
    address.

    :param node: Vpp node.
    :param file: Contents of file to write.
    :param dst: Destination path.
    :type node: dict
    :type file: str
    :type dst: str
    """
    print "File: {}".format(file)
    write_file = 'echo "{}" > /tmp/tempRSA.tmp'.format(file)
    exec_cmd_no_error(node,write_file)
    if 'ike' in dst:
        exec_cmd(node,'mkdir /tmp/ike',sudo=True)
    exec_cmd_no_error(node,'mv /tmp/tempRSA.tmp {}'.format(dst),sudo=True)

