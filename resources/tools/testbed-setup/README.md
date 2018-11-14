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

### Prepare the PXE bootstrap server when there is no http server AMD64

  - `sudo apt-get install isc-dhcp-server tftpd-hpa nginx-light ansible`
  - edit dhcpd.conf and place it to /etc/dhcp/
  - `sudo cp dhcpd.cfg /etc/dhcp/`
  - `sudo service isc-dhcp-server restart`
  - `cd ~testuser/host-setup`
  - `sudo mkdir /mnt/cdrom`
  - Ubuntu Bionic
    - `wget 'http://cdimage.ubuntu.com/ubuntu/releases/18.04/release/ubuntu-18.04-server-amd64.iso'`
    - `sudo mount -o loop ubuntu-18.04-server-amd64.iso /mnt/cdrom/`
  - `sudo cp -r /mnt/cdrom/install/netboot/* /var/lib/tftpboot/`
  - figure out where nginx will look for files on the filesystem when
    responding to HTTP requests. The configuration is in one of the
    files in /etc/nginx/conf.d/, /etc/nginx/sites-enabled/ or in
    /etc/nginx/nginx.conf under section server/root. Save the path to WWW_ROOT
  - `sudo mkdir -p ${WWW_ROOT}/download/ubuntu`
  - `sudo cp -r /mnt/cdrom/* ${WWW_ROOT}/download/ubuntu/`
  - `sudo cp /mnt/cdrom/ubuntu/isolinux/ldlinux.c32 /var/lib/tftpboot`
  - `sudo cp /mnt/cdrom/ubuntu/isolinux/libcom32.c32 /var/lib/tftpboot`
  - `sudo cp /mnt/cdrom/ubuntu/isolinux/libutil.c32 /var/lib/tftpboot`
  - `sudo cp /mnt/cdrom/ubuntu/isolinux/chain.c32 /var/lib/tftpboot`
  - `sudo umount /mnt/cdrom`
  - edit ks.cfg and replace IP address with that of your PXE bootstrap server and subdir in /var/www (in this case /download)
  - `sudo cp ks.cfg ${WWW_ROOT}/download/ks.cfg`
  - edit boot-screens_txt.cfg and replace IP address with that of your PXE bootstrap server and subdir in /var/www (in this case /download)
  - `sudo cp boot-screens_txt.cfg /var/lib/tftpboot/ubuntu-installer/amd64/boot-screens/txt.cfg`
  - `sudo cp syslinux.cfg /var/lib/tftpboot/ubuntu-installer/amd64/boot-screens/syslinux.cfg`

### New testbed host - manual preparation

- set CIMC address
- set CIMC username, password and hostname
- set IPMI address
- set IPMI username, password and hostname

### Bootstrap the host

Convenient way to re-stage host via script:

  `sudo ./bootstrap_setup_testbed.sh <linux_ip> <mgmt_ip> <username> <pass>`

Optional: CIMC - From PXE boostrap server

  - Initialize args.ip: Power-Off, reset BIOS defaults, Enable console redir, get LOM MAC addr
  - `./cimc.py -u admin -p Cisco1234 $CIMC_ADDRESS -d -i`
  - Adjust BIOS settings
  - `./cimc.py -u admin -p Cisco1234 $CIMC_ADDRESS -d -s '<biosVfIntelHyperThreadingTech rn="Intel-HyperThreading-Tech" vpIntelHyperThreadingTech="disabled" />' -s '<biosVfEnhancedIntelSpeedStepTech rn="Enhanced-Intel-SpeedStep-Tech" vpEnhancedIntelSpeedStepTech="disabled" />' -s '<biosVfIntelTurboBoostTech rn="Intel-Turbo-Boost-Tech" vpIntelTurboBoostTech="disabled" />'`
  - Add MAC address to DHCP (/etc/dhcp/dhcpd.conf)
  - If RAID is not created in CIMC. Create RAID array. Reboot.
      - `./cimc.py -u admin -p Cisco1234 $CIMC_ADDRESS -d --wipe`
      - `./cimc.py -u admin -p Cisco1234 $CIMC_ADDRESS -d -r -rl 1 -rs <disk size> -rd '[1,2]'`
        Alternatively, create the RAID array manually.
  - Reboot server with boot from PXE (restart immediately)
  - `./cimc.py -u admin -p Cisco1234 $CIMC_ADDRESS -d -pxe`
  - Set the next boot from HDD (without restart) Execute while Ubuntu install is running.
  - `./cimc.py -u admin -p Cisco1234 $CIMC_ADDRESS -d -hdd`

Optional: IPMI - From PXE boostrap server

    - Get MAC address of LAN0
    - `ipmitool -U ADMIN -H $HOST_ADDRESS raw 0x30 0x21 | tail -c 18`
    - Add MAC address to DHCP (/etc/dhcp/dhcpd.conf)
    - Reboot into PXE for next boot only
    - `ipmitool -I lanplus -H $HOST_ADDRESS -U ADMIN chassis bootdev pxe`
    - `ipmitool -I lanplus -H $HOST_ADDRESS -U ADMIN power reset`
    - For live watching SOL (Serial-over-LAN console)
    - `ipmitool -I lanplus -H $HOST_ADDRESS -U ADMIN sol activate`
    - `ipmitool -I lanplus -H $HOST_ADDRESS -U ADMIN sol deactivate`

When installation is finished:

  - Copy ssh keys for no pass access: `ssh-copy-id 10.30.51.x`
  - Clone CSIT actual repo: `git clone https://gerrit.fd.io/r/csit`
  - Go to ansible directory: `cd csit/resources/tools/testbed-setup/ansible`
  - Edit production file and uncomment servers that are supposed to be
    installed.
  - Run ansible on selected hosts:
    `ansible-playbook --vault-id vault_pass --extra-vars '@vault.yml' --inventory production site.yaml`

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

The VIRL host should now be operational. Test, and when ready, create a
~jenkins-in/status file with the appropriate status.
