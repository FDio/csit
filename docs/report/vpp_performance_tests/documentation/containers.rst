
.. _container_orchestration_in_csit:

Container Orchestration in CSIT
===============================

Overview
--------

Linux Containers
~~~~~~~~~~~~~~~~

Linux Containers is an OS-level virtualization method for running
multiple isolated Linux systems (containers) on a compute host using a
single Linux kernel. Containers rely on Linux kernel cgroups
functionality for controlling usage of shared system resources (i.e.
CPU, memory, block I/O, network) and for namespace isolation. The latter
enables complete isolation of applications' view of operating
environment, including process trees, networking, user IDs and mounted
file systems.

:abbr:`LXC (Linux Containers)` combine kernel's cgroups and support for isolated
namespaces to provide an isolated environment for applications. Docker
does use LXC as one of its execution drivers, enabling image management
and providing deployment services. More information in [lxc]_, [lxcnamespace]_
and [stgraber]_.

Linux containers can be of two kinds: privileged containers and
unprivileged containers.

Unprivileged Containers
~~~~~~~~~~~~~~~~~~~~~~~

Running unprivileged containers is the safest way to run containers in a
production environment. From LXC 1.0 one can start a full system
container entirely as a user, allowing to map a range of UIDs on the
host into a namespace inside of which a user with UID 0 can exist again.
In other words an unprivileged container does mask the userid from the
host, making it impossible to gain a root access on the host even if a
user gets root in a container. With unprivileged containers, non-root
users can create containers and will appear in the container as the
root, but will appear as userid <non-zero> on the host. Unprivileged
containers are also better suited to supporting multi-tenancy operating
environments. More information in [lxcsecurity]_ and [stgraber]_.

Privileged Containers
~~~~~~~~~~~~~~~~~~~~~

Privileged containers do not mask UIDs, and container UID 0 is mapped to
the host UID 0. Security and isolation is controlled by a good
configuration of cgroup access, extensive AppArmor profile preventing
the known attacks as well as container capabilities and SELinux. Here a
list of applicable security control mechanisms:

- Capabilities - keep (whitelist) or drop (blacklist) Linux capabilities,
  [capabilities]_.
- Control groups - cgroups, resource bean counting, resource quotas, access
  restrictions, [cgroup1]_, [cgroup2]_.
- AppArmor - apparmor profiles aim to prevent any of the known ways of
  escaping a container or cause harm to the host, [apparmor]_.
- SELinux - Security Enhanced Linux is a Linux kernel security module
  that provides similar function to AppArmor, supporting access control
  security policies including United States Department of Defense–style
  mandatory access controls. Mandatory access controls allow an
  administrator of a system to define how applications and users can
  access different resources such as files, devices, networks and inter-
  process communication, [selinux]_.
- Seccomp - secure computing mode, enables filtering of system calls,
  [seccomp]_.

More information in [lxcsecurity]_ and [lxcsecfeatures]_.

**Linux Containers in CSIT**

CSIT is using Privileged Containers as the ``sysfs`` is mounted with RW
access. Sysfs is required to be mounted as RW due to VPP accessing
:command:`/sys/bus/pci/drivers/uio_pci_generic/unbind`. This is not the case of
unprivileged containers where ``sysfs`` is mounted as read-only.


Orchestrating Container Lifecycle Events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Following Linux container lifecycle events need to be addressed by an
orchestration system:

1. Acquire - acquiring/downloading existing container images via
   :command:`docker pull` or :command:`lxc-create -t download`.

2. Build - building a container image from scratch or another
   container image via :command:`docker build <dockerfile/composefile>` or
   customizing LXC templates in
   `GitHub: https://github.com/lxc/lxc/tree/master/templates`_.

3. (Re-)Create - creating a running instance of a container application
   from anew, or re-creating one that failed. A.k.a. (re-)deploy via
   :command:`docker run` or :command:`lxc-start`

