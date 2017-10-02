CSIT Linux Container Lifecycle integration
==========================================

Overview
--------

**Linux Containers**

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

For more information see [1]_, [2]_ and [3]_.

**Unprivileged Linux Containers**

Running unprivileged containers is the safest way to run containers in a
production environment. From LXC 1.0 one can start a full system
container entirely as a user, allowing to map a range of UIDs on the
host into a namespace inside of which a user with UID 0 can exist again.
In other words an unprivileged container does mask the userid from the
host, making it impossible to gain a root access on the host even if a
user gets root in a container. With unprivileged containers, non-root
users can create containers and will have and appear in the container as
root, but will appear as userid <non-zero> on the host Unprivileged
containers are also better suited to supporting multi-tenancy operating
environments.

For more information see [4]_.

**Privileged Linux Containers**

Privileged containers do not mask UIDs, and container UID 0 is mapped to
the host UID 0. Security and isolation is controlled by a good
configuration of cgroup access, extensive AppArmor profile preventing
the known attacks as well as container capabilities and SELinux. Here a
summary list of applicable security control mechanisms:

- Capabilities - keep (whitelist) or drop (blacklist) Linux capabilities,
  as listed in [5]_;
- Control groups - resource bean counting, resource quotas, access
  restrictions, more detail in [6]_ and [7]_;
- AppArmor - apparmor profiles aim to prevent any of the known ways of
  escaping a container or cause harm to the host;
- SELinux - Security Enhanced Linux is a Linux kernel security module
  that provides similar function to AppArmor, supporting access control
  security policies including United States Department of Defense–style
  mandatory access controls. Mandatory access controls allow an
  administrator of a system to define how applications and users can
  access different resources such as files, devices, networks and
  inter-process communication. More detail in [8]_;
- Seccomp - secure computing mode, enables filtering of system calls.

For more information on Linux container security see [9]_.

**Linux Containers in CSIT**

CSIT is using **Privileged Container** due to the need to
deterministically allocate CPU core resources, shared memory and other
([mk] need to complete this list).

Container Lifecycle
~~~~~~~~~~~~~~~~~~~

Lifecycle of containerized application: build, (re-)create, execute, distribute

1. Acquire - [mk] add short description.
2. Build - [mk] add short description.
3. (Re-)Create/(Re-)Deploy - [mk] add short description.
4. Execute - [mk] add short description.
5. Distribute - currently not implemented in CSIT;

Container orchestration
~~~~~~~~~~~~~~~~~~~~~~~

- **LXC**

  - Well-known and heavily tested low-level Linux container runtime [10]_;
  - Set of tools and libraries
  - LXC is a userspace interface for the Linux kernel containment features.
    Through a powerful API and simple tools, it lets Linux users easily create
    and manage system or application containers.
  - Current LXC uses the following kernel features to contain processes:

    - Kernel namespaces (ipc, uts, mount, pid, network and user);
    - Apparmor [Apparmor] and SELinux [SElinux] profiles;
    - Seccomp policies; [mk] add references from https://linuxcontainers.org/
    - Chroots (using pivot_root);
    - Kernel capabilities; [mk] what capabilities - get them from https://linuxcontainers.org/
    - CGroups (control groups);

  - **Questions**

    - Currently in CSIT using cgroup to pin data plane lxc thread to cpu cores;

      - Is there a better way to pin data plane lxc threads to cpu cores?

  - **Issues**

    - current limitation in CSIT: only single instance of lxc runtime
    - lxc pinning to cpu cores that are part of isolcpus is an issue as CFS does
      prevent to schedule LXC's containers on isolated cores. Need to be solved
      with correct mapping of cgroups to lxc instances

- **Docker**

  - Leading software container platform [11]_. Docker technology is not a
    replacement for LXC. "LXC" refers to capabilities of the Linux kernel
    (specifically namespaces and control groups) which allow sandboxing
    processes from one another, and controlling their resource allocations. On
    top of this low-level foundation of kernel features, Docker offers a
    high-level tool with several powerful functionalities. Docker uses a
    client-server architecture. The Docker client talks to the Docker daemon,
    which does the heavy lifting of building, running, and distributing your
    Docker containers. The Docker client and daemon can run on the same system,
    or you can connect a Docker client to a remote Docker daemon. The Docker
    client and daemon communicate using a REST API, over UNIX sockets or a
    network interface.

    A container image is a lightweight, stand-alone, executable package of a piece
of software that includes everything needed to run it: code, runtime, system
tools, system libraries, settings. Containers isolate software from its
surroundings.


  - Wrapping the processes and maintaining them, it is responsible for executing
    them
  - Relies on kernel container libraries: LXC libraries, cgroups, ...; ([mk] need to complete the list)

  - ETCD is packaged in docker image
  - Kafka is packaged in docker image

  - **Questions**

    - does docker rely on any lxc libraries and/or tools?
    - jjb for building csit-centric vpp docker images vs. ligato ones?

  - **Issues**

    - docker process threads pinning to cpu cores
      can define range of cpu cores the docker image must run on
      and then vpp thread pinning is driving by vpp startup.conf.
      This is controlled via CLI and/or docker configuration file.


