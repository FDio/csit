Calibration Data - Haswell
--------------------------

Following sections include sample calibration data measured on t1-sut1
server running in one of the Intel Xeon Haswell testbeds as specified in
`CSIT/Testbeds: Xeon Hsw, VIRL
<https://wiki.fd.io/view/CSIT/Testbeds:_Xeon_Hsw,_VIRL.#FD.io_CSIT_testbeds_-_Xeon_Haswell.2C_VIRL>`_.

Calibration data obtained from all other servers in Haswell testbeds
shows the same or similar values.


Linux cmdline
~~~~~~~~~~~~~

::

    $ cat /proc/cmdline
    BOOT_IMAGE=/vmlinuz-4.15.0-36-generic root=UUID=5d2ecc97-245b-4e94-b0ae-c3548567de19 ro isolcpus=1-17,19-35 nohz_full=1-17,19-35 rcu_nocbs=1-17,19-35 numa_balancing=disable intel_pstate=disable intel_iommu=on iommu=pt nmi_watchdog=0 audit=0 nosoftlockup processor.max_cstate=1 intel_idle.max_cstate=1 hpet=disable tsc=reliable mce=off console=tty0 console=ttyS0,115200n8


Linux uname
~~~~~~~~~~~

::

    $ uname -a
    Linux t1-tg1 4.15.0-36-generic #39-Ubuntu SMP Mon Sep 24 16:19:09 UTC 2018 x86_64 x86_64 x86_64 GNU/Linux


System-level Core Jitter
~~~~~~~~~~~~~~~~~~~~~~~~

::

    $ sudo taskset -c 3 /home/testuser/pma_tools/jitter/jitter -i 30
    Linux Jitter testing program version 1.8
    Iterations=30
    The pragram will execute a dummy function 80000 times
    Display is updated every 20000 displayUpdate intervals
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
        160024     172636      12612     160028     160024     172636    1573060608 3205463144          1
        160024     188236      28212     160028     160024     188236     958595072 3205500844          2
        160024     185676      25652     160028     160024     188236     344129536 3205485976          3
        160024     172608      12584     160024     160024     188236    4024631296 3205472740          4
        160024     179260      19236     160028     160024     188236    3410165760 3205502164          5
        160024     172432      12408     160024     160024     188236    2795700224 3205452036          6
        160024     178820      18796     160024     160024     188236    2181234688 3205455408          7
        160024     172512      12488     160028     160024     188236    1566769152 3205461528          8
        160024     172636      12612     160028     160024     188236     952303616 3205478820          9
        160024     173676      13652     160028     160024     188236     337838080 3205470412         10
        160024     178776      18752     160028     160024     188236    4018339840 3205481472         11
        160024     172788      12764     160028     160024     188236    3403874304 3205492336         12
        160024     174616      14592     160028     160024     188236    2789408768 3205474904         13
        160024     174440      14416     160028     160024     188236    2174943232 3205479448         14
        160024     178748      18724     160024     160024     188236    1560477696 3205482668         15
        160024     172588      12564     169404     160024     188236     946012160 3205510496         16
        160024     172636      12612     160024     160024     188236     331546624 3205472204         17
        160024     172480      12456     160024     160024     188236    4012048384 3205455864         18
        160024     172740      12716     160028     160024     188236    3397582848 3205464932         19
        160024     179200      19176     160028     160024     188236    2783117312 3205476012         20
        160024     172480      12456     160028     160024     188236    2168651776 3205465632         21
        160024     172728      12704     160024     160024     188236    1554186240 3205497204         22
        160024     172620      12596     160028     160024     188236     939720704 3205466972         23
        160024     172640      12616     160028     160024     188236     325255168 3205471216         24
        160024     172484      12460     160028     160024     188236    4005756928 3205467388         25
        160024     172636      12612     160028     160024     188236    3391291392 3205482748         26
        160024     179056      19032     160024     160024     188236    2776825856 3205467152         27
        160024     172672      12648     160024     160024     188236    2162360320 3205483268         28
        160024     176932      16908     160024     160024     188236    1547894784 3205488536         29
        160024     172452      12428     160028     160024     188236     933429248 3205440636         30


Memory Bandwidth
~~~~~~~~~~~~~~~~

