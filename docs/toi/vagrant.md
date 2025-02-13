# FD.io CSIT Development Environment

The intent of this document is to give you a quick start guide for setting up a CSIT development and testing environment inside a Vagrant VM.

## Pulling CSIT code

The first step is to pull the FD.io CSIT code. Eventhough the fastest way is to pull the code anonymously using https by typing the below command, the recommended way is to pull code via ssh if you intend to develop and commit changes upstream.
```
git clone https://gerrit.fd.io/r/csit
```
To pull the code via ssh, you'll first need to setup a Linux Foundation (LF) account as fd.io uses the Linux Foundations identity system. If you do not have an LF account, proceed to [Linux_Foundations_Identity_Setup](https://identity.linuxfoundation.org) to setup one. Once you have setup your Linux Foundation username and password, you can use if for all fd.io logins.

After you've setup your account, make sure you have registered your [ssh key with
gerrit](https://wiki.fd.io/view/DEV/Setting_up_Gerrit). Then pull the code by typing the below command. Replace USERNAME with your Linux Foundation username.

```
git clone ssh://USERNAME@gerrit.fd.io:29418/csit.git
```

## Standing up Linux VM

To setup your dev environment, you'll want to stand up a Linux VM. The CSIT repo provides a
Vagrantfile to help you quickly setup an Ubuntu Jammy VM. This file is located in the csit.infra.vagrant folder.

If you haven't already installed Vagrant, install it by following the instructions [here](https://developer.hashicorp.com/vagrant/docs/installation).

Vagrant works well with the VirtualBox provider. We have only tested Vagrant with the VirtualBox provider for setting up a CSIT dev/test environment. Install the VirtualBox hypervisor on your
host machine by following the instructions for [Installing VirtualBox](https://www.virtualbox.org/wiki/Downloads).

If you've more than one hypervisor in use on the host machine, you'll most likely encounter an error when bringing up the VM. You must ensure that other hyperviors such as Hyper-V or KVM are disabled.

### Ensure KVM and Hyper-V are disabled on the host

If you have a Linux machine, ensure KVM is disabled:
```
lsmod | grep kvm
```
If you see kvm or kvm_intel in the output, you'll need to use the blacklist command to add it to the deny list.
```
echo 'blacklist kvm-intel' | sudo tee -a /etc/modprobe.d/blacklist.conf
```

If you have a Windows machine, ensure Hyper-V is disabled in system settings.

 - Right click on the Windows button and select 'Apps and Features'.
 - Select Turn Windows Features on or off.
 - Unselect Hyper-V and click OK.

 Reboot your host machine for the changes to take effect.

### Starting the Vagrant VM

The CSIT Vagrantfile: csit/csit.infra.vagrant/Vagrantfile is used to start up the Ubuntu
jammy VM with 8GB of RAM and 4 VCPUs. Vagrant boots up the VM and provisions software in it
using ansible local. Ansible installation is not required on the host.

The inventory path for ansible provisioning on the vagrant VM is located at:
csit/fdio.infra.ansible/inventories/vagrant_inventory/hosts.

The ansible playbook used for the vagrant host is located at:
/home/vagrant/csit/fdio.infra.ansible/vagrant.yaml

If your host OS is Linux, you may have to increase the maximum map count to a high value to
ensure that the Linux Kernel allows the VirtualBox hypervisor to allocate the required memory
maps. You can do this by typing the below command:
```
sudo sysctl -w vm.max_map_count=262144
```

If you're using a proxy, you'll need to export your proxy settings to facilitate software provisioning within the Vagrant VM.
```
export VAGRANT_APT_HTTP_PROXY=http://{Your_Proxy_URL}:{Proxy_Port}
export VAGRANT_APT_HTTPS_PROXY=http://{Your_Proxy_URL}:{Proxy_Port}
export VAGRANT_HTTPS_PROXY=http://{Your_Proxy_URL}:{Proxy_Port}
export VAGRANT_HTTP_PROXY=http://{Your_Proxy_URL}:{Proxy_Port}
```

Ansible downloads stable VPP packages from Packagecloud. The VPP version used for testing
can be set by updating the file: csit/VPP_STABLE_VER_UBUNTU_JAMMY.

To bring up the Ubuntu jammy VM with virtualbox provider and provision software, type the command
```
vagrant up
```

If everything goes well, vagrant will boot up the VM, mount shared folders and provision all the required software for running CSIT tests. The csit repository on the host will be mounted at /home/vagrant/csit on the VM.

### Running Device Tests

After your VM is provisioned, start by running VPP device tests. To do this type the
following commands:
```
vagrant ssh   # login to the VM
cd /home/vagrant/csit/resources/libraries/bash/entry
./bootstrap_vpp_device.sh csit-vpp-device-master-ubuntu2004-1n-vbox
```

The script will pack and copy the test framework into the docker containers named csit-tg-* and csit-dut1-* via ssh. The copied tarball will be extracted in the docker container.
Once the nodes are ready, you'll see device tests being executed in the docker container and the test results.

### Your questions answered

1) Where are the tests located and how are they written?

    CSIT tests are written using an open source automation framework called the [Robot Framework](https://robotframework.org/). The tests are present in the /tests folder. Infact these tests are used as templates to generate new robot tests for testing various interface types. The new interface tests are generated at runtime and stored in the /generated/tests folder. For VM based testing of interfaces, you should see robot tests generated for 1GE interfaces in this folder.

2) I am getting a robot error, [ ERROR ] Suite 'Tests' contains no tests matching tag '2 node single link topo', not matching tags 'avf', 'vhost', 'flow', 'NIC "HW 4xxx"', 'NIC "HW C4xxx"', 'NIC Amazon-Nitro-100G', 'NIC Amazon-Nitro-200G', 'NIC Amazon-Nitro-50G', 'NIC Intel-DSA', 'NIC Intel-E810CQ', 'NIC Intel-E810XXV', 'NIC Intel-E822CQ', 'NIC Intel-X520-DA2', 'NIC Intel-X553', 'NIC Intel-X710', 'NIC Intel-XL710', 'NIC Intel-XXV710', 'NIC Mellanox-CX556A', 'NIC Mellanox-CX6DX', 'NIC Mellanox-CX7VEAT' or 'NIC azure-mlx-40g' and matching name 'devicetest' in suite 'tests.vpp.device'. How do I resolve this?

    This error means that the robot framework is missing the virtual interface specification in its configuration. To resolve this issue, update the file: resources/library/python/Constants.py by adding a mapping for the nic named virtual. For instance, create two mappings such as:
    ```
    "virtual": "1ge1p82540em"
    "virtual": ["vfio-pci"]
    ```
    Add the appropriate mapping into,
     -  NIC_CODE_TO_NAME
     -  NIC_CODE_TO_SHORT_NAME
     -  NIC_NAME_TO_DRIVER
     -  NIC_DRIVER_TO_PLUGINS
     -  NIC_DRIVER_TO_TAG
     -  NIC_DRIVER_TO_SUITE_PREFIX
     -  NIC_DRIVER_TO_VFS
     -  DPDK_NIC_NAME_TO_DRIVER

    After this, delete the /generated/tests folder. We are using job_spec files for test definition. See /resources/job_specs/vpp_device. If a job spec is missing for vbox, create a new job spec by just copying and pasting the existing vpp-1n-spr.md to vpp-1n-vbox.md. However, change the NIC to virtual!

    Next, in the file: resources/libraries/bash/function/common.sh add the below line to create a substitution for the virtual NIC,
    ```
    awk_nics_sub_cmd+='gsub("virtual","1ge1p82540em");'
    ```
    Also, keep the “virtual” in vpp-1n-vbox.md (column 4).
    Now re-run the tests and in robot command line (log) you should start seeing --test <name> --test <name> etc.

3) Where can I find test run logs?

    Test run logs are present in the /archives folder. You should find a file named log.hml in this folder.