4. Execute - execute system operations within the container by attaching to
   running container. THis is done by :command:`lxc-attach` or
   :command:`docker exec`

5. Distribute - distributing pre-built container images to the compute
   nodes. Currently not implemented in CSIT.


Container Orchestration Systems Used in CSIT
--------------------------------------------

Current CSIT testing framework integrates following Linux container
orchestration mechanisms:

- LXC/Docker for complete VPP container lifecycle control.
- Combination of Kubernetes (container orchestration), Docker (container
  images) and Ligato (container networking).

LXC
~~~

LXC is the well-known and heavily tested low-level Linux container
runtime [lxcsource]_, that provides a userspace interface for the Linux kernel
containment features. With a powerful API and simple tools, LXC enables
Linux users to easily create and manage system or application
containers. LXC uses following kernel features to contain processes:

- Kernel namespaces: ipc, uts, mount, pid, network and user.
- AppArmor and SELinux security profiles.
- Seccomp policies.
- Chroot.
- Cgroups.

CSIT uses LXC runtime and LXC usertools to test VPP data plane performance in
a range of virtual networking topologies.

**Known Issues**

- Current CSIT restriction: only single instance of lxc runtime due to
  the cgroup policies used in CSIT. There is plan to add the capability into
  code to create cgroups per container instance to address this issue. This sort
  of functionality is better supported in LXC 2.1 but can be done is current
  version as well.

- CSIT code is currently using cgroup to control the range of CPU cores the
  LXC container runs on. VPP thread pinning is defined vpp startup.conf.

Docker
~~~~~~

Docker builds on top of Linux kernel containment features, and
offers a high-level tool for wrapping the processes, maintaining and
executing them in containers [docker]_. Currently it using *runc* a CLI tool for
spawning and running containers according to the `OCI specification
<https://www.opencontainers.org/>`_

A Docker container image is a lightweight, stand-alone, executable
package of a piece of software that includes everything needed to run
it: code, runtime, system tools, system libraries, settings.

CSIT uses Docker to manage the maintenance and execution of
containerized applications used in CSIT performance tests.

- Data plane thread pinning to CPU cores - Docker CLI and/or Docker
  configuration file controls the range of CPU cores the Docker image
  must run on. VPP thread pinning defined vpp startup.conf.

Kubernetes
~~~~~~~~~~

Kubernetes [k8sdoc]_, or K8s, is a production-grade container orchestration
platform for automating the deployment, scaling and operating
application containers. Kubernetes groups containers that make up an
application into logical units, pods, for easy management and discovery.
K8s pod definitions including compute resource allocation is provided in
.yaml files.

CSIT uses K8s and its infrastructure components like etcd to control all
phases of container based virtualized network topologies.

Ligato
~~~~~~

Ligato [ligato]_ is an open-source project developing a set of cloud-native
tools for orchestrating container networking. Ligato integrates with FD.io VPP
using goVPP [govpp]_ and vpp-agent [vppagent]_.

**Known Issues**

- Currently using a separate LF Jenkins job for building csit-centric
  prod_vpp_agent docker images vs. dockerhub/ligato ones.

Implementation
--------------

CSIT container orchestration is implemented in CSIT Level-1 keyword
Python libraries following the Builder design pattern. Builder design
pattern separates the construction of a complex object from its
representation, so that the same construction process can create
different representations e.g. LXC, Docker, other.

CSIT Robot Framework keywords are then responsible for higher level
lifecycle control of of the named container groups. One can have
multiple named groups, with 1..N containers in a group performing
different role/functionality e.g. NFs, Switch, Kafka bus, ETCD
datastore, etc. ContainerManager class acts as a Director and uses
ContainerEngine class that encapsulate container control.

Current CSIT implementation is illustrated using UML Class diagram:

1. Acquire
2. Build
3. (Re-)Create
4. Execute

