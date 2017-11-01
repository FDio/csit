CRUD Loopback
`````````````
::

    ==============================================================================
    CRUD Loopback
    ==============================================================================
    test_crud (test_interface_crud.TestLoopbackInterfaceCRUD)                OK
    test_down (test_interface_crud.TestLoopbackInterfaceCRUD)                OK

Flowprobe feature
`````````````````
::

    ==============================================================================
    Re-enable Flowprobe feature
    ==============================================================================
    disable flowprobe feature after first packets and re-enable              SKIP
    ==============================================================================
    collect information on Ethernet, IP4 and IP6 datapath (no timers)
    ==============================================================================
    no timers, one CFLOW packet, 9 Flows inside                              OK
    no timers, two CFLOW packets (mtu=256), 3 Flows in each                  OK
    L2 data on IP4 datapath                                                  OK
    L2 data on IP6 datapath                                                  OK
    L2 data on L2 datapath                                                   OK
    L3 data on IP4 datapath                                                  OK
    L3 data on IP6 datapath                                                  OK
    L3 data on L2 datapath                                                   OK
    L4 data on IP4 datapath                                                  OK
    L4 data on IP6 datapath                                                  OK
    L4 data on L2 datapath                                                   OK
    verify templates on IP6 datapath                                         OK
    verify templates on IP4 datapath                                         OK
    verify template on L2 datapath                                           OK
    ==============================================================================
    Disable Flowprobe feature
    ==============================================================================
    disable flowprobe feature after first packets                            SKIP
    ==============================================================================
    Re-enable IPFIX
    ==============================================================================
    disable IPFIX after first packets and re-enable after few packets        SKIP
    ==============================================================================
    Disable IPFIX
    ==============================================================================
    disable IPFIX after first packets                                        SKIP

DHCP
````
::

    ==============================================================================
    DHCP Test Case
    ==============================================================================
    DHCPv6 Proxy                                                             OK
    DHCP Client                                                              OK
    DHCPv4 Proxy                                                             OK

IPv4 VRF Multi-instance
```````````````````````
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
    interface with bfd session deleted                                       SKIP
    bring BFD session up                                                     SKIP
    bring BFD session up - first frame looked up by address pair             SKIP
    ==============================================================================
    BFD-FIB interactions (IPv6)
    ==============================================================================
    BFD-FIB interactions                                                     SKIP

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
    ND Duplicates                                                            OK
    IPv6 Router Solicitation Exceptions                                      OK
    ==============================================================================
    IPv6 disabled
    ==============================================================================
    IP Disabled                                                              OK
    ==============================================================================
    IPv6 ND ProxyTest Case
    ==============================================================================
    IPv6 Proxy ND                                                            OK
    ==============================================================================
    IPv6 Load-Balancing
    ==============================================================================
    IPv6 Load-Balancing                                                      OK
    ==============================================================================
    IPv6 routes via NULL
    ==============================================================================
    IP NULL route                                                            OK

SPAN Tests
``````````
::

    ==============================================================================
    SPAN Test Case
    ==============================================================================
    SPAN device rx mirror test                                               OK
    SPAN l2 tx mirror test                                                   OK
    SPAN l2 rx mirror test                                                   OK
    SPAN l2 rx mirror into gre-subif+vtr                                     OK
    SPAN l2 rx mirror into subif+vtr                                         OK
    SPAN l2 rx mirror into vxlan test                                        OK

GRE Tests
`````````
::

    ==============================================================================
    GRE Test Case
    ==============================================================================
    GRE IPv4 tunnel Tests                                                    OK
    GRE IPv6 tunnel Tests                                                    OK
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