4) I am seeing a Docker image not found error when running tests.
   How do I build the required docker images?

    You should have two docker images inside the VM named,
    - base-ubuntu2204:local
    - csit_sut-ubuntu2204:local.

    If these images are missing, you can create them by typing the below commands:
    ```
    cd /opt/csit-docker-images/base
    docker build -t base-ubuntu2204:local .

    cd /opt/csit-docker-images/csit-sut
    docker build -t csit_sut-ubuntu2204:local .
    ```

5) VPP is failing to start inside the docker container. How do I fix this?

    First start by looking at the log.html file. You should find the startup configuration used to start VPP. For instance, your startup.conf file could look like the below,
    ```
    {
        log /var/log/vpp/vpp.log
        cli-listen /run/vpp/cli.sock
        cli-no-pager
        gid vpp
        full-coredump
    }
    socksvr
    {
        socket-name /run/vpp/api.sock
    }
    memory
    {
        main-heap-size 2G
        main-heap-page-size 2M
        default-hugepage-size 2M
    }
    statseg
    {
        size 2G
        page-size 2M
        per-node-counters on
    }
    plugins
    {
        plugin default
        {
            disable
        }
        plugin dpdk_plugin.so
        {
            enable
        }
    }
    dpdk
    {
        dev 0000:00:10.0
        dev 0000:00:11.0
    }
    ip6
    {
        hash-buckets 2000000
        heap-size 4G
    }
    ```
    One common reason for VPP not starting up is not allocating enough hugepages for VPP inside the VM. Increase the number of hugepages to 2560 by typing the below command and try running the tests again.

    ```
    sudo sysctl -w vm.nr_hugepages=2650
    ```

