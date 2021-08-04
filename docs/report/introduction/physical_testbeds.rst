.. _tested_physical_topologies:

Performance Physical Testbeds
=============================

All :abbr:`FD.io (Fast Data Input/Ouput)` :abbr:`CSIT (Continuous System
Integration and Testing)` performance test results included in this
report are executed on the physical testbeds hosted by :abbr:`LF (Linux
Foundation)` FD.io project, unless otherwise noted.

Two physical server topology types are used:

- **2-Node Topology**: Consists of one server acting as a System Under
  Test (SUT) and one server acting as a Traffic Generator (TG), with
  both servers connected into a ring topology. Used for executing tests
  that require frame encapsulations supported by TG.

- **3-Node Topology**: Consists of two servers acting as a Systems Under
  Test (SUTs) and one server acting as a Traffic Generator (TG), with
  all servers connected into a ring topology. Used for executing tests
  that require frame encapsulations not supported by TG e.g. certain
  overlay tunnel encapsulations and IPsec. Number of native Ethernet,
  IPv4 and IPv6 encapsulation tests are also executed on these testbeds,
  for comparison with 2-Node Topology.

Current FD.io production testbeds are built with SUT servers based on
the following processor architectures:

- Intel Xeon: Skylake Platinum 8180, Cascadelake 6252N, (Icelake 8358 
  to be added).
- Intel Atom: Denverton C3858.
- Arm: TaiShan 2280, hip07-d05.
- AMD EPYC: Zen2 7532.

CSIT-2106 report data for Intel Xeon Icelake testbeds comes from
testbeds in Intel labs set up per CSIT specification and running CSIT
code. Physical setup used is specified in 2n-icx and 3n-icx sections
below. For details about tested VPP and CSIT versions
see :ref:`vpp_performance_tests_release_notes`.

Server SUT performance depends on server and processor type, hence
results for testbeds based on different servers must be reported
separately, and compared if appropriate.

Complete technical specifications of compute servers used in CSIT
physical testbeds are maintained in FD.io CSIT repository:
https://git.fd.io/csit/tree/docs/lab/testbed_specifications.md.

Physical NICs and Drivers
-------------------------

SUT and TG servers are equipped with a number of different NIC models
with some of them tested on SUT servers with multiple drivers.

VPP is performance tested with the following NICs and drivers:

#. 2p10GE: x520, x550, x553 Intel (codename Niantic)
   - DPDK Poll Mode Driver (PMD).
#. 4p10GE: x710-DA4 Intel (codename Fortville, FVL)
   - DPDK PMD.
   - AVF in PMD mode.
   - AF_XDP in PMD mode.
#. 2p25GE: xxv710-DA2 Intel (codename Fortville, FVL)
   - DPDK PMD.
   - AVF in PMD mode.
   - AF_XDP in PMD mode.
#. 2p100GE: cx556a-edat Mellanox ConnectX5
   - RDMA_core in PMD mode.
#. 2p100GE: E810-2CQDA2 Intel (codename Columbiaville, CVL)
   - DPDK PMD.
   - AVF in PMD mode.

DPDK applications, testpmd and l3fwd, are tested exclusively with DPDK
drivers for all NICs.

TRex is using DPDK drivers for all NICs.

For more information see :ref:`vpp_test_environment`
and :ref:`dpdk_test_environment` 

2-Node AMD EPYC Zen2 (2n-zn2)
-----------------------------

One 2n-zn2 testbed in in operation in FD.io labs. It is built based on
two SuperMicro SuperMicro AS-1114S-WTRT servers, with SUT and TG servers
equipped with one AMD EPYC Zen2 7532 processor each (256 MB Cache, 2.40
GHz, 32 cores). 2n-zn2 physical topology is shown below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/introduction/}}
                \includegraphics[width=0.90\textwidth]{testbed-2n-zn2}
                \label{fig:testbed-2n-zn2}
        \end{figure}

.. only:: html

    .. figure:: testbed-2n-zn2.svg
        :alt: testbed-2n-zn2
        :align: center

SUT server is populated with the following NIC models:

#. NIC-1: x710-DA4 4p10GE Intel.
#. NIC-2: xxv710-DA2 2p25GE Intel.
#. NIC-3: cx556a-edat ConnectX5 2p100GE Mellanox.

TG server runs TRex application and is populated with the following
NIC models:

#. NIC-1: x710-DA4 4p10GE Intel.
#. NIC-2: xxv710-DA2 2p25GE Intel.
#. NIC-3: cx556a-edat ConnectX5 2p100GE Mellanox.

All AMD EPYC Zen2 7532 servers run with AMD SMT enabled, doubling the
number of logical cores exposed to Linux.

2-Node Xeon Cascadelake (2n-clx)
---------------------------------

