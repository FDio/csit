Integration Tests
=================

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
extendability and maintenance, under the guideline of VPP core team.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED",  "MAY", and "OPTIONAL" in this document are to be
interpreted as described in :rfc:`8174`.

Overview
--------

.. only:: latex

    .. raw:: latex

        \begin{figure}[H]
            \centering
                \graphicspath{{../_tmp/src/vpp_device_tests/}}
                \includegraphics[width=0.90\textwidth]{vpp_device}
                \label{fig:vpp_device}
        \end{figure}

.. only:: html

    .. figure:: vpp_device.svg
        :alt: vpp_device
        :align: center

Physical Testbeds
-----------------

All :abbr:`FD.io (Fast Data Input/Ouput)` :abbr:`CSIT (Continuous System
Integration and Testing)` vpp-device tests are executed on physical testbeds
built with bare-metal servers hosted by :abbr:`LF (Linux Foundation)` FD.io
project. Two 1-node testbed topologies are used:

- **2-Container Topology**: Consisting of one Docker container acting as SUT
  (System Under Test) and one Docker container as TG (Traffic Generator), both
  connected in ring topology via physical NIC cross-connecting.

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
                \graphicspath{{../_tmp/src/vpp_device_tests/}}
                \includegraphics[width=0.90\textwidth]{vf-2n-nic2nic}
                \label{fig:vf-2n-nic2nic}
        \end{figure}

.. only:: html

    .. figure:: vf-2n-nic2nic.svg
        :alt: vf-2n-nic2nic
        :align: center

Server is populated with the following NIC models:

#. NIC-1: x710-da4 4p10GE Intel.
#. NIC-2: x710-da4 4p10GE Intel.

All Intel Xeon Skylake servers run with Intel Hyper-Threading enabled,
doubling the number of logical cores exposed to Linux, with 56 logical
cores and 28 physical cores per processor socket.

NIC interfaces are shared using Linux vfio_pci and VPP VF drivers:

- DPDK VF driver,
- Fortville AVF driver.

Provided Intel x710-da4 4p10GE NICs support 32 VFs per interface, 128 per NIC.

Complete 1n-skx testbeds specification is available on `CSIT LF Testbeds
<https://wiki.fd.io/view/CSIT/Testbeds:_Xeon_Skx,_Arm,_Atom.>`_ wiki page.

Total of two 1n-skx testbeds are in operation in FD.io labs.

1-Node Virtualbox (1n-vbox)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1n-skx testbed can run in single VirtualBox VM machine. This solution replaces
the previously used Vagrant environment based on 3 VMs.

VirtualBox VM MAY be created by Vagrant and MUST have additional 4 virtio NICs
each pair attached to separate private networks to simulate back-to-back
connections. It SHOULD be 82545EM device model (otherwise can be changed in
boostrap scripts). Example of Vagrant configuration:

::

    Vagrant.configure(2) do |c|
      c.vm.network "private_network", type: "dhcp", auto_config: false,
          virtualbox__intnet: "port1", nic_type: "82545EM"
      c.vm.network "private_network", type: "dhcp", auto_config: false,
          virtualbox__intnet: "port2", nic_type: "82545EM"

      c.vm.provider :virtualbox do |v|
        v.customize ["modifyvm", :id, "--nicpromisc2", "allow-all"]
        v.customize ["modifyvm", :id, "--nicpromisc3", "allow-all"]
        v.customize ["modifyvm", :id, "--nicpromisc4", "allow-all"]
        v.customize ["modifyvm", :id, "--nicpromisc5", "allow-all"]

Vagrant VM is populated with the following NIC models:

#. NIC-1: 82545EM Intel.
#. NIC-2: 82545EM Intel.
#. NIC-3: 82545EM Intel.
#. NIC-4: 82545EM Intel.

Containers
----------

It was agreed on :abbr:`TWS (Technical Work Stream)` call to continue with
Ubuntu 18.04 LTS as a baseline system with OPTIONAL extend to Centos 7 and
SuSE per demand [TWSLink]_.

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
in align of long term solution for container lifecycle and ability to build
new version of docker images.

