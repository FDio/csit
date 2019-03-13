=========================
VPP Control Plane Testing
=========================

--------
Overview
--------
With increasing number of VPP clients it's difficult to make the right choice
which one to use. The aim of this document is to help pick the right one (for
your use case) based on facts and collected data presented in simple feature/
performance matrix.

This document describes the methodology for testing VPP control plane, using
selected VPP clients: VPP-Agent, Honeycomb, Sweetcomb and PAPI client in
controlled environment.

PAPI client (python API client) is being used as baseline for comparing the
outcomes, because it has the smallest overhead for calling VPP binary APIs and
supports all VPP calls.

---------------------------------
Control plane performance testing
---------------------------------
Methodology
-----------
- Topology will be brought up before Robot Framework tests are executed.
- The topology will be configured in Robot Framework according to
  the specification below.
- Data configuration will be tested.
- Datasets (restconf/netconf data) for tests will be pre-generated to save
  time during test execution.
- Configuration removal will also be tested as part of each testcase that
  configures items.
- State data retrieval will be tested.
- Both synchronous and asynchronous calls will be measured.
- Synchronous call measurements will correspond to API execution time.
- Asynchronous calls will be measured in two ways - API execution time and
  the time between API execution and API callback notifying that it has
  finished. No other calls may be executed during the waiting for the callback,
  as that would interfere with performance.
- To increase confidence in measured values, all tests will be performed
  in 10 iterations.
- The final value will be computed as average of time needed to configure one
  item from all iterations with lowest and highest value removed from the set.
- Total time: total time needed for the client to complete the requested
  operation (eg: Configure 255 IPs on selected interface).
- Time per item: average time needed to configure one configuration item for
  the requested operation, which will be calculated using the following
  formula::

    time per item = total time / # of configuration items

  For example: total time for configuring 255 IPs on interface took 100ms::

    time per item = 100 / 255 = 0,3921 ms

  We measured that one IP was configured, on average, in 0,3921 milliseconds
- Measurement unit: milliseconds

Validation
----------
Validation will be done using PAPI with corresponding VPP command
and will not be part of time measured. Due to the different nature of client
communication, each test case will include validation method for each tested
client.

Test environment parameters
---------------------------

#. Testbed hardware Configuration

   Configuration description can be found on this `FD.io Wiki`_ page

   .. _FD.io Wiki: https://wiki.fd.io/view/CSIT/CSIT_LF_testbed#FD.IO_CSIT_testbed_-_Server_HW_Configuration

#. Versions

   - Different versions of VPP could affect control plane performance, since
     the code that handles the binary API calls might be different. Ideally
     we'd test with the same VPP version across all clients, but the clients
     might not necessarily support the same version. How to resolve this is an
     open question, but we could start with release 19.04 as PoC. For master,
     we'll update the version when the package disappears from packagecloud,
     just as it's done in regular CSIT testing.
   - We'll use the latest version of each client. This brings the possibility
     of an API mismatch between the client and VPP. If there is such
     a mismatch, the test will fall back to latest VPP and the job should send
     an e-mail about the mismatch. Or we could just let the test fail, but
     the e-mail should still be sent, so that we have a reliable way of knowing
     that the reference VPP version needs to be updated.

#. Containerization

   Some clients have been designed/are used in a container (or the whole
   topology has been designed as such). The containerization aspect of VPP/API
   client will be informed by how the actual client is used in real world.
   The client might be used both in a container and directly on the host.

#. `VPP`_

   .. _VPP: https://wiki.fd.io/view/VPP

   - Version:  Stable 19.04/master that works with as many clients as possbile
   - Package source: https://packagecloud.io/fdio/1904
   - Configuration: Default VPP configuration provided by installed package
     with possible performance tweaks:

     - Number of cores/worker threads
     - Memory

     ::

       TODO: attach configuration snippet

   - Containerization: Both, depending on API client's use case.

