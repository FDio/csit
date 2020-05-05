TG Settings - TRex
------------------

TG Version
~~~~~~~~~~

|trex-release|

DPDK Version
~~~~~~~~~~~~

DPDK v19.05

TG Installation
~~~~~~~~~~~~~~~

T-Rrex installation is managed via Ansible role.

TG Startup Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ sudo -E -S sh -c 'cat << EOF > /etc/trex_cfg.yaml
  - version: 2
    c: 15
    limit_memory: 8192
    interfaces: ["${pci1}","${pci2}"]
    port_info:
      - dest_mac: [${dest_mac1}]
        src_mac: [${src_mac1}]
      - dest_mac: [${dest_mac2}]
        src_mac: [${src_mac2}]
    platform :
      master_thread_id: 0
      latency_thread_id: 16
      dual_if:
          - socket: 0
            threads: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
  EOF'

TG Startup Command
~~~~~~~~~~~~~~~~~~

::

  $ sh -c 'cd <t-rex-install-dir>/scripts/ && \
    sudo nohup ./t-rex-64 -i --prefix $(hostname) --hdrh --no-scapy-server \
    > /tmp/trex.log 2>&1 &' > /dev/null

TG API Driver
~~~~~~~~~~~~~

`TRex driver`_
