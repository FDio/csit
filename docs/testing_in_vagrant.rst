Running CSIT locally in Vagrant
-------------------------------

Install prerequisites
=====================

Run all commands from command line.

1. Download and install latest virtualbox from `official page
   <https://www.virtualbox.org/wiki/Downloads>`_.
   To verify the installation, run VBoxManage:

   - on windows::

      "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" --version

   - on nix::

      VBoxManage --version

   You should see virtualbox manager version printed, eg: 6.1.12r139181

2. Download and install latest vagrant `from official page
   <https://www.vagrantup.com/downloads.html>`_.
   To verify the installtion, run::

      vagrant -v

   You should see vagrant version printed, eg: Vagrant 2.2.9

3. Install vagrant plugins::

      vagrant plugin install vagrant-vbguest
      vagrant plugin install vagrant-cachier

   If you are behind a proxy, install proxyconf plugin and update proxy
   settings in Vagrantfile::

      vagrant plugin install vagrant-proxyconf

Set up and run Vagrant virtualbox
======================================

Before running following commands change working directory to Vagrant specific directory
(from within root CSIT directory) ::

    cd resources/tools/vagrant

This allows Vagrant to automatically find Vagrantfile and corresponding Vagrant environment.

Start the provisioning::

   vagrant up --provider virtualbox

Your new VPP Device virtualbox machine will be created and configured.
Master branch of csit project will be cloned inside virtual machine into

   /home/vagrant/csit folder.

Once the process is finished, you can login to the box using::

   vagrant ssh

In case you need to completely rebuild the box and start from scratch,
run these commands::

   vagrant destroy -f
   vagrant up --provider virtualbox


Run tests
==============================

From within the box run the tests using::

   cd /home/vagrant/csit/resources/libraries/bash/entry
   ./bootstrap_vpp_device.sh csit-vpp-device-master-ubuntu1804-1n-vbox

To run only selected tests based on TAGS, export environment variables before
running the test suite::

   export GERRIT_EVENT_TYPE="comment-added"
   export GERRIT_EVENT_COMMENT_TEXT="devicetest memif"

   # now it will run tests, selected based on tags
   ./bootstrap_vpp_device.sh csit-vpp-device-master-ubuntu1804-1n-vbox


