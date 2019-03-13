============================================
Control Plane Performance Testing BigPicture
============================================

Intention
---------
Define test methotology to provide Control Plane Performance Testing via several
VPP configuration agents (honeycomb, sweetcomb, vpp-agent and papi)

Posible testing cases
---------------------
 - route creation
 - memif/loopback interafce creation
 - ( IP ADDRESS CONFIGURATION ON INTERFACE )

Multiple configurations
-----------------------
Configuration agents provides multiple posible configruration methods including:

- vpp-agent

  - Etcd or ( REDIS ) for KV datastore engine
  - Grpc or direct KV config
  - single vs multiple values set in one atomic operatoin

- sweetcomb

  - based on documentation only ip address setup on interface is currently supported

Test cases
----------

==VPP-agent with Redis KV database 1c2t

Topology
+------------------------------------------------------------------------+
|  Host1 - SUT                                                           |
|                                                                        |
|  +-----------------------+                                             |
|  |                       |           +---------+       +---------+     |
|  |      Docker with      = GE0       |  Kafka  |       |  Redis  |     |
|  |                       |           |  Docker |       |  Docker |     |
|  |   VPP and VPP-agent   = GE1       +---||----+       +---||----+     |
|  |                       |               ||                ||          |
|  +------||---------------+               ||                ||          |
|         ||       Docker bridge network   ||                ||          |
|         =====================================================          |
|                                                                 eth0   |
+-------------------------------------------------------------------|----+
                                                                    |
+-------------------------------------------------------------------|----+
|  Host2 - MC (Management console)                                eth0   |
|                                                                        |
|  Redis-cli                                                             |
|                                                                        |
+------------------------------------------------------------------------+

Test methotology

This test will use Docker image with compiled VPP and VPP-agent with default VPP 
configuration 1 core for main thread and 2 workers. VPP-agent also requires 
Kafka for mesaaging and KV datastore for configuration. Our test will use 
spotify/kafka docker image and oficial Redis docker image downloaded from 
DockerHub. This 2 images will run on the same physical host, and will be
interconnected via docker bridge network with vpp-agent. Testing data will be
sent from diferent management console host via redis-cli redis client.
Requested configuration will consist from creating 25500 (100x255) IP addresses
on DPDK VPP interface GE0. These Ip addreses will use /32 netmask to create
adequeate routes in fib table. 
Result will be time required to complete this operation and will be presented as
ip address setup rate per second. 

Validation method

Validation of succesfull operation will compare ip address configuration on 
GE0 interafce via vppctl with requested configuration data. If this comparision
will not be equal subsequent test will use reduced number of IP addresses, until
comparison will be equal.

Testing scale
-------------
We expect to test with multiplies (cca 10-20x) of 255 items per test, which could be easily
addresable (172.16.0.0/12 block) to create /24 - /32 interfaces and routes.
Every test need to be repeated 5-10 times to eliminate caches

Known issues
------------
- complexity to setup SUT with particular agent and it's requirements (KV datastore, netopper2-server ...)
- delay while icmp start to respond (probably caused by arp lookup)
- performance can by affected by configuration of required 3th party servers (Redis, Etcd...)
- time of KV datastore/netconf provider accept psuhed data
- time of requested VPP configration will be efective
- time of vpp provider recieve callback of succesfull configuration (if such method exists)