6) How do I check if the robot test cases for virtual interfaces have been successfully generated?

    Check the /generated/tests folder for all the generated tests. If you're running VPP device tests, generated tests will be found in the sub-folder named vpp/device. If you've named your virtual interface  "1ge1p82540em", you will find robot test files with names 2n1l-1ge1p82540em-*

7) For debugging, how do I prevent the test environment from being torn down after a test run?

    You can disable the CSIT framework from cleaning up the test environment by setting the environment variable CSIT_NO_CLEANUP=1.

    To reset the environment back for regular test runs, reboot the VM by typing the command,

    ```
    vagrant reload
    ```

    This will terminate all docker containers and free up all pci interfaces grabbed by dpdk.

    ```
    cd /home/vagrant/csit/resources/libraries/bash/entry
    CSIT_NO_CLEANUP=1 ./bootstrap_vpp_device.sh csit-vpp-device-master-ubuntu2004-1n-vbox
    ```

8) How do I ssh into the docker container for further troubleshooting?

    First disable test environment cleanups by following the instructions above. This will leave the TG and DUT1 docker containers running. You can now ssh into the csit-dut1-* docker container for further troubleshooting, such as running VPP or robot tests by hand. To do so, find the port published by the DUT1 docker container by typing the below command and then ssh into the container as root. The default root password is Csit1234.
    ```
    docker ps  # list all running containers and get the csit-dut1-* container ID
    docker port ${DUT1_CONTAINER_ID}   # get the published docker container port
    ssh root@{HOST_IP_ADDRESS} -p {DOCKER_PORT}  # ssh into the container
    ```

9) What's the CSIT test topology used for VM tests and where's the topology file?

    CSIT generates a 2 node topology with a TG docker node connected to a DUT1 docker node.
    The topology file is located at topologies/available/vpp_device.yaml
    For instance, here's a sample topology file generated by CSIT -
    ```
    metadata:
    version: 0.1
    schema:
        - resources/topology_schemas/2_node_topology.sch.yaml
        - resources/topology_schemas/topology.sch.yaml
    tags: [dcr, 2-node]

    nodes:
    TG:
        type: "TG"
        host: "10.0.2.15"
        arch: "x86_64"
        port: 32768
        username: "root"
        interfaces:
            port0:
                mac_address: "08:00:27:0f:e0:4d"
                pci_address: "0000:00:08.0"
                link: "link0"
                model: virtual
                driver: "e1000"
                vlan: 0
            port1:
                mac_address: "08:00:27:61:f7:ad"
                pci_address: "0000:00:09.0"
                link: "link1"
                model: virtual
                driver: "e1000"
                vlan: 0

    DUT1:
        type: "DUT"
        host: "10.0.2.15"
        arch: "x86_64"
        port: 32769
        username: "root"
        interfaces:
            port0:
                mac_address: "08:00:27:38:5e:58"
                pci_address: "0000:00:10.0"
                link: "link0"
                model: virtual
                driver: "e1000"
                vlan: 0
            port1:
                mac_address: "08:00:27:e3:f5:42"
                pci_address: "0000:00:11.0"
                link: "link1"
                model: virtual
                driver: "e1000"
                vlan: 0
    ```

10) How do I run an ansible task after the VM is provisioned?

    You can run a specific ansible task after the VM has been provisioned using ansible tags.
    For instance, you can run the tasks that has been tagged docker_images, by typing the below ansible command,

    ```
    cd ~/csit/fdio.infra.ansible
    ansible-playbook vagrant.yaml --tags "docker_images" -i inventories/vagrant_inventory/hosts
    ```

11) Docker image build is failing due to a network error. Where do I set proxy settings for Docker?

    You can set proxy settings for Docker in the file ~/.docker/config.json. Update this file with your environment's proxy info -
    ```
    {
        "proxies":
        {
            "default":
            {
            "httpProxy": "http://{Proxy_IP_Address}:{Proxy_Port}",
            "httpsProxy": "http://{Proxy_IP_Address}:{Proxy_Port}",
            "noProxy": "localhost,127.0.0.1"
            }
        }
    }
    ```

12) Where should I set the proxy vars for Ansible?

    Set Ansible proxy variables in the file - fdio.infra.ansible/roles/common/defaults/main.yaml. Uncomment the proxy_env: section and fill the correct proxy values for your dev/test environment.
