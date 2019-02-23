Testbed Setup
=============

Introduction
------------

This directory contains the *high-level* process to set up a hardware machine
as a CSIT testbed, either for use as a physical performance testbed host or as
a vpp_device host.

Code in this directory is NOT executed as part of a regular CSIT test case
but is stored here for ad-hoc installation of HW, archiving and documentation
purposes.

Setting up a hardware host
--------------------------

Documentation below is step by step tutorial and assumes an understanding of PXE
boot and Ansible and managing physical hardware via CIMC or IPMI.

This process is not specific for LF lab, but associated files and code, is based
on the assumption that it runs in LF environment. If run elsewhere, changes
will be required in following files:

#. Inventory directory: `ansible/inventories/sample_inventory/`
#. Inventory files: `ansible/inventories/sample_inventory/hosts`
#. Kickseed file: `pxe/ks.cfg`
#. DHCPD file: `pxe/dhcpd.conf`
#. Bootscreen file: `boot-screens_txt.cfg`

The process below assumes that there is a host used for bootstrapping (referred
to as "PXE bootstrap server" below).

Prepare the PXE bootstrap server when there is no http server AMD64
```````````````````````````````````````````````````````````````````

#. Clone the csit repo:

   .. code-block:: bash

      git clone https://gerrit.fd.io/r/csit
      cd csit/resources/tools/testbed-setup/pxe

#. Setup prerequisities (isc-dhcp-server tftpd-hpa nginx-light ansible):

   .. code-block:: bash

      sudo apt-get install isc-dhcp-server tftpd-hpa nginx-light ansible

#. Edit dhcpd.cfg:

   .. code-block:: bash

      sudo cp dhcpd.cfg /etc/dhcp/
      sudo service isc-dhcp-server restart
      sudo mkdir /mnt/cdrom

#. Download Ubuntu 18.04 LTS - X86_64:

   .. code-block:: bash

      wget http://cdimage.ubuntu.com/ubuntu/releases/18.04/release/ubuntu-18.04-server-amd64.iso
      sudo mount -o loop ubuntu-18.04-server-amd64.iso /mnt/cdrom/
      sudo cp -r /mnt/cdrom/install/netboot/* /var/lib/tftpboot/

      # Figure out root folder for NGINX webserver. The configuration is in one
      # of the files in /etc/nginx/conf.d/, /etc/nginx/sites-enabled/ or in
      # /etc/nginx/nginx.conf under section server/root. Save the path to
      # variable WWW_ROOT.
      sudo mkdir -p ${WWW_ROOT}/download/ubuntu
      sudo cp -r /mnt/cdrom/* ${WWW_ROOT}/download/ubuntu/
      sudo cp /mnt/cdrom/ubuntu/isolinux/ldlinux.c32 /var/lib/tftpboot
      sudo cp /mnt/cdrom/ubuntu/isolinux/libcom32.c32 /var/lib/tftpboot
      sudo cp /mnt/cdrom/ubuntu/isolinux/libutil.c32 /var/lib/tftpboot
      sudo cp /mnt/cdrom/ubuntu/isolinux/chain.c32 /var/lib/tftpboot
      sudo umount /mnt/cdrom

#. Edit ks.cfg and replace IP address of PXE bootstrap server and subdir in
   `/var/www` (in this case `/var/www/download`):

   .. code-block:: bash

      sudo cp ks.cfg ${WWW_ROOT}/download/ks.cfg

#. Edit boot-screens_txt.cfg and replace IP address of PXE bootstrap server and
   subdir in `/var/www` (in this case `/var/www/download`):

   .. code-block:: bash

      sudo cp boot-screens_txt.cfg /var/lib/tftpboot/ubuntu-installer/amd64/boot-screens/txt.cfg
      sudo cp syslinux.cfg /var/lib/tftpboot/ubuntu-installer/amd64/boot-screens/syslinux.cfg

New testbed host - manual preparation
`````````````````````````````````````

Set CIMC/IPMI address, username, password and hostname an BIOS.

Bootstrap the host
``````````````````

Optional: CIMC - From PXE boostrap server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Initialize args.ip: Power-Off, reset BIOS defaults, Enable console redir, get
   LOM MAC addr:

   .. code-block:: bash

     ./cimc.py -u admin -p Cisco1234 $CIMC_ADDRESS -d -i

#. Adjust BIOS settings:

   .. code-block:: bash

      ./cimc.py -u admin -p Cisco1234 $CIMC_ADDRESS -d -s '<biosVfIntelHyperThreadingTech rn="Intel-HyperThreading-Tech" vpIntelHyperThreadingTech="disabled" />' -s '<biosVfEnhancedIntelSpeedStepTech rn="Enhanced-Intel-SpeedStep-Tech" vpEnhancedIntelSpeedStepTech="disabled" />' -s '<biosVfIntelTurboBoostTech rn="Intel-Turbo-Boost-Tech" vpIntelTurboBoostTech="disabled" />'

#. If RAID is not created in CIMC. Create RAID array. Reboot:

   .. code-block:: bash

      ./cimc.py -u admin -p Cisco1234 $CIMC_ADDRESS -d --wipe
      ./cimc.py -u admin -p Cisco1234 $CIMC_ADDRESS -d -r -rl 1 -rs <disk size> -rd '[1,2]'