NAT44 Test Cases
````````````````
::

    ==============================================================================
    NAT44 Test Cases
    ==============================================================================
    NAT44 dynamic translation test                                           OK
    NAT44 handling of client packets with TTL=1                              OK
    NAT44 handling of error responses to client packets with TTL=2           OK
    NAT44 handling of server packets with TTL=1                              OK
    NAT44 handling of error responses to server packets with TTL=2           OK
    NAT44 interfaces without configured IP address                           OK
    NAT44 hairpinning - 1:1 NAPT                                             OK
    NAT44 hairpinning - 1:1 NAT                                              OK
    1:1 NAT translate packet with unknown protocol - hairpinning             OK
    NAT44 translate packet with unknown protocol - hairpinning               OK
    NAT44 multiple inside interfaces with overlapping address space          OK
    Acquire NAT44 addresses from interface                                   OK
    Static mapping with addresses from interface                             OK
    IPFIX logging NAT addresses exhausted                                    OK
    IPFIX logging NAT44 session created/delted                               OK
    MAX translations per user - recycle the least recently used              OK
    NAT44 multiple non-overlapping address space inside interfaces           OK
    NAT44 interface output feature (in2out postrouting)                      OK
    NAT44 interface output feature hairpinning (in2out postrouting)          OK
    NAT44 interface output feature VRF aware (in2out postrouting)            OK
    Ping internal host from outside network                                  OK
    Ping NAT44 out interface from outside network                            OK
    NAT44 add pool addresses to FIB                                          OK
    1:1 NAT initialized from inside network                                  OK
    NAT44 interfaces without configured IP address - 1:1 NAT                 OK
    NAT44 local service load balancing                                       OK
    1:1 NAT initialized from outside network                                 OK
    1:1 NAT translate packet with unknown protocol                           OK
    1:1 NAT VRF awareness                                                    OK
    1:1 NAPT initialized from inside network                                 OK
    NAT44 interfaces without configured IP address - 1:1 NAPT                OK
    1:1 NAPT initialized from outside network                                OK
    NAT44 translate packet with unknown protocol                             OK
    NAT44 tenant VRF independent address pool mode                           OK
    NAT44 tenant VRF aware address pool mode                                 OK
    ==============================================================================
    Deterministic NAT Test Cases
    ==============================================================================
    Deterministic NAT translation test (TCP, UDP, ICMP)                      OK
    NAT plugin run deterministic mode                                        OK
    Deterministic NAT multiple users                                         OK
    Deterministic NAT maximum sessions per user limit                        SKIP
    Deterministic NAT session timeouts                                       SKIP
    Set deterministic NAT timeouts                                           OK
    Deterministic NAT TCP session close from inside network                  OK
    Deterministic NAT TCP session close from outside network                 OK

NAT64 Test Cases
````````````````
::

    ==============================================================================
    NAT64 Test Cases
    ==============================================================================
    NAT64 dynamic translation test                                           OK
    NAT64 hairpinning                                                        OK
    NAT64 translate packet with unknown protocol - hairpinning               OK
    NAT64 ICMP Error message translation                                     OK
    Enable/disable NAT64 feature on the interface                            OK
    Add/delete address to NAT64 pool                                         OK
    NAT64 Network-Specific Prefix                                            OK
    NAT64 session timeout                                                    SKIP
    Set NAT64 timeouts                                                       OK
    NAT64 static translation test                                            OK
    Add/delete static BIB entry                                              OK
    NAT64 translate packet with unknown protocol                             OK

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
    ==============================================================================
    IPv4 Subnets
    ==============================================================================
    IP Sub Nets                                                              OK
    ==============================================================================
    IPv4 VLAN-0
    ==============================================================================
    IP VLAN-0                                                                OK
    ==============================================================================
    IPv4 Load-Balancing
    ==============================================================================
    IP Load-Balancing                                                        OK

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