::

 +-----------------------------------------------------------------------+
 |              RF Keywords (high level lifecycle control)               |
 +-----------------------------------------------------------------------+
 | Construct VNF containers on all DUTs                                  |
 | Acquire all '${group}' containers                                     |
 | Create all '${group}' containers                                      |
 | Install all '${group}' containers                                     |
 | Configure all '${group}' containers                                   |
 | Stop all '${group}' containers                                        |
 | Destroy all '${group}' containers                                     |
 +-----------------+-----------------------------------------------------+
                   |  1
                   |
                   |  1..N
 +-----------------v-----------------+        +--------------------------+
 |          ContainerManager         |        |  ContainerEngine         |
 +-----------------------------------+        +--------------------------+
 | __init()__                        |        | __init(node)__           |
 | construct_container()             |        | acquire(force)           |
 | construct_containers()            |        | create()                 |
 | acquire_all_containers()          |        | stop()                   |
 | create_all_containers()           | 1    1 | destroy()                |
 | execute_on_container()            <>-------| info()                   |
 | execute_on_all_containers()       |        | execute(command)         |
 | install_vpp_in_all_containers()   |        | system_info()            |
 | configure_vpp_in_all_containers() |        | install_supervisor()     |
 | stop_all_containers()             |        | install_vpp()            |
 | destroy_all_containers()          |        | restart_vpp()            |
 +-----------------------------------+        | create_vpp_exec_config() |
                                              | create_vpp_startup_config|
                                              | is_container_running()   |
                                              | is_container_present()   |
                                              | _configure_cgroup()      |
                                              +-------------^------------+
                                                            |
                                                            |
                                                            |
                                                 +----------+---------+
                                                 |                    |
                                          +------+-------+     +------+-------+
                                          |     LXC      |     |    Docker    |
                                          +--------------+     +--------------+
                                          | (inherinted) |     | (inherinted) |
                                          +------+-------+     +------+-------+
                                                  |                   |
                                                  +---------+---------+
                                                            |
                                                            | constructs
                                                            |
                                                  +---------v---------+
                                                  |     Container     |
                                                  +-------------------+
                                                  | __getattr__(a)    |
                                                  | __setattr__(a, v) |
                                                  +-------------------+

Sequentional diagram that illustrates the creation of a single container.

::

 Legend:
    e  = engine [Docker|LXC]
    .. = kwargs (variable number of keyword argument)

 +-------+                  +------------------+       +-----------------+
 | RF KW |                  | ContainerManager |       | ContainerEngine |
 +---+---+                  +--------+---------+       +--------+--------+
     |                               |                          |
     |  1: new ContainerManager(e)   |                          |
    +-+---------------------------->+-+                         |
    |-|                             |-| 2: new ContainerEngine  |
    |-|                             |-+----------------------->+-+
    |-|                             |-|                        |-|
    |-|                             +-+                        +-+
    |-|                              |                          |
    |-| 3: construct_container(..)   |                          |
    |-+---------------------------->+-+                         |
    |-|                             |-| 4: init()               |
    |-|                             |-+----------------------->+-+
    |-|                             |-|                        |-| 5: new  +-------------+
    |-|                             |-|                        |-+-------->| Container A |
    |-|                             |-|                        |-|         +-------------+
    |-|                             |-|<-----------------------+-|
    |-|                             +-+                        +-+
    |-|                              |                          |
    |-| 6: acquire_all_containers()  |                          |
    |-+---------------------------->+-+                         |
    |-|                             |-| 7: acquire()            |
    |-|                             |-+----------------------->+-+
    |-|                             |-|                        |-|
    |-|                             |-|                        |-+--+
    |-|                             |-|                        |-|  | 8: is_container_present()
    |-|                             |-|             True/False |-|<-+
    |-|                             |-|                        |-|
    |-|                             |-|                        |-|
 +---------------------------------------------------------------------------------------------+
 |  |-| ALT [isRunning & force]     |-|                        |-|--+                          |
 |  |-|                             |-|                        |-|  | 8a: destroy()            |
 |  |-|                             |-|                        |-<--+                          |
 +---------------------------------------------------------------------------------------------+
    |-|                             |-|                        |-|
    |-|                             +-+                        +-+
    |-|                              |                          |
    |-| 9: create_all_containers()   |                          |
    |-+---------------------------->+-+                         |
    |-|                             |-| 10: create()            |
    |-|                             |-+----------------------->+-+
    |-|                             |-|                        |-+--+
    |-|                             |-|                        |-|  | 11: wait('RUNNING')
    |-|                             |-|                        |-<--+
    |-|                             +-+                        +-+
    |-|                              |                          |
 +---------------------------------------------------------------------------------------------+
 |  |-| ALT                          |                          |                              |
 |  |-| (install_vpp, configure_vpp) |                          |                              |
 |  |-|                              |                          |                              |
 +---------------------------------------------------------------------------------------------+
    |-|                              |                          |
    |-| 12: destroy_all_containers() |                          |
    |-+---------------------------->+-+                         |
    |-|                             |-| 13: destroy()           |
    |-|                             |-+----------------------->+-+
    |-|                             |-|                        |-|
    |-|                             +-+                        +-+
    |-|                              |                          |
    +++                              |                          |
     |                               |                          |
     +                               +                          +

