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

IPv4 VRF Multi-instance
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

FIB Tests
`````````
::

    ==============================================================================
    FIB Test Case
    ==============================================================================
    FIB Unit Tests                                                           OK

BFD IPv6
````````
::

    ==============================================================================
    Bidirectional Forwarding Detection (BFD) (IPv6)
    ==============================================================================
    echo function used                                                       SKIP
    echo packets looped back                                                 SKIP
    hold BFD session up                                                      SKIP
    bring BFD session up                                                     SKIP
    bring BFD session up - first frame looked up by address pair             SKIP

BFD authentication
``````````````````
::

    ==============================================================================
    Bidirectional Forwarding Detection (BFD) (SHA1 auth)
    ==============================================================================
    hold BFD session up                                                      SKIP
    hold BFD session up - meticulous auth                                    SKIP
    session is not brought down by unauthenticated msg                       SKIP
    session is not brought down by msg with non-existent key-id              SKIP
    session is not brought down by msg with wrong auth type                  SKIP
    simulate remote peer restart and resynchronization                       SKIP
    session is not kept alive by msgs with bad sequence numbers              SKIP
    bring BFD session up                                                     SKIP

BFD CLI
````````
::

    ==============================================================================
    Bidirectional Forwarding Detection (BFD) (CLI)
    ==============================================================================
    create/modify/delete IPv4 BFD UDP session                                SKIP
    create/modify/delete IPv6 BFD UDP session                                SKIP
    create/modify/delete IPv6 BFD UDP session (authenticated)                SKIP
    create/modify/delete IPv4 BFD UDP session (authenticated)                SKIP
    put session admin-up and admin-down                                      SKIP
    turn authentication on and off                                           SKIP
    turn authentication on and off (delayed)                                 SKIP
    set/delete meticulous SHA1 auth key                                      SKIP
    set/delete SHA1 auth key                                                 SKIP
    set/del udp echo source                                                  SKIP
    show commands                                                            SKIP

BFD API
````````
::

    ==============================================================================
    Bidirectional Forwarding Detection (BFD) - API
    ==============================================================================
    activate SHA1 authentication                                             SKIP
    create BFD session using non-existent SHA1 (negative case)               SKIP
    create a BFD session                                                     SKIP
    create IPv6 BFD session                                                  SKIP
    create a BFD session (SHA1)                                              SKIP
    add SHA1 keys                                                            SKIP
    change SHA1 key                                                          SKIP
    deactivate SHA1 authentication                                           SKIP
    create the same BFD session twice (negative case)                        SKIP
    create the same BFD session twice (negative case) (SHA1)                 SKIP
    modify BFD session parameters                                            SKIP
    share single SHA1 key between multiple BFD sessions                      SKIP

BFD authentication change
`````````````````````````
::

    ==============================================================================
    Bidirectional Forwarding Detection (BFD) (changing auth)
    ==============================================================================
    change auth key without disturbing session state (delayed)               SKIP
    change auth key without disturbing session state (immediate)             SKIP
    turn auth off without disturbing session state (delayed)                 SKIP
    turn auth off without disturbing session state (immediate)               SKIP
    turn auth on without disturbing session state (delayed)                  SKIP
    turn auth on without disturbing session state (immediate)                SKIP

BFD IPv4
````````

::

    ==============================================================================
    Bidirectional Forwarding Detection (BFD)
    ==============================================================================
    put session admin-up and admin-down                                      SKIP
    configuration change while peer in demand mode                           SKIP
    verify session goes down after inactivity                                SKIP
    echo function                                                            SKIP
    session goes down if echo function fails                                 SKIP
    echo packets looped back                                                 SKIP
    echo function stops if echo source is removed                            SKIP
    echo function stops if peer sets required min echo rx zero               SKIP
    hold BFD session up                                                      SKIP
    immediately honor remote required min rx reduction                       SKIP
    echo packets with invalid checksum don't keep a session up               SKIP
    large remote required min rx interval                                    SKIP
    modify detect multiplier                                                 SKIP
    modify session - double required min rx                                  SKIP
    modify session - halve required min rx                                   SKIP
    no periodic frames outside poll sequence if remote demand set            SKIP
    test correct response to control frame with poll bit set                 SKIP
    test poll sequence queueing                                              SKIP
    bring BFD session down                                                   SKIP
    bring BFD session up                                                     SKIP
    bring BFD session up - first frame looked up by address pair             SKIP
    verify slow periodic control frames while session down                   SKIP
    stale echo packets don't keep a session up                               SKIP
    no packets when zero remote required min rx interval                     SKIP

