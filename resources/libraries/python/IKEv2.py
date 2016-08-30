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

"""IKEv2 and StrongSwan utilities.
"""

from resources.libraries.python.VatExecutor import VatExecutor
from resources.libraries.python.ssh import exec_cmd_no_error, exec_cmd

str_policy = 'strictcrlpolicy=yes\n\n'
ike_def = 'ike=aes256-sha1-modp2048!\n\t'
esp_def = 'esp=aes192-sha1-noesn!\n\t'
mobike_def = 'mobike=no\n\t'
keyexchange_def = 'keyexchange=ikev2\n\t'
ikelifetime_def = 'ikelifetime=24h\n\t'
lifetime_def = 'lifetime=24h\n'
right_def = 'right=192.168.100.3\n\t'
rightsubnet_def = 'rightsubnet=192.168.124.0/24\n\t'
rightauth_def = 'rightauth=psk\n\t'
rightid_def = 'rightid=@vpp.home\n\t'
left_def = 'left=192.168.100.2\n\t'
leftsubnet_def = 'leftsubnet=192.168.255.0/24\n\t'
leftauth_def = 'leftauth=psk\n\t'
leftid_def = 'leftid=@roadwarrior.vpn.example.com\n\t'
auto_def = 'auto=start\n\t'


def set_strongswan_config(node, config_dict):
    """Upon call, can set default strongswan config file if no parameters are
    provided, or any could be specified and ipsec.secrets file is subsequently
    updated.

    Bellow are the keys used from this file :
        /resources/test_data/ikev2/ikev2_variables.py

    KEY_strict_policy: Defines if a fresh CRL must be available in order for
    the peer authentication based on RSA.
    KEY_ike: Comma-separated list of IKE/ISAKMP SA encryption/authentication
    algorithms to be used.
    KEY_esp: Comma-separated list of ESP encryption/authentication algorithms
    to be used for the connection.
    KEY_mobike: Enables the IKEv2 MOBIKE protocol defined by RFC 4555.
    KEY_key_exchange: Method of key exchange (IKE,IKEv1,IKEv2).
    KEY_ike_lifetime: How long the keying channel of a connection should last.
    KEY_lifetime: How long a particular instance of a connection should last.
    KEY_right: Destination interface IP.
    KEY_right_subnet: Destination IP range for TS (Traffic Selector).
    KEY_right_auth: Type of authentication for destination.
    KEY_right_id: Destination ID.
    KEY_left: Source interface IP.
    KEY_left_subnet: Source IP range for TS (Traffic Selector).
    KEY_left_auth: Type of authentication for source.
    KEY_left_id: Source ID
    KEY_auto: What operation, if any, should be done automatically at
    IPsec startup.
    KEY_cacert: CA certificate if needed (OPTIONAL).
    KEY_auth_by: How the two security gateways should authenticate each other
    (OPTIONAL).
    KEY_left_cert: Server certificate name (OPTIONAL).
    KEY_right_cert: Client certificate name (OPTIONAL).

    :param node: The node to connect.
    :param config_dict: Dictionary of values needed for Strongswan config file.
    :type node: dict
    :type config_dict: dict
    """
    temp_file = "config setup\n\t"
    temp_file += 'strictcrlpolicy={0}\n'.format(config_dict['strict_policy']) \
        if config_dict['strict_policy'] else str_policy
    if 'cacet' in config_dict:
        temp_file += 'ca roadwarrior\n\t'
        temp_file += 'cacert={}\n'.format(config_dict['cacert'])
    temp_file += 'conn %default\n\t'
    temp_file += 'ike={}\n\t'.format(config_dict['ike']) \
        if 'ike' in config_dict else ike_def
    temp_file += 'esp={}\n\t'.format(config_dict['esp']) \
        if 'esp' in config_dict else esp_def
    temp_file += 'mobike={}\n\t'.format(config_dict['mobike']) \
        if 'mobike' in config_dict else mobike_def
    temp_file += 'keyexchange={}\n\t'.format(config_dict['key_exchange']) \
        if 'key_exchange' in config_dict else keyexchange_def
    temp_file += 'ikelifetime={}\n\t'.format(config_dict['ike_lifetime']) \
        if 'ike_lifetime' in config_dict else ikelifetime_def
    temp_file += 'lifetime={}\n'.format(config_dict['lifetime']) \
        if 'lifetime' in config_dict else lifetime_def
    if 'auth_by' in config_dict:
        temp_file += '\tauthby={}\n'.format(config_dict['auth_by'])
    temp_file += 'conn net-net\n\t'
    temp_file += 'right={}\n\t'.format(config_dict['right']) \
        if 'right' in config_dict else right_def
    temp_file += 'rightsubnet={}\n\t'.format(config_dict['right_subnet']) \
        if 'right_subnet' in config_dict else rightsubnet_def
    if 'right_cert' in config_dict:
        temp_file += 'rightcert={}\n\t'.format(config_dict['right_cert'])
    temp_file += 'rightauth={}\n\t'.format(config_dict['right_auth']) \
        if 'right_auth' in config_dict else rightauth_def
    temp_file += 'rightid={}\n\t'.format(config_dict['right_id']) \
        if 'right_id' in config_dict else rightid_def
    temp_file += 'left={}\n\t'.format(config_dict['left']) \
        if 'left' in config_dict else left_def
    temp_file += 'leftsubnet={}\n\t'.format(config_dict['left_subnet']) \
        if 'left_subnet' in config_dict else leftsubnet_def
    if 'left_cert' in config_dict:
        temp_file += 'leftcert={}\n\t'.format(config_dict['left_cert'])
    temp_file += 'leftauth={}\n\t'.format(config_dict['left_auth']) \
        if 'left_auth' in config_dict else leftauth_def
    temp_file += 'leftid={}\n\t'.format(config_dict['left_id']) \
        if 'left_id' in config_dict else leftid_def
    temp_file += 'auto={}\n'.format(config_dict['auto']) \
        if 'auto' in config_dict else auto_def

    write_file = 'echo "{}" > /tmp/ipsec.tmp'.format(temp_file)
    exec_cmd_no_error(node, write_file)
    exec_cmd_no_error(node, 'mv /tmp/ipsec.tmp /etc/ipsec.conf', sudo=True)


