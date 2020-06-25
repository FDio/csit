
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
  security policies including United States Department of Defense-style
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
   `GitHub <https://github.com/lxc/lxc/tree/master/templates>`_.

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
executing them in containers [docker]_. Currently it is using *runc*,
a CLI tool for spawning and running containers according to the
`OCI specification <https://www.opencontainers.org/>`_.

A Docker container image is a lightweight, stand-alone, executable
package that includes everything needed to run the container:
code, runtime, system tools, system libraries, settings.

CSIT uses Docker to manage the maintenance and execution of
containerized applications used in CSIT performance tests.

- Data plane thread pinning to CPU cores - Docker CLI and/or Docker
  configuration file controls the range of CPU cores the Docker image
  must run on. VPP thread pinning defined vpp startup.conf.

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
                                          +------+------+      +------+------+
                                          |     LXC     |      |    Docker   |
                                          +-------------+      +-------------+
                                          | (inherited) |      | (inherited) |
                                          +------+------+      +------+------+
                                                 |                    |
                                                 +----------+---------+
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

There is no parameters check functionality. Passing the correct arguments
is a responsibility of the caller.

Examples
~~~~~~~~

This section contains a high-level example of multiple initialization steps
via ContainerManager; taken from an actual CSIT code,
but with non-code lines (comments, Documentation) removed for brevity.

:

.. code-block:: robotframework

  | Start containers for test
  | | [Arguments] | ${dut}=${None} | ${nf_chains}=${1} | ${nf_nodes}=${1}
  | | ... | ${auto_scale}=${True} | ${pinning}=${True}
  | |
  | | Set Test Variable | @{container_groups} | @{EMPTY}
  | | Set Test Variable | ${container_group} | CNF
  | | Set Test Variable | ${nf_nodes}
  | | Import Library | resources.libraries.python.ContainerUtils.ContainerManager
  | | ... | engine=${container_engine} | WITH NAME | ${container_group}
  | | Construct chains of containers
  | | ... | dut=${dut} | nf_chains=${nf_chains} | nf_nodes=${nf_nodes}
  | | ... | auto_scale=${auto_scale} | pinning=${pinning}
  | | Acquire all '${container_group}' containers
  | | Create all '${container_group}' containers
  | | Configure VPP in all '${container_group}' containers
  | | Start VPP in all '${container_group}' containers
  | | Append To List | ${container_groups} | ${container_group}
  | | Save VPP PIDs

Kubernetes
~~~~~~~~~~

For the future use, Kubernetes [k8sdoc]_ is implemented as separate library
``KubernetesUtils.py``, with a class with the same name. This utility provides
an API for L2 Robot Keywords to control ``kubectl`` installed on each of DUTs.
One time initialization script, ``resources/libraries/bash/k8s_setup.sh``
does reset/init kubectl, and initializes the ``csit`` namespace. CSIT
namespace is required to not to interfere with existing setups and it
further simplifies apply/get/delete Pod/ConfigMap operations on SUTs.

Kubernetes utility is based on YAML templates to avoid crafting the huge
YAML configuration files, what would lower the readability of code and
requires complicated algorithms.

Two types of YAML templates are defined:

- Static - do not change between deployments, that is infrastructure
  containers like Kafka, Calico, ETCD.

- Dynamic - per test suite/case topology YAML files.

Making own python wrapper library of ``kubectl`` instead of using the
official Python package allows to control and deploy environment over
the SSH library without the need of using isolated driver running on
each of DUTs.

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