#. `VPP/Python API`_

   .. _VPP/Python API: https://wiki.fd.io/view/VPP/Python_API

   - Version: Same as VPP
   - Supported protocols: N/A, PAPI executes direct binary calls
   - Configuration: N/A
   - Interprocess communication: shm, socket
   - Client Containerization: No
   - VPP Containerization: No
   - Topology: VPP running directly on the host

#. `vpp-agent`_

   .. _vpp-agent: https://ligato.io/vpp-agent/

   - Version: TODO: to be defined
   - Redis docker image: redis
   - Kafka docker image: spotify/kafka
   - Agent Docker container with VPP and VPP-agent
   - Client Docker container with redis-cli binary and test data
   - Supported Protocols: gRPC, .. TODO: others
   - Configuration: .. TODO: to be defined
     ::

       TODO: attach configuration snippet

   - Client Containerization: Yes
   - VPP Containerization: Yes
   - Topology::

      +-----------------------------------------------------------+
      |  Host1 - SUT                                              |
      |                                                           |
      |  +-Core 1-2-+                                             |
      |  |          |           +-Core 3-4-+      +-Core 5-6-+    |
      |  |   Agent  = GE0       |  Kafka   |      |  Redis   |    |
      |  |          |           |  Docker  |      |  Docker  |    |
      |  |  Docker  = GE1       +---||-----+      +---||-----+    |
      |  |          |               ||                ||          |
      |  +----||----+               ||                ||          |
      |       ||                    ||                ||          |
      |    ===================================================    |
      |       Docker Bridge Network                ||             |
      |                                 +-Core 6-7----+           |
      |                                 |   Client    |           |
      |                                 |   Docker    |           |
      |                                 +-------------+           |
      |                                                           |
      +-----------------------------------------------------------+


#. `Honeycomb`_

   .. _Honeycomb: https://wiki.fd.io/view/Honeycomb

   - Version: Latest master
   - VPP Java API Version: Defined by Honeycomb dependency
   - Supported Protocols: Netconf (over either TCP and SSH),
     Restconf (over HTTP, HTTPS and websocket)
   - Package source: https://packagecloud.io/fdio/1904
   - Configuration: Default Honeycomb configuration provided by installed
     package with possible performance tweaks along with Java tuning:

       - netconf-netty-threads
       - netconf-tcp-enabled
       - netconf-ssh-enabled
       - restconf-http-enabled
       - restconf-https-enabled

         - These four enabled/disabled config options will be enabled/disabled
           on test case basis (only the two protocols tested will be enabled)

       - restconf-pool-max-size
       - restconf-pool-min-size
       - restconf-acceptors-size
       - restconf-selectors-size
       - restconf-https-acceptors-size
       - restconf-https-selectors-size
       - log level ERROR
       - TODO: Java options
       - possible java options: https://jira.fd.io/browse/HC2VPP-398

     ::

       /opt/honeycomb/config/netconf.json
       {
        "netconf-netty-threads": 2,
        "netconf-tcp-enabled": "false",
        "netconf-tcp-binding-address": "0.0.0.0",
        "netconf-tcp-binding-port": 7777,
        "netconf-ssh-enabled": "true",
        "netconf-ssh-binding-address": "0.0.0.0",
        "netconf-ssh-binding-port": 2831,
        "netconf-notification-stream-name": "honeycomb"
       }

       /opt/honeycomb/config/restconf.json
       {
         "restconf-http-enabled": "true",
         "restconf-root-path": "/restconf",
         "restconf-binding-address": "0.0.0.0",
         "restconf-port": 8183,
         "restconf-https-enabled": "false",
         "restconf-https-binding-address": "0.0.0.0",
         "restconf-https-port": 8445,
         "restconf-keystore": "/honeycomb-keystore",
         "restconf-keystore-password": "OBF:1v9s1unr1unn1vv51zlk1t331vg91x1b1vgl1t331zly1vu51uob1uo71v8u",
         "restconf-keystore-manager-password": "OBF:1v9s1unr1unn1vv51zlk1t331vg91x1b1vgl1t331zly1vu51uob1uo71v8u",
         "restconf-truststore": "/honeycomb-keystore",
         "restconf-truststore-password": "OBF:1v9s1unr1unn1vv51zlk1t331vg91x1b1vgl1t331zly1vu51uob1uo71v8u",
         "restconf-websocket-address": "0.0.0.0",
         "restconf-websocket-port": 7779,
         "restconf-pool-max-size": 10,
         "restconf-pool-min-size": 1,
         "restconf-acceptors-size": 1,
         "restconf-selectors-size": 1,
         "restconf-https-acceptors-size": 1,
         "restconf-https-selectors-size": 1
       }

       /opt/honeycomb/config/logback.xml
       ...
         <logger name="org.opendaylight" level="ERROR"/>
         <logger name="io.fd" level="ERROR"/>
       ...

   - Interprocess communication: shm, provided by JVPP, not configurable
   - Client Containerization: No
   - VPP Containerization: No
   - Topology: Both VPP and Honeycomb running directly on the host