Container Data Structure
~~~~~~~~~~~~~~~~~~~~~~~~

Container is represented in Python L1 library as a separate Class with instance
variables and no methods except overriden ``__getattr__`` and ``__setattr__``.
Instance variables are assigned to container dynamically during the
``construct_container(**kwargs)`` call and are passed down from the RF keyword.

Usage example:

.. code-block:: robotframework

  | Construct VNF containers on all DUTs
  | | [Arguments] | ${technology} | ${image} | ${cpu_count}=${1} | ${count}=${1}
  | | ...
  | | ${group}= | Set Variable | VNF
  | | ${skip_cpus}= | Evaluate | ${vpp_cpus}+${system_cpus}
  | | Import Library | resources.libraries.python.ContainerUtils.ContainerManager
  | | ... | engine=${container_engine} | WITH NAME | ${group}
  | | ${duts}= | Get Matches | ${nodes} | DUT*
  | | :FOR | ${dut} | IN | @{duts}
  | | | ${env}= | Create List | DEBIAN_FRONTEND=noninteractive
  | | | ${mnt}= | Create List | /tmp:/mnt/host | /dev:/dev
  | | | ${cpu_node}= | Get interfaces numa node | ${nodes['${dut}']}
  | | | ... | ${dut1_if1} | ${dut1_if2}
  | | | Run Keyword | ${group}.Construct containers
  | | | ... | name=${dut}_${group} | node=${nodes['${dut}']} | mnt=${mnt}
  | | | ... | image=${container_image} | cpu_count=${container_cpus}
  | | | ... | cpu_skip=${skip_cpus} | cpuset_mems=${cpu_node}
  | | | ... | cpu_shared=${False} | env=${env} | count=${container_count}
  | | | ... | install_dkms=${container_install_dkms}
  | | Append To List | ${container_groups} | ${group}

Mandatory parameters to create standalone container are: ``node``, ``name``,
``image`` [imagevar]_, ``cpu_count``, ``cpu_skip``, ``cpuset_mems``,
``cpu_shared``.

There is no parameters check functionality. Passing required arguments is in
coder responsibility. All the above parameters are required to calculate the
correct cpu placement. See documentation for the full reference.

Kubernetes
~~~~~~~~~~

Kubernetes is implemented as separate library ``KubernetesUtils.py``,
with a class with the same name. This utility provides an API for L2
Robot Keywords to control ``kubectl`` installed on each of DUTs. One
time initialization script, ``resources/libraries/bash/k8s_setup.sh``
does reset/init kubectl, applies Calico v2.6.3 and initializes the
``csit`` namespace. CSIT namespace is required to not to interfere with
existing setups and it further simplifies apply/get/delete
Pod/ConfigMap operations on SUTs.

