VPP_Device Integration Tests
============================

Abstract
--------

FD.io VPP software data plane technology has become very popular across
a wide range of VPP eco-system use cases, putting higher pressure on
continuous verification of VPP software quality.

This document describes a proposal for design and implementation of extended
continuous VPP testing by extending existing test environments.
Furthermore it describes and summarizes implementation details of Integration
and System tests platform *1-Node VPP_Device*. It aims to provide a complete
end-to-end view of *1-Node VPP_Device* environment in order to improve
extendibility and maintenance, under the guideline of VPP core team.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED",  "MAY", and "OPTIONAL" in this document are to be
interpreted as described in :rfc:`8174`.

Overview
--------

.. todo: Covert to SVG

.. image:: vpp-device.png

Physical Testbeds
-----------------

All :abbr:`FD.io (Fast Data Input/Ouput)` :abbr:`CSIT (Continuous System
Integration and Testing)` vpp-device tests are executed on physical testbeds
built with bare-metal servers hosted by :abbr:`LF (Linux Foundation)` FD.io
project. Two 1-node testbed topologies are used:

- **3-Node Topology**: Consisting of two Docker containers acting as SUTs
  (Systems Under Test) and one Docker container as TG (Traffic Generator), all
  connected in ring topology via physical NIC crossconnecting.
- **2-Node Topology**: Consisting of one Docker container acting as SUT (System
  Under Test) and one Docker container as TG (Traffic Generator), both connected
  in ring topology via physical NIC crossconnecting.

Current FD.io production testbeds are built with servers based on one
processor generation of Intel Xeons: Skylake (Platinum 8180). Testbeds built
with servers based on Arm processors are in the process of being added to FD.io
production.

Following section describe existing production 1n-skx testbed.

1-Node Xeon Skylake (1n-skx)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1n-skx testbed is based on single SuperMicro SYS-7049GP-TRT server equipped with
two Intel Xeon Skylake Platinum 8180 2.5 GHz 28 core processors. Physical
testbed topology is depicted in a figure below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/introduction/}}
                \includegraphics[width=0.90\textwidth]{testbed-1n-skx}
                \label{fig:testbed-1n-skx}
        \end{figure}

.. only:: html

    .. figure:: testbed-1n-skx.svg
        :alt: testbed-1n-skx
        :align: center

Logical view is depicted in a figure below.

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/introduction/}}
                \includegraphics[width=0.90\textwidth]{logical-1n-skx}
                \label{fig:logical-1n-skx}
        \end{figure}

.. only:: html

    .. figure:: logical-1n-skx.svg
        :alt: logical-1n-skx
        :align: center

Server is populated with the following NIC models:

#. NIC-1: x710-DA4 4p10GE Intel.
#. NIC-2: x710-DA4 4p10GE Intel.
#. NIC-3: x710-DA4 4p10GE Intel.
#. NIC-4: x710-DA4 4p10GE Intel.
#. NIC-5: x710-DA4 4p10GE Intel.
#. NIC-6: x710-DA4 4p10GE Intel.

All Intel Xeon Skylake servers run with Intel Hyper-Threading enabled,
doubling the number of logical cores exposed to Linux, with 56 logical
cores and 28 physical cores per processor socket.

NIC interfaces are shared using Linux vfio_pci and VPP VF drivers:

- DPDK VF driver,
- Fortville AVF driver.

Provided Intel x710 4p10GE NICs suppport 32 VFs per interface, 128 per NIC.

Complete 1n-skx testbeds specification is available on
`CSIT LF Testbeds <https://wiki.fd.io/view/CSIT/Testbeds:_Xeon_Skx,_Arm,_Atom.>`_
wiki page.

Total of two 1n-skx testbeds are in operation in FD.io labs.

1-Node ARM (1n-arm)
~~~~~~~~~~~~~~~~~~~

.. todo: Add specification of 1n-arm

Containers
----------

It was agreed on :abbr:`TWS (Technical Work Stream)` call to continue with
Ubuntu 18.04 LTS as a baseline system with OPTIONAL extend to Centos 7 and
SuSE per demand [tws]_.

