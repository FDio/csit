Calibration Data - TaiShan
--------------------------

Following sections include sample calibration data measured on
s17-t33-sut1 server running in one of the Cortex-A72 testbeds.

Calibration data obtained from all other servers in TaiShan testbeds shows the
same or similar values.


Linux cmdline
~~~~~~~~~~~~~

::

    $ cat /proc/cmdline
    BOOT_IMAGE=/boot/vmlinuz-4.15.0-54-generic root=/dev/mapper/huawei--1--vg-root ro isolcpus=1-15,17-31,33-47,49-63 nohz_full=1-15     17-31,33-47,49-63 rcu_nocbs=1-15     17-31,33-47,49-63 intel_iommu=on nmi_watchdog=0 audit=0 nosoftlockup processor.max_cstate=1 console=ttyAMA0,115200n8

Linux uname
~~~~~~~~~~~

::

    $ uname -a
    Linux s17-t33-sut1 4.15.0-54-generic #58-Ubuntu SMP Mon Jun 24 10:56:40 UTC 2019 aarch64 aarch64 aarch64 GNU/Linux


System-level Core Jitter
~~~~~~~~~~~~~~~~~~~~~~~~

::

    $ sudo taskset -c 3 /home/testuser/pma_tools/jitter/jitter -i 20
    Linux Jitter testing program version 1.9
    Iterations=30
    The pragram will execute a dummy function 80000 times
    Display is updated every 20000 displayUpdate intervals
    Thread affinity will be set to core_id:7
    Timings are in CPU Core cycles
    Inst_Min:    Minimum Excution time during the display update interval(default is ~1 second)
    Inst_Max:    Maximum Excution time during the display update interval(default is ~1 second)
    Inst_jitter: Jitter in the Excution time during rhe display update interval. This is the value of interest
    last_Exec:   The Excution time of last iteration just before the display update
    Abs_Min:     Absolute Minimum Excution time since the program started or statistics were reset
    Abs_Max:     Absolute Maximum Excution time since the program started or statistics were reset
    tmp:         Cumulative value calcualted by the dummy function
    Interval:    Time interval between the display updates in Core Cycles
    Sample No:   Sample number

       Inst_Min   Inst_Max   Inst_jitter last_Exec  Abs_min    Abs_max      tmp       Interval     Sample No
        160022     172254      12232     160042     160022     172254    1903230976 3204401362          1
        160022     173148      13126     160044     160022     173148     814809088 3204619316          2
        160022     169460       9438     160044     160022     173148    4021354496 3204391306          3
        160024     170270      10246     160044     160022     173148    2932932608 3204385830          4
        160022     169660       9638     160044     160022     173148    1844510720 3204387290          5
        160022     169410       9388     160040     160022     173148     756088832 3204375832          6
        160022     169012       8990     160042     160022     173148    3962634240 3204378924          7
        160022     169556       9534     160044     160022     173148    2874212352 3204374882          8
        160022     171684      11662     160042     160022     173148    1785790464 3204394596          9
        160022     171546      11524     160024     160022     173148     697368576 3204602774         10
        160022     169248       9226     160042     160022     173148    3903913984 3204401676         11
        160022     168458       8436     160042     160022     173148    2815492096 3204256350         12
        160022     169574       9552     160044     160022     173148    1727070208 3204278116         13
        160022     169352       9330     160044     160022     173148     638648320 3204327234         14
        160022     169100       9078     160044     160022     173148    3845193728 3204388132         15
        160022     169338       9316     160042     160022     173148    2756771840 3204380724         16
        160022     170828      10806     160046     160022     173148    1668349952 3204430452         17
        160022     173162      13140     160026     160022     173162     579928064 3204611318         18
        160022     170482      10460     160042     160022     173162    3786473472 3204389896         19
        160024     170704      10680     160044     160022     173162    2698051584 3204422126         20
        160024     169302       9278     160044     160022     173162    1609629696 3204397334         21
        160022     171848      11826     160044     160022     173162     521207808 3204389818         22
        160022     169438       9416     160042     160022     173162    3727753216 3204395382         23
        160022     169312       9290     160042     160022     173162    2639331328 3204371202         24
        160022     171368      11346     160044     160022     173162    1550909440 3204440464         25
        160022     171998      11976     160042     160022     173162     462487552 3204609440         26
        160022     169740       9718     160046     160022     173162    3669032960 3204405826         27
        160022     169610       9588     160044     160022     173162    2580611072 3204390608         28
        160022     169254       9232     160044     160022     173162    1492189184 3204399760         29
        160022     169386       9364     160046     160022     173162     403767296 3204417762         30

.. include:: ../introduction/test_environment_sut_meltspec_tsh.rst