#. `Sweetcomb`_

   .. _Sweetcomb: https://wiki.fd.io/view/Sweetcomb

   - Version: .. TODO: to be defined
   - Agent Docker container with VPP, sysrepod, sysrepo-plugind and netopeer2-server
   - Client Docker container with netoopeer2-cli binary
   - Supported Protocols: Netconf (over either TCP and SSH), Restconf
   - Configuration: .. TODO: to be defined
     ::

       TODO: attach configuration snippet

   - Interprocess communication: .. TODO: to be defined
   - Client Containerization: Yes
   - VPP Containerization: Yes
   - Topology::

      .. TODO: to be defined
      +-----------------------------------------------------------+
      |  Host1 - SUT                                              |
      |                                                           |
      |  +-Core 1-2-+                                             |
      |  |          |                                             |
      |  |   Agent  = GE0                                         |
      |  |          |                                             |
      |  |  Docker  = GE1                                         |
      |  |          |                                             |
      |  +------||--+                                             |
      |         ||                                                |
      |    ===================================================    |
      |       Docker Bridge Network                ||             |
      |                                 +-Core 6-7----+           |
      |                                 |   Client    |           |
      |                                 |   Docker    |           |
      |                                 +-------------+           |
      |                                                           |
      +-----------------------------------------------------------+


Resource scaling/performance considerations
-------------------------------------------
These resources of the SUT/Docker containers running on the SUT will be scaled:

- CPU cores available for VPP, configured in VPP configuration.
- CPU cores available for API clients, configured with the ``taskset`` utility
  if not possible in API client's configuration.
- There will be no overlap between cores available for VPP and the API client.
- Memory available for VPP, configured in VPP configuration.
- Memory available for API clients if available, configured in API client's
  configuration.
- Interprocess communication method, such as socket vs shared memory,
  if available.
- Logging level.
- Client-specific performance configuration (e.g. Java tuning in Honeycomb)
- Possible other performance tweaks currently not considered.

Test case scaling
-----------------
Initial configuration items scale: 1, 500, 5500, 10500, 15500, 20500, 25500,
62025.
This scale will be re-adjusted based on test results if needed.

----------
Test cases
----------
TC01: Configure IP address(es) on an interface

-------------------------
Test results presentation
-------------------------
Measured values will be presented in a matrix where:
  - X axis: Test cases with individual scales
  - Y axis: VPP client
  - value: measured time in milliseconds

::

  +---------------+-------------------------------------------------------+
  |  Client / TC  |    TC01 - Configure IP address(es) on an interface    |
  |---------------+------+------+------+------+------+------+------+------+
  |  # of items   |     1|   500|  5500| 10500| 15500| 20500| 25500| 62025|
  +===============+======+======+======+======+======+======+======+======+
  |  Python API   |      |      |      |      |      |      |      |      |
  +---------------+------+------+------+------+------+------+------+------+
  |   vpp-agent   |      |      |      |      |      |      |      |      |
  +---------------+------+------+------+------+------+------+------+------+
  |   Sweetcomb   |      |      |      |      |      |      |      |      |
  +---------------+------+------+------+------+------+------+------+------+
  |   Honeycomb   |      |      |      |      |      |      |      |      |
  +---------------+------+------+------+------+------+------+------+------+
