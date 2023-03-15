---
bookToc: false
title: "Telemetry"
weight: 20
---

# Telemetry

OpenMetrics specifies the de-facto standard for transmitting cloud-native
metrics at scale, with support for both text representation and Protocol
Buffers.

## RFC

- RFC2119
- RFC5234
- RFC8174
- draft-richih-opsawg-openmetrics-00

## Reference

[OpenMetrics](https://github.com/OpenObservability/OpenMetrics/blob/master/specification/OpenMetrics.md)

## Metric Types

- Gauge
- Counter
- StateSet
- Info
- Histogram
- GaugeHistogram
- Summary
- Unknown

Telemetry module in CSIT currently support only Gauge, Counter and Info.

## Anatomy of CSIT telemetry implementation

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

## MRR measurement

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


    |<                                measure                                 >|
    |                                 (r=mrr)                                  |
    |                                                                          |
    |<    traffic_trial0    >|<    traffic_trial1    >|<    traffic_trialN    >|
    |    (i=0,t=duration)    |    (i=1,t=duration)    |    (i=N,t=duration)    |
    |                        |                        |                        |
  --o------------------------o------------------------o------------------------o--->
                                                                                 t


## MLR measurement

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


## MRR measurement

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


    |<                                measure                                 >|
    |                                 (r=mrr)                                  |
    |                                                                          |
    |<    traffic_trial0    >|<    traffic_trial1    >|<    traffic_trialN    >|
    |    (i=0,t=duration)    |    (i=1,t=duration)    |    (i=N,t=duration)    |
    |                        |                        |                        |
  --o------------------------o------------------------o------------------------o--->
                                                                                 t


    |<                              stat_runtime                              >|
    |                                                                          |
    |<       program0       >|<       program1       >|<       programN       >|
    |       (@=params)       |       (@=params)       |       (@=params)       |
    |                        |                        |                        |
  --o------------------------o------------------------o------------------------o--->
                                                                                 t


## MLR measurement

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
