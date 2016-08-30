rsa_path= '${EXECDIR}/resources/test_data/ikev2/ikev2_rsa'

dst_tun_ip=  '10.0.0.5'
src_tun_ip=  '10.0.0.10'
src_ip=  '10.0.10.1'
dst_ip=  '10.0.5.1'
prefix=  '24'
ipsec_index=  '6'

STRONGSWAN_CONF_DEFAULT = {
    'strict_policy' :  'no',
    'ike' :  'aes256-sha1-modp2048!',
    'esp' :  'aes192-sha1-noesn!',
    'mobike' :  'no',
    'key_exchange' :  'ikev2',
    'ike_lifetime' :  '24h',
    'lifetime' :  '24h',
    'default_secret' : ': PSK "Vpp123"',
    'right' : '10.0.0.5',
    'right_subnet' : '10.0.5.1/24',
    'right_auth' : 'psk',
    'left' : '10.0.0.10',
    'left_subnet' : '10.0.10.1/24',
    'left_auth' : 'psk'

}

RSA_CONF = {
    'strict_policy' :  'no',
    'ike' :  'aes256-sha1-modp2048!',
    'esp' :  'aes192-sha1-noesn!',
    'mobike' :  'no',
    'key_exchange' :  'ikev2',
    'ike_lifetime' :  '24h',
    'lifetime' :  '24h',
    'default_secret' : ': RSA server-key.pem',
    'right' : '10.0.0.5',
    'right_subnet' : '10.0.5.1/24',
    'right_auth' : 'pubkey',
    'left' : '10.0.0.10',
    'left_subnet' : '10.0.10.1/24',
    'left_auth' : 'pubkey',
    'swan_secret' :  ': RSA server-key.pem',
    'vpp_key' :  '/tmp/ike/client-key.pem',
    'cacert' :  'ca-cert.pem',
    'auth_by' :  'rsasig',
    'right_cert' :  'client-cert.pem',
    'left_cert' :  'server-cert.pem'

}

ID_IP = {
    'pr_name' : 'pr0',
    'auth_method' : 'shared-key-mic' ,
    'auth_data' : 'Vpp123',
    'id_type_loc' : 'ip4-addr',
    'id_data_loc' : '192.168.100.1',
    'id_type_rem' : 'ip4-addr',
    'id_data_rem' : '192.168.200.1',
    'protocol_loc' : 0,
    'protocol_rem' : 0,
    'sport_loc' : 0,
    'eport_loc' : 65535,
    'saddr_loc' : '10.0.5.0',
    'eaddr_loc' : '10.0.5.255',
    'sport_rem' : 0,
    'eport_rem' : 65535,
    'saddr_rem' : '10.0.10.0',
    'eaddr_rem' : '10.0.10.255',
    'right_id' : '192.168.100.1',
    'left_id' : '192.168.200.1',
    'auto' : 'start'

}

PSK = {
    'pr_name' : 'pr0',
    'auth_method' : 'shared-key-mic' ,
    'auth_data' : 'Vpp123',
    'id_type_loc' : 'fqdn',
    'id_data_loc' : 'vpp.home',
    'id_type_rem' : 'fqdn',
    'id_data_rem' : 'roadwarrior.vpn.example.com',
    'protocol_loc' : 0,
    'protocol_rem' : 0,
    'sport_loc' : 0,
    'eport_loc' : 65535,
    'saddr_loc' : '10.0.5.0',
    'eaddr_loc' : '10.0.5.255',
    'sport_rem' : 0,
    'eport_rem' : 65535,
    'saddr_rem' : '10.0.10.0',
    'eaddr_rem' : '10.0.10.255',
    'right_auth' : 'psk',
    'left_auth' : 'psk',
    'right_id' : '@vpp.home',
    'left_id' : '@roadwarrior.vpn.example.com'

}

ID_RFC = {
    'pr_name' : 'pr0',
    'auth_method' : 'shared-key-mic' ,
    'auth_data' : 'Vpp123',
    'id_type_loc' : 'rfc822',
    'id_data_loc' : 'vpp@cisco.com',
    'id_type_rem' : 'rfc822',
    'id_data_rem' : 'roadwarrior@cisco.com',
    'protocol_loc' : 0,
    'protocol_rem' : 0,
    'sport_loc' : 0,
    'eport_loc' : 65535,
    'saddr_loc' : '10.0.5.0',
    'eaddr_loc' : '10.0.5.255',
    'sport_rem' : 0,
    'eport_rem' : 65535,
    'saddr_rem' : '10.0.10.0',
    'eaddr_rem' : '10.0.10.255',
    'right_auth' : 'psk',
    'left_auth' : 'psk',
    'right_id' : 'vpp@cisco.com',
    'left_id' : 'roadwarrior@cisco.com'

}

ID_KEY = {
    'pr_name' : 'pr0',
    'auth_method' : 'shared-key-mic' ,
    'auth_data' : 'Vpp123',
    'id_type_loc' : 'key-id',
    'id_data_loc' : '0xab12cd34',
    'id_type_rem' : 'key-id',
    'id_data_rem' : '0x12ab34cd',
    'protocol_loc' : 0,
    'protocol_rem' : 0,
    'sport_loc' : 0,
    'eport_loc' : 65535,
    'saddr_loc' : '10.0.5.0',
    'eaddr_loc' : '10.0.5.255',
    'sport_rem' : 0,
    'eport_rem' : 65535,
    'saddr_rem' : '10.0.10.0',
    'eaddr_rem' : '10.0.10.255',
    'right_auth' : 'psk',
    'left_auth' : 'psk',
    'right_id' : '@#ab12cd34',
    'left_id' : '@#12ab34cd'

}

RSA = {
    'pr_name' : 'pr0',
    'auth_method' : 'rsa-sig' ,
    'auth_data' : '/tmp/ike/server-cert.pem',
    'id_type_loc' : 'fqdn',
    'id_data_loc' : 'vpp.home',
    'id_type_rem' : 'fqdn',
    'id_data_rem' : 'roadwarrior.vpn.example.com',
    'protocol_loc' : 0,
    'protocol_rem' : 0,
    'sport_loc' : 0,
    'eport_loc' : 65535,
    'saddr_loc' : '10.0.5.0',
    'eaddr_loc' : '10.0.5.255',
    'sport_rem' : 0,
    'eport_rem' : 65535,
    'saddr_rem' : '10.0.10.0',
    'eaddr_rem' : '10.0.10.255',
    'right_auth' : 'pubkey',
    'left_auth' : 'pubkey',
    'right_id' : '@vpp.home',
    'left_id' : '@roadwarrior.vpn.example.com'

}