- **Kubernetes**

  - Production-grade container orchestration.
  - It groups containers that make up an application into logical units for
    easy management and discovery.
  - Is doing scalability using pods.
  - Defininig the pods incl. resource allocation. Config is .yaml driven
  - Is managing the shared compute resources based on docker requirements
  - Relies on docker images
  - **Questions**

    - Contiv/Calico/...?

  - **Issues**

    - unable to pin k8s pods to cpu cores


- **Ligato**

  - cloud-native nfv orchestration

  - **Questions**

    - jjb for building vpp docker images (vpp docker images are bundled
      together)?

- **Fd.io VPP**

  - fast network data plane


Implementation
--------------

CSIT Container implementation is based on Builder desing pattern written in
python L1 libraries of CSIT hierarchical design. Builder design pattern
separates the construction of a complex object from its representation so that
the same construction process can create different representations (e.g.
LXC/Docker/...).
Robot framework keywords are responsible for high level control of
lifecycle of named container groups. We can have multiple named groups with
1..N containers representing different role/functionality (e.g. VNFs, vswitch,
Kafka, ETCD, ...). ContainerManager class acts as a Director and uses
ContainerEngine class that encapsulate container control.

Implementation illustrated with UML Class diagram:


1. Acquire
2. Build
3. (Re-)Create/(Re-)Deploy
4. Execute
5. Distribute

::

 +-----------------------------------------------------------------------+
 |              RF Keywords (high level lifecycle control)               |
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
                                          |             |     |              |   [mk] can't be empty, if inherinted, say it so, symbol or word.
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

[mk] what "RF KW" is meant below?

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

Container data structure
~~~~~~~~~~~~~~~~~~~~~~~~

Container is represented in Python L1 library as separate Class with instance
variables and no methods except overriden ``__getattr__``, ``__setattr__`` and
``__repr__``. Instance variables are assigned to container dynamically during
``construct_container(**kwargs)`` and are passed from RF keyword. Example:

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

There is no parameters check functionality. Passing required arguments is in
coder responsibility. Mandatory parameters are ``node``, ``name``, ``image``
[5]_, ``cpu_count``, ``cpu_skip``, ``smt_used``, ``cpuset_mems``,
``cpu_shared``. All the cpu parameters are required to calculate the correct
cpu placement. See documentation for the full reference.

Kubernetes
~~~~~~~~~~

Kubernetes is implemented as separate library ``KubernetesUtils.py``, with class
of the same name. This utility provides the API for L2 Robot Keywords to control
``kubectl`` installed on each of DUTs. One time initialization script,
``resources/libraries/bash/k8s_setup.sh`` does init/reset kubectl and applies
Calico v2.4.1 and initialize ``csit`` namespace. CSIT namespace is required to
not interfere with existing setups and also it does simplify apply/get/delete
Pod/ConfigMap/Service on DUTs.

Utility is based on YAML templates to avoid crafting of huge YAML configuration
files that would lower the readability of code and requires complicated
algorithms. This can be leveraged to future separate tasks. Templates can be
found in ``resources/templates/kubernetes``. There are two
types of YAML templates:

- static

    - Does not change between deployments (e.g: Kafka, Calico, ETCD)

- dynamic

    - Per test case topology YAML files. (e.g. SFC_controller, VNF, VSWITCH)

Making own python wrapper library of ``kubectl` instead of using the official
Python package allows us to control and deploy environment over the SSH library
without the need of using isolated driver running on each of DUTs.

Ligato
~~~~~~

Ligato integration does require to compile the ``vnf-agent`` tool. Compilation
of ``vnf-agent`` depends on specific VPP. In ``vnf-agent`` repository there are
well prepared scripts for building the Docker image. Building docker image is
possible via series of commands:

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
also takes a significant amount of time (~1-1,5h depending on internet bandwidth
and allocated cores). The optimal solution would be to build the image on
jenkins slave, transfer the Docker image to DUTs and execute separate suite of
tests.

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
.. [2] `Resource management: Linux kernel Namespaces and cgroups <https://www.cs.ucsb.edu/~rich/class/cs293b-cloud/papers/lxc-namespace.pdf>`_
.. [3] `LXC 1.0: Blog post series <https://stgraber.org/2013/12/20/lxc-1-0-blog-post-series/>`_
.. [4] `LXC 1.0: Unprivileged containers <https://stgraber.org/2014/01/17/lxc-1-0-unprivileged-containers/>`_
.. [5] `Linux manual - capabilities - overview of Linux capabilities http://man7.org/linux/man-pages/man7/capabilities.7.html`_
.. [6] `Linux kernel documentation: cgroups <https://www.kernel.org/doc/Documentation/cgroup-v1/cgroups.txt>`_
.. [7] `Linux kernel documentation: Control Group v2 <https://www.kernel.org/doc/Documentation/cgroup-v2.txt>`_
.. [8] `SELinux Project Wiki <http://selinuxproject.org/page/Main_Page>`_
.. [9] `LXC 1.0: Security features <https://stgraber.org/2014/01/01/lxc-1-0-security-features/>`_
.. [10] `Linux Containers source <https://github.com/lxc/lxc>`_
.. [11] `Docker <https://www.docker.com/what-docker>`_
.. [1] `What is a Container <https://www.docker.com/what-container>`_
.. [5] Image parameter is required in initial commit version. There is plan
    to implement container build class to build Docker/LXC image.
[Apparmor] https://wiki.ubuntu.com/AppArmor
[SElinux] https://selinuxproject.org/page/Main_Page

