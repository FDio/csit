TG Settings - TRex
------------------

TG Version
~~~~~~~~~~

|trex-release|

DPDK Version
~~~~~~~~~~~~

DPDK v19.02

TG Build Script Used
~~~~~~~~~~~~~~~~~~~~

`TRex installation`_

TG Startup Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

::

    $ cat /etc/trex_cfg.yaml
    - version         : 2
      interfaces      : ["0000:0d:00.0","0000:0d:00.1"]
      port_info       :
        - dest_mac        :   [0x3c,0xfd,0xfe,0x9c,0xee,0xf5]
          src_mac         :   [0x3c,0xfd,0xfe,0x9c,0xee,0xf4]
        - dest_mac        :   [0x3c,0xfd,0xfe,0x9c,0xee,0xf4]
          src_mac         :   [0x3c,0xfd,0xfe,0x9c,0xee,0xf5]

TG Startup Command
~~~~~~~~~~~~~~~~~~

::

    $ sh -c 'cd <t-rex-install-dir>/scripts/ && sudo nohup ./t-rex-64 -i -c 7 > /tmp/trex.log 2>&1 &'> /dev/null

TG API Driver
~~~~~~~~~~~~~

`TRex driver`_