Kubernetes utility is based on YAML templates to avoid crafting the huge
YAML configuration files, what would lower the readability of code and
requires complicated algorithms. The templates can be found in
``resources/templates/kubernetes`` and can be leveraged in the future
for other separate tasks.

Two types of YAML templates are defined:

- Static - do not change between deployments, that is infrastructure
  containers like Kafka, Calico, ETCD.

- Dynamic - per test suite/case topology YAML files e.g. SFC_controller,
  VNF, VSWITCH.

Making own python wrapper library of ``kubectl`` instead of using the
official Python package allows to control and deploy environment over
the SSH library without the need of using isolated driver running on
each of DUTs.

Ligato
~~~~~~

Ligato integration does require to compile the ``vpp-agent`` tool and build the
bundled Docker image. Compilation of ``vpp-agent`` depends on specific VPP. In
``ligato/vpp-agent`` repository there are well prepared scripts for building the
Docker image. Building docker image is possible via series of commands:

::

  git clone https://github.com/ligato/vpp-agent
  cd vpp_agent/docker/dev_vpp_agent
  sudo docker build -t dev_vpp_agent --build-arg AGENT_COMMIT=<agent commit id>\
      --build-arg VPP_COMMIT=<vpp commit id> --no-cache .
  sudo ./shrink.sh
  cd ../prod_vpp_agent
  sudo ./build.sh
  sudo ./shrink.sh

CSIT requires Docker image to include the desired VPP version (per patch
testing, nightly testing, on demand testing).

The entire build process of building ``dev_vpp_agent`` image heavily depends
on internet connectivity and also takes a significant amount of time (~1-1.5h
based on internet bandwidth and allocated resources). The optimal solution would
be to build the image on jenkins slave, transfer the Docker image to DUTs and
execute separate suite of tests.

To adress the amount of time required to build ``dev_vpp_agent`` image, we can
pull existing specific version of ```dev_vpp_agent``` and exctract the
```vpp-agent``` from it.

We created separate sets of Jenkins jobs, that will be executing following:

1. Clone latest CSIT and Ligato repositaries.
2. Pull specific version of ``dev_vpp_agent`` image from Dockerhub.
3. Extract VPP API (from ``.deb`` package) and copy into ``dev_vpp_agent``
   image
4. Rebuild vpp-agent and extract outside image.
5. Build ``prod_vpp_image`` Docker image from ``dev_vpp_agent`` image.
6. Transfer ``prod_vpp_agent`` image to DUTs.
7. Execute subset of performance tests designed for Ligato testing.

::

 +-----------------------------------------------+
 |                  ubuntu:16.04                 <-----| Base image on Dockerhub
 +------------------------^----------------------+
                          |
                          |
 +------------------------+----------------------+
 |               ligato/dev_vpp_agent            <------| Pull this image from
 +------------------------^----------------------+      | Dockerhub ligato/dev_vpp_agent:<version>
                          |
                          | Rebuild and extract agent.tar.gz from dev_vpp_agent
 +------------------------+----------------------+
 |                 prod_vpp_agent                <------| Build by passing own
 +-----------------------------------------------+      | vpp.tar.gz (from nexus
                                                        | or built by JJB) and
                                                        | agent.tar.gz extracted
                                                        | from ligato/dev_vpp_agent


Approximate size of vnf-agent docker images:

::

  REPOSITORY            TAG       IMAGE ID        CREATED        SIZE
  dev-vpp-agent         latest    78c53bd57e2     6 weeks ago    9.79GB
  prod_vpp_agent        latest    f68af5afe601    5 weeks ago    443MB

