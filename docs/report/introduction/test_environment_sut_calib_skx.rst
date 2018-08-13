Xeon Skylake HW Calibration
---------------------------

mk: add some description.

Linux cmdline
~~~~~~~~~~~~~

::

    $ cat /proc/cmdline
    BOOT_IMAGE=/vmlinuz-4.15.0-23-generic root=UUID=10184ffc-8723-4c9f-b547-bcbc367bf8f1 ro isolcpus=1-27,29-55,57-83,85-111 nohz_full=1-27,29-55,57-83,85-111 rcu_nocbs=1-27,29-55,57-83,85-111 numa_balancing=disable intel_pstate=disable intel_iommu=on iommu=pt console=tty0 console=ttyS0,115200n8

Linux uname
~~~~~~~~~~~

::

    $ uname -a
    Linux s5-t22-sut1 4.15.0-23-generic #25-Ubuntu SMP Wed May 23 18:02:16 UTC 2018 x86_64 x86_64 x86_64 GNU/Linux


System-level core jitter
~~~~~~~~~~~~~~~~~~~~~~~~

::

    $ sudo taskset -c 3 ./jitter -i 20
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
        125018     135640      10622     125018     125018     135640    3329949696 2502875936          1
        125018     133052       8034     125024     125018     135640    1893400576 2502805180          2
        125018     132890       7872     125022     125018     135640     456851456 2502851454          3
        125018     133336       8318     125020     125018     135640    3315269632 2502798868          4
        125018     133230       8212     125020     125018     135640    1878720512 2502804746          5
        125018     135214      10196     125022     125018     135640     442171392 2503084050          6
        125018     133892       8874     125022     125018     135640    3300589568 2502904294          7
        125018     137476      12458     125022     125018     137476    1864040448 2502874450          8
        125018     132822       7804     125018     125018     137476     427491328 2502790132          9
        125018     132336       7318     125018     125018     137476    3285909504 2502811854         10
        125018     133184       8166     125018     125018     137476    1849360384 2502842788         11
        125018     132242       7224     125020     125018     137476     412811264 2502792968         12
        125018     132650       7632     125020     125018     137476    3271229440 2502806046         13
        125018     132874       7856     125018     125018     137476    1834680320 2502887768         14
        125018     132596       7578     125018     125018     137476     398131200 2502858432         15
        125018     136040      11022     125024     125018     137476    3256549376 2503025236         16
        125018     133398       8380     125020     125018     137476    1820000256 2502886104         17
        125018     133104       8086     125018     125018     137476     383451136 2502868568         18
        125018     133524       8506     125020     125018     137476    3241869312 2502911338         19
        125018     133576       8558     125020     125018     137476    1805320192 2502898720         20


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
           0        108034.1        16945.5
           1        50657.1 19468.8

::

    $ sudo ./mlc --peak_injection_bandwidth
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --peak_injection_bandwidth

    Using buffer size of 100.000MB/thread for reads and an additional 100.000MB/thread for writes

    Measuring Peak Injection Memory Bandwidths for the system
    Bandwidths are in MB/sec (1 MB/sec = 1,000,000 Bytes/sec)
    Using all the threads from each core if Hyper-threading is enabled
    Using traffic with the following read-write ratios
    ALL Reads        :      127368.2
    3:1 Reads-Writes :      106957.3
    2:1 Reads-Writes :      106292.0
    1:1 Reads-Writes :      90591.7
    Stream-triad like:      96077.4

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
    ALL Reads        :      131333.24
    3:1 Reads-Writes :      109840.77
    2:1 Reads-Writes :      106802.71
    1:1 Reads-Writes :      89597.48
    Stream-triad like:      108473.33


Memory latency
~~~~~~~~~~~~~~

::

    $ sudo ./mlc --latency_matrix
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --latency_matrix

    Using buffer size of 2000.000MB
    Measuring idle latencies (in ns)...
                    Numa node
    Numa node            0       1
           0          81.1   144.5
           1         139.6    72.7

::

    $ sudo ./mlc --idle_latency
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --idle_latency

    Using buffer size of 2000.000MB
    Each iteration took 201.7 core clocks ( 80.7    ns)

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
     00000  278.27   130637.1
     00002  282.72   130495.3
     00008  277.21   130676.3
     00015  278.57   130972.4
     00050  276.26   131114.1
     00100  269.04   131151.5
     00200  162.42   118076.2
     00300  109.54    93030.9
     00400   99.02    76541.4
     00500   94.80    66299.7
     00700   93.29    54388.3
     01000   90.96    44316.0
     01300   89.04    34875.3
     01700   88.58    26920.8
     02500   87.85    18598.4
     03500   88.52    13516.4
     05000   84.47     9728.5
     09000   81.13     5779.2
     20000   80.14     3046.6

L1/L2/LLC latency
~~~~~~~~~~~~~~~~~

::

    $ sudo ./mlc --c2c_latency
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --c2c_latency

    Measuring cache-to-cache transfer latency (in ns)...
    Local Socket L2->L2 HIT  latency        50.3
    Local Socket L2->L2 HITM latency        50.3
    Remote Socket L2->L2 HITM latency (data address homed in writer socket)
                            Reader Numa Node
    Writer Numa Node     0       1
                0        -   108.6
                1    108.5       -
    Remote Socket L2->L2 HITM latency (data address homed in reader socket)
                            Reader Numa Node
    Writer Numa Node     0       1
                0        -   170.8
                1    173.2       -