def set_secrets_strongswan(node, secret):
    """Update ipsec.secrets file with RSA secret key or PSK key.

    :param node: The node to connect.
    :param secret: Either PSK key or RSA file.
    :type node: dict
    :type secret: str
    """
    write_file = 'echo "{}" > /tmp/ipsec.secrets'.format(secret)
    exec_cmd_no_error(node, write_file)
    exec_cmd_no_error(node, 'mv /tmp/ipsec.secrets /etc/ipsec.secrets',
                      sudo=True)


def set_ipsec_if_state(node, sw_if_index, state):
    """Sets IPSEC interface up/down.

    :param node: The node to connect.
    :param sw_if_index: Ipsec index.
    :param state: up/down.
    :type node: dict
    :type sw_if_index: int
    :type state: str
    """
    VatExecutor.cmd_from_template(node, 'set_if_state.vat', state=state,
                                  sw_if_index=sw_if_index)


def set_ipsec_route(node, dst_ip, int_ip, ipsec_if):
    """Set route for ipsec. Temporary because of vat command problem.

    :param node: The node to connect.
    :param dst_ip: Destination IP.
    :param int_ip: IP for the IPSec interface.
    :param ipsec_if: Ipsec interface.
    :type node: dict
    :type dst_ip: str
    :type int_ip: str
    :type ipsec_if: int
    """
    VatExecutor.cmd_from_template(node, 'ikev_ipsec_route.vat',
                                  address=dst_ip,
                                  ipsec_ip=int_ip,
                                  ipsec=ipsec_if)


def set_ikev2_profile(node, name):
    """Set IKEv2 profile for IKE connection.

    :param node: The node to connect.
    :param name: Profile name.
    :type node: dict
    :type name: str
    """
    VatExecutor.cmd_from_template(node, 'ikev2_profile.vat',
                                  name=name)


def set_ikev2_auth(node, name, auth_method, auth_data):
    """Set IKEv2 authentication method and data.

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
    """Set IKEv2 ID. Both local and remote should be set.

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


def set_ikev2_key(node, key):
    """Set IKEv2 RSA key location.

    :param node: The node to connect.
    :param key: Path to key.
    :type node: dict
    :type key: str
    """
    VatExecutor.cmd_from_template(node, 'ikev2_set_key.vat',
                                  file=key)


def set_ikev2_ts(node, name, protocol, sport, eport, saddr, eaddr, place):
    """Set IKEv2 traffic selector for local/remote.

    :param node: The node to connect.
    :param name: Profile name.
    :param protocol: Protocol number.
    :param sport: Start port.
    :param eport: End port.
    :param saddr: Start address.
    :param eaddr: End address.
    :param place: Local/remote.
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


def strongswan_ipsec(node, cmd):
    """Start or stop ipsec.

    :param node: The node to connect.
    :param cmd: Start or stop ipsec
    :type node: dict
    :type cmd: str
    """
    cmd = 'ipsec {}'.format(cmd)
    exec_cmd_no_error(node, cmd, sudo=True)


def get_vpp_ipsec_keys(node, side):
    """Gets the sh ipsec output and retrieves the SPI, crypto and integrity keys.

    :param node: Vpp node.
    :param side: You can specify local or remote.
    :type node:dict
    :type side:str
    :return: SPI, crypto and integrity keys.
    :rtype: tuple
    :raises ValueError: Occurs when no SPI, Encryption and Authentication key
    are found. (IPSec was not configured correctly).
    :raises RuntimeError: Unknown error occured during running sh ipsec command.
    """
    cmd = 'vppctl sh ipsec'
    (out, err) = exec_cmd_no_error(node, cmd, sudo=True)
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
    print("SPI {}: {}".format(side, spi))
    print("Encryption key - {}: {}".format(side, enc_key))
    print("Authentication key - {}: {}".format(side, auth_key))
    return spi, enc_key, auth_key


def transfer_rsa_file(node, file_to_transfer, dst):
    """Takes file and writes it to temp file. Then it is moved to destination
    address.

    :param node: Vpp node.
    :param file_to_transfer: Contents of file to write.
    :param dst: Destination path.
    :type node: dict
    :type file_to_transfer: str
    :type dst: str
    """
    print("File: {}".format(file_to_transfer))
    write_file = 'echo "{}" > /tmp/tempRSA.tmp'.format(file_to_transfer)
    exec_cmd_no_error(node, write_file)
    if 'ike' in dst:
        exec_cmd(node, 'mkdir /tmp/ike', sudo=True)
    exec_cmd_no_error(node, 'mv /tmp/tempRSA.tmp {}'.format(dst), sudo=True)
