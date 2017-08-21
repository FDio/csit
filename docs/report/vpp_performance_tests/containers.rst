CSIT Linux Container Lifecycle integration
==========================================

Overview
--------

**Container**

A container image is a lightweight, stand-alone, executable package of a piece
of software that includes everything needed to run it: code, runtime, system
tools, system libraries, settings. Containers isolate software from its
surroundings.

More info can be found [1]_

**Unprivileged containers**

Unprivileged containers are safe by design. The container uid 0 is mapped to an
unprivileged user outside of the container and only has extra rights on
resources that it owns itself.
With such container, the use of SELinux, AppArmor, Seccomp and capabilities
isn't necessary for security. :abbr:`LXC (Linux Containers)` will still use
those to add an extra layer of security which may be handy in the event of a
kernel security issue but the security model isn't enforced by them.

**Privileged containers**

Privileged containers are defined as any container where the container uid 0 is
mapped to the host's uid 0. In such containers, protection of the host and
prevention of escape is entirely done through Mandatory Access Control
(apparmor, selinux), seccomp filters, dropping of capabilities and namespaces.

CSIT is using **Privileged Container** due to the requirements of shared memory
access by VPP process running in container.

Container Lifecycle
~~~~~~~~~~~~~~~~~~~

Lifecycle of containerized application: build, (re-)create, execute, distribute

1. Acquire
2. Build
3. (Re-)Deploy/(Re-)Create
4. Execute
5. Distribute

Container orchestration
~~~~~~~~~~~~~~~~~~~~~~~

- **LXC**

  - Well-known and heavily tested low-level Linux container runtime [2]_, [3]_
  - Set of tools and libraries
  - LXC is a userspace interface for the Linux kernel containment features.
    Through a powerful API and simple tools, it lets Linux users easily create
    and manage system or application containers.
  - Current LXC uses the following kernel features to contain processes:

    - Kernel namespaces (ipc, uts, mount, pid, network and user)
    - Apparmor and SELinux profiles
    - Seccomp policies
    - Chroots (using pivot_root)
    - Kernel capabilities
    - CGroups (control groups)

  - **Questions**

    - Is there a better way to pin data plane lxc threads to cpu cores?

  - **Issues**

    - current limitation in CSIT: only single instance of lxc runtime
    - lxc pinning to cpu cores that are part of isolcpus is an issue as CFS does
      prevent to schedule LXC's containers on isolated cores. Need to be solved
      with correct mapping of cgroups to lxc instances

- **Docker**

  - Leading software container platform [4]_. Docker technology is not a
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
  - Wrapping the processes and maintaining them, it is responsible for executing
    them
  - Relies on kernel container libraries

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
 | configure_vpp_in_all_containers() |        | install_supervisors()    |
 | stop_all_containers()             |        | install_vpp()            |
 | destroy_all_containers()          |        | restart_vpp()            |
 +-----------------------------------+        | create_vpp_exec_config() |
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
                                          |             |     |              |
                                          +------+------+     +------+-------+
                                                 |                   |
                                                 +---------+---------+
                                                           |
                                                           | constructs
                                                           |
                                                     +-----v-----+
                                                     | Container |
                                                     +-----------+
                                                     |           |
                                                     +-----------+

Sequentional diagram that illustrate the creation of a single container.

::

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
    |-| 3: construct_container(**)   |                          |
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
``construct_container(**kwargs)`` and are passed from RF keyword.

.. code-block:: robotframework

    | Construct VNF containers on all DUTs
    | | [Arguments] | ${technology} | ${image} | ${cpu_count}=${1} | ${count}=${1}
    | | ...
    | | ${group}= | Set Variable | VNF
    | | @{env}= | Create List | LC_ALL="en_US.UTF-8"
    | | ... | DEBIAN_FRONTEND=noninteractive | ETCDV3_ENDPOINTS=172.17.0.1:2379
    | | ${guest_dir}= | Set Variable | /mnt/host
    | | ${host_dir}= | Set Variable | /tmp
    | | ${skip_cpus}= | Evaluate | ${vpp_cpus}+${system_cpus}
    | | Import Library | resources.libraries.python.ContainerUtils.ContainerManager
    | | ... | engine=${technology} | WITH NAME | ${group}
    | | ${duts}= | Get Matches | ${nodes} | DUT*
    | | :FOR | ${dut} | IN | @{duts}
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
coder responsibility. Mendatory parameters are ``node``, ``name``, ``image``
[5]_, ``cpu_count``, ``cpu_skip``, ``smt_used``, ``cpuset_mems``,
``cpu_shared``. All the cpu parameters are required to calculate the correct
cpu placement. See docuementation for the full reference.


Ligato
------

TBD

Notes
-----

.. note:
    Sample notes


References
----------

.. [1] `What is a Container <https://www.docker.com/what-container>`_
.. [2] `Linux Containers <https://linuxcontainers.org/>`_
.. [3] `Linux Containers source <https://github.com/lxc/lxc>`_
.. [4] `Docker <https://www.docker.com/what-docker>`_
.. [5] Image parameter is required in initial commit version. There is plan
    to implement container build class to build Docker/LXC image.