In parallel, the effort is started to find the outsourced Docker registry
service.

Versioning
~~~~~~~~~~

As of initial version of vpp-device, we do have only single latest version of
Docker image hosted on [dockerhub]_. This will be addressed as further
improvement with proper semantic versioning.

jenkins-slave-dcr
~~~~~~~~~~~~~~~~~

This :abbr:`DCR` acts as the Jenkins slave (known also as jenkins minion). It
can connect over SSH protocol to TCP port 6022 of **csit-shim-dcr** and executes
non-interactive reservation script. Nomad is responsible for scheduling this
container execution onto specific **1-Node VPP_Device** testbed. It executes
:abbr:`CSIT` environment including :abbr:`CSIT` framework.

All software dependencies including VPP/DPDK that are not present in
**csit-sut-dcr** container image and/or needs to be compiled prior running on
**csit-sut-dcr** SHOULD be compiled in this container.

- *Container Image Location*: Docker image at snergster/vpp-ubuntu18.

- *Container Definition*: Docker file specified at [JenkinsSlaveDcrFile]_.

- *Initializing*: Container is initialized from within *Consul by HashiCorp*
  and *Nomad by HashiCorp*.

csit-shim-dcr
~~~~~~~~~~~~~

This :abbr:`DCR` acts as an intermediate layer running script responsible for
orchestrating topologies under test and reservation. Responsible for managing VF
resources and allocation to :abbr:`DUT (Device Under Test)`, :abbr:`TG
(Traffic Generator)` containers. This MUST to be done on **csit-shim-dcr**.
This image also acts as the generic reservation mechanics arbiter to make sure
that only Y number of simulations are spawned on any given HW node.

- *Container Image Location*: Docker image at snergster/csit-shim.

- *Container Definition*: Docker file specified at [CsitShimDcrFile]_.

- *Initializing*: Container is initialized from within *Consul by HashiCorp*
  and *Nomad by HashiCorp*. Required docker parameters, to be able to run
  nested containers with VF reservation system are: privileged, net=host,
  pid=host.

- *Connectivity*: Over SSH only, using <host>:6022 format. Currently using
  *root* user account as primary. From the jenkins slave it will be able to
  connect via env variable, since the jenkins slave doesn't actually know what
  host its running on.

  ::

      ssh -p 6022 root@10.30.51.node

csit-sut-dcr
~~~~~~~~~~~~

This :abbr:`DCR` acts as an :abbr:`SUT (System Under Test)`. Any :abbr:`DUT` or
:abbr:`TG` application is installed there. It is RECOMMENDED to install DUT and
all DUT dependencies via commands ``rpm -ihv`` on RedHat based OS or ``dpkg -i``
on Debian based OS.

Container is designed to be a very lightweight Docker image that only installs
packages and execute binaries (previously built or downloaded on
**jenkins-slave-dcr**) and contains libraries necessary to run CSIT framework
including those required by DUT/TG.

- *Container Image Location*: Docker image at snergster/csit-sut.

- *Container Definition*: Docker file specified at [CsitSutDcrFile]_.

- *Initializing*:
  ::

    docker run
    # Run the container in the background and print the new container ID.
    --detach=true
    # Give extended privileges to this container. A "privileged" container is
    # given access to all devices and able to run nested containers.
    --privileged
    # Publish all exposed ports to random ports on the host interfaces.
    --publish-all
    # Automatically remove the container when it exits.
    --rm
    # Size of /dev/shm.
    dcr_stc_params+="--shm-size 512M "
    # Override access to PCI bus by attaching a filesystem mount to the
    # container.
    dcr_stc_params+="--mount type=tmpfs,destination=/sys/bus/pci/devices "
    # Mount vfio to be able to bind to see bound interfaces. We cannot use
    # --device=/dev/vfio as this does not see newly bound interfaces.
    dcr_stc_params+="--volume /dev/vfio:/dev/vfio "
    # Mount docker.sock to be able to use docker deamon of the host.
    dcr_stc_params+="--volume /var/run/docker.sock:/var/run/docker.sock "
    # Mount /opt/boot/ where VM kernel and initrd are located.
    dcr_stc_params+="--volume /opt/boot/:/opt/boot/ "
    # Mount host hugepages for VMs.
    dcr_stc_params+="--volume /dev/hugepages/:/dev/hugepages/ "

  Container name is catenated from **csit-** prefix and uuid generated uniquely
  for each container instance.

