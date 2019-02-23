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

Documentation below is step by step tutorial and assumes an understanding of PXE
boot and `Ansible <https://www.ansible.com/>`_ and managing physical hardware
via CIMC or IPMI.

This process is not specific for Linux Foundation lab, but associated files and
code, is based on the assumption that it runs in Linux Foundation environment.
If run elsewhere, changes will be required in following files:

#. Inventory directory: `ansible/inventories/sample_inventory/`
#. Inventory files: `ansible/inventories/sample_inventory/hosts`

The process below assumes that there is a host used for bootstrapping (referred
to as a "Cobbler provision host" below), with reachable DHCP service.

Ansible host
------------

Prerequisities for running Ansible
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- CIMC/IPMI address, username, password are set in BIOS.
- Ansible can be invoked on any host that has direct SSH connectivity to
  the remote hosts that will be provisioned (does not need to be Cobbler
  provision host). This may require installed ssh_keys `ssh-copy-id` on remote
  host or disabled StrictHostChecking on host running Ansible:

  ::

  Host <host_ip or host subnet_ip>
        StrictHostKeyChecking no
        UserKnownHostsFile=/dev/null

- Ansible version 2.7+ is installed via PIP or via standard package
  distribution (apt, yum, dnf).
- User `testuser` with password `Csit1234` is created with home folder
  initialized on all remote machines that will be provisioned.
- Inventory directory is created with same or similar content as
  `inventories/lf_inventory` in `inventories/` directory (`sample_inventory`
  can be used).
- Group variables in `ansible/inventories/<inventory>/group_vars/all.yaml` are
  adjusted per environment with special attention to `proxy_env` variable.
- Host variables in `ansible/inventories/<inventory>/host_vars/x.x.x.x.yaml` are
  defined.

Ansible structure
~~~~~~~~~~~~~~~~~

Ansible is defining roles `tg` (Traffic Generator), `sut` (System Under Test),
`vpp_device` (vpp_device host for functional device testing), `common`
(Applicable for all hosts in inventory) and `cobbler` (Cobbler provision host).

Each host has corresponding Ansible role mapped and is applied only if a host
with that role is present in inventory file. As a part of optimization the role
`common` contains Ansible tasks applied for all hosts.

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
   │   ├── cobbler                     # Role applied for Cobbler host only.
   │   ├── common                      # Role applied for all hosts.
   │   ├── sut                         # Role applied for all SUTs only.
   │   ├── tg                          # Role applied for all TGs only.
   │   ├── tg_sut                      # Role applied for TGs and SUTs only.
   │   └── vpp_device                  # Role applied for vpp_device only.
   ├── site.yaml                       # Main playbook.
   ├── sut.yaml                        # SUT playbook.
   ├── tg.yaml                         # TG playbook.
   ├── vault_pass                      # Main password for vault.
   ├── vault.yml                       # Ansible vault storage.
   └── vpp_device.yaml                 # vpp_device playbook.

Tagging
~~~~~~~

Every task, handler, role or playbook is tagged with self-explanatory tag(s)
that could be used to limit which Ansible objects are applied to target systems.

You can see what tags are applied to tasks, roles, and static imports by
running `ansible-playbook` with the `--list-tasks` option. You can display all
tags applied to the tasks with the `--list-tags` option.

Running Ansible
~~~~~~~~~~~~~~~

#. Go to ansible directory: `$ cd csit/resources/tools/testbed-setup/ansible`
#. Run ansible on selected hosts:
   `$ ansible-playbook --vault-password-file=vault_pass --extra-vars
   '@vault.yml' --inventory <inventory_file> site.yaml --limit <host_ip>`
#. (Optional) Run ansible on selected hosts with selected tags:
   `$ ansible-playbook --vault-password-file=vault_pass --extra-vars
   '@vault.yml' --inventory <inventory_file> site.yaml --limit <host_ip>
   --tags 'copy-90-csit'`

.. note::

   In case you want to provision only particular role. You can use tags: `tg`,
   `sut`, `vpp_device`.

Baremetal provisioning of host via Ansible Cobbler module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Baremetal provisioning of the host with Ansible is done via `Cobbler
<https://cobbler.github.io/>`_. Ansible contains a role `cobbler` that includes
a set of tasks for deploying Cobbler in a container on dedicated host.
Container is built during Ansible run of `cobbler` role and it provides DHCPD,
TFTPD, HTTTP and Cobbler services.

There is a special set of tasks and handlers in `common` role that does include
a system into Cobbler and reboots provisioned host.

#. Go to Ansible directory: `$ cd csit/resources/tools/testbed-setup/ansible`
#. Prepare Cobbler provision host via Ansible on dedicated hosts:
   `$ ansible-playbook --vault-password-file=vault_pass --extra-vars
   '@vault.yml' --inventory <inventory_file> site.yaml --limit <cobbler_ip>`
#. Run Ansible on selected hosts with selected tags:
   `$ ansible-playbook --vault-password-file=vault_pass --extra-vars
   '@vault.yml' --inventory <inventory_file> site.yaml --limit <host_ip>
   --tags 'provision'`