All :abbr:`DCR (Docker container)` images are REQUIRED to be hosted on Docker
registry available from LF network, publicly available and trackable. For
backup, tracking and contributing purposes all Dockerfiles (including files
needed for building container) MUST be available and stored in [fdiocsitgerrit]_
repository under appropriate folders. This allows the peer review process to be
done for every change of infrastructure related to scope of this document.
Currently only **csit-shim-dcr** and **csit-sut-dcr** containers will be stored
and maintained under CSIT repository by CSIT contributors.

At the time of designing solution described in this document the interconnection
between [dockerhub]_ and  [fdiocsitgerrit]_ for automated build purposes and
image hosting cannot be established with the trust and respectful to
security of FD.io project. Unless adressed, :abbr:`DCR` images will be placed in
custom registry service [fdioregistry]_. Automated Jenkins jobs will be created
in align of long term solution for container lifecycle.

In parallel, the effort is started to find the outsourced service.

Versioning
~~~~~~~~~~

.. todo: Find the proper versioning scheme (achieved by tagging containers on registry service).
.. todo:  > Proposal 1: Use git/job versioning similar to vpp?

.. todo:  > Proposal 2: Use semantic versioning?
.. todo:  > Proposal 2: [EJK], [PM]
.. todo:  > Proposal 2: - Cons: manual (unless we find some super plugin). Need to create verify/merge jobs.

.. todo:  > Proposal 3: Git TAGs, currently not in use in CSIT? (compatibility with fd.io gerrit)

jenkins-slave-dcr
~~~~~~~~~~~~~~~~~

This :abbr:`DCR` acts as the jenkins slave (known also as
jenkins minion) it can connect over SSH protocol to known port to
**csit-shim-dcr** and execute non-interactive scripts. This image acts as the
generic reservation mechanic to make sure that only Y number are spawned on any
given HW node. Responsible for scheduling test job execution onto specific
**1-Node VPP_Device** testbed.

All software dependencies including VPP/DPDK that are not present in package
lists of standard linux distributions and/or needs to be compiled prior running
on **csit-sut-dcr** SHOULD be compiled in this container.

- *Container Image Location*: Docker image at [jenkins-slave-dcr-img]_

- *Container Definition*: Docker file specified at [jenkins-slave-dcr-file]_

csit-shim-dcr
~~~~~~~~~~~~~

This :abbr:`DCR` acts as an intermediate layer running scripts responsible for
orchestrating topologies under test and executing :abbr:`CSIT` environment
including :abbr:`CSIT` framework by instantiating **csit-sut-dcr**. Responsible
for managing VF resources and allocation to :abbr:`DUT (Device Under Test)` and
:abbr:`TG (Traffic Generator)` containers. This MUST to be done on
**csit-shim-dcr**, not on nomad instance running locally.

Container MAY do compilation of dependencies in future as an addition to
**jenkins-slave-dcr**. List of installed libraries does allow to compile
dependencies here.

- *Container Image Location*: Docker image at [csit-shim-dcr-img]_

- *Container Definition*: Docker file specified at [csit-shim-dcr-file]_

- *Initializing*:
  .. todo: Describe initialization of csit-shim-dcr.

- *Connectivity*: Over SSH only, using <host>:6022 format. Currently using
  *root* user account as primary. From the jenkins slave it will be able to
  connect via env variable, since the jenkins slave doesn't actually know what
  host its running on.
  ::
    ssh -p 6022 root@10.30.51.node

csit-sut-dcr
~~~~~~~~~~~~

This :abbr:`DCR` acts as an :abbr:`SUT (System Under Test)`. Any :abbr:`DUT` or
:abbr:`TG` application is installed there. It is RECOMMENDED to install them
with packaging system (APT/DPKG on Debian based system or DNF/YUM on RedHat
based systems).

It is designed to be very lightweight Docker image that only installs packages
and execute binaries (built on **jenkins-slave-dcr**) and contains libraries
necessary to run CSIT framework.

- *Container Image Location*: Docker image at [csit-sut-dcr-img]_

- *Container Definition*: Docker file specified at [csit-sut-dcr-file]_

- *Initializing*:
  ::
    docker run --privileged --shm-size 512M -d -p 10.30.51.node:port:22/tcp hub/image

- *Connectivity*: Over SSH only, using <host>[:<port>] format. Currently using
  *root* user account as primary.
  ::
    ssh -p <port> root@10.30.51.<node>