ACL Security Groups
```````````````````
::

    ==============================================================================
    ACL plugin Test Case
    ==============================================================================
    ACL plugin version check; learn MACs                                     OK
    ACL create/delete test                                                   OK
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
    VPP-687 zero length udp ipv4 packet                                      OK
    VPP-687 zero length udp ipv6 packet                                      OK
    permit TCPv4 + non-match range                                           OK
    permit TCPv6 + non-match range                                           OK
    permit UDPv4 + non-match range                                           OK
    permit UDPv6 + non-match range                                           OK
    deny TCPv4/v6 + non-match range                                          OK
    deny UDPv4/v6 + non-match range                                          OK
    ==============================================================================
    ACL plugin connection-oriented extended testcases
    ==============================================================================
    Prepare the settings                                                     SKIP
    IPv4: Basic conn timeout test reflect on ingress                         SKIP
    IPv4: Basic conn timeout test reflect on egress                          SKIP
    IPv4: reflect egress, clear conn                                         SKIP
    IPv4: reflect ingress, clear conn                                        SKIP
    IPv4: Idle conn behind active conn, reflect on ingress                   SKIP
    IPv4: Idle conn behind active conn, reflect on egress                    SKIP
    IPv6: Basic conn timeout test reflect on ingress                         SKIP
    IPv6: Basic conn timeout test reflect on egress                          SKIP
    IPv6: reflect egress, clear conn                                         SKIP
    IPv6: reflect ingress, clear conn                                        SKIP
    IPv6: Idle conn behind active conn, reflect on ingress                   SKIP
    IPv6: Idle conn behind active conn, reflect on egress                    SKIP
    Prepare for TCP session tests                                            SKIP
    IPv4: transient TCP session (incomplete 3WHS), ref. on ingress           SKIP
    IPv4: transient TCP session (incomplete 3WHS), ref. on egress            SKIP
    IPv4: established TCP session (complete 3WHS), ref. on ingress           SKIP
    IPv4: established TCP session (complete 3WHS), ref. on egress            SKIP
    IPv4: transient TCP session (3WHS,ACK,FINACK), ref. on ingress           SKIP
    IPv4: transient TCP session (3WHS,ACK,FINACK), ref. on egress            SKIP
    IPv6: transient TCP session (incomplete 3WHS), ref. on ingress           SKIP
    IPv6: transient TCP session (incomplete 3WHS), ref. on egress            SKIP
    IPv6: established TCP session (complete 3WHS), ref. on ingress           SKIP
    IPv6: established TCP session (complete 3WHS), ref. on egress            SKIP
    IPv6: transient TCP session (3WHS,ACK,FINACK), ref. on ingress           SKIP
    IPv6: transient TCP session (3WHS,ACK,FINACK), ref. on egress            SKIP

MPLS Tests
``````````
::

    ==============================================================================
    MPLS-L2
    ==============================================================================
    Virtual Private LAN Service                                              OK
    Virtual Private Wire Service                                             OK
    ==============================================================================
    MPLS Test Case
    ==============================================================================
    MPLS Local Label Binding test                                            OK
    MPLS Deagg                                                               OK
    MPLS label imposition test                                               OK
    MPLS Interface Receive                                                   OK
    MPLS Multicast Head-end                                                  OK
    MPLS IPv4 Multicast Tail                                                 OK
    MPLS IPv6 Multicast Tail                                                 OK
    MPLS Multicast Mid Point                                                 OK
    MPLS label swap tests                                                    OK
    MPLS Tunnel Tests                                                        OK
    MPLS V4 Explicit NULL test                                               OK
    MPLS V6 Explicit NULL test                                               OK
    ==============================================================================
    MPLS PIC edge convergence
    ==============================================================================
    MPLS eBGP PIC edge convergence                                           OK
    MPLS iBGP PIC edge convergence                                           OK
    MPLSv6 eBGP PIC edge convergence                                         OK
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
    IPv6 Multicast Replication in non-default table                          OK
    IP Multicast Replication                                                 OK
    IP Multicast Connected Source check                                      OK
    IP Multicast Signal                                                      OK
    IP Multicast Replication in non-default table                            OK

Classifier
``````````
::
#######
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

VXLAN-GPE Tests
```````````
::

    ==============================================================================
    VXLAN-GPE Test Case
    ==============================================================================
    Decapsulation test                                                       SKIP
    Encapsulation test                                                       SKIP
    Multicast flood test                                                     SKIP
    Multicast receive test                                                   SKIP
    Unicast flood test                                                       SKIP

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
    L2 FIB test 5 - Program 10 new MAC entries, learn 10                     OK
    L2 FIB test 6 - flush first interface                                    OK
    L2 FIB test 7 - flush bd_id                                              OK
    L2 FIB test 8 - flush all                                                OK
    L2 FIB test 9 - mac learning events                                      OK

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

