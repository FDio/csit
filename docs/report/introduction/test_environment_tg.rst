.. _test_environment_tg:

TG Settings - TRex
------------------

TG Version
~~~~~~~~~~

|trex-release|

DPDK Version
~~~~~~~~~~~~

DPDK v21.02

TG Installation
~~~~~~~~~~~~~~~

T-Rex installation is managed via Ansible role.

TG Startup Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ sudo -E -S sh -c 'cat << EOF > /etc/trex_cfg.yaml
  - version: 2
    c: 8
    limit_memory: 8192
    interfaces: ["${pci1}","${pci2}"]
    port_info:
        - dest_mac: [${dest_mac1}]
          src_mac: [${src_mac1}]
        - dest_mac: [${dest_mac2}]
          src_mac: [${src_mac2}]
    platform :
        master_thread_id: 0
        latency_thread_id: 9
        dual_if:
            - socket: 0
              threads: [1, 2, 3, 4, 5, 6, 7, 8]
  EOF'

TG Startup Command (Stateless Mode)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ sudo -E -S sh -c "cd '${trex_install_dir}/scripts/' && \
    nohup ./t-rex-64 -i --prefix $(hostname) --hdrh --no-scapy-server \
    --mbuf-factor 32 > /tmp/trex.log 2>&1 &" > /dev/null

Also, Python client is now starting traffic with:

::

  core_mask=STLClient.CORE_MASK_PIN

TG Startup Command (Stateful Mode)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ sudo -E -S sh -c "cd '${trex_install_dir}/scripts/' && \
    nohup ./t-rex-64 -i --prefix $(hostname) --astf --hdrh --no-scapy-server \
    --mbuf-factor 32 > /tmp/trex.log 2>&1 &" > /dev/null


TG API Driver
~~~~~~~~~~~~~

`TRex driver`_
