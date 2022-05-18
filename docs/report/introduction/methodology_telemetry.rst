.. _telemetry:

OpenMetrics
-----------

OpenMetrics specifies the de-facto standard for transmitting cloud-native
metrics at scale, with support for both text representation and Protocol
Buffers.

RFC
~~~

- RFC2119
- RFC5234
- RFC8174
- draft-richih-opsawg-openmetrics-00

Reference
~~~~~~~~~

`OpenMetrics <https://github.com/OpenObservability/OpenMetrics/blob/master/specification/OpenMetrics.md>`_

Metric Types
~~~~~~~~~~~~

- Gauge
- Counter
- StateSet
- Info
- Histogram
- GaugeHistogram
- Summary
- Unknown

Telemetry module in CSIT currently support only Gauge, Counter and Info.

Example metric file
~~~~~~~~~~~~~~~~~~~

```
  # HELP calls_total Number of calls total
  # TYPE calls_total counter
  calls_total{name="api-rx-from-ring",state="active",thread_id="0",thread_lcore="1",thread_name="vpp_main"} 0.0
  calls_total{name="fib-walk",state="any wait",thread_id="0",thread_lcore="1",thread_name="vpp_main"} 0.0
  calls_total{name="ip6-mld-process",state="any wait",thread_id="0",thread_lcore="1",thread_name="vpp_main"} 0.0
  calls_total{name="ip6-ra-process",state="any wait",thread_id="0",thread_lcore="1",thread_name="vpp_main"} 0.0
  calls_total{name="unix-epoll-input",state="polling",thread_id="0",thread_lcore="1",thread_name="vpp_main"} 39584.0
  calls_total{name="avf-0/18/6/0-output",state="active",thread_id="1",thread_lcore="2",thread_name="vpp_wk_0"} 91.0
  calls_total{name="avf-0/18/6/0-tx",state="active",thread_id="1",thread_lcore="2",thread_name="vpp_wk_0"} 91.0
  calls_total{name="avf-input",state="polling",thread_id="1",thread_lcore="2",thread_name="vpp_wk_0"} 91.0
  calls_total{name="ethernet-input",state="active",thread_id="1",thread_lcore="2",thread_name="vpp_wk_0"} 91.0
  calls_total{name="ip4-input-no-checksum",state="active",thread_id="1",thread_lcore="2",thread_name="vpp_wk_0"} 91.0
  calls_total{name="ip4-lookup",state="active",thread_id="1",thread_lcore="2",thread_name="vpp_wk_0"} 91.0
  calls_total{name="ip4-rewrite",state="active",thread_id="1",thread_lcore="2",thread_name="vpp_wk_0"} 91.0
  calls_total{name="avf-0/18/2/0-output",state="active",thread_id="2",thread_lcore="0",thread_name="vpp_wk_1"} 91.0
  calls_total{name="avf-0/18/2/0-tx",state="active",thread_id="2",thread_lcore="0",thread_name="vpp_wk_1"} 91.0
  calls_total{name="avf-input",state="polling",thread_id="2",thread_lcore="0",thread_name="vpp_wk_1"} 91.0
  calls_total{name="ethernet-input",state="active",thread_id="2",thread_lcore="0",thread_name="vpp_wk_1"} 91.0
  calls_total{name="ip4-input-no-checksum",state="active",thread_id="2",thread_lcore="0",thread_name="vpp_wk_1"} 91.0
  calls_total{name="ip4-lookup",state="active",thread_id="2",thread_lcore="0",thread_name="vpp_wk_1"} 91.0
  calls_total{name="ip4-rewrite",state="active",thread_id="2",thread_lcore="0",thread_name="vpp_wk_1"} 91.0
  calls_total{name="unix-epoll-input",state="polling",thread_id="2",thread_lcore="0",thread_name="vpp_wk_1"} 1.0
```

Anatomy of existing CSIT telemetry implementation
-------------------------------------------------

Existing implementation consists of several measurment building blocks:
the main measuring block running search algorithms (MLR, PLR, SOAK, MRR, ...),
the latency measuring block and the several telemetry blocks with or without
traffic running on a background.

The main measuring block must not be interrupted by any read operation that can
impact data plane traffic processing during throughput search algorithm. Thus
operational reads are done before (pre-stat) and after (post-stat) that block.