MACIP Access Control Tests
``````````
::

    ==============================================================================
    MACIP Test Case
    ==============================================================================
    IP4 MACIP wildcardMAC|exactIP ACL bridged traffic                        OK
    MACIP 10 ACLs each with 100+ entries                                     OK
    MACIP 10 ACLs each with 100+ entries with IP4 traffic                    OK
    MACIP 10 ACLs each with 100+ entries with IP6 traffic                    OK
    MACIP ACL with 10 entries                                                OK
    MACIP ACL with 100 entries                                               OK
    MACIP ACL with 2 entries                                                 OK
    MACIP ACL with 20 entries                                                OK
    MACIP ACL with 5 entries                                                 OK
    MACIP ACL with 50 entries                                                OK
    MACIP 2 ACLs each with 100+ entries                                      OK
    IP4 MACIP exactMAC|exactIP ACL bridged traffic                           OK
    IP4 MACIP exactMAC|subnetIP ACL bridged traffic                          OK
    IP4 MACIP exactMAC|wildIP ACL bridged traffic                            OK
    IP4 MACIP ouiMAC|exactIP ACL bridged traffic                             OK
    IP4 MACIP ouiMAC|subnetIP ACL bridged traffic                            OK
    IP4 MACIP ouiMAC|wildIP ACL bridged traffic                              OK
    IP4 MACIP wildcardMAC|subnetIP ACL bridged traffic                       OK
    IP4 MACIP wildcardMAC|wildIP ACL bridged traffic                         OK
    IP6 MACIP exactMAC|exactIP ACL bridged traffic                           OK
    IP6 MACIP exactMAC|subnetIP ACL bridged traffic                          OK
    IP6 MACIP exactMAC|wildIP ACL bridged traffic                            OK
    IP6 MACIP oui_MAC|exactIP ACL bridged traffic                            OK
    IP6 MACIP ouiMAC|subnetIP ACL bridged traffic                            OK
    IP6 MACIP ouiMAC|wildIP ACL bridged traffic                              OK
    IP6 MACIP wildcardMAC|exactIP ACL bridged traffic                        OK
    IP6 MACIP wildcardMAC|subnetIP ACL bridged traffic                       OK
    IP6 MACIP wildcardMAC|wildIP ACL bridged traffic                         OK
    MACIP replace ACL                                                        OK
    MACIP replace ACL with IP4 traffic                                       OK
    MACIP replace ACL with IP6 traffic                                       OK
    IP4 MACIP exactMAC|exactIP ACL routed traffic                            OK
    IP4 MACIP exactMAC|subnetIP ACL routed traffic                           OK
    IP4 MACIP exactMAC|wildIP ACL routed traffic                             OK
    IP4 MACIP ouiMAC|exactIP ACL routed traffic                              OK
    IP4 MACIP ouiMAC|subnetIP ACL routed traffic                             OK
    IP4 MACIP ouiMAC|wildIP ACL routed traffic                               OK
    IP4 MACIP wildcardMAC|exactIP ACL routed traffic                         OK
    IP4 MACIP wildcardMAC|subnetIP ACL routed traffic                        OK
    IP4 MACIP wildcardMAC|wildIP ACL                                         OK
    IP6 MACIP exactMAC|exactIP ACL routed traffic                            OK
    IP6 MACIP exactMAC|subnetIP ACL routed traffic                           OK
    IP6 MACIP exactMAC|wildIP ACL routed traffic                             OK
    IP6 MACIP ouiMAC|exactIP ACL routed traffic                              OK
    IP6 MACIP ouiMAC|subnetIP ACL routed traffic                             OK
    IP6 MACIP ouiMAC|wildIP ACL routed traffic                               OK
    IP6 MACIP wildcardMAC|exactIP ACL routed traffic                         OK
    IP6 MACIP wildcardMAC|subnetIP ACL routed traffic                        OK
    IP6 MACIP wildcardMAC|wildIP ACL                                         OK
    MACIP ACL delete intf with acl                                           OK

SRv6 Tests
``````````
::

    ==============================================================================
    SRv6 Test Case
    ==============================================================================
    Test SRv6 End (without PSP) behavior.                                    OK
    Test SRv6 End.DT4 behavior.                                              OK
    Test SRv6 End.DT6 behavior.                                              OK
    Test SRv6 End.DX2 behavior.                                              OK
    Test SRv6 End.DX4 behavior.                                              OK
    Test SRv6 End.DX6 behavior.                                              OK
    Test SRv6 End.X (without PSP) behavior.                                  OK
    Test SRv6 End.X with PSP behavior.                                       OK
    Test SRv6 End with PSP behavior.                                         OK
    Test SRv6 Transit.Encaps behavior for IPv6.                              OK
    Test SRv6 Transit.Encaps behavior for IPv4.                              OK
    Test SRv6 Transit.Encaps behavior for L2.                                SKIP
    Test SRv6 Transit.Insert behavior (IPv6 only).                           OK

