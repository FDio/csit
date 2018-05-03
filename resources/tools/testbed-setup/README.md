# Testbed Setup

## Introduction

This directoctory contains the *high-level* process to set up a hardware
machine as a CSIT testbed, either for use as a physical testbed host or
as a VIRL server.

Code in this directory is NOT executed as part of a regular CSIT test case
but is stored here merely for archiving and documentation purposes.


## Setting up a hardware host

Documentation below is just bullet points and assumes and understanding
of PXE boot and ansible.

This process is specific for LF lab, and both examples given here as
well as associated code, are based on the assumption that they are run
in LF environment. If run elsewhere, changes will be required to IP addresses
and other parameters.

The process below assumes that there is a host used for boostrapping (referred
to as "PXE boostrap server" below), and that the directory containig this README
is available on the PXE bootstrap server in ~testuser/host-setup.

### Prepare the PXE bootstrap server when there is no http server

  - `sudo apt-get install isc-dhcp-server tftpd-hpa nginx-light ansible`
  - edit dhcpd.conf and place it to /etc/dhcp/
  - `sudo cp dhcpd.cfg /etc/dhcp/`
  - `sudo service isc-dhcp-server restart`
  - `cd ~testuser/host-setup`
  - `wget 'http://releases.ubuntu.com/16.04.2/ubuntu-16.04.2-server-amd64.iso'`
  - `sudo mkdir /mnt/cdrom`
  - `sudo mount -o loop ubuntu-16.04.2-server-amd64.iso /mnt/cdrom/`
  - `sudo cp -r /mnt/cdrom/install/netboot/* /var/lib/tftpboot/`
  - figure out the server root of nginx, this is the filesystem path where nginx will look for files when responding to http requests
  - `grep -r root /etc/nginx/`, save that to NGINX_ROOT
  - `sudo mkdir -p ${NGINX_ROOT}/download/ubuntu`
  - `sudo cp -r /mnt/cdrom/* ${NGINX_ROOT}/download/ubuntu/`
  - `sudo cp /mnt/cdrom/ubuntu/isolinux/ldlinux.c32 /var/lib/tftpboot`
  - `sudo cp /mnt/cdrom/ubuntu/isolinux/libcom32.c32 /var/lib/tftpboot`
  - `sudo cp /mnt/cdrom/ubuntu/isolinux/libutil.c32 /var/lib/tftpboot`
  - `sudo cp /mnt/cdrom/ubuntu/isolinux/chain.c32 /var/lib/tftpboot`
  - `sudo umount /mnt/cdrom`
  - edit ks.cfg and replace IP address with that of your PXE bootstrap server
  - `sudo cp ks.cfg ${NGINX_ROOT}/download/ks.cfg`
  - edit boot-screens_txt.cfg and replace IP address with that of your PXE bootstrap server
  - `sudo cp boot-screens_txt.cfg /var/lib/tftpboot/ubuntu-installer/amd64/boot-screens/txt.cfg`
  - `sudo cp syslinux.cfg /var/lib/tftpboot/ubuntu-installer/amd64/boot-screens/syslinux.cfg`

### PREFERED: Prepare the PXE bootstrap server when an http server is already configured

  - `sudo apt-get install isc-dhcp-server tftpd-hpa ansible`
  - edit dhcpd.conf and place it to /etc/dhcp/
  - `sudo cp dhcpd.cfg /etc/dhcp/`
  - `sudo service isc-dhcp-server restart`
  - `cd ~testuser/host-setup`
  - `wget 'http://releases.ubuntu.com/16.04.2/ubuntu-16.04.2-server-amd64.iso'`
  - `sudo mkdir /mnt/cdrom`
  - `sudo mount -o loop ubuntu-16.04.1-server-amd64.iso /mnt/cdrom/`
  - `sudo cp -r /mnt/cdrom/install/netboot/* /var/lib/tftpboot/`
  - `sudo mkdir /var/www/download/ubuntu`
  - `sudo cp -r /mnt/cdrom/* /var/www/download/ubuntu/`
  - `sudo cp /mnt/cdrom/ubuntu/isolinux/ldlinux.c32 /var/lib/tftpboot`
  - `sudo cp /mnt/cdrom/ubuntu/isolinux/libcom32.c32 /var/lib/tftpboot`
  - `sudo cp /mnt/cdrom/ubuntu/isolinux/libutil.c32 /var/lib/tftpboot`
  - `sudo cp /mnt/cdrom/ubuntu/isolinux/chain.c32 /var/lib/tftpboot`
  - `sudo umount /mnt/cdrom`
  - edit ks.cfg and replace IP address with that of your PXE bootstrap server and subdir in /var/www (in this case /download)
  - `sudo cp ks.cfg /var/www/download/ks.cfg`
  - edit boot-screens_txt.cfg and replace IP address with that of your PXE bootstrap server and subdir in /var/www (in this case /download)
  - `sudo cp boot-screens_txt.cfg /var/lib/tftpboot/ubuntu-installer/amd64/boot-screens/txt.cfg`
  - `sudo cp syslinux.cfg /var/lib/tftpboot/ubuntu-installer/amd64/boot-screens/syslinux.cfg`

