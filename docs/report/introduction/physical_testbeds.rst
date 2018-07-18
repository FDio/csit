Physical Testbeds
=================

All :abbr:`FD.io (Fast Data Input/Ouput)` :abbr:`CSIT (Continuous System
Integration and Testing)` performance testing listed in this report are
executed on physical testbeds built with bare-metal servers hosted by
:abbr:`LF (Linux Foundation)` FD.io project.

Two testbed topologies are used:

- **3-Node Topology** - Consisting of two servers acting as SUTs
  (Systems Under Test) and one server as TG (Traffic Generator), all
  connected in ring topology. Used for executing all of the data plane
  tests including overlay tunnels and IPSec tests.
- **2-Node Topology** - Consisting of one server acting as SUTs (Systems
  Under Test) and one server as TG (Traffic Generator), both connected
  back-to-back. Used for execution of tests without any overlay tunnel
  encapsulations. Added in CSIT rls18.07.

Current FD.io production testbeds are built with servers based on two
Intel Xeon processor generations: Intel Xeon Haswell-SP (Model
E5-2699v3) and Intel Xeon Skylake (Model Platinum 8180). Testbeds built
with servers based on Arm processors are in the process of being added
to FD.io production.

Note that SUT performance greatly depends on server and processor type,
hence results for testbeds based on different servers must be reported
separately, and compared if appropriate.

Following sections describe existing production testbeds.

3-Node Xeon Haswell (3n-hsw)
----------------------------

3n-hsw testbed is based on three Cisco UCS-c240m3 servers each equipped
with two Intel Xeon Haswell-SP E5-2699v3 2.3 GHz 18 core processors.
Physical testbed topology is depicted in a figure below.

Figure: 3n-hsw testbed topology.

SUT1 and SUT2 NIC population is as follows:

#. NIC-1: VIC 1385 2p40GE Cisco.
#. NIC-2: NIC x520 2p10GE Intel.
#. NIC-3: empty.
#. NIC-4: NIC xl710 2p40GE Intel.
#. NIC-5: NIC x710 2p10GE Intel.
#. NIC-6: QAT 8950 50G (Walnut Hill) Intel.

Complete 3n-hsw testbed specification is available on
`CSIT LF testbed <https://wiki.fd.io/view/CSIT/CSIT_LF_testbed>`_
wiki page.

3-Node Xeon Skylake (3n-skx)
----------------------------

3n-skx testbed is based on three SuperMicro SYS-7049GP-TRT servers each
equipped with two Intel Xeon Skylake Platinum 8180 2.5 GHz 28 core
processors. Physical testbed topology is depicted in a figure below.

Figure: 3n-skx testbed topology.

SUT1 and SUT2 NIC population is as follows:

#. NIC-1: x710-4p10GE Intel.
#. NIC-2: xxv710-DA2-2p25GE Intel.
#. NIC-3: ConnectX5-2p100GE Mellanox.
#. NIC-4: empty, future expansion.
#. NIC-5: empty, future expansion.
#. NIC-6: empty, future expansion.

Complete 3n-skx testbed pecification is available on
`CSIT LF lab extension <https://wiki.fd.io/view/CSIT/fdio_csit_lab_ext_lld_draft>`_
wiki page.

2-Node Xeon Skylake (2n-skx)
----------------------------

2n-skx testbed is based on two SuperMicro SYS-7049GP-TRT servers each
equipped with two Intel Xeon Skylake Platinum 8180 2.5 GHz 28 core
processors. Physical testbed topology is depicted in a figure below.

Figure: 2n-skx testbed topology.

SUT1 NIC population is as follows:

#. NIC-1: x710-4p10GE Intel.
#. NIC-2: xxv710-DA2-2p25GE Intel.
#. NIC-3: ConnectX5-2p100GE Mellanox.
#. NIC-4: empty, future expansion.
#. NIC-5: empty, future expansion.
#. NIC-6: empty, future expansion.

Complete 2n-skx testbed pecification is available on
`CSIT LF lab extension <https://wiki.fd.io/view/CSIT/fdio_csit_lab_ext_lld_draft>`_
wiki page.