PPPoE Tests
```````````
::

    ==============================================================================
    PPPoE Test Case
    ==============================================================================
    PPPoE Add Same Session Twice Test                                        OK
    PPPoE Decap Test                                                         OK
    PPPoE Decap Multiple Sessions Test                                       OK
    PPPoE Delete Same Session Twice Test                                     OK
    PPPoE Encap Test                                                         OK
    PPPoE Encap Multiple Sessions Test                                       OK

VTR VLAN Tag Rewrite Tests
``````````````````````````
::

    ==============================================================================
    VTR Test Case
    ==============================================================================
    1AD VTR pop 1 test                                                       OK
    1AD VTR pop 2 test                                                       OK
    1AD VTR push 1 1AD test                                                  OK
    1AD VTR push 1 1Q test                                                   OK
    1AD VTR push 2 1AD test                                                  OK
    1AD VTR push 2 1Q test                                                   OK
    1AD VTR translate 1 -> 1 1AD test                                        OK
    1AD VTR translate 1 -> 1 1Q test                                         OK
    1AD VTR translate 1 -> 2 1AD test                                        OK
    1AD VTR translate 1 -> 2 1Q test                                         OK
    1AD VTR translate 2 -> 1 1AD test                                        OK
    1AD VTR translate 2 -> 1 1Q test                                         OK
    1AD VTR translate 2 -> 2 1AD test                                        OK
    1AD VTR translate 2 -> 2 1Q test                                         OK
    1Q VTR pop 1 test                                                        OK
    1Q VTR push 1 test                                                       OK
    1Q VTR push 2 test                                                       OK
    1Q VTR translate 1 -> 1 test                                             OK
    1Q VTR translate 1 -> 2 test                                             OK

ARP Tests
`````````
::

    ==============================================================================
    ARP Test Case
    ==============================================================================
    ARP                                                                      OK
    ARP Duplicates                                                           OK
    ARP Static                                                               OK
    ARP reply with VRRP virtual src hw addr                                  OK
    MPLS                                                                     OK
    Proxy ARP                                                                OK
    Interface Mirror Proxy ARP                                               OK
    ==============================================================================
    L2BD arp termination Test Case
    ==============================================================================
    L2BD arp term - add 5 hosts, verify arp responses                        OK
    L2BD arp term - delete 3 hosts, verify arp responses                     OK
    L2BD arp term - recreate BD1, readd 3 hosts, verify arp responses        OK
    L2BD arp term - 2 IP4 addrs per host                                     OK
    L2BD arp term - create and update 10 IP4-mac pairs                       OK
    L2BD arp/ND term - hosts with both ip4/ip6                               OK
    L2BD ND term - Add and Del hosts, verify ND replies                      OK
    L2BD ND term - Add and update IP+mac, verify ND replies                  OK
    L2BD arp term - send garps, verify arp event reports                     OK
    L2BD arp term - send duplicate garps, verify suppression                 OK
    L2BD arp term - disable ip4 arp events,send garps, verify no events      OK
    L2BD ND term - send NS packets verify reports                            OK
    L2BD ND term - send duplicate ns, verify suppression                     OK
    L2BD ND term - disable ip4 arp events,send ns, verify no events          OK

P2P Ethernet Subinterface ests
``````````````````````````````
::

    ==============================================================================
    P2P Ethernet tests
    ==============================================================================
    delete/create p2p subif                                                  OK
    create 100k of p2p subifs                                                SKIP
    create 1k of p2p subifs                                                  OK
    ==============================================================================
    P2P Ethernet IPv4 tests
    ==============================================================================
    receive ipv4 packet via p2p subinterface                                 OK
    route rx packet not matching p2p subinterface                            OK
    send ip4 packet via p2p subinterface                                     OK
    drop tx ip4 packet not matching p2p subinterface                         OK
    ==============================================================================
    P2P Ethernet IPv6 tests
    ==============================================================================
    receive ipv6 packet via p2p subinterface                                 OK
    drop rx packet not matching p2p subinterface                             OK
    route rx ip6 packet not matching p2p subinterface                        OK
    send packet via p2p subinterface                                         OK
    drop tx ip6 packet not matching p2p subinterface                         OK
    standard routing without p2p subinterfaces                               OK

GTPU Test Case
``````````````
::

    ==============================================================================
    GTPU Test Case
    ==============================================================================
    Decapsulation test                                                       OK
    Encapsulation test                                                       OK
    Multicast flood test                                                     OK
    Multicast receive test                                                   OK
    Unicast flood test                                                       OK

Other Tests
```````````
::

    ==============================================================================
    VAPI test
    ==============================================================================
    run C VAPI tests                                                         SKIP
    run C++ VAPI tests                                                       SKIP
    ==============================================================================
    Ping Test Case
    ==============================================================================
    basic ping test                                                          OK
    burst ping test                                                          OK
    ==============================================================================
    Template verification, timer tests
    ==============================================================================
    timer less than template timeout                                         OK
    timer greater than template timeout                                      OK
    verify cflow packet fields                                               OK
    ==============================================================================
    JVPP Core Test Case
    ==============================================================================
    JVPP Acl Callback Api Test Case                                          OK
    JVPP Acl Future Api Test Case                                            OK
    JVPP Core Callback Api Test Case                                         OK
    JVPP Core Future Api Test Case                                           OK
    JVPP Ioamexport Callback Api Test Case                                   OK
    JVPP Ioamexport Future Api Test Case                                     OK
    JVPP Ioampot Callback Api Test Case                                      OK
    JVPP Ioampot Future Api Test Case                                        OK
    JVPP Ioamtrace Callback Api Test Case                                    OK
    JVPP Ioamtrace Future Api Test Case                                      OK
    JVPP Snat Callback Api Test Case                                         OK
    JVPP Snat Future Api Test Case                                           OK