### New testbed host - manual preparation

- set CIMC address
- set CIMC username, password and hostname

### Bootstrap the host

From PXE boostrap server:

  - `cd ~testuser/host-setup/cimc`
  - Initialize args.ip: Power-Off, reset BIOS defaults, Enable console redir, get LOM MAC addr
  - `./cimc.py -u admin -p Cisco1234 $CIMC_ADDRESS -d -i`
  - Adjust BIOS settings
  - `./cimc.py -u admin -p Cisco1234 $CIMC_ADDRESS -d -s '<biosVfIntelHyperThreadingTech rn="Intel-HyperThreading-Tech" vpIntelHyperThreadingTech="disabled" />' -s '<biosVfEnhancedIntelSpeedStepTech rn="Enhanced-Intel-SpeedStep-Tech" vpEnhancedIntelSpeedStepTech="disabled" />' -s '<biosVfIntelTurboBoostTech rn="Intel-Turbo-Boost-Tech" vpIntelTurboBoostTech="disabled" />'`
  - add MAC address to DHCP (/etc/dhcp/dhcpd.conf)
  - Reboot server with boot from PXE (restart immediately)
  - `./cimc.py -u admin -p Cisco1234 $CIMC_ADDRESS -d -pxe`

While Ubuntu install is running:

  - create RAID array. Reboot if needed.
      - `./cimc.py -u admin -p Cisco1234 $CIMC_ADDRESS -d --wipe`
      - `./cimc.py -u admin -p Cisco1234 $CIMC_ADDRESS -d -r -rl 1 -rs <disk size> -rd '[1,2]'`
        Alternatively, create the RAID array manually.

  - Set the next boot from HDD (without restart)
  - `./cimc.py -u admin -p Cisco1234 $CIMC_ADDRESS -d -hdd`

When installation is finished:

  - `ssh-copy-id 10.30.51.x`
  - `cd ~testuser/host-setup/playbooks`
  - edit /etc/ansible/hosts; add the hosts you are installing. *REMOVE ANY HOSTS YOU ARE NOT CURRENTLY INSTALLING*.

    Example for physical testbed hosts:
    ~~~
    [tg]
    10.30.51.24 hostname=t3-tg1 isolcpus="1-17,19-35" ansible_python_interpreter=/usr/bin/python2.7

    [sut]
    10.30.51.25 hostname=t3-sut1 isolcpus="1-17,19-35" ansible_python_interpreter=/usr/bin/python2.7
    10.30.51.26 hostname=t3-sut2 isolcpus="1-17,19-35" ansible_python_interpreter=/usr/bin/python2.7
    ~~~

    Example for VIRL hosts -- use the "virl" tag and specify the flat network start and end addresses:

    ~~~
    [virl]
    10.30.51.28 hostname=t4-virl1 virl_l2_start=10.30.52.2 virl_l2_end=10.30.52.253 virl_l2_network=10.30.52.0/24 virl_l2_ip=10.30.52.254 virl_public_port=eth0
    ~~~

  - `ansible-playbook --ask-sudo-pass 01-host-setup.yaml`
  - `ansible-playbook reboot.yaml`

For non-VIRL hosts, stop here.


### VIRL installation

After the host has rebooted:

  - `ansible-playbook 02-virl-bootstrap.yaml`
  - ssh to host
      - `sudo -s`
      - `cd virl-bootstrap`
      - `./virl-bootstrap-wrapper`

        This command will error out when run the first time, as the VIRL host is not yet licensed.

        Make sure we contact all three VIRL SALT masters:

      - `for a in 1 2 4 ; do sudo salt-call --master us-${a}.virl.info test.ping ; done`

      - Contact the VIRL team, provide the hostname and domain (linuxfoundation.org), and ask them
        to accept the key

      - After the key has been accepted, verify that connectivity with the SALT master is now OK:

        `for a in 1 2 4 ; do sudo salt-call --master us-${a}.virl.info test.ping ; done`

      - `./virl-bootstrap-wrapper`
      - `reboot`

After reboot, ssh to host again
  - as VIRL user, NOT AS ROOT:
     - `vinstall all`
     - `sudo reboot`

After reboot, ssh to host again
  - as VIRL user:
      - `sudo salt-call state.sls virl.routervms.all`
      - `sudo salt-call state.sls virl.vmm.vmmall`

Back on the PXE bootstrap server:

  - obtain the current server disk image and place it into
    `files/virl-server-image/` as `server.qcow2`

    TO-DO: Need to find a place to store this image

  - `ansible-playbook 03-virl-post-install.yaml`

  - Run the following command ONLY ONCE. Otherwise it will create
    duplicates of the VIRL disk image:

    `ansible-playbook 04-disk-image.yaml`

The VIRL host should now be operational. Test, and when ready, create a ~jenkins-in/status file with the appropriate status.