- *Connectivity*: Over SSH only, using <host>[:<port>] format. Currently using
  *root* user account as primary.
  ::

    ssh -p <port> root@10.30.51.<node>

Container required to run as ``--privileged`` due to ability to create nested
containers and have full read/write access to sysfs (for bind/unbind). Docker
automatically pick free network port (``--publish-all``) for ability to connect
over ssh. To be able to limit access to PCI bus, container is creating tmpfs
mount type in PCI bus tree. CSIT reservation script is dynamically linking only
PCI devices (NIC cards) that are reserved for particular container. This
way it is not colliding with other containers. To make vfio work, access to
``/dev/vfio`` must be granted.

.. todo: Change default user to testuser with non-privileged and install sudo.

Environment initialization
--------------------------

All 1-node servers are to be managed and provisioned via the [ansiblelink]_ set
of playbooks with *vpp-device* role. Full playbooks can be found under
[fdiocsitansible]_ directory. This way we are able to track all configuration
changes of physical servers in gerrit (in structured yaml format) as well as we
are able to extend *vpp-device* to additional servers with less effort or
re-stage servers in case of failure.

SR-IOV VF initialization is done via ``systemd`` service during host system boot
up. Service with name *csit-initialize-vfs.service* is created under systemd
system context (``/etc/systemd/system/``). By default service is calling
``/usr/local/bin/csit-initialize-vfs.sh`` with single parameter:

- **start**: Creates maximum number of :abbr:`virtual functions (VFs)` (detected
  from ``sriov_totalvfs``) for each whitelisted PCI device.
- **stop**: Removes all :abbr:`VFs` for all whitelisted PCI device.

Service is considered active even when all of its processes exited successfully.
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
  initialization (usefull for e.g. excluding management network interfaces).
- **pci_whitelist**: PCI addresses to be included for :abbr:`VFs`
  initialization.

VF reservation
--------------

During topology initialization phase of script, mutex is used to avoid multiple
instances of script to interact with each other during resources allocation.
Mutal exclusion ensure that no two distinct instances of script will get same
resource list.

Reservation function reads the list of all available virtual function network
devices in system:

