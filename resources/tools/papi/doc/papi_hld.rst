Python API
==========

Overview
--------

The vpp-papi module in ``vpp-api/python/`` provides a Python binding to the VPP
API. The Python bindings to the API is auto-generated from JSON API definitions.
These JSON definitions must be passed to the VPP class init method. Both
individual components and plugins provide API definitions. The JSON files are
also generated, from .api files. In a binary installation the JSON API
definitions are installed under ``/usr/share/vpp/api/`` directory.

Currently there are three classes of VPP API methods:

1) Simple request / reply. For example the ``show_version()`` call the
   SHOW_VERSION message is the request and the SHOW_VERSION_REPLY is the answer
   back. By convention replies are named ending with _REPLY.

2) Dump functions. For example ``sw_interface_dump()`` send the
   SW_INTERFACE_DUMP message and receive a set of messages back. In this example
   SW_INTERFACE_DETAILS and SW_INTERFACE_SET_FLAGS are (typically) received.
   The CONTROL_PING/CONTROL_PING_REPLY is used as a method to signal to the
   client that the last message has been received. By convention the request
   message have names ending with _DUMP and the replies have names ending in
   _DETAILS.

3) Register for events. For example ``want_stats()`` sends a WANT_STATS message,
   get a WANT_STATS_REPLY message back, and the client will then asynchronously
   receive VNET_INTERFACE_COUNTERS messages.

The API is by default blocking although there is possible to get asynchronous
behaviour by setting the function argument ``async=True``.

Each call uses the arguments as specified in the API definitions file (e.g.
vpe.api). The "client_index" and "context" fields are handled by the module
itself. A call returns a named tuple or a list of named tuples.

Implementation in CSIT
----------------------

Usage of Python API in CSIT requires split the implementation into two parts:

1) Executable python script that will run on remote host (DUT) where VPP is
   installed and running.

2) Papi library that will be used on local host (e.g. jenkins slave) where Robot
   Framework is running.

Executable python script provides:

- creation of VPP API object

- connection to / disconnection from VPP API object

- execution of API functions and returning the reply message(s)

Papi library is responsible for:

- providing necessary API data (api name, api arguments)

- processing of received reply message(s)

Data between executable python script and papi library are exchanged in JSON
format.

JSON data in direction papi library -> executable python script consist of list
of dictionaries with client names and requested APIs with arguments:

::

    [
        {
            "client_name": "api_set1",
            "apis":[
                    {
                        "api_name": "show_version",
                        "api_args":{
                        }
                    },
                    {
                        "api_name": "sw_interface_dump",
                        "api_args":{
                            "name_filter_valid": 1,
                            "name_filter": "GigabitEthernet0/10/0"
                        }
                    }
                ]
        },
        {
            "client_name": "api_set2",
            "apis":[
                    {
                        "api_name": "sw_interface_set_flags",
                        "api_args":{
                            "sw_if_index": 4,
                            "admin_up_down": 1
                        }
                    }
                ]
        }
    ]


JSON data in direction executable python script -> papi library consist of list
of dictionaries with client names and replies to APIs:

::

    [
        {
            "client_name": "api_set1",
            "apis":[
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
            "apis":[
                    {
                        "api_name": "sw_interface_set_flags",
                        "api_reply":sw_interface_set_flags_reply(_0=76, context=3, retval=0)
                    }
                ]
        }
    ]
