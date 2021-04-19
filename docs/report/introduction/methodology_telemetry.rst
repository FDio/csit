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

Exesting stats implementation was abstracted to having pre-/post-run-stats
phases. Improvement will be done by merging pre-/post- logic implementation into
separated stat-runtime block configurable and locally executed on SUT.

This will increase precision, remove complexity and move implementation into
spearated module.

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
  - stat_pre_trial
    - vpp-clear-stats
    - vpp-enable-packettrace  // if extended_debug == True
  - stat_post_trial
    - vpp-show-stats
    - vpp-show-packettrace    // if extended_debug == True
```


Tooling
-------

Prereqisities:
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

```yaml
  logging:
    version: 1
    formatters:
      console:
        format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
      prom:
        format: '%(message)s'
    handlers:
      console:
        class: logging.StreamHandler
        level: INFO
        formatter: console
        stream: ext://sys.stdout
      prom:
        class: logging.handlers.RotatingFileHandler
        level: INFO
        formatter: prom
        filename: /tmp/metric.prom
        mode: w
    loggers:
      prom:
        handlers: [prom]
        level: INFO
        propagate: False
    root:
      level: INFO
      handlers: [console]
  scheduler:
    duration: 1
  programs:
    - name: bundle_bpf
      metrics:
        counter:
          - name: cpu_cycle
            documentation: Cycles processed by CPUs
            namespace: bpf
            labelnames:
              - name
              - cpu
              - pid
          - name: cpu_instruction
            documentation: Instructions retired by CPUs
            namespace: bpf
            labelnames:
              - name
              - cpu
              - pid
          - name: llc_reference
            documentation: Last level cache operations by type
            namespace: bpf
            labelnames:
              - name
              - cpu
              - pid
          - name: llc_miss
            documentation: Last level cache operations by type
            namespace: bpf
            labelnames:
              - name
              - cpu
              - pid
      events:
        - type: 0x0 # HARDWARE
          name: 0x0 # PERF_COUNT_HW_CPU_CYCLES
          target: on_cpu_cycle
          table: cpu_cycle
        - type: 0x0 # HARDWARE
          name: 0x1 # PERF_COUNT_HW_INSTRUCTIONS
          target: on_cpu_instruction
          table: cpu_instruction
        - type: 0x0 # HARDWARE
          name: 0x2 # PERF_COUNT_HW_CACHE_REFERENCES
          target: on_cache_reference
          table: llc_reference
        - type: 0x0 # HARDWARE
          name: 0x3 # PERF_COUNT_HW_CACHE_MISSES
          target: on_cache_miss
          table: llc_miss
      code: |
        #include <linux/ptrace.h>
        #include <uapi/linux/bpf_perf_event.h>

        const int max_cpus = 256;

        struct key_t {
            int cpu;
            int pid;
            char name[TASK_COMM_LEN];
        };

        BPF_HASH(llc_miss, struct key_t);
        BPF_HASH(llc_reference, struct key_t);
        BPF_HASH(cpu_instruction, struct key_t);
        BPF_HASH(cpu_cycle, struct key_t);

        static inline __attribute__((always_inline)) void get_key(struct key_t* key) {
            key->cpu = bpf_get_smp_processor_id();
            key->pid = bpf_get_current_pid_tgid();
            bpf_get_current_comm(&(key->name), sizeof(key->name));
        }

        int on_cpu_cycle(struct bpf_perf_event_data *ctx) {
            struct key_t key = {};
            get_key(&key);

            cpu_cycle.increment(key, ctx->sample_period);
            return 0;
        }
        int on_cpu_instruction(struct bpf_perf_event_data *ctx) {
            struct key_t key = {};
            get_key(&key);

            cpu_instruction.increment(key, ctx->sample_period);
            return 0;
        }
        int on_cache_reference(struct bpf_perf_event_data *ctx) {
            struct key_t key = {};
            get_key(&key);

            llc_reference.increment(key, ctx->sample_period);
            return 0;
        }
        int on_cache_miss(struct bpf_perf_event_data *ctx) {
            struct key_t key = {};
            get_key(&key);

            llc_miss.increment(key, ctx->sample_period);
            return 0;
        }
```

CSIT captured metrics
---------------------

SUT
~~~

Compute resource
________________

- BPF /process
  - BPF_HASH(llc_miss, struct key_t);
  - BPF_HASH(llc_reference, struct key_t);
  - BPF_HASH(cpu_instruction, struct key_t);
  - BPF_HASH(cpu_cycle, struct key_t);

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
  - BPF_HASH(llc_miss, struct key_t);
  - BPF_HASH(llc_reference, struct key_t);
  - BPF_HASH(cpu_instruction, struct key_t);
  - BPF_HASH(cpu_cycle, struct key_t);

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