::

    # Find the first ${device_count} number of available TG Linux network
    # VF device names. Only allowed VF PCI IDs are filtered.
    for netdev in ${tg_netdev[@]}
    do
        for netdev_path in $(grep -l "${pci_id}" \
                             /sys/class/net/${netdev}*/device/device \
                             2> /dev/null)
        do
            if [[ ${#TG_NETDEVS[@]} -lt ${device_count} ]]; then
                tg_netdev_name=$(dirname ${netdev_path})
                tg_netdev_name=$(dirname ${tg_netdev_name})
                TG_NETDEVS+=($(basename ${tg_netdev_name}))
            else
                break
            fi
        done
        if [[ ${#TG_NETDEVS[@]} -eq ${device_count} ]]; then
            break
        fi
    done

Where ``${pci_id}`` is ID of white-listed VF PCI ID. For more information please
see [pciids]_. This act as security constraint to prevent taking other unwanted
interfaces.
The output list of all VF network devices is split into two lists for TG and
SUT side of connection. First two items from each TG or SUT network devices
list are taken to expose directly to namespace of container. This can be done
via commands:

::

    $ ip link set ${netdev} netns ${DCR_CPIDS[tg]}
    $ ip link set ${netdev} netns ${DCR_CPIDS[dut1]}

In this stage also symbolic links to PCI devices under sysfs bus directory tree
are created in running containers. Once VF devices are assigned to container
namespace and PCI deivces are linked to running containers and mutex is exited.
Selected VF network device automatically dissapear from parent container
namespace, so another instance of script will not find device under that
namespace.

Once Docker container exits, network device is returned back into parent
namespace and can be reused.

Network traffic isolation - Intel i40evf
----------------------------------------

In a virtualized environment, on Intel(R) Server Adapters that support SR-IOV,
the virtual function (VF) may be subject to malicious behavior. Software-
generated layer two frames, like IEEE 802.3x (link flow control), IEEE 802.1Qbb
(priority based flow-control), and others of this type, are not expected and
can throttle traffic between the host and the virtual switch, reducing
performance. To resolve this issue, configure all SR-IOV enabled ports for
VLAN tagging. This configuration allows unexpected, and potentially malicious,
frames to be dropped. [inteli40e]_

To configure VLAN tagging for the ports on an SR-IOV enabled adapter,
use the following command. The VLAN configuration SHOULD be done
before the VF driver is loaded or the VM is booted. [inteli40e]_

::

    $ ip link set dev <PF netdev id> vf <id> vlan <vlan id>

For example, the following instructions will configure PF eth0 and
the first VF on VLAN 10.

::

    $ ip link set dev eth0 vf 0 vlan 10

VLAN Tag Packet Steering allows to send all packets with a specific VLAN tag to
a particular SR-IOV virtual function (VF). Further, this feature allows to
designate a particular VF as trusted, and allows that trusted VF to request
selective promiscuous mode on the Physical Function (PF). [inteli40e]_

To set a VF as trusted or untrusted, enter the following command in the
Hypervisor:

::

  $ ip link set dev eth0 vf 1 trust [on|off]

Once the VF is designated as trusted, use the following commands in the VM
to set the VF to promiscuous mode. [inteli40e]_

- For promiscuous all:
  ::

      $ ip link set eth2 promisc on

- For promiscuous Multicast:
  ::

      $ ip link set eth2 allmulti on

.. note::

    By default, the ethtool priv-flag vf-true-promisc-support is set to
    *off*, meaning that promiscuous mode for the VF will be limited. To set the
    promiscuous mode for the VF to true promiscuous and allow the VF to see
    all ingress traffic, use the following command.
    $ ethtool set-priv-flags p261p1 vf-true-promisc-support on
    The vf-true-promisc-support priv-flag does not enable promiscuous mode;
    rather, it designates which type of promiscuous mode (limited or true)
    you will get when you enable promiscuous mode using the ip link commands
    above. Note that this is a global setting that affects the entire device.
    However,the vf-true-promisc-support priv-flag is only exposed to the first
    PF of the device. The PF remains in limited promiscuous mode (unless it
    is in MFP mode) regardless of the vf-true-promisc-support setting.
    [inteli40e]_

Service described earlier *csit-initialize-vfs.service* is responsible for
assigning 802.1Q vlan tagging to each vitual function via physical function
from list of white-listed PCI addresses by following (simplified) code.

::

    SCRIPT_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
    source "${SCRIPT_DIR}/csit-initialize-vfs-data.sh"

    # Initilize whitelisted NICs with maximum number of VFs.
    pci_idx=0
    for pci_addr in ${PCI_WHITELIST[@]}; do
        if ! [[ ${PCI_BLACKLIST[*]} =~ "${pci_addr}" ]]; then
            pci_path="/sys/bus/pci/devices/${pci_addr}"
            # SR-IOV initialization
            case "${1:-start}" in
                "start" )
                    sriov_totalvfs=$(< "${pci_path}"/sriov_totalvfs)
                    ;;
                "stop" )
                    sriov_totalvfs=0
                    ;;
            esac
            echo ${sriov_totalvfs} > "${pci_path}"/sriov_numvfs
            # SR-IOV 802.1Q isolation
            case "${1:-start}" in
                "start" )
                    pf=$(basename "${pci_path}"/net/*)
                    for vf in $(seq "${sriov_totalvfs}"); do
                        # PCI address index in array (pairing siblings).
                        if [[ -n ${PF_INDICES[@]} ]]
                        then
                            vlan_pf_idx=${PF_INDICES[$pci_addr]}
                        else
                            vlan_pf_idx=$((pci_idx % (${#PCI_WHITELIST[@]}/2)))
                        fi
                        # 802.1Q base offset.
                        vlan_bs_off=1100
                        # 802.1Q PF PCI address offset.
                        vlan_pf_off=$(( vlan_pf_idx * 100 + vlan_bs_off ))
                        # 802.1Q VF PCI address offset.
                        vlan_vf_off=$(( vlan_pf_off + vf - 1 ))
                        # VLAN string.
                        vlan_str="vlan ${vlan_vf_off}"
                        # MAC string.
                        mac5="$(printf '%x' ${pci_idx})"
                        mac6="$(printf '%x' $(( vf - 1 )))"
                        mac_str="mac ba:dc:0f:fe:${mac5}:${mac6}"
                        # Set 802.1Q VLAN id and MAC address
                        ip link set ${pf} vf $(( vf - 1)) ${mac_str} ${vlan_str}
                        ip link set ${pf} vf $(( vf - 1)) trust on
                        ip link set ${pf} vf $(( vf - 1)) spoof off
                    done
                    pci_idx=$(( pci_idx + 1 ))
                    ;;
            esac
            rmmod i40evf
            modprobe i40evf
        fi
    done

Assignment starts at VLAN 1100 and incrementing by 1 for each VF and by 100 for
each white-listed PCI address up to the middle of the PCI list. Second half of
the lists is assumed to be directly (cable) paired siblings and assigned with
same 802.1Q VLANs as its siblings.

Open tasks
----------

Security
~~~~~~~~

.. note::

    Switch to non-privileged containers: As of now all three container
    flavors are using privileged containers to make it working. Explore options
    to switch containers to non-privileged with explicit rather implicit
    privileges.

.. note::

    Switch to testuser account intead of root.

Maintainability
~~~~~~~~~~~~~~~

.. note::

    Docker image distribution: Create jenkins jobs with full pipiline of
    CI/CD for CSIT Docker images.

Stability
~~~~~~~~~

.. note::

    Implement queueing mechanism: Currently there is no mechanics that
    would place starving jobs in queue in case of no resources available.

.. note::

    Replace reservation script with Docker network plugin written in
    GOLANG/SH/Python - platform independent.

Links
-----

.. [TWSLink] `TWS <https://wiki.fd.io/view/CSIT/TWS>`_
.. [dockerhub] `Docker hub <https://hub.docker.com/>`_
.. [fdiocsitgerrit] `FD.io/CSIT gerrit <https://gerrit.fd.io/r/CSIT>`_
.. [fdioregistry] `FD.io registy <registry.fdiopoc.net>`_
.. [JenkinsSlaveDcrFile] `jenkins-slave-dcr-file <https://github.com/snergfdio/multivppcache/blob/master/ubuntu18/Dockerfile>`_
.. [CsitShimDcrFile] `csit-shim-dcr-file <https://github.com/snergfdio/multivppcache/blob/master/csit-shim/Dockerfile>`_
.. [CsitSutDcrFile] `csit-sut-dcr-file <https://github.com/snergfdio/multivppcache/blob/master/csit-sut/Dockerfile>`_
.. [ansiblelink] `ansible <https://www.ansible.com/>`_
.. [fdiocsitansible] `Fd.io/CSIT ansible <https://git.fd.io/csit/tree/fdio.infra.ansible>`_
.. [inteli40e] `Intel i40e <https://downloadmirror.intel.com/26370/eng/readme.txt>`_
.. [pciids] `pci ids <http://pci-ids.ucw.cz/v2.2/pci.ids>`_