::

    $ sudo /home/testuser/mlc --bandwidth_matrix
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --bandwidth_matrix

    Using buffer size of 100.000MB/thread for reads and an additional 100.000MB/thread for writes
    Measuring Memory Bandwidths between nodes within system
    Bandwidths are in MB/sec (1 MB/sec = 1,000,000 Bytes/sec)
    Using all the threads from each core if Hyper-threading is enabled
    Using Read-only traffic type
                     Numa node
    Numa node        0       1
        0        57935.5   30265.2
        1        30284.6   58409.9

::

    $ sudo /home/testuser/mlc --peak_injection_bandwidth
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --peak_injection_bandwidth

    Using buffer size of 100.000MB/thread for reads and an additional 100.000MB/thread for writes

    Measuring Peak Injection Memory Bandwidths for the system
    Bandwidths are in MB/sec (1 MB/sec = 1,000,000 Bytes/sec)
    Using all the threads from each core if Hyper-threading is enabled
    Using traffic with the following read-write ratios
    ALL Reads        :  115762.2
    3:1 Reads-Writes :  106242.2
    2:1 Reads-Writes :  103031.8
    1:1 Reads-Writes :  87943.7
    Stream-triad like:  100048.4

::

    $ sudo /home/testuser/mlc --max_bandwidth
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --max_bandwidth

    Using buffer size of 100.000MB/thread for reads and an additional 100.000MB/thread for writes

    Measuring Maximum Memory Bandwidths for the system
    Will take several minutes to complete as multiple injection rates will be tried to get the best bandwidth
    Bandwidths are in MB/sec (1 MB/sec = 1,000,000 Bytes/sec)
    Using all the threads from each core if Hyper-threading is enabled
    Using traffic with the following read-write ratios
    ALL Reads        :  115782.41
    3:1 Reads-Writes :  105965.78
    2:1 Reads-Writes :  103162.38
    1:1 Reads-Writes :  88255.82
    Stream-triad like:  105608.10


Memory Latency
~~~~~~~~~~~~~~

::

    $ sudo /home/testuser/mlc --latency_matrix
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --latency_matrix

    Using buffer size of 200.000MB
    Measuring idle latencies (in ns)...
                     Numa node
    Numa node        0       1
        0           101.0   132.0
        1           141.2    98.8

::

    $ sudo /home/testuser/mlc --idle_latency
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --idle_latency

    Using buffer size of 200.000MB
    Each iteration took 227.2 core clocks ( 99.0    ns)

::

    $ sudo /home/testuser/mlc --loaded_latency
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --loaded_latency

    Using buffer size of 100.000MB/thread for reads and an additional 100.000MB/thread for writes

    Measuring Loaded Latencies for the system
    Using all the threads from each core if Hyper-threading is enabled
    Using Read-only traffic type
    Inject  Latency Bandwidth
    Delay   (ns)    MB/sec
    ==========================
     00000  294.08   115841.6
     00002  294.27   115851.5
     00008  293.67   115821.8
     00015  278.92   115587.5
     00050  246.80   113991.2
     00100  206.86   104508.1
     00200  123.72    72873.6
     00300  113.35    52641.1
     00400  108.89    41078.9
     00500  108.11    33699.1
     00700  106.19    24878.0
     01000  104.75    17948.1
     01300  103.72    14089.0
     01700  102.95    11013.6
     02500  102.25     7756.3
     03500  101.81     5749.3
     05000  101.46     4230.4
     09000  101.05     2641.4
     20000  100.77     1542.5


L1/L2/LLC Latency
~~~~~~~~~~~~~~~~~

::

    $ sudo /home/testuser/mlc --c2c_latency
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --c2c_latency

    Measuring cache-to-cache transfer latency (in ns)...
    Local Socket L2->L2 HIT  latency    42.1
    Local Socket L2->L2 HITM latency    47.0
    Remote Socket L2->L2 HITM latency (data address homed in writer socket)
                      Reader Numa Node
    Writer Numa Node     0       1
                0        -   108.0
                1    106.9       -
    Remote Socket L2->L2 HITM latency (data address homed in reader socket)
                      Reader Numa Node
    Writer Numa Node     0       1
                0        -   107.7
                1    106.6       -

.. include:: ../introduction/test_environment_sut_meltspec_hsw.rst
