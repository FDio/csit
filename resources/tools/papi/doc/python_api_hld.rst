Python API high level description
=================================

Overview
--------

`Python API <https://wiki.fd.io/view/VPP/Python_API>`_ provides python binding
for VPP API via vpp-papi module in ``vpp-api/python/``.

Each Python API call uses arguments as specified in the API definitions file
(e.g. vpe.api). The "client_index" and "context" fields are handled by the
module itself.

::

    vpp.api.show_version()
    vpp.api.sw_interface_dump(name_filter_valid=1,
        name_filter="GigabitEthernet0/10/0")


A call returns a named tuple or a list of named tuples.

::

    show_version_reply(_0=832, context=1, retval=0, program='vpe\x00\x00\x00\x00
        \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
        \x00\x00\x00\x00\x00\x00\x00', version='18.10-rc0~593-gb7620fd~b5386\x00
        \x00\x00\x00', build_date='Fri Oct  5 18:40:55 UTC 2018\x00\x00\x00
        \x00',build_directory='/w/workspace/vpp-merge-master-ubuntu1604\x00\x00
        \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
        \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
        \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
        \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
        \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
        \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
        \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
        \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
        \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
        \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
        \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
        \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    [sw_interface_details(_0=86, context=5, sw_if_index=3, sup_sw_if_index=3,
        l2_address_length=6, l2_address="\x08\x00'\x1f\xdf\xf5\x00\x00",
        interface_name='GigabitEthernet0/10/0\x00\x00\x00\x00\x00\x00\x00\x00
        \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
        \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        admin_up_down=0, link_up_down=0, link_duplex=2, link_speed=4,
        link_mtu=9202, mtu=[9000, 0, 0, 0], sub_id=0, sub_dot1ad=0,
        sub_dot1ah=0, sub_number_of_tags=0, sub_outer_vlan_id=0,
        sub_inner_vlan_id=0, sub_exact_match=0, sub_default=0,
        sub_outer_vlan_id_any=0, sub_inner_vlan_id_any=0, vtr_op=0,
        vtr_push_dot1q=0, vtr_tag1=0, vtr_tag2=0, tag='\x00\x00\x00\x00\x00\x00
        \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
        \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
        \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
        \x00\x00\x00\x00', outer_tag=0, b_dmac='\x00\x00\x00\x00\x00\x00',
        b_smac='\x00\x00\x00\x00\x00\x00', b_vlanid=0, i_sid=0)]


Implementation in CSIT
----------------------

Usage of Python API in CSIT requires splitting the implementation into two
parts:

1) Executable python script that will run on remote host (DUT) where VPP is
   installed and running.

2) Papi library that will be used on local host (e.g. jenkins slave) where Robot
   Framework is running.

Executable python script provides:

- creation of VPP API object,
- connection to / disconnection from VPP API object,
- execution of API functions and returning the reply message(s).

PAPI library is responsible for:

- providing necessary API data (API name, API arguments),
- processing of received reply message(s).

Data between executable python script and PAPI library is exchanged in JSON
format.

JSON data in direction from Robot framework executor library to remote python
script running on DUT (API request) consist of list of dictionaries with client
names and requested APIs with arguments:

::

    [
        {
            "client_name": "api_set1",
            "apis": [
                        {
                            "api_name": "show_version",
                            "api_args": {
                            }
                        },
                        {
                            "api_name": "sw_interface_dump",
                            "api_args": {
                                "name_filter_valid": 1,
                                "name_filter": "GigabitEthernet0/10/0"
                            }
                        }
                ]
        },
        {
            "client_name": "api_set2",
            "apis": [
                        {
                            "api_name": "sw_interface_set_flags",
                            "api_args": {
                                "sw_if_index": 4,
                                "admin_up_down": 1
                            }
                        }
                ]
        }
    ]


where

- client_name is required by vpp_papi; can be used as api set name,
- apis is the list of commands to be executed,
- api_name is the name of the command to be executed,
- api_args is the dictionary of input arguments with their values for command.

JSON data in direction from remote python script running on DUT to Robot
framework executor library (API reply) consist of list of dictionaries with
client names and replies to APIs:

::

    [
        {
            "client_name": "api_set1",
            "apis": [
                        {
                            "api_name": "show_version",
                            "api_reply": show_version_reply(_0=832, context=1, retval=0, program='vpe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', version='18.10-rc0~593-gb7620fd~b5386\x00\x00\x00\x00', build_date='Fri Oct  5 18:40:55 UTC 2018\x00\x00\x00\x00', build_directory='/w/workspace/vpp-merge-master-ubuntu1604\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
                        },
                        {
                            "api_name": "sw_interface_dump",
                            "api_reply": [sw_interface_details(_0=86, context=2, sw_if_index=3, sup_sw_if_index=3, l2_address_length=6, l2_address="\x08\x00'\x1f\xdf\xf5\x00\x00", interface_name='GigabitEthernet0/10/0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', admin_up_down=0, link_up_down=0, link_duplex=2, link_speed=4, link_mtu=9202, mtu=[9000, 0, 0, 0], sub_id=0, sub_dot1ad=0, sub_dot1ah=0, sub_number_of_tags=0, sub_outer_vlan_id=0, sub_inner_vlan_id=0, sub_exact_match=0, sub_default=0, sub_outer_vlan_id_any=0, sub_inner_vlan_id_any=0, vtr_op=0, vtr_push_dot1q=0, vtr_tag1=0, vtr_tag2=0, tag='\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', outer_tag=0, b_dmac='\x00\x00\x00\x00\x00\x00', b_smac='\x00\x00\x00\x00\x00\x00', b_vlanid=0, i_sid=0)]
                        }
                ]
        },
        {
            "client_name": "api_set2",
            "apis": [
                        {
                            "api_name": "sw_interface_set_flags",
                            "api_reply": sw_interface_set_flags_reply(_0=76, context=3, retval=0)
                        }
                ]
        }
    ]

where

- client_name is the api set name from API request,
- apis is the list of executed commands,
- api_name is the name of executed command,
- api_reply is named tuple or a list of named tuples for executed command.