VF reservation
--------------

.. todo: Discuss VF reservation mechanics.
.. todo:  > Proposal 1: PM: Kicking off net_devs (enpNNsXfY) into destination container.
.. todo:  > Proposal 1:     Currently POC is being tested on .51 host (no need to use Pipework). Mutex works.
.. todo:  > Proposal 1:     Right now it does assume csit-shim-dcr is having access to all VF net_devs.
.. todo:  > Proposal 1:     Small modification can be detection if net_dev is PF or VF.
.. todo:  > Proposal 1:     + No DB, mutex guaranteed, pure bash.
.. todo:  > Proposal 1:     - net_devs must be in csit_shim.

.. todo:  > Proposal 2: PM: Doing directly on @PCI. PCI address to be parameter to csit-sut-dcr. I need to verify if isolation works.
.. todo:  > Proposal 2:     - More code, isolation between containers?
.. todo:  > Proposal 2:     + no need to kick off net_dev to csit-shim-dcr

Environment initialization
--------------------------

All DUT servers are to be managed and provisioned via the [ansible]_ set of
playbooks with *vpp-device* role. Full playbook can be found under
[fdiocsitansible]_ directory.

SR-IOV VF initialization is done via systemd service during host system boot up.
Service with name *csit-initialize-vfs.service* is created under system context
(/etc/systemd/system/). By default service is calling *csit-initialize-vfs.sh*
with single parameter:

- **start**: Creates maximum number of :abbr:`virtual functions (VFs)` (detected
  from ``sriov_totalvfs``) under each PCI address.
- **stop**: Removes all :abbr:`VFs` under PCI Physical function.

With ``Type=one-shot`` it is designed to run once to initialize :abbr:`VFs`.
Stopping service will automatically remove :abbr:`VFs`.

::
    [Unit]
    Description=CSIT Initialize SR-IOV VFs
    After=network.target

    [Service]
    Type=one-shot
    RemainAfterExit=True
    ExecStart=/usr/local/bin/csit-initialize-vfs.sh start
    ExecStop=/usr/local/bin/csit-initialize-vfs.sh stop

    [Install]
    WantedBy=default.target

Script is driven by two array variables ``pci_blacklist``/``pci_whitelist``.
They MUST store all PCI addresses in **<domain>:<bus>:<device>.<func>** format,
where:

- **pci_blacklist**: PCI addresses to be skipped from :abbr:`VFs`
  initialization (usefeull for e.g. management interfaces).
- **pci_whitelist**: PCI addresses to be included for :abbr:`VFs`
  initialization.

.. todo: Discuss Environment initialization
.. todo:  > PM: I created simple script for starting csit-sut-dcr.

Q&A
---

.. todo: Issues spotted: s1-t11-sut1 Machine no NICs detected by system.
.. todo: Issues spotted: > LF ticket [FD.io Helpdesk #60368]

.. todo: Issues spotted: s2-t12-sut1 Freezing/crashing/rebooting.
.. todo: Issues spotted: > Seems to be related to running jenkins slaves with
.. todo: Issues spotted: > vpp compilation on machine where physical NICs are
.. todo: Issues spotted: > present.

Links
-----

.. todo: Update the links below in case of change.

.. _tws: https://wiki.fd.io/view/CSIT/TWS
.. _dockerhub: https://hub.docker.com/
.. _fdiocsitgerrit: https://gerrit.fd.io/r/CSIT
.. _fdioregistry: registry.fdiopoc.net
.. _jenkins-slave-dcr-img: snergster/vpp-ubuntu18
.. _jenkins-slave-dcr-file: https://hub.docker.com/r/snergster/vpp-ubuntu18/~/dockerfile/
.. _csit-shim-dcr-img: registry.fdiopoc.net/vpp/ubuntu18ssh
.. _csit-shim-dcr-file: https://github.com/Snergster/vppcache/blob/master/ubuntu18-ssh/Dockerfile
.. _csit-sut-dcr-file: https://hub.docker.com/r/pmikus/csit-vpp-device-test/~/dockerfile/
.. _csit-sut-dcr-img: pmikus/csit-vpp-device-test
.. _ansible: https://www.ansible.com/
.. _fdiocsitansible: https://git.fd.io/csit/tree/resources/tools/testbed-setup/ansible