IPv6 Tests
``````````
::

    ==============================================================================
    IPv6 Test Case
    ==============================================================================
    IPv6 FIB test                                                            OK
    IPv6 Neighbour Solicitation Exceptions                                   OK
    IPv6 Router Solicitation Exceptions                                      OK
    ==============================================================================
    IPv6 disabled
    ==============================================================================
    IP Disabled                                                              OK
    IPv6 ND Proxy
    ==============================================================================
    IPv6 ND ProxyTest Case
    ==============================================================================
    IPv6 Proxy ND                                                            OK
    ==============================================================================
    IPv6 routes via NULL
    ==============================================================================
    IP NULL route                                                            OK

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

L2BD Multi-instance
```````````````````
::

    ==============================================================================
    L2BD Multi-instance Test Case
    ==============================================================================
    L2BD Multi-instance test 1 - create 5 BDs                                SKIP
    L2BD Multi-instance test 2 - update data of 5 BDs                        SKIP
    L2BD Multi-instance 3 - delete 2 BDs                                     SKIP
    L2BD Multi-instance test 4 - add 2 BDs                                   SKIP
    L2BD Multi-instance 5 - delete 5 BDs                                     SKIP

MAP Tests
`````````
::

    ==============================================================================
    MAP Test Case
    ==============================================================================
    MAP-E                                                                    OK

LISP tests
``````````
::

    ==============================================================================
    Basic LISP test
    ==============================================================================
    Test case for basic encapsulation                                        OK

NAT Test Cases
``````````````
::

    ==============================================================================
    SNAT Test Cases
    ==============================================================================
    SNAT dynamic translation test                                            OK
    SNAT handling of client packets with TTL=1                               OK
    SNAT handling of error responses to client packets with TTL=2            OK
    SNAT handling of server packets with TTL=1                               OK
    SNAT handling of error responses to server packets with TTL=2            OK
    SNAT hairpinning                                                         OK
    SNAT multiple inside interfaces with overlapping address space           OK
    Acquire SNAT addresses from interface                                    OK
    Static mapping with addresses from interface                             OK
    S-NAT IPFIX logging NAT addresses exhausted                              OK
    S-NAT IPFIX logging NAT44 session created/delted                         OK
    MAX translations per user - recycle the least recently used              OK
    SNAT multiple inside interfaces (non-overlapping address space)          OK
    Ping internal host from outside network                                  OK
    Ping SNAT out interface from outside network                             OK
    S-NAT add pool addresses to FIB                                          OK
    SNAT 1:1 NAT initialized from inside network                             OK
    SNAT 1:1 NAT initialized from outside network                            OK
    SNAT 1:1 NAT VRF awareness                                               OK
    SNAT 1:1 NAT with port initialized from inside network                   OK
    SNAT 1:1 NAT with port initialized from outside network                  OK
    S-NAT tenant VRF independent address pool mode                           OK
    S-NAT tenant VRF aware address pool mode                                 OK
    ==============================================================================
    Deterministic NAT Test Cases
    ==============================================================================
    S-NAT run deterministic mode                                             OK

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
    ==============================================================================
    IPv4 routes via NULL
    ==============================================================================
    IP NULL route                                                            OK
    ==============================================================================
    IPv4 disabled
    ==============================================================================
    IP Disabled                                                              OK

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

ACL Security Groups
```````````````````
::

    ==============================================================================
    ACL plugin Test Case
    ==============================================================================
    ACL plugin version check; learn MACs                                     OK
    ACL create test                                                          OK
    permit ACL apply test                                                    OK
    deny ACL apply test                                                      OK
    VPP_624 permit ICMPv4                                                    OK
    VPP_624 permit ICMPv6                                                    OK
    VPP_624 deny ICMPv4                                                      OK
    VPP_624 deny ICMPv6                                                      OK
    permit TCPv4                                                             OK
    permit TCPv6                                                             OK
    permit UDPv4                                                             OK
    permit UDPv6                                                             OK
    deny TCPv4/v6                                                            OK
    deny UDPv4/v6                                                            OK
    verify add/dump acls                                                     OK
    permit single TCPv4                                                      OK
    permit single UDPv4                                                      OK
    permit single TCPv6                                                      OK
    permit single UPPv6                                                      OK
    deny single TCPv4/v6                                                     OK
    deny single UDPv4/v6                                                     OK
    deny single UDPv4/v6, permit ip any, verify non-initial fragment blocked OK

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
    ==============================================================================
    MPLS disabled
    ==============================================================================
    MPLS Disabled                                                            OK

IPv6 VRF Multi-instance
```````````````````````
::

    ==============================================================================
    IP6 VRF  Multi-instance Test Case
    ==============================================================================
    IP6 VRF  Multi-instance test 1 - create 4 VRFs                           OK
    IP6 VRF  Multi-instance test 2 - reset 2 VRFs                            OK
    IP6 VRF  Multi-instance 3 - add 2 VRFs                                   OK
    IP6 VRF  Multi-instance test 4 - reset 4 VRFs                            OK