Some operational reads must be done while traffic is running and usually
consists of two reads (pre-run-stat, post-run-stat) with defined delay between
them.

MRR measurement
~~~~~~~~~~~~~~~

```
  traffic_start(r=mrr)               traffic_stop       |<     measure     >|
    |                                  |                |      (r=mrr)      |
    |   pre_run_stat   post_run_stat   |    pre_stat    |                   |  post_stat
    |        |               |         |       |        |                   |      |
  --o--------o---------------o---------o-------o--------+-------------------+------o------------>
                                                                                              t

Legend:
  - pre_run_stat
    - vpp-clear-runtime
  - post_run_stat
    - vpp-show-runtime
    - bash-perf-stat            // if extended_debug == True
  - pre_stat
    - vpp-clear-stats
    - vpp-enable-packettrace    // if extended_debug == True
    - vpp-enable-elog
  - post_stat
    - vpp-show-stats
    - vpp-show-packettrace      // if extended_debug == True
    - vpp-show-elog
```

```
    |<                                measure                                 >|
    |                                 (r=mrr)                                  |
    |                                                                          |
    |<    traffic_trial0    >|<    traffic_trial1    >|<    traffic_trialN    >|
    |    (i=0,t=duration)    |    (i=1,t=duration)    |    (i=N,t=duration)    |
    |                        |                        |                        |
  --o------------------------o------------------------o------------------------o--->
                                                                                 t
```

MLR measurement
~~~~~~~~~~~~~~~

```
    |<     measure     >|   traffic_start(r=pdr)               traffic_stop   traffic_start(r=ndr)               traffic_stop  |< [    latency    ] >|
    |      (r=mlr)      |    |                                  |              |                                  |            |     .9/.5/.1/.0     |
    |                   |    |   pre_run_stat   post_run_stat   |              |   pre_run_stat   post_run_stat   |            |                     |
    |                   |    |        |               |         |              |        |               |         |            |                     |
  --+-------------------+----o--------o---------------o---------o--------------o--------o---------------o---------o------------[---------------------]--->
                                                                                                                                                       t

Legend:
  - pre_run_stat
    - vpp-clear-runtime
  - post_run_stat
    - vpp-show-runtime
    - bash-perf-stat          // if extended_debug == True
  - pre_stat
    - vpp-clear-stats
    - vpp-enable-packettrace  // if extended_debug == True
    - vpp-enable-elog
  - post_stat
    - vpp-show-stats
    - vpp-show-packettrace    // if extended_debug == True
    - vpp-show-elog
```


Improving existing solution
---------------------------

Improving existing CSIT telemetry implementaion including these areas.

- telemetry optimization
  - reducing ssh overhead
  - removing stats without added value
- telemetry scheduling
  - improve accuracy
  - improve configuration
- telemetry output
  - standardize output

Existing stats implementation was abstracted to having pre-/post-run-stats
phases. Improvement will be done by merging pre-/post- logic implementation into
separated stat-runtime block configurable and locally executed on SUT.

This will increase precision, remove complexity and move implementation into
separated module.

OpenMetric format for cloud native metric capturing will be used to ensure
integration with post processing module.

MRR measurement
~~~~~~~~~~~~~~~

```
    traffic_start(r=mrr)               traffic_stop                 |<     measure     >|
      |                                  |                          |      (r=mrr)      |
      |   |<      stat_runtime      >|   |          stat_pre_trial  |                   |  stat_post_trial
      |   |                          |   |             |            |                   |     |
  ----o---+--------------------------+---o-------------o------------+-------------------+-----o------------->
                                                                                                          t

Legend:
  - stat_runtime
    - vpp-runtime
    - perf-stat-runtime
  - stat_pre_trial
    - vpp-clear-stats
    - vpp-enable-packettrace  // if extended_debug == True
  - stat_post_trial
    - vpp-show-stats
    - vpp-show-packettrace    // if extended_debug == True
```

```
    |<                                measure                                 >|
    |                                 (r=mrr)                                  |
    |                                                                          |
    |<    traffic_trial0    >|<    traffic_trial1    >|<    traffic_trialN    >|
    |    (i=0,t=duration)    |    (i=1,t=duration)    |    (i=N,t=duration)    |
    |                        |                        |                        |
  --o------------------------o------------------------o------------------------o--->
                                                                                 t
```

