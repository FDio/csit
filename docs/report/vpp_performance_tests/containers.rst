CSIT Linux Container Lifecycle Integration
==========================================

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

Linux Containers (LXC) combine kernel's cgroups and support for isolated
namespaces to provide an isolated environment for applications. Docker
does use LXC as one of its execution drivers, enabling image management
and providing deployment services.

More information in [1]_, [2]_ and [3]_.

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
environments.

More information in [4]_ and [5]_.

Privileged Containers
~~~~~~~~~~~~~~~~~~~~~

Privileged containers do not mask UIDs, and container UID 0 is mapped to
the host UID 0. Security and isolation is controlled by a good
configuration of cgroup access, extensive AppArmor profile preventing
the known attacks as well as container capabilities and SELinux. Here a
list of applicable security control mechanisms:

- Capabilities - keep (whitelist) or drop (blacklist) Linux capabilities,
  see [6]_.
- Control groups - resource bean counting, resource quotas, access
  restrictions, see [7]_, [8]_.
- AppArmor - apparmor profiles aim to prevent any of the known ways of
  escaping a container or cause harm to the host.
- SELinux - Security Enhanced Linux [9]_ is a Linux kernel security module
  that provides similar function to AppArmor, supporting access control
  security policies including United States Department of Defense–style
  mandatory access controls. Mandatory access controls allow an
  administrator of a system to define how applications and users can
  access different resources such as files, devices, networks and inter-
  process communication.
- Seccomp - secure computing mode, enables filtering of system calls.

More information in [4]_ and [10]_.

**Linux Containers in CSIT**

CSIT is using Privileged Containers due to the need to allocate CPU core
resources and memory within specific NUMA collocated with the NICs.

.. mk: complete this list of reasons why using privileged containers.

Orchestrating Container Lifecycle Events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Following Linux container lifecycle events need to be addressed by an
orchestration system:

1. Acquire - ..
.. mk add short description.
2. Build - ..
.. mk add short description.
3. (Re-)Create/(Re-)Deploy - ..
.. mk add short description.
4. Execute - ..
.. mk add short description.
5. Distribute - .. currently not implemented in CSIT.
.. mk add short description.

Container Orchestration Systems Used in CSIT
--------------------------------------------

Current CSIT testing framework integrates following Linux container
orchestration mechanisms:

- LXC for complete VPP container lifecycle control.
- Combination of Docker (container images), Kubernetes (container
  orchestration) and Ligato (container networking).

LXC
~~~

LXC is the well-known and heavily tested low-level Linux container
runtime [11]_, that provides a userspace interface for the Linux kernel
containment features. With a powerful API and simple tools, LXC enables
Linux users to easily create and manage system or application
containers. LXC uses following kernel features to contain processes:

- Kernel namespaces: ipc, uts, mount, pid, network and user.
- AppArmor [12]_ and SELinux [9]_ security profiles.
- Seccomp policies [13]_.
- Chroots using pivot_root.
- CGroups - control groups.

CSIT uses LXC runtime and LXC APIs to test VPP data plane performance in
a range of virtual networking topologies.

**Known Issues**

- Current CSIT restriction: only single instance of lxc runtime.
.. mk: add explanation about the limiting factor here.
- Data plane thread pinning to CPU cores - Linux CFS prevents scheduling
  LXC containers onto cores isolated with isolcpu. Currently addressed
  by using correct mapping of cgroups to lxc instances.

**Open Questions**

- CSIT code is  currently using cgroup to pin lxc data plane thread to
  cpu cores. Is there a better way to do it?

Docker
~~~~~~

Docker builds on top of LXC and Linux kernel containment features, and
offers a high-level tool for wrapping the processes, maintaining and
executing them in containers [14]_.

A Docker container image is a lightweight, stand-alone, executable
package of a piece of software that includes everything needed to run
it: code, runtime, system tools, system libraries, settings.

CSIT uses Docker to manage the maintenance and execution of
containerized applications used in CSIT performance tests.

**Known Issues**

- Data plane thread pinning to CPU cores - Docker CLI and/or Docker
  configuration file controls the range of CPU cores the Docker image
  must run on. VPP thread pinning defined vpp startup.conf.
- Need a separate LF Jenkins job for for building csit-centric vpp docker
  images vs. ligato ones.

**Open Questions**

- What specific LXC libraries and/or tools does Docker rely on?

Kubernetes
~~~~~~~~~~

Kubernetes [15]_, or K8s, is a production-grade container orchestration
platform for automating the deployment, scaling and operating
application containers. Kubernetes groups containers that make up an
application into logical units, pods, for easy management and discovery.
K8s pod definitions including compute resource allocation is provided in
.yaml files.

CSIT uses K8s and its infrastructure components like etcd to control all
phases of container based virtualized network topologies.

**Known Issues**

- Unable to pin k8s pods to cpu cores.

**Open Questions**

- Clarify the functions provided by Contiv and Calico in Ligato system?

Ligato
~~~~~~