#. Reboot server with boot from PXE (restart immediately):

   .. code-block:: bash

      ./cimc.py -u admin -p Cisco1234 $CIMC_ADDRESS -d -pxe

#. Set the next boot from HDD (without restart). Execute while Ubuntu install
   is running:

   .. code-block:: bash

      ./cimc.py -u admin -p Cisco1234 $CIMC_ADDRESS -d -hdd

Optional: IPMI - From PXE boostrap server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Get MAC address of LAN0:

   .. code-block:: bash

      ipmitool -U ADMIN -H $HOST_ADDRESS raw 0x30 0x21 | tail -c 18

#. Reboot into PXE for next boot only:

   .. code-block:: bash

      ipmitool -I lanplus -H $HOST_ADDRESS -U ADMIN chassis bootdev pxe
      ipmitool -I lanplus -H $HOST_ADDRESS -U ADMIN power reset

#. For live watching SOL (Serial-over-LAN console):

   .. code-block:: bash

      ipmitool -I lanplus -H $HOST_ADDRESS -U ADMIN sol activate
      ipmitool -I lanplus -H $HOST_ADDRESS -U ADMIN sol deactivate

Ansible machine
~~~~~~~~~~~~~~~

Baremetal provisioning of machine via Cobbler module
....................................................

# TODO: (remove all steps above and document usage of cobbler module)

Prerequisities for running Ansible
..................................

- Ansible can run on any machine that has direct SSH connectivity to target
  machines that will be provisioned (does not need to be PXE server).
- User `testuser` with password `Csit1234` is created with home folder
  initialized on all target machines that will be provisioned.
- Inventory directory is created with same or similar content as
  `inventories/lf_inventory` in `inventories/` directory (`sample_inventory`
  can be used).
- Group variables in `ansible/inventories/<inventory>/group_vars/all.yaml` are
  adjusted per environment. Special attention to `proxy_env` variable.
- Host variables in `ansible/inventories/<inventory>/host_vars/x.x.x.x.yaml` are
  defined.

Ansible structure
.................

Ansible is defining roles `TG` (Traffic Generator), `SUT` (System Under Test),
`VPP_DEVICE` (vpp_device host for functional testing). `COMMON` (Applicable
for all servers in inventory).

Each Host has corresponding Ansible role mapped and is applied only if Host
with that role is present in inventory file. As a part of optimization the role
`common` contains Ansible tasks applied for all Hosts.

.. note::

   You may see `[WARNING]: Could not match supplied host pattern, ignoring:
   <role>` in case you have not define hosts for that particular role.

Ansible structure is described below:

.. code-block:: bash

   .
   ├── inventories                     # Contains all inventories.
   │   ├── sample_inventory            # Sample, free for edits outside of LF.
   │   │   ├── group_vars              # Variables applied for all hosts.
   │   │   │   └── all.yaml
   │   │   ├── hosts                   # Inventory list with sample hosts.
   │   │   └── host_vars               # Variables applied for single host only.
   │   │       └── 1.1.1.1.yaml        # Sample host with IP 1.1.1.1
   │   └── lf_inventory                # Linux Foundation inventory.
   │       ├── group_vars
   │       │   └── all.yaml
   │       ├── hosts
   │       └── host_vars
   ├── roles                           # CSIT roles.
   │   ├── common                      # Role applied for all hosts.
   │   ├── sut                         # Role applied for all SUTs only.
   │   ├── tg                          # Role applied for all TGs only.
   │   ├── tg_sut                      # Role applied for TGs and SUTs only.
   │   └── vpp_device                  # Role applied for vpp_device only.
   ├── site.yaml                       # Main playbook.
   ├── sut.yaml                        # SUT playbook.
   ├── tg.yaml                         # TG playbook.
   ├── vault_pass                      # Main password for vualt.
   ├── vault.yml                       # Ansible vualt storage.
   └── vpp_device.yaml                 # vpp_device playbook.

Tagging
.......

Every task, handler, role, playbook is tagged with self-explanatory tags that
could be used to limit which objects are applied to target systems.

You can see which tags are applied to tasks, roles, and static imports by
running `ansible-playbook` with the `--list-tasks` option. You can display all
tags applied to the tasks with the `--list-tags` option.

Running Ansible
...............

#. Go to ansible directory: `cd csit/resources/tools/testbed-setup/ansible`
#. Run ansible on selected hosts:
   `ansible-playbook --vault-password-file=vault_pass --extra-vars '@vault.yml'
   --inventory <inventory_file> site.yaml --limit x.x.x.x`

#. Run ansible on selected hosts with selected tags:
   `ansible-playbook --vault-password-file=vault_pass --extra-vars '@vault.yml'
   --inventory <inventory_file> site.yaml --limit x.x.x.x --tags copy-90-csit`

.. note::

   In case you want to provision only particular role. You can use tags: `tg`,
   `sut`, `vpp_device`.

Reboot hosts
------------

# TODO: Document rebooting of machine via IMPI/CIMC/reboot handler.