```
    |<                              stat_runtime                              >|
    |                                                                          |
    |<       program0       >|<       program1       >|<       programN       >|
    |       (@=params)       |       (@=params)       |       (@=params)       |
    |                        |                        |                        |
  --o------------------------o------------------------o------------------------o--->
                                                                                 t
```


MLR measurement
~~~~~~~~~~~~~~~

```
    |<     measure     >|   traffic_start(r=pdr)               traffic_stop   traffic_start(r=ndr)               traffic_stop  |< [    latency    ] >|
    |      (r=mlr)      |     |                                  |              |                                  |           |     .9/.5/.1/.0     |
    |                   |     |   |<      stat_runtime      >|   |              |   |<      stat_runtime      >|   |           |                     |
    |                   |     |   |                          |   |              |   |                          |   |           |                     |
  --+-------------------+-----o---+--------------------------+---o--------------o---+--------------------------+---o-----------[---------------------]--->
                                                                                                                                                       t

Legend:
  - stat_runtime
    - vpp-runtime
    - perf-stat-runtime
  - stat_pre_trial
    - vpp-clear-stats
    - vpp-enable-packettrace  // if extended_debug == True
  - stat_post_trial
    - vpp-show-stats
    - vpp-show-packettrace    // if extended_debug == True
```

vpp-runtime
~~~~~~~~~~~
It's a phase when VPP telemetry is collected. VPP uses perfmon to collect
counters for different events.

How VPP measures performance counters:

  Reset perfmon counters.
  Opens file descriptor (FD) and attaches to event ~ 2ms
  Then waits 1s ~ 1001ms
  Show perfmon counters for measured event ~ 1ms

Counters collected per event:
  - context-switches
    - CONTEXT_SWITCHES (0x3)
  - page-faults
    - PAGE-FAULTS-MINOR (0x5)
    - PAGE-FAULTS-MAJOR (0x6)
  - inst-and-clock
    - INTEL_CORE_E_INST_RETIRED_ANY_P (0xc0)
    - INTEL_CORE_E_CPU_CLK_UNHALTED_THREAD_P (0x3c)
    - INTEL_CORE_E_CPU_CLK_UNHALTED_REF_TSC (0x300)
  - cache-hierarchy
    - INTEL_CORE_E_MEM_LOAD_RETIRED_L1_HIT (0xd1, 0x01)
    - INTEL_CORE_E_MEM_LOAD_RETIRED_L1_MISS (0xd1, 0x08)
    - INTEL_CORE_E_MEM_LOAD_RETIRED_L2_MISS (0xd1, 0x10)
    - INTEL_CORE_E_MEM_LOAD_RETIRED_L3_MISS (0xd1, 0x20)
  - load-blocks
    - INTEL_CORE_E_LD_BLOCKS_STORE_FORWARD (0x203)
    - INTEL_CORE_E_LD_BLOCKS_NO_SR (0x803)
    - INTEL_CORE_E_LD_BLOCKS_PARTIAL_ADDRESS_ALIAS (0x107)
  - branch-mispred
    - INTEL_CORE_E_BR_INST_RETIRED_ALL_BRANCHES (0xc4)
    - INTEL_CORE_E_BR_INST_RETIRED_NEAR_TAKEN (0x20c4)
    - INTEL_CORE_E_BR_MISP_RETIRED_ALL_BRANCHES (0xc5)
  - power-licensing
    - INTEL_CORE_E_CPU_CLK_UNHALTED_THREAD_P (0x3c)
    - INTEL_CORE_E_CORE_POWER_LVL0_TURBO_LICENSE (0x728)
    - INTEL_CORE_E_CORE_POWER_LVL1_TURBO_LICENSE (0x1828)
    - INTEL_CORE_E_CORE_POWER_LVL2_TURBO_LICENSE (0x2028)
    - INTEL_CORE_E_CORE_POWER_THROTTLE (0x4028)
  - memory-bandwidth
    - INTEL_UNCORE_E_IMC_UNC_M_CAS_COUNT_RD
    - INTEL_UNCORE_E_IMC_UNC_M_CAS_COUNT_WR

