.. _tested_physical_topologies:

Physical Testbeds
=================

All :abbr:`FD.io (Fast Data Input/Ouput)` :abbr:`CSIT (Continuous System
Integration and Testing)` performance testing listed in this report are
executed on physical testbeds built with bare-metal servers hosted by
:abbr:`LF (Linux Foundation)` FD.io project.

Two testbed topologies are used:

- **3-Node Topology**: Consisting of two servers acting as SUTs
  (Systems Under Test) and one server as TG (Traffic Generator), all
  connected in ring topology. Used for executing all of the data plane
  tests including overlay tunnels and IPSec tests.
- **2-Node Topology**: Consisting of one server acting as SUTs (Systems
  Under Test) and one server as TG (Traffic Generator), both connected
  in ring topology. Used for execution of tests without any overlay
  tunnel encapsulations. Added in CSIT rls18.07.

Current FD.io production testbeds are built with servers based on two
processor generations of Intel Xeons: Haswell-SP (E5-2699v3) and Skylake
(Platinum 8180). Testbeds built with servers based on Arm processors are
in the process of being added to FD.io production.

Server SUT and DUT performance depends on server and processor type,
hence results for testbeds based on different servers must be reported
separately, and compared if appropriate.

Following sections describe existing production testbed types.

3-Node Xeon Haswell (3n-hsw)
----------------------------

3n-hsw testbed is based on three Cisco UCS-c240m3 servers each equipped
with two Intel Xeon Haswell-SP E5-2699v3 2.3 GHz 18 core processors.
Physical testbed topology is depicted in a figure below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
        \centering
            \includesvg[width=0.90\textwidth]{../_tmp/src/introduction/testbed-3n-hsw}
            \label{fig:testbed-3n-hsw}
        \end{figure}

.. only:: html

    .. figure:: testbed-3n-hsw.svg
        :alt: testbed-3n-hsw
        :align: center

SUT1 and SUT2 servers are populated with the following NIC models:

#. NIC-1: VIC 1385 2p40GE Cisco.
#. NIC-2: NIC x520 2p10GE Intel.
#. NIC-3: empty.
#. NIC-4: NIC xl710-QDA2 2p40GE Intel.
#. NIC-5: NIC x710-DA2 2p10GE Intel.
#. NIC-6: QAT 8950 50G (Walnut Hill) Intel.

TG servers run T-Rex application and are populated with the following
NIC models:

#. NIC-1: NIC xl710-QDA2 2p40GE Intel.
#. NIC-2: NIC x710-DA2 2p10GE Intel.
#. NIC-3: empty.
#. NIC-4: NIC xl710-QDA2 2p40GE Intel.
#. NIC-5: NIC x710-DA2 2p10GE Intel.
#. NIC-6: NIC x710-DA2 2p10GE Intel. (For self-tests.)

All Intel Xeon Haswell servers run with Intel Hyper-Threading disabled,
making the number of logical cores exposed to Linux match the number of
18 physical cores per processor socket.

Complete 3n-hsw testbeds specification is available on
`CSIT LF testbed <https://wiki.fd.io/view/CSIT/CSIT_LF_testbed>`_
wiki page.

Total of three 3n-hsw testbeds are in operation in FD.io labs.

3-Node Xeon Skylake (3n-skx)
----------------------------

3n-skx testbed is based on three SuperMicro SYS-7049GP-TRT servers each
equipped with two Intel Xeon Skylake Platinum 8180 2.5 GHz 28 core
processors. Physical testbed topology is depicted in a figure below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
        \centering
            \includesvg[width=0.90\textwidth]{../_tmp/src/introduction/testbed-3n-skx}
            \label{fig:testbed-3n-skx}
        \end{figure}

.. only:: html

    .. figure:: testbed-3n-skx.svg
        :alt: testbed-3n-skx
        :align: center

SUT1 and SUT2 servers are populated with the following NIC models:

#. NIC-1: x710-DA4 4p10GE Intel.
#. NIC-2: xxv710-DA2 2p25GE Intel.
#. NIC-3: empty, future expansion.
#. NIC-4: empty, future expansion.
#. NIC-5: empty, future expansion.
#. NIC-6: empty, future expansion.

TG servers run T-Rex application and are populated with the following
NIC models:

#. NIC-1: x710-DA4 4p10GE Intel.
#. NIC-2: xxv710-DA2 2p25GE Intel.
#. NIC-3: empty, future expansion.
#. NIC-4: empty, future expansion.
#. NIC-5: empty, future expansion.
#. NIC-6: x710-DA4 4p10GE Intel. (For self-tests.)

All Intel Xeon Skylake servers run with Intel Hyper-Threading enabled,
doubling the number of logical cores exposed to Linux, with 56 logical
cores and 28 physical cores per processor socket.

Complete 3n-skx testbeds specification is available on
`CSIT LF lab extension <https://wiki.fd.io/view/CSIT/fdio_csit_lab_ext_lld_draft>`_
wiki page.

Total of two 3n-skx testbeds are in operation in FD.io labs.

2-Node Xeon Skylake (2n-skx)
----------------------------

2n-skx testbed is based on two SuperMicro SYS-7049GP-TRT servers each
equipped with two Intel Xeon Skylake Platinum 8180 2.5 GHz 28 core
processors. Physical testbed topology is depicted in a figure below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
        \centering
            \includesvg[width=0.90\textwidth]{../_tmp/src/introduction/testbed-2n-skx}
            \label{fig:testbed-2n-skx}
        \end{figure}

.. only:: html

    .. figure:: testbed-2n-skx.svg
        :alt: testbed-2n-skx
        :align: center

SUT servers are populated with the following NIC models:

#. NIC-1: x710-DA4 4p10GE Intel.
#. NIC-2: xxv710-DA2 2p25GE Intel.
#. NIC-3: mcx556a-edat ConnectX5 2p100GE Mellanox. (Not used yet.)
#. NIC-4: empty, future expansion.
#. NIC-5: empty, future expansion.
#. NIC-6: empty, future expansion.

TG servers run T-Rex application and are populated with the following
NIC models:

#. NIC-1: x710-DA4 4p10GE Intel.
#. NIC-2: xxv710-DA2 2p25GE Intel.
#. NIC-3: mcx556a-edat ConnectX5 2p100GE Mellanox. (Not used yet.)
#. NIC-4: empty, future expansion.
#. NIC-5: empty, future expansion.
#. NIC-6: x710-DA4 4p10GE Intel. (For self-tests.)

All Intel Xeon Skylake servers run with Intel Hyper-Threading enabled,
doubling the number of logical cores exposed to Linux, with 56 logical
cores and 28 physical cores per processor socket.

Complete 2n-skx testbed specification is available on
`CSIT LF lab extension <https://wiki.fd.io/view/CSIT/fdio_csit_lab_ext_lld_draft>`_
wiki page.

Total of four 2n-skx testbeds are in operation in FD.io labs.
