Calibration Data - Haswell
--------------------------

Following sections include sample calibration data measured on a server used in Intel Xeon Haswell testbeds as specified in `CSIT/Testbeds: Xeon Hsw, VIRL
<https://wiki.fd.io/view/CSIT/Testbeds:_Xeon_Hsw,_VIRL.#FD.io_CSIT_testbeds_-_Xeon_Haswell.2C_VIRL>`_.

Calibration data obtained from all other servers in Haswell testbeds
shows the same or similar values.

Linux cmdline
~~~~~~~~~~~~~

::

    $ cat /proc/cmdline
    BOOT_IMAGE=/vmlinuz-4.4.0-72-generic root=UUID=3969c7a5-20ed-4f9e-9f62-224a297e3c91 ro isolcpus=1-17,19-35 nohz_full=1-17,19-35 rcu_nocbs=1-17,19-35 intel_pstate=disable console=tty0 console=ttyS0,115200n8

Linux uname
~~~~~~~~~~~
::

    $ uname -a
    Linux t3-sut2 4.4.0-72-generic #93-Ubuntu SMP Fri Mar 31 14:07:41 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux


System-level core jitter
~~~~~~~~~~~~~~~~~~~~~~~~

::

    $ sudo taskset -c 9 ./jitter -i 20
    Linux Jitter testing program version 1.8
    Iterations=20
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
        160024     189800      29776     160028     160024     189800    3858759680 3207726364          1
        160024     212000      51976     160024     160024     212000    2785017856 3207890684          2
        160024     200568      40544     160024     160024     212000    1711276032 3207881960          3
        160024     189640      29616     160024     160024     212000     637534208 3207914340          4
        160024     193996      33972     160028     160024     212000    3858759680 3207833472          5
        160024     190388      30364     160024     160024     212000    2785017856 3207919492          6
        160024     194268      34244     160028     160024     212000    1711276032 3207798064          7
        160024     189812      29788     160024     160024     212000     637534208 3207731200          8
        160024     188672      28648     160028     160024     212000    3858759680 3207592096          9
        160024     186420      26396     160024     160024     212000    2785017856 3207568460         10
        160024     196128      36104     160028     160024     212000    1711276032 3207964180         11
        160024     189936      29912     160024     160024     212000     637534208 3207511772         12
        160024     190700      30676     160024     160024     212000    3858759680 3207596496         13
        160024     187592      27568     160024     160024     212000    2785017856 3207490816         14
        160024     189484      29460     160028     160024     212000    1711276032 3207602292         15
        160024     182644      22620     160028     160024     212000     637534208 3207681140         16
        160024     187584      27560     160028     160024     212000    3858759680 3207540192         17
        160024     187848      27824     160028     160024     212000    2785017856 3207375488         18
        160024     190060      30036     160024     160024     212000    1711276032 3207548348         19
        160024     190692      30668     160028     160024     212000     637534208 3207807304         20


Memory bandwidth
~~~~~~~~~~~~~~~~

::

    $ sudo ./mlc --bandwidth_matrix
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --bandwidth_matrix

    Using buffer size of 100.000MB/thread for reads and an additional 100.000MB/thread for writes
    Measuring Memory Bandwidths between nodes within system
    Bandwidths are in MB/sec (1 MB/sec = 1,000,000 Bytes/sec)
    Using all the threads from each core if Hyper-threading is enabled
    Using Read-only traffic type
                    Numa node
    Numa node            0       1
           0        57929.6 30301.6
           1        30239.7 57916.7

::

    $ sudo ./mlc --peak_injection_bandwidth
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --peak_injection_bandwidth

    Using buffer size of 100.000MB/thread for reads and an additional 100.000MB/thread for writes

    Measuring Peak Injection Memory Bandwidths for the system
    Bandwidths are in MB/sec (1 MB/sec = 1,000,000 Bytes/sec)
    Using all the threads from each core if Hyper-threading is enabled
    Using traffic with the following read-write ratios
    ALL Reads        :      115474.0
    3:1 Reads-Writes :      106140.0
    2:1 Reads-Writes :      103085.2
    1:1 Reads-Writes :      88131.4
    Stream-triad like:      99441.4

::

    $ sudo ./mlc --max_bandwidth
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --max_bandwidth

    Using buffer size of 100.000MB/thread for reads and an additional 100.000MB/thread for writes

    Measuring Maximum Memory Bandwidths for the system
    Will take several minutes to complete as multiple injection rates will be tried to get the best bandwidth
    Bandwidths are in MB/sec (1 MB/sec = 1,000,000 Bytes/sec)
    Using all the threads from each core if Hyper-threading is enabled
    Using traffic with the following read-write ratios
    ALL Reads        :      115445.46
    3:1 Reads-Writes :      105865.17
    2:1 Reads-Writes :      103209.58
    1:1 Reads-Writes :      88237.94
    Stream-triad like:      105331.80


Memory latency
~~~~~~~~~~~~~~

::

    $ sudo ./mlc --latency_matrix
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --latency_matrix

    Using buffer size of 200.000MB
    Measuring idle latencies (in ns)...
                    Numa node
    Numa node            0       1
           0          97.5   139.6
           1         132.8    98.0

::

    $ sudo ./mlc --idle_latency
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --idle_latency

    Using buffer size of 200.000MB
    Each iteration took 221.8 core clocks ( 96.7    ns)

::

    $ sudo ./mlc --loaded_latency
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --loaded_latency

    Using buffer size of 100.000MB/thread for reads and an additional 100.000MB/thread for writes

    Measuring Loaded Latencies for the system
    Using all the threads from each core if Hyper-threading is enabled
    Using Read-only traffic type
    Inject  Latency Bandwidth
    Delay   (ns)    MB/sec
    ==========================
     00000  293.43   115506.3
     00002  293.49   115530.3
     00008  292.85   115383.6
     00015  279.41   115462.2
     00050  246.46   114521.9
     00100  205.84   109191.0
     00200  122.31    81005.1
     00300  111.43    58581.9
     00400  106.28    45752.9
     00500  104.78    37498.6
     00700  102.54    27679.7
     01000  100.90    19953.1
     01300  100.18    15657.4
     01700   99.55    12227.0
     02500   98.99     8595.7
     03500   98.73     6355.8
     05000   98.52     4662.1
     09000   98.26     2890.2
     20000   98.21     1663.0


L1/L2/LLC latency
~~~~~~~~~~~~~~~~~

::

    $ sudo ./mlc --c2c_latency
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --c2c_latency

    Measuring cache-to-cache transfer latency (in ns)...
    Local Socket L2->L2 HIT  latency        42.2
    Local Socket L2->L2 HITM latency        47.1
    Remote Socket L2->L2 HITM latency (data address homed in writer socket)
                            Reader Numa Node
    Writer Numa Node     0       1
                0        -   106.5
                1    106.7       -
    Remote Socket L2->L2 HITM latency (data address homed in reader socket)
                            Reader Numa Node
    Writer Numa Node     0       1
                0        -   106.4
                1    106.4       -