perf-stat-runtime
~~~~~~~~~~~
It's a phase when linux telemetry is collected. CSIT uses perf command
to collect perf counters for different events. CSIT and VPP use the same events
for measurement.

How CSIT measures performance counters:

  perf stat commands executes with specified event for 1s
  output data are separated by ";"
  then data are processed to Prometheus openmetrics format

Counters collected per event:
  - context-switches
    - CONTEXT_SWITCHES (0x3)
  - page-faults
    - PAGE-FAULTS-MINOR (0x5)
    - PAGE-FAULTS-MAJOR (0x6)
  - inst-and-clock
    - INSTRUCTIONS (0xc0)
    - CPU-CYCLES (0x3c)
  - cache-hierarchy
    - CACHE_REFERENCES (0x1)
    - CACHE_MISSES (0x2)

Other counters are not used.

Tooling
-------

Prerequisites:
- bpfcc-tools
- python-bpfcc
- libbpfcc
- libbpfcc-dev
- libclang1-9 libllvm9

```bash
  $ sudo apt install bpfcc-tools python3-bpfcc libbpfcc libbpfcc-dev libclang1-9 libllvm9
```


Configuration
-------------

```vpp_runtime
resources/templates/telemetry/vpp_runtime.yaml

bpf_runtime
resources/templates/telemetry/bpf_runtime.yaml
```

CSIT captured metrics
---------------------

SUT
~~~

Compute resource
________________

- BPF /process
  - BPF_HASH(cpu_instruction, struct key_t);
  - BPF_HASH(cpu_cycle, struct key_t);
  - BPF_HASH(cache_reference, struct key_t);
  - BPF_HASH(cache_miss, struct key_t);
  - BPF_HASH(sw_context_switches, struct key_t);
  - BPF_HASH(sw_page_faults_maj, struct key_t);
  - BPF_HASH(sw_page_faults_maj, struct key_t);

Memory resource
_______________

- BPF /process
  - tbd

Network resource
________________

- BPF /process
  - tbd

DUT VPP metrics
~~~~~~~~~~~~~~~

Compute resource
________________

- runtime /node `show runtime`
  - calls
  - vectors
  - suspends
  - clocks
  - vectors_calls
- perfmon /bundle
  - inst-and-clock      node      intel-core          instructions/packet, cycles/packet and IPC
  - cache-hierarchy     node      intel-core          cache hits and misses
  - context-switches    thread    linux               per-thread context switches
  - branch-mispred      node      intel-core          Branches, branches taken and mis-predictions
  - page-faults         thread    linux               per-thread page faults
  - load-blocks         node      intel-core          load operations blocked due to various uarch reasons
  - power-licensing     node      intel-core          Thread power licensing
  - memory-bandwidth    system    intel-uncore        memory reads and writes per memory controller channel

Memory resource - tbd
_____________________

- memory /segment `show memory verbose api-segment stats-segment main-heap`
  - total
  - used
  - free
  - trimmable
  - free-chunks
  - free-fastbin-blks
  - max-total-allocated
- physmem `show physmem`
  - pages
  - subpage-size

Network resource
________________

- counters /node `show node counters`
  - count
  - severity
- hardware /interface `show interface`
  - rx_stats
  - tx_stats
- packets /interface `show hardware`
  - rx_packets
  - rx_bytes
  - rx_errors
  - tx_packets
  - tx_bytes
  - tx_errors
  - drops
  - punt
  - ip4
  - ip6
  - rx_no_buf
  - rx_miss


DUT DPDK metrics - tbd
~~~~~~~~~~~~~~~~~~~~~~

Compute resource
________________

- BPF /process
  - BPF_HASH(cpu_instruction, struct key_t);
  - BPF_HASH(cpu_cycle, struct key_t);
  - BPF_HASH(cache_reference, struct key_t);
  - BPF_HASH(cache_miss, struct key_t);
  - BPF_HASH(sw_context_switches, struct key_t);
  - BPF_HASH(sw_page_faults_maj, struct key_t);
  - BPF_HASH(sw_page_faults_maj, struct key_t);

Memory resource
_______________

- BPF /process
  - tbd

Network resource
________________

- packets /interface
  - inPackets
  - outPackets
  - inBytes
  - outBytes
  - outErrorPackets
  - dropPackets