Ligato [16]_ is an open-source project developing a set of cloud-native tools
for orchestrating container networking. Ligato integrates with FD.io VPP
using goVPP [17]_ and vpp-agent [18]_.

**Known Issues**

**Open Questions**

- Need a separate LF Jenkins job for for building csit-centric vpp docker
  images vs. ligato ones.

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
3. (Re-)Create/(Re-)Deploy
4. Execute
5. Distribute

::

 +-----------------------------------------------------------------------+
 |              RF Keywords (high level lifecycle control)               |
 +-----------------+-----------------------------------------------------+
 .. mk: what RF keywords are these?
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
                                              |                          |
                                              +------------^-------------+
                                                           |
                                                           |
                                                           |
                                                 +---------+---------+
                                                 |                   |
                                          +------+------+     +------+-------+
                                          |     LXC     |     |    Docker    |
                                          +-------------+     +--------------+
                                          |             |     |              |   .. mk: can't be empty, if inherinted, say it so, symbol or word.
                                          +------+------+     +------+-------+
                                                 |                   |
                                                 +---------+---------+
                                                           |
                                                           | constructs
                                                           |
                                                 +---------v---------+
                                                 |     Container     |
                                                 +-------------------+
                                                 | __repr__()        |
                                                 | __getattr__(a)    |  [mk] storing variables.
                                                 | __setattr__(a, v) |
                                                 +-------------------+

Sequentional diagram that illustrates the creation of a single container.

.. mk: what "RF KW" is meant below?
.. mk: the flow sequence should adhere to the lifecycle events listed earlier in this doc.

::

 +-------+                  +------------------+       +-----------------+
 | RF KW |                  | ContainerManager |       | ContainerEngine |
 +---+---+                  +--------+---------+       +--------+--------+
     |                               |                          |
     |  1: new ContainerManager(e)   |                          |     [mk] (e=event)
    +-+---------------------------->+-+                         |
    |-|                             |-| 2: new ContainerEngine  |
    |-|                             |-+----------------------->+-+
    |-|                             |-|                        |-|
    |-|                             +-+                        +-+
    |-|                              |                          |
    |-| 3: construct_container(..)   |                          |     [mk] (..=variable arguments)
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
    |-|                             |-|                        |-|  | 8: is_container_running()
    |-|                             |-|             True/False |-|<-+
    |-|                             |-|<-----------------------+-|
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
variables and no methods except overriden ``__getattr__``, ``__setattr__`` and
``__repr__``. Instance variables are assigned to container dynamically during the
``construct_container(**kwargs)`` operation and are passed down from the RF keyword.

Usage example:

.. code-block:: robotframework

  | Construct VNF containers on all DUTs
  | | [Arguments] | ${technology} | ${image} | ${cpu_count}=${1} | ${count}=${1}
  | | ...
  | | ${group}= | Set Variable | VNF
  | | ${guest_dir}= | Set Variable | /mnt/host
  | | ${host_dir}= | Set Variable | /tmp
  | | ${skip_cpus}= | Evaluate | ${vpp_cpus}+${system_cpus}
  | | Import Library | resources.libraries.python.ContainerUtils.ContainerManager
  | | ... | engine=${technology} | WITH NAME | ${group}
  | | ${duts}= | Get Matches | ${nodes} | DUT*
  | | :FOR | ${dut} | IN | @{duts}
  | | | {env}= | Create List | LC_ALL="en_US.UTF-8"
  | | | ... | DEBIAN_FRONTEND=noninteractive | ETCDV3_ENDPOINTS=172.17.0.1:2379
  | | | ${cpu_node}= | Get interfaces numa node | ${nodes['${dut}']}
  | | | ... | ${dut1_if1} | ${dut1_if2}
  | | | Run Keyword | ${group}.Construct containers
  | | | ... | name=${dut}_${group}
  | | | ... | node=${nodes['${dut}']}
  | | | ... | host_dir=${host_dir}
  | | | ... | guest_dir=${guest_dir}
  | | | ... | image=${image}
  | | | ... | cpu_count=${cpu_count}
  | | | ... | cpu_skip=${skip_cpus}
  | | | ... | smt_used=${False}
  | | | ... | cpuset_mems=${cpu_node}
  | | | ... | cpu_shared=${False}
  | | | ... | env=${env}

Mandatory keyword parameters are ``node``, ``name``, ``image`` [19]_,
``cpu_count``, ``cpu_skip``, ``smt_used``, ``cpuset_mems``,
``cpu_shared``. There is no parameters check functionality. Passing
required arguments is in coder responsibility. All the cpu parameters
are required to calculate the correct cpu placement. See documentation
for the full reference.

Kubernetes
~~~~~~~~~~

Kubernetes is implemented as separate library ``KubernetesUtils.py``,
with a class with the same name. This utility provides an API for L2
Robot Keywords to control ``kubectl`` installed on each of DUTs. One
time initialization script, ``resources/libraries/bash/k8s_setup.sh``
does init/reset kubectl, applies Calico v2.4.1 and initializes the
``csit`` namespace. CSIT namespace is required not to interfere with
existing setups and it further simplifies apply/get/delete
Pod/ConfigMap/Service operations on SUTs.

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

