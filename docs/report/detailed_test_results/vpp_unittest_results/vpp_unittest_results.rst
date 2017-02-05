CRUD Loopback
`````````````
::

    ==============================================================================
    CRUD Loopback
    ==============================================================================
    test_crud (test_interface_crud.TestLoopbackInterfaceCRUD)                OK
    test_down (test_interface_crud.TestLoopbackInterfaceCRUD)                OK

Flow-per-packet plugin
``````````````````````
::

    ==============================================================================
    Flow-per-packet plugin: test both L2 and IP4 reporting
    ==============================================================================
    Flow per packet L3 test                                                  OK

DHCP
````
::

    ==============================================================================
    DHCP Test Case
    ==============================================================================
    DHCPv6 Proxy                                                             OK
    DHCPv4 Proxy                                                             OK

IP4 VRF Multi-instance
``````````````````````
::

    ==============================================================================
    IP4 VRF  Multi-instance Test Case
    ==============================================================================
    IP4 VRF  Multi-instance test 1 - create 5 BDs                            OK
    IP4 VRF  Multi-instance test 2 - delete 2 VRFs                           OK
    IP4 VRF  Multi-instance 3 - add 2 VRFs                                   OK
    IP4 VRF  Multi-instance test 4 - delete 4 VRFs                           OK

Load Balancer
`````````````
::

    ==============================================================================
    Load Balancer Test Case
    ==============================================================================
    Load Balancer IP4 GRE4                                                   OK
    Load Balancer IP4 GRE6                                                   OK
    Load Balancer IP6 GRE4                                                   OK
    Load Balancer IP6 GRE6                                                   OK

BFD IPv4
````````

::

    ==============================================================================
    Bidirectional Forwarding Detection (BFD)
    ==============================================================================
    verify session goes down after inactivity                                OK
    hold BFD session up                                                      OK
    immediately honor remote min rx reduction                                OK
    large remote RequiredMinRxInterval                                       OK
    bring BFD session down                                                   OK
    bring BFD session up                                                     OK
    verify slow periodic control frames while session down                   OK
    no packets when zero BFD RemoteMinRxInterval                             OK

BFD IPv6
````````
::

    ==============================================================================
    Bidirectional Forwarding Detection (BFD) (IPv6)
    ==============================================================================
    hold BFD session up                                                      OK
    bring BFD session up                                                     OK

BFD API tests
`````````````
::

    ==============================================================================
    Bidirectional Forwarding Detection (BFD) - API
    ==============================================================================
    activate SHA1 authentication                                             OK
    create BFD session using non-existent SHA1 (negative case)               OK
    create a BFD session                                                     OK
    create IPv6 BFD session                                                  OK
    create a BFD session (SHA1)                                              OK
    add SHA1 keys                                                            OK
    test_change_key (test_bfd.BFDAPITestCase)                                OK
    deactivate SHA1 authentication                                           OK
    create the same BFD session twice (negative case)                        OK
    create the same BFD session twice (negative case) (SHA1)                 OK
    share single SHA1 key between multiple BFD sessions                      OK

BFD authorization
`````````````````
::

    ==============================================================================
    Bidirectional Forwarding Detection (BFD) (changing auth)
    ==============================================================================
    change auth key without disturbing session state (delayed)               OK
    change auth key without disturbing session state (immediate)             OK
    turn auth off without disturbing session state (delayed)                 OK
    turn auth off without disturbing session state (immediate)               OK
    turn auth on without disturbing session state (delayed)                  OK
    turn auth on without disturbing session state (immediate)                OK

BFD authentication
``````````````````
::

    ==============================================================================
    Bidirectional Forwarding Detection (BFD) (SHA1 auth)
    ==============================================================================
    hold BFD session up                                                      OK
    hold BFD session up - meticulous auth                                    OK
    session is not brought down by unauthenticated msg                       OK
    session is not brought down by msg with non-existent key-id              OK
    session is not brought down by msg with wrong auth type                  OK
    simulate remote peer restart and resynchronization                       OK
    session is not kept alive by msgs with bad seq numbers                   OK
    bring BFD session up                                                     OK

IPv6 Tests
``````````
::

    ==============================================================================
    IPv6 Test Case
    ==============================================================================
    IPv6 FIB test                                                            OK
    IPv6 Neighbour Solicitation Exceptions                                   OK
    IPv6 Router Solicitation Exceptions                                      OK

SPAN Test
`````````
::

    ==============================================================================
    SPAN Test Case
    ==============================================================================
    SPAN test                                                                OK

GRE Tests
`````````
::

    ==============================================================================
    GRE Test Case
    ==============================================================================
    GRE tunnel Tests                                                         OK
    GRE tunnel L2 Tests                                                      OK
    GRE tunnel VRF Tests                                                     OK

SNAT Test Cases
```````````````
::

    ==============================================================================
    SNAT Test Cases
    ==============================================================================
    SNAT dynamic translation test                                            OK
    SNAT hairpinning                                                         OK
    SNAT multiple inside interfaces with overlapping address space           OK
    Acquire SNAT addresses from interface                                    OK
    Static mapping with addresses from interface                             OK
    S-NAT IPFIX logging NAT addresses exhausted                              OK
    S-NAT IPFIX logging NAT44 session created/delted                         OK
    MAX translations per user - recycle the least recently used              OK
    SNAT multiple inside interfaces (non-overlapping address space)          OK
    S-NAT add pool addresses to FIB                                          OK
    SNAT 1:1 NAT initialized from inside network                             OK
    SNAT 1:1 NAT initialized from outside network                            OK
    SNAT 1:1 NAT VRF awareness                                               OK
    SNAT 1:1 NAT with port initialized from inside network                   OK
    SNAT 1:1 NAT with port initialized from outside network                  OK

L2XC Multi-instance
```````````````````
::

    ==============================================================================
    L2XC Multi-instance Test Case
    ==============================================================================
    L2XC Multi-instance test 1 - create 10 cross-connects                    OK
    L2XC Multi-instance test 2 - delete 4 cross-connects                     OK
    L2BD Multi-instance 3 - add new 4 cross-connects                         OK
    L2XC Multi-instance test 4 - delete 10 cross-connects                    OK

IPv4 Tests
``````````
::

    ==============================================================================
    IPv4 Test Case
    ==============================================================================
    IPv4 FIB test                                                            OK

IPv4 FIB CRUD
`````````````
::

    ==============================================================================
    FIB - add/update/delete - ip4 routes
    ==============================================================================
    Add 1k routes                                                            OK
    Delete 100 routes                                                        OK
    Add 1k routes                                                            OK
    Delete 1.5k routes                                                       OK

IRB Tests
`````````
::

    ==============================================================================
    IRB Test Case
    ==============================================================================
    IPv4 IRB test 1                                                          OK
    IPv4 IRB test 2                                                          OK

MPLS Tests
``````````
::

    ==============================================================================
    MPLS Test Case
    ==============================================================================
    MPLS Local Label Binding test                                            OK
    MPLS Deagg                                                               OK
    MPLS label imposition test                                               OK
    MPLS label swap tests                                                    OK
    MPLS Tunnel Tests                                                        OK
    MPLS V4 Explicit NULL test                                               OK
    MPLS V6 Explicit NULL test                                               OK

L2XC Tests
``````````
::

    ==============================================================================
    L2XC Test Case
    ==============================================================================
    L2XC dual-loop test                                                      OK
    L2XC single-loop test                                                    OK

Classifier
``````````
::

    ==============================================================================
    Classifier Test Case
    ==============================================================================
    IP ACL test                                                              OK
    MAC ACL test                                                             OK
    IP PBR test                                                              OK

VXLAN Tests
```````````
::

    ==============================================================================
    VXLAN Test Case
    ==============================================================================
    Decapsulation test                                                       OK
    Encapsulation test                                                       OK
    Multicast flood test                                                     OK
    Multicast receive test                                                   OK
    Unicast flood test                                                       OK

L2 FIB CRUD
```````````
::

    ==============================================================================
    L2 FIB Test Case
    ==============================================================================
    L2 FIB test 1 - program 100 MAC addresses                                OK
    L2 FIB test 2 - delete 12 MAC entries                                    OK
    L2 FIB test 3 - program new 100 MAC addresses                            OK
    L2 FIB test 4 - delete 160 MAC entries                                   OK

L2BD Tests
``````````
::

    ==============================================================================
    L2BD Test Case
    ==============================================================================
    L2BD MAC learning dual-loop test                                         OK
    L2BD MAC learning single-loop test                                       OK