In CSIT we need to create separate performance suite under
``tests/kubernetes/perf`` which contains modified Suite setup in comparison
to standard perf tests. This is due to reason that VPP will act as vswitch in
Docker image and not as standalone installed service.

Tested Topologies
~~~~~~~~~~~~~~~~~

Listed CSIT container networking test topologies are defined with DUT
containerized VPP switch forwarding packets between NF containers. Each
NF container runs their own instance of VPP in L2XC configuration.

Following container networking topologies are tested in |csit-release|:

- LXC topologies:

  - eth-l2xcbase-eth-2memif-1lxc.
  - eth-l2bdbasemaclrn-eth-2memif-1lxc.

- Docker topologies:

  - eth-l2xcbase-eth-2memif-1docker.
  - eth-l2xcbase-eth-1memif-1docker

- Kubernetes/Ligato topologies:

  - eth-1drcl2bdbasemaclrn-eth-2memif-1drcl2xc-1paral
  - eth-1drcl2bdbasemaclrn-eth-2memif-2drcl2xc-1horiz
  - eth-1drcl2bdbasemaclrn-eth-2memif-4drcl2xc-1horiz
  - eth-1drcl2bdbasemaclrn-eth-4memif-2drcl2xc-1chain
  - eth-1drcl2bdbasemaclrn-eth-8memif-4drcl2xc-1chain
  - eth-1drcl2xcbase-eth-2memif-1drcl2xc-1paral
  - eth-1drcl2xcbase-eth-2memif-2drcl2xc-1horiz
  - eth-1drcl2xcbase-eth-2memif-4drcl2xc-1horiz
  - eth-1drcl2xcbase-eth-4memif-2drcl2xc-1chain
  - eth-1drcl2xcbase-eth-8memif-4drcl2xc-1chain

References
~~~~~~~~~~

.. [lxc] `Linux Containers <https://linuxcontainers.org/>`_
.. [lxcnamespace] `Resource management: Linux kernel Namespaces and cgroups <https://www.cs.ucsb.edu/~rich/class/cs293b-cloud/papers/lxc-namespace.pdf>`_.
.. [stgraber] `LXC 1.0: Blog post series <https://stgraber.org/2013/12/20/lxc-1-0-blog-post-series/>`_.
.. [lxcsecurity] `Linux Containers Security <https://linuxcontainers.org/lxc/security/>`_.
.. [capabilities] `Linux manual - capabilities - overview of Linux capabilities <http://man7.org/linux/man-pages/man7/capabilities.7.html>`_.
.. [cgroup1] `Linux kernel documentation: cgroups <https://www.kernel.org/doc/Documentation/cgroup-v1/cgroups.txt>`_.
.. [cgroup2] `Linux kernel documentation: Control Group v2 <https://www.kernel.org/doc/Documentation/cgroup-v2.txt>`_.
.. [selinux] `SELinux Project Wiki <http://selinuxproject.org/page/Main_Page>`_.
.. [lxcsecfeatures] `LXC 1.0: Security features <https://stgraber.org/2014/01/01/lxc-1-0-security-features/>`_.
.. [lxcsource] `Linux Containers source <https://github.com/lxc/lxc>`_.
.. [apparmor] `Ubuntu AppArmor <https://wiki.ubuntu.com/AppArmor>`_.
.. [seccomp] `SECure COMPuting with filters <https://www.kernel.org/doc/Documentation/prctl/seccomp_filter.txt>`_.
.. [docker] `Docker <https://www.docker.com/what-docker>`_.
.. [k8sdoc] `Kubernetes documentation <https://kubernetes.io/docs/home/>`_.
.. [ligato] `Ligato <https://github.com/ligato>`_.
.. [govpp] `FD.io goVPP project <https://wiki.fd.io/view/GoVPP>`_.
.. [vppagent] `Ligato vpp-agent <https://github.com/ligato/vpp-agent>`_.
.. [imagevar] Image parameter is required in initial commit version. There is plan to implement container build class to build Docker/LXC image.