Three 2n-clx testbeds are in operation in FD.io labs. Each 2n-clx testbed
is built with two SuperMicro SYS-7049GP-TRT servers, SUTs are equipped with two
Intel Xeon Gold 6252N processors (35.75 MB Cache, 2.30 GHz, 24 cores).
TGs are equiped with Intel Xeon Cascade Lake Platinum 8280 processors (38.5 MB
Cache, 2.70 GHz, 28 cores). 2n-clx physical topology is shown below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/introduction/}}
                \includegraphics[width=0.90\textwidth]{testbed-2n-clx}
                \label{fig:testbed-2n-clx}
        \end{figure}

.. only:: html

    .. figure:: testbed-2n-clx.svg
        :alt: testbed-2n-clx
        :align: center

SUT servers are populated with the following NIC models:

#. NIC-1: x710-DA4 4p10GE Intel.
#. NIC-2: xxv710-DA2 2p25GE Intel.
#. NIC-3: cx556a-edat ConnectX5 2p100GE Mellanox.
#. NIC-4: empty, future expansion.
#. NIC-5: empty, future expansion.
#. NIC-6: empty, future expansion.

TG servers run T-Rex application and are populated with the following
NIC models:

#. NIC-1: x710-DA4 4p10GE Intel.
#. NIC-2: xxv710-DA2 2p25GE Intel.
#. NIC-3: cx556a-edat ConnectX5 2p100GE Mellanox.
#. NIC-4: empty, future expansion.
#. NIC-5: empty, future expansion.
#. NIC-6: x710-DA4 4p10GE Intel. (For self-tests.)

All Intel Xeon Cascadelake servers run with Intel Hyper-Threading enabled,
doubling the number of logical cores exposed to Linux.

2-Node Xeon Icelake (2n-icx) EXPERIMENTAL
-----------------------------------------

One 2n-icx testbed located in Intel labs was used for CSIT testing. It
is built with two SuperMicro SYS-740GP-TNRT servers. SUT is equipped
with two Intel Xeon Gold 6338N processors (48 MB Cache, 2.20 GHz, 32
cores). TG is equiped with two Intel Xeon Ice Lake Platinum 8360Y
processors (54 MB Cache, 2.40 GHz, 36 cores). 2n-icx physical topology
is shown below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/introduction/}}
                \includegraphics[width=0.90\textwidth]{testbed-2n-icx}
                \label{fig:testbed-2n-icx}
        \end{figure}

.. only:: html

    .. figure:: testbed-2n-icx.svg
        :alt: testbed-2n-icx
        :align: center

SUT and TG servers are populated with the following NIC models:

#. NIC-1: E810-2CQDA2 2p100GbE Intel.

All Intel Xeon Icelake servers run with Intel Hyper-Threading enabled,
doubling the number of logical cores exposed to Linux.

3-Node Xeon Icelake (3n-icx) EXPERIMENTAL
-----------------------------------------

One 3n-icx testbed located in Intel labs was used for CSIT testing. It
is built with three SuperMicro SYS-740GP-TNRT servers. SUTs are
equipped each with two Intel Xeon Platinum 8360Y processors (54 MB
Cache, 2.40 GHz, 36 cores). TG is equiped with two Intel Xeon Ice Lake
Platinum 8360Y processors (54 MB Cache, 2.40 GHz, 36 cores). 3n-icx
physical topology is shown below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/introduction/}}
                \includegraphics[width=0.90\textwidth]{testbed-3n-icx}
                \label{fig:testbed-3n-icx}
        \end{figure}

.. only:: html

    .. figure:: testbed-3n-icx.svg
        :alt: testbed-3n-icx
        :align: center

SUT and TG servers are populated with the following NIC models:

#. NIC-1: E810-2CQDA2 2p100GbE Intel.

All Intel Xeon Icelake servers run with Intel Hyper-Threading enabled,
doubling the number of logical cores exposed to Linux.

2-Node Xeon Skylake (2n-skx)
----------------------------

Four 2n-skx testbeds are in operation in FD.io labs. Each 2n-skx testbed
is built with two SuperMicro SYS-7049GP-TRT servers, each in turn
equipped with two Intel Xeon Skylake Platinum 8180 processors (38.5 MB
Cache, 2.50 GHz, 28 cores). 2n-skx physical topology is shown below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/introduction/}}
                \includegraphics[width=0.90\textwidth]{testbed-2n-skx}
                \label{fig:testbed-2n-skx}
        \end{figure}

.. only:: html

    .. figure:: testbed-2n-skx.svg
        :alt: testbed-2n-skx
        :align: center

SUT servers are populated with the following NIC models:

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

3-Node Xeon Skylake (3n-skx)
----------------------------

Two 3n-skx testbeds are in operation in FD.io labs. Each 3n-skx testbed
is built with three SuperMicro SYS-7049GP-TRT servers, each in turn
equipped with two Intel Xeon Skylake Platinum 8180 processors (38.5 MB
Cache, 2.50 GHz, 28 cores). 3n-skx physical topology is shown below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/introduction/}}
                \includegraphics[width=0.90\textwidth]{testbed-3n-skx}
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