L2XC Tests
``````````
::

    ==============================================================================
    L2XC Test Case
    ==============================================================================
    L2XC dual-loop test                                                      OK
    L2XC single-loop test                                                    OK

MFIB Tests
``````````
::

    ==============================================================================
    MFIB Test Case
    ==============================================================================
    MFIB Unit Tests                                                          OK

IP Multicast Tests
``````````````````
::

    ==============================================================================
    IP Multicast Test Case
    ==============================================================================
    IPv6 Multicast Replication                                               OK
    IP Multicast Replication                                                 OK
    IP Multicast Connected Source check                                      OK
    IP Multicast Signal                                                      OK

Classifier
``````````
::

    ==============================================================================
    Classifier Test Case
    ==============================================================================
    IP ACL test                                                              OK
    MAC ACL test                                                             OK
    IP PBR test                                                              OK

IRB Tests
`````````
::

    ==============================================================================
    IRB Test Case
    ==============================================================================
    ACL plugin prepare                                                       OK
    ACL IPv6 routed -> bridged, L2 ACL deny                                  OK
    ACL IPv6 routed -> bridged, L3 ACL deny                                  OK
    ACL IPv4 routed -> bridged, L2 ACL deny                                  OK
    ACL IPv4 routed -> bridged, L3 ACL deny                                  OK
    ACL IPv6 bridged -> routed, L2 ACL deny                                  OK
    ACL IPv6 bridged -> routed, L3 ACL deny                                  OK
    ACL IPv4 bridged -> routed, L2 ACL deny                                  OK
    ACL IPv4 bridged -> routed, L3 ACL deny                                  OK
    ACL IPv6 routed -> bridged, L2 ACL permit+reflect                        OK
    ACL IPv6 bridged -> routed, L2 ACL permit+reflect                        OK
    ACL IPv4 routed -> bridged, L2 ACL permit+reflect                        OK
    ACL IPv4 bridged -> routed, L2 ACL permit+reflect                        OK
    ACL IPv6 routed -> bridged, L3 ACL permit+reflect                        OK
    ACL IPv6 bridged -> routed, L3 ACL permit+reflect                        OK
    ACL IPv4 routed -> bridged, L3 ACL permit+reflect                        OK
    ACL IPv4 bridged -> routed, L3 ACL permit+reflect                        OK
    ACL IPv6+EH routed -> bridged, L2 ACL deny                               OK
    ACL IPv6+EH routed -> bridged, L3 ACL deny                               OK
    ACL IPv6+EH bridged -> routed, L2 ACL deny                               OK
    ACL IPv6+EH bridged -> routed, L3 ACL deny                               OK
    ACL IPv6+EH routed -> bridged, L2 ACL permit+reflect                     OK
    ACL IPv6+EH bridged -> routed, L2 ACL permit+reflect                     OK
    ACL IPv6+EH routed -> bridged, L3 ACL permit+reflect                     OK
    ACL IPv6+EH bridged -> routed, L3 ACL permit+reflect                     OK
    ACL IPv4+MF routed -> bridged, L2 ACL deny                               OK
    ACL IPv4+MF routed -> bridged, L3 ACL deny                               OK
    ACL IPv4+MF bridged -> routed, L2 ACL deny                               OK
    ACL IPv4+MF bridged -> routed, L3 ACL deny                               OK
    ACL IPv4+MF routed -> bridged, L2 ACL permit+reflect                     OK
    ACL IPv4+MF bridged -> routed, L2 ACL permit+reflect                     OK
    ACL IPv4+MF routed -> bridged, L3 ACL permit+reflect                     OK
    ACL IPv4+MF bridged -> routed, L3 ACL permit+reflect                     OK
    ACL plugin set old L2 datapath                                           OK
    ACL IPv6 routed -> bridged, L2 ACL deny                                  OK
    ACL IPv6 routed -> bridged, L3 ACL deny                                  OK
    ACL IPv4 routed -> bridged, L2 ACL deny                                  OK
    ACL IPv4 routed -> bridged, L3 ACL deny                                  OK
    ACL IPv6 bridged -> routed, L2 ACL deny                                  OK
    ACL IPv6 bridged -> routed, L3 ACL deny                                  OK
    ACL IPv4 bridged -> routed, L2 ACL deny                                  OK
    ACL IPv4 bridged -> routed, L3 ACL deny                                  OK

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

ARP Tests
`````````
::

    ==============================================================================
    ARP Test Case
    ==============================================================================
    ARP                                                                      OK
    MPLS                                                                     OK
    Proxy ARP                                                                OK

L2BD Tests
``````````
::

    ==============================================================================
    L2BD Test Case
    ==============================================================================
    L2BD MAC learning dual-loop test                                         OK
    L2BD MAC learning single-loop test                                       OK
