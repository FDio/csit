# test variables for invalid VxLAN settings
vxlan_invalid = [
    # same source and destination IPs
    {'src': '192.168.0.2', 'dst': '192.168.0.2', 'vni': 88, 'encap-vrf-id': 0},
    # missing source
    {'dst': '192.168.0.2', 'vni': 88, 'encap-vrf-id': 0},
    # missing destination
    {'src': '192.168.0.2', 'vni': 88, 'encap-vrf-id': 0},
    # missing vni
    {'src': '192.168.0.2', 'dst': '192.168.0.3', 'encap-vrf-id': 0},
    # missing encap id
    {'src': '192.168.0.2', 'vni': 88, 'encap-vrf-id': 0}
]
