TG Configuration - TRex
-----------------------

**TG Version**

|trex-release|

**DPDK version**

DPDK v17.11

**TG Build Script used**

`TRex intallation`_

**TG Startup Configuration**

::

    $ cat /etc/trex_cfg.yaml
    - port_limit      : 2
      version         : 2
      interfaces      : ["0000:0d:00.0","0000:0d:00.1"]
      port_info       :
        - dest_mac        :   [0x3c,0xfd,0xfe,0x9c,0xee,0xf5]
          src_mac         :   [0x3c,0xfd,0xfe,0x9c,0xee,0xf4]
        - dest_mac        :   [0x3c,0xfd,0xfe,0x9c,0xee,0xf4]
          src_mac         :   [0x3c,0xfd,0xfe,0x9c,0xee,0xf5]

**TG Startup Command**

::

    $ sh -c 'cd <t-rex-install-dir>/scripts/ && sudo nohup ./t-rex-64 -i -c 7 --iom 0 > /tmp/trex.log 2>&1 &'> /dev/null

**TG common API - pointer to driver**

`TRex driver`_