2-Node Atom Denverton (2n-dnv)
------------------------------

2n-dnv testbed is built with: i) one Intel S2600WFT server acting as TG
and equipped with two Intel Xeon Skylake Platinum 8180 processors (38.5
MB Cache, 2.50 GHz, 28 cores), and ii) one SuperMicro SYS-E300-9A server
acting as SUT and equipped with one Intel Atom C3858 processor (12 MB
Cache, 2.00 GHz, 12 cores). 2n-dnv physical topology is shown below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/introduction/}}
                \includegraphics[width=0.90\textwidth]{testbed-2n-dnv}
                \label{fig:testbed-2n-dnv}
        \end{figure}

.. only:: html

    .. figure:: testbed-2n-dnv.svg
        :alt: testbed-2n-dnv
        :align: center

SUT server have four internal 10G NIC port:

#. P-1: x553 copper port.
#. P-2: x553 copper port.
#. P-3: x553 fiber port.
#. P-4: x553 fiber port.

TG server run T-Rex software traffic generator and are populated with the
following NIC models:

#. NIC-1: x550-T2 2p10GE Intel.
#. NIC-2: x550-T2 2p10GE Intel.
#. NIC-3: x520-DA2 2p10GE Intel.
#. NIC-4: x520-DA2 2p10GE Intel.

The 2n-dnv testbed is in operation in Intel SH labs.

3-Node Atom Denverton (3n-dnv)
------------------------------

One 3n-dnv testbed is built with: i) one SuperMicro SYS-7049GP-TRT
server acting as TG and equipped with two Intel Xeon Skylake Platinum
8180 processors (38.5 MB Cache, 2.50 GHz, 28 cores), and ii) one
SuperMicro SYS-E300-9A server acting as SUT and equipped with one Intel
Atom C3858 processor (12 MB Cache, 2.00 GHz, 12 cores). 3n-dnv physical
topology is shown below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/introduction/}}
                \includegraphics[width=0.90\textwidth]{testbed-3n-dnv}
                \label{fig:testbed-3n-dnv}
        \end{figure}

.. only:: html

    .. figure:: testbed-3n-dnv.svg
        :alt: testbed-3n-dnv
        :align: center

SUT1 and SUT2 servers are populated with the following NIC models:

#. NIC-1: x553 2p10GE fiber Intel.
#. NIC-2: x553 2p10GE copper Intel.

TG servers run T-Rex application and are populated with the following
NIC models:

#. NIC-1: x710-DA4 4p10GE Intel.

3-Node ARM TaiShan (3n-tsh)
---------------------------

One 3n-tsh testbed is built with: i) one SuperMicro SYS-7049GP-TRT
server acting as TG and equipped with two Intel Xeon Skylake Platinum
8180 processors (38.5 MB Cache, 2.50 GHz, 28 cores), and ii) one Huawei
TaiShan 2280 server acting as SUT and equipped with one  hip07-d05
processor (64* ARM Cortex-A72). 3n-tsh physical topology is shown below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/introduction/}}
                \includegraphics[width=0.90\textwidth]{testbed-3n-tsh}
                \label{fig:testbed-3n-tsh}
        \end{figure}

.. only:: html

    .. figure:: testbed-3n-tsh.svg
        :alt: testbed-3n-tsh
        :align: center

SUT1 and SUT2 servers are populated with the following NIC models:

#. NIC-1: connectx4 2p25GE Mellanox.
#. NIC-2: x520 2p10GE Intel.

TG server runs T-Rex application and is populated with the following
NIC models:

#. NIC-1: x710-DA4 4p10GE Intel.
#. NIC-2: xxv710-DA2 2p25GE Intel.
#. NIC-3: xl710-QDA2 2p40GE Intel.

2-Node ARM ThunderX2 (2n-tx2)
---------------------------

One 2n-tx2 testbed is built with: i) one SuperMicro SYS-7049GP-TRT
server acting as TG and equipped with two Intel Xeon Skylake Platinum
8180 processors (38.5 MB Cache, 2.50 GHz, 28 cores), and ii) one Marvell
ThnderX2 9975 (28* ThunderX2) server acting as SUT and equipped with two
ThunderX2 ARMv8 CN9975 processors. 2n-tx2 physical topology is shown below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/introduction/}}
                \includegraphics[width=0.90\textwidth]{testbed-2n-tx2}
                \label{fig:testbed-2n-tx2}
        \end{figure}

.. only:: html

    .. figure:: testbed-2n-tx2.svg
        :alt: testbed-2n-tx2
        :align: center

SUT server is populated with the following NIC models:

#. NIC-1: xl710-QDA2 2p40GE Intel (not connected).
#. NIC-2: xl710-QDA2 2p40GE Intel.

TG server run T-Rex application and is populated with the following
NIC models:

#. NIC-1: xl710-QDA2 2p40GE Intel.
