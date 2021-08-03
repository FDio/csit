.. _nic_drivers_methodology:

Physical NICs in CSIT
---------------------

CSIT performance tests are executed on a number of physical testbeds
described in :ref:`tested_physical_topologies` and equipped with the
following NICs:

- x553 ..., codename Niantic.
- x710-DA4 4p10GE Intel, codename Fortville (FVL).
- xxv710-DA2 2p25GE Intel, codename Fortville (FVL)
- cx556a-edat ConnectX5 2p100GE Mellanox.
- E810-2CQDA2 2p100GbE Intel, codename Columbiaville (CVL)

Each NIC is tested with native VPP drivers and DPDK drivers.

Intel Niantic
~~~~~~~~~~~~~~~

- DPDK 21.05

Intel Fortville
~~~~~~~~~~~~~~~

- AVF
- DPDK 21.05
- AF_XDP

Intel Columbiaville
~~~~~~~~~~~~~~~

- AVF
- DPDK 21.05
- AF_XDP

Mellanox ConnectX5
~~~~~~~~~~~~~~~~~~

- RDMA_CORE