Making own python wrapper library of ``kubectl` instead of using the
official Python package allows to control and deploy environment over
the SSH library without the need of using isolated driver running on
each of DUTs.

Ligato
~~~~~~

Ligato integration does require to compile the ``vnf-agent`` tool.
Compilation of ``vnf-agent`` depends on specific VPP. In ``vnf-agent``
repository there are well prepared scripts for building the Docker
image. Building docker image is possible via series of commands:

::

  git clone https://github.com/ligato/vpp-agent
  cd vpp_agent/docker/dev_vpp_agent
  sudo docker build -t dev_vpp_agent --build-arg AGENT_COMMIT=<agent commit id> \
      --build-arg VPP_COMMIT=<vpp commit id> --no-cache .
  sudo ./shrink.sh
  cd ../prod_vpp_agent
  sudo ./build.sh
  sudo ./shrink.sh

CSIT requires Docker image to include the desired VPP version (per patch
testing, nightly testing, on demand testing).

The entire build process heavily depends on internet connectivity and
also takes a significant amount of time (~1-1,5h depending on internet
bandwidth and allocated cores). The optimal solution would be to build
the image on jenkins slave, transfer the Docker image to DUTs and
execute separate suite of tests.

.. mk: 1..1.5hrs to build an image - way too long!?

To solve the basic issue with existing VPP on DUTs, we will create separate
sets of Jenkins jobs, that will be doing following:

1. Clone latest CSIT and Ligato repositaries
2. Build ``dev_vpp_image`` Docker image
3. Shrink image using ``docker/dev_vpp_image/shrink.sh`` script
4. Build ``prod_vpp_image`` Docker image from ``dev_vpp_image``
5. Shrink image using ``docker/dev_vpp_image/shrink.sh`` script
6. Transfer ``prod_vpp_image`` image to DUTs
7. Execute subset of performance tests designed for Ligato testing (separation
   from existing ones).

Approximate size of vnf-agent docker images:

::

  REPOSITORY            TAG       IMAGE ID        CREATED        SIZE
  dev_vpp_agent         latest    442771972e4a    8 hours ago    3.57 GB
  dev_vpp_agent_shrink  latest    bd2e76980236    8 hours ago    1.68 GB
  prod_vpp_agent        latest    e33a5551b504    2 days ago     404 MB
  prod_vpp_agent_shrink latest    446b271cce26    2 days ago     257 MB


In CSIT we need to create separate performance suite under ``tests/ligato/perf``
that will contain modified Suite setup in comparison to standard perf tests.
This is due to reason that VPP will act as vswitch in Docker image and not
as standalone installed service.

Tested topologies
~~~~~~~~~~~~~~~~~

.. note:
    TBD

References
----------

.. [1] `Linux Containers <https://linuxcontainers.org/>`_
.. [2] `Resource management: Linux kernel Namespaces and cgroups <https://www.cs.ucsb.edu/~rich/class/cs293b-cloud/papers/lxc-namespace.pdf>`_.
.. [3] `LXC 1.0: Blog post series <https://stgraber.org/2013/12/20/lxc-1-0-blog-post-series/>`_.
.. [4] `Linux Containers Security <https://linuxcontainers.org/lxc/security/>`_.
.. [5] `LXC 1.0: Unprivileged containers <https://stgraber.org/2014/01/17/lxc-1-0-unprivileged-containers/>`_.
.. [6] `Linux manual - capabilities - overview of Linux capabilities http://man7.org/linux/man-pages/man7/capabilities.7.html`_.
.. [7] `Linux kernel documentation: cgroups <https://www.kernel.org/doc/Documentation/cgroup-v1/cgroups.txt>`_.
.. [8] `Linux kernel documentation: Control Group v2 <https://www.kernel.org/doc/Documentation/cgroup-v2.txt>`_.
.. [9] `SELinux Project Wiki <http://selinuxproject.org/page/Main_Page>`_.
.. [10] `LXC 1.0: Security features <https://stgraber.org/2014/01/01/lxc-1-0-security-features/>`_.
.. [11] `Linux Containers source <https://github.com/lxc/lxc>`_.
.. [12] `Ubuntu AppArmor <https://wiki.ubuntu.com/AppArmor>`_.
.. [13] `SECure COMPuting with filters <https://www.kernel.org/doc/Documentation/prctl/seccomp_filter.txt>`_.
.. [14] `Docker <https://www.docker.com/what-docker>`_.
.. [15] `Kubernetes documentation <https://kubernetes.io/docs/home/>`_.
.. [16] `Ligato <https://github.com/ligato>`_.
.. [17] `FD.io goVPP project <https://wiki.fd.io/view/GoVPP>`_.
.. [18] `Ligato vpp-agent <https://github.com/ligato/vpp-agent>`_.
.. [19] Image parameter is required in initial commit version. There is plan to implement container build class to build Docker/LXC image.