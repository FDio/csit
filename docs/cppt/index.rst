=========================
VPP Control Plane Testing
=========================

---------
Intention
---------
With increasing number of VPP clients it's difficult to make the right choice
which one to use. The aim of this document is to help pick the right one (for
your use case) based on facts and collected data presented in simple feature/
performance matrix.

--------
Overview
--------
This document describes methodology for testing VPP control plane, using
selected VPP clients: VPP-Agent, Honeycomb, Sweetcomb and PAPI client in
controlled environment.
PAPI client (python API client) is being used as baseline for comparing the
outcomes, because it has the smallest overhead for calling VPP binary APIs and
supports all VPP calls.

-----------------
Performance Tests
-----------------

-------
Preface
-------
- VPP client process affinity will be set specifically to skip first core so
  that it does not interfere with VPP main thread. This will be set and
  checked using taskset utility.
- To increase confidence in measured values, all tests will be performed
  in 10 iterations.
- Presented final value will be computed as average of all iterations with
  lowest and highest value removed from the set.
- Datasets (restconf/netconf data) for tests will be pre-generated to save
  time during test execution.

Definitions
-----------
Unit of work: one unit of requested VPP operation.
Examples: configured IP, created interface, created route, etc.

Test environment parameters
---------------------------

1. Testbed hardware Configuration

   Configuration description can be found on .. this `FD.io Wiki`_ page

   .. _FD.io Wiki: https://wiki.fd.io/view/CSIT/CSIT_LF_testbed#FD.IO_CSIT_testbed_-_Server_HW_Configuration

2. `VPP`_

   .. _VPP: https://wiki.fd.io/view/VPP

   - Version:  19.04-rc0~353-g0f5a3b254~b2236
   - Configuration: default VPP configuration provided by installed Debian package
   - Package source: TODO: attach link to packagecloud.fd.io Debian package provided by VPP project

   ::

     TODO: attach configuration snippet

3. `VPP/Python API`_

   .. _VPP/Python API: https://wiki.fd.io/view/VPP/Python_API

   - Version: TODO: to be defined
   - Topology: TODO: to be defined
   - Configuration: TODO: to be defined

4. `vpp-agent`_

   .. _vpp-agent: https://ligato.io/vpp-agent/

   - Version: TODO: to be defined
   - Redis docker image: TODO: to be defined
   - Kafka docker image: TODO: to be defined
   - Topology:

   ::

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

   - Configuration: .. TODO: to be defined

   ::

     TODO: attach configuration snippet


5. `Honeycomb`_

   .. _Honeycomb: https://wiki.fd.io/view/Honeycomb

   - Version: 1.19.04-2036
   - VPP Java API Version: 19.04-rc0~16-g2fc0352~b50
   - Topology: .. TODO: to be defined
   - Configuration:

   ::

     TODO: attach configuration snippet


6. `Sweetcomb`_

   .. _Sweetcomb: https://wiki.fd.io/view/Sweetcomb

   - Version: .. TODO: to be defined
   - Topology: .. TODO: to be defined

   ::

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

   - Configuration: .. TODO: to be defined

   ::

     TODO: attach configuration snippet


-----------
Measurement
-----------
- Total time: total time needed for the client to complete requested operation
  (eg: Configure 255 IPs on selected interface).
  Measurement unit: milliseconds
- Time per unit: time needed to complete one unit of work for requested
  operation, which will be calculated with following formula:

  ::

    time per unit = total time / units of work

  (eg: if total time for configuring 255 IPs on interface = 100ms, then:

  ::

    time per unit = 100 / 255 = 0,3921 ms

  meaning: one IP was configured in 0,3921 milliseconds)
  Measurement unit: milliseconds

----------
Validation
----------
Validation will be done using vppctl utility with corresponding VPP command
and will not be part of time measured. Due to the different nature of client
communication, each test case will include validation method for each tested
client.

----------------
Resource scaling
----------------
In our tests we will be scaling resources of the VPP docker container where
VPP and VPP client will be installed.
- CPU cores available for VPP and VPP client, scaled linearly to use: 2,4,8.
- VPP will be locked to use first core by adjusting it's configuration.
- VPP client will be locked to the remaining cores using taskset utility.

-----------------
Test case scaling
-----------------
Initial units of work scale: 1, 500, 5500, 10500, 15500, 20500, 25500, 62025.
This scale will be re-adjusted based on the test results if needed.

----------
Test Cases
----------
TC01: Configure IP address on interface

-------------------------
Test results presentation
-------------------------
Measured values will be presented in a matrix where:
  - X axis: Test cases with individual scales
  - Y axis: VPP client
  - value: measured time in milliseconds

  +---------------+-------------------------------------------------------+
  |  Client / TC  |        TC01 - Configure IP address on interface       |
  |               +------+------+------+------+------+------+------+------+
  | Units of work |     1|   500|  5500| 10500| 15500| 20500| 25500| 62025|
  +===============+======+======+======+======+======+======+======+======+
  |  Python API   |      |      |      |      |      |      |      |      |
  +---------------+------+------+------+------+------+------+------+------+
  |   vpp-agent   |      |      |      |      |      |      |      |      |
  +---------------+------+------+------+------+------+------+------+------+
  |   Sweetcomb   |      |      |      |      |      |      |      |      |
  +---------------+------+------+------+------+------+------+------+------+
  |   Honeycomb   |      |      |      |      |      |      |      |      |
  +---------------+------+------+------+------+------+------+------+------+


