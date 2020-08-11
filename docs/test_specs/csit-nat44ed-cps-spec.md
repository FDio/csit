## Content

<!-- MarkdownTOC autolink="true" -->

- [Tests for NAT44ED](#tests-for-nat44ed)
- [CPS Test Objectives](#cps-test-objectives)
- [Input Parameters](#input-parameters)
- [Stateful traffic profiles](#stateful-traffic-profiles)
- [UDP CPS Tests](#udp-cps-tests)
  - [UDP TRex Measurements](#udp-trex-measurements)
    - [Counters](#counters)
    - [Calculations](#calculations)
    - [CPS Trial PASS](#cps-trial-pass)
    - [CPS-MRR](#cps-mrr)
    - [CPS-PDR](#cps-pdr)
    - [CPS-NDR](#cps-ndr)
  - [UDP VPP Telemetry](#udp-vpp-telemetry)
    - [Counters](#counters-1)
    - [Errors](#errors)
- [TCP/IP CPS Tests](#tcpip-cps-tests)
  - [TCP/IP TRex Measurements](#tcpip-trex-measurements)
    - [Counters](#counters-2)
    - [Calculations](#calculations-1)
    - [CPS Trial PASS](#cps-trial-pass-1)
    - [CPS-MRR](#cps-mrr-1)
    - [CPS-PDR](#cps-pdr-1)
    - [CPS-NDR](#cps-ndr-1)
  - [TCP/IP VPP Telemetry](#tcpip-vpp-telemetry)
    - [Counters](#counters-3)
    - [Errors](#errors-1)

<!-- /MarkdownTOC -->

## Tests for NAT44ED

Three types of stateful tests are developed for NAT44ED (source network address
and port translation IPv4 to IPv4 with 5-tuple session state):

- Connections-Per-Second (CPS), discovering the maximum rate of creating
  NAT44ED sessions. Measured separately for UDP and TCP connections and
  for different session scale.

- Packets-Per-Second (PPS), discovering the maximum rate of
  simultaneously creating NAT44ED sessions and transfering bulk of data
  packets across the corresponding connections. Measured separately for
  UDP and TCP connections with different session scale and different
  data packet sizes per each connection.

This note describes CPS tests.

## CPS Test Objectives

Discover DUT's highest sustain rate of creating fully functional NAT44ED
5-tuple stateful session entries. Session entry is considered fully
functional, if packets associated with this entry are NAT44ED processed
by DUT and forwarded in both directions without loss.

Similarly to packet throughput tests, three CPS rates are discovered:

- CPS-MRR, maximum receive rate for CPS, regardless of connection loss
  (connections not established).
- CPS-NDR, non-drop rate for CPS, with zero connection loss.
- CPS-PDR, partial drop rate for CPS, with configured connection loss
  ratio.

## Input Parameters

- `max_cps_rate`, maximum rate of establishing connections, to be used by
  traffic generator, limited by traffic generator capabilities, Ethernet
  link(s) rate and NIC model.
- `min_cps_rate`, minimum rate of establishing connections to be used for
  measurements. Search fails if lower transmit rate needs to be used to
  meet search criteria.
- `max_session_number`, maximum number of sessions to be established and
  tested.
- `target_loss_ratio`, maximum acceptable connections loss ratio search
  criteria for PDR measurements with UDP tests. Indicates packet drop
  impact on connection establishment rate.
- `final_relative_width`, required measurement resolution expressed as
  (lower_bound, upper_bound) interval width relative to upper_bound.

- stateful traffic profiles, TRex ASTF program defining the CPS
  transaction per L4 protocol tested (TCP, UDP), including connect and
  close sequence. Delay phase is required to account for successfully
  established and closed connections with associated packet and
  connection counters.

## Stateful traffic profiles

TRex ASTF program defines following TCP and UDP transactions for
discovering NAT44ED CPS limits:

- CPS with TCP
  - connect(syn,syn-ack,ack),
    - pkts client tx 2, rx 1
    - pkts server tx 1, rx 2
  - delay,
    - no packets
  - close(fin,fin-ack,ack,ack)
    - pkts client tx 2, rx 2
    - pkts server tx 1, rx 2
- CPS with UDP
  - connect_and_close(req,ack),
    - pkts client tx 1, rx 1
    - pkts server tx 1, rx 1

TRex ASTF program configuration parameters:

- `limit` of connections, set to `max_session_number`.
- `multiplier`, target number of transactions per second to be executed.
  Multiplier applies to connect and close phases.
- IPv4 source and destination address and port ranges matching the
  limit of connections.
  - Source and destination address changing packet-by-packet with two
    separate profiles i) incrementing sequentially pair-wise and ii)
    changed randomly (with seed) pair-wise.
  - Source port changing randomly within the range.
- `trial_duration`, function of `max_session_number` and `trial_cps_rate`
  - `trial_cps_rate`, subject of the search, value in the range (`min_cps_rate`,`max_cps_rate`)
  - `target_setup_duration` = `max_session_number` / `trial_cps_rate`
  - For UDP:
    - `trial_duration` = `target_setup_duration` + `cool_down_delay`
    - `cool_down_delay` = `target_setup_duration` * 0.2 (TODO Vratko to confirm)
  - For TCP:
    - `trial_duration` = 2 * `target_setup_duration` + `cool_down_delay`
    - `cool_down_delay` = `target_setup_duration` * 0.4 (TODO Vratko to confirm)

## UDP CPS Tests

### UDP TRex Measurements

#### Counters

Following TRex ASTF counters are collected by UDP CPS tests for automated
results evaluation (r) and debugging purposes (d):

- Interface 1 Client
  - (r) `opackets`
  - (r) `packets`
- Interface 2 Server
  - (r) `opackets`
  - (r) `packets`
- Traffic Client
  - (d) `m_active_flows`
  - (r) `m_est_flows`
  - (r) `m_traffic_duration`
  - (d) `udps_connects`
  - (d) `udps_closed`
  - (d) `udps_sndbyte`
  - (d) `udps_sndpkt`
  - (d) `udps_rcvbyte`
  - (d) `udps_rcvpkt`
  - (d) `udps_keepdrops`, TRex out of capacity, dropping UDP KAs(?) (TODO Test criteria.)
  - (d) `err_rx_throttled`, TRex out of capacity, throttling workers due to Rx overload(?) (TODO Test criteria.)
  - (d) `err_c_nf_throttled`, Number of client side flows that were not opened due to flow-table overflow(?) (TODO Test criteria.)
  - (d) `err_flow_overflow`, too many flows(?) (TODO Test criteria.)
- Traffic Server
  - (d) `m_active_flows`
  - (r) `m_est_flows`
  - (r) `m_traffic_duration`
  - (d) `udps_accepts`
  - (d) `udps_closed`
  - (d) `udps_sndbyte`
  - (d) `udps_sndpkt`
  - (d) `udps_rcvbyte`
  - (d) `udps_rcvpkt`
  - (d) `err_rx_throttled`, TRex out of capacity, throttling workers due to Rx overload(?) (TODO Test criteria.)

[TRex ASTF counters reference](https://trex-tgn.cisco.com/trex/doc/trex_astf.html#_counters_reference).

TRex counters are polled periodically by CSIT python code every 1 sec
interval. (TODO: Shall we also consider more frequent polling e.g. every
0.5 sec ?)

Two specific sets of (r) TRex counters are used for test results evaluation:

- Target-Counters: Counters collected at the lowest value of
  `c_m_traffic_duration` conforming with (`c_m_traffic_duration` >
  `target_setup_duration`).
- Final-Counters: Final cumulative counters after trial ends.

Note: Target-Counters are used for CPS test results evaluations, unless
otherwise stated.

#### Calculations

- Interface packet loss
  - `pktloss_c_s` = `c_opackets` - `s_ipackets`
  - `pktloss_s_c` = `s_opackets` - `c_ipackets`
  - `pktloss_ratio` = (`pktloss_s_c` + `pktloss_c_s`) / (`c_opackets` + `s_opackets`)
- UDP session packet loss (TODO REMOVE?)
  - `udp_pktloss_c_s` = `c_udps_sndpkt` - `s_udps_rcvpkt`
  - `udp_pktloss_s_c` = `s_udps_sndpkt` - `c_udps_rcvpkt`
  - `udp_pktloss_ratio` = (`udp_pktloss_s_c` + `udp_pktloss_c_s`) / (`c_udps_sndpkt` + `s_udps_sndpkt`)
- UDP session byte loss (TODO REMOVE?)
  - `udp_byteloss_c_s` = `c_udps_sndbyte` - `s_udps_rcvbyte`
  - `udp_byteloss_s_c` = `s_udps_sndbyte` - `c_udps_rcvbyte`
  - `udp_byteloss_ratio` = (`udp_byteloss_s_c` + `udp_byteloss_c_s`) / (`c_udps_sndbyte` + `s_udps_sndbyte`)
- UDP session integrity (TODO REMOVE?)
  - `udp_attempted_connection_count` = `c_udps_connects`
    - `udp_attempted_connection_count` = `max_session_number`
  - `udp_failed_connection_count` = `s_udps_accepts` - `c_udps_connects`
    - `udp_failed_connection_count` = `udp_attempted_connection_count` - `c_udps_rcvpkt` (taken from Final-Counters)

#### CPS Trial PASS

PASS of UDP CPS test trial is conditioned on all of the following criteria being met:

- PASS-C1 TRex must attempt all configured `max_session_number` in `target_setup_duration` time
   - IOW TRex must send connect packets at configured `trial_cps_rate`.
- PASS-C2 Following TRex errors ARE NOT recorded in Target-Counters:
  - Traffic Client
    - `udps_keepdrops`, TRex out of capacity, dropping UDP KAs(?)
    - `err_rx_throttled`, TRex out of capacity, throttling workers due to Rx overload(?)
    - `err_c_nf_throttled`, Number of client side flows that were not opened due to flow-table overflow(?)
    - `err_flow_overflow`, too many flows(?)
  - Traffic Server
    - `err_rx_throttled`, TRex out of capacity, throttling workers due to Rx overload(?)

#### CPS-MRR

Reported MRR values are equal to the following TRex counters from Target-Counters:
- `c_m_est_flows`
- `s_m_est_flows`

TODO Add description of separate set of tests for discovering a **safe**
CPS-MTR value (Maximum Transmit Rate) for TRex, where TRex errors **are not**
observed in Target-Counters.

#### CPS-PDR

CPS-PDR values are discovered using MLRsearch, a binary search optimized
for the overall test duration.

CPS-PDR = `trial_cps_rate`, if all of the following conditions are met:

- `udp_failed_connection_count` < `target_loss_ratio`
- `udp_pktloss_ratio` < `target_loss_ratio`
- `pktloss_ratio` < `target_loss_ratio`

Measurements to be reported in the CPS-PDR result test message:

- `trial_cps_rate`
- `c_m_est_flows`
- `s_m_est_flows`

#### CPS-NDR

CPS-NDR values are discovered using MLRsearch, a binary search optimized
for the overall test duration.

CPS-NDR = `trial_cps_rate`, if all of the following conditions are met:

- `udp_failed_connection_count` = 0
- `udp_pktloss_ratio` = 0
- `pktloss_ratio` = 0

Measurements to be reported in the CPS-PDR result test message:

- `trial_cps_rate`
- `c_m_est_flows`
- `s_m_est_flows`

### UDP VPP Telemetry

#### Counters

- VPP show nat44 summary

  ```
  max translations per thread: 81920
  max translations per user: 81920
  total timed out sessions: 0
  total sessions: 64514
  total tcp sessions: 0
  total tcp established sessions: 0
  total tcp transitory sessions: 0
  total tcp transitory (WAIT-CLOSED) sessions: 0
  total tcp transitory (CLOSED) sessions: 0
  total udp sessions: 64514
  total icmp sessions: 0
  ```

- VPP show interface

  ```
  <TODO add sample output>
  ```

- VPP show runtime

  ```
  <TODO add sample output>
  ```

#### Errors

- VPP show errors

  ```
  Count                    Node                  Reason
       32258       nat44-in2out-worker-handoff      same worker
       32256       nat44-in2out-worker-handoff      do handoff
       32258             nat44-ed-out2in            good out2in packets processed
       32258             nat44-ed-out2in            UDP packets
       32258        nat44-ed-in2out-slowpath        good in2out packets processed
       32258        nat44-ed-in2out-slowpath        UDP packets
       32256       nat44-out2in-worker-handoff      same worker
       32258       nat44-out2in-worker-handoff      do handoff
       32256             nat44-ed-out2in            good out2in packets processed
       32256             nat44-ed-out2in            UDP packets
       32256        nat44-ed-in2out-slowpath        good in2out packets processed
       32256        nat44-ed-in2out-slowpath        UDP packets
  ```

## TCP/IP CPS Tests

### TCP/IP TRex Measurements

#### Counters

Following TRex ASTF counters are collected by UDP CPS tests for automated
results evaluation (r) and debugging purposes (d):

- Interface 1 Client
  - (r) `opackets`
  - (r) `packets`
- Interface 2 Server
  - (r) `opackets`
  - (r) `packets`
- Traffic Client
  - (d) `m_active_flows`
  - (r) `m_est_flows`
  - (r) `m_traffic_duration`
  - (d) `tcps_connattempt`
  - (d) `tcps_connects`
  - (d) `tcps_closed`
- Traffic Server
  - (d) `m_active_flows`
  - (r) `m_est_flows`
  - (r) `m_traffic_duration`
  - (d) `tcps_accepts`
  - (d) `tcps_connects`
  - (d) `tcps_closed`
  - (d) `err_no_template`, server can’t match L7 template no destination port or IP range

[TRex ASTF counters reference](https://trex-tgn.cisco.com/trex/doc/trex_astf.html#_counters_reference).

TRex counters polled periodically by CSIT python code every 1 sec
interval. (TODO: Shall we also consider more frequent polling e.g. every
0.5 sec ?)

Counter values evaluated for two specific sets read from TRex:

- Target-Counters: Counters collected at the lowest value of
  `c_m_traffic_duration` conforming with (`c_m_traffic_duration` >
  `target_setup_duration`).
- Final-Counters: Final cumulative counters after trial ends.

Note: Target-Counters are used for CPS test results evaluations, unless
otherwise stated.

#### Calculations

- Interface packet loss
  - `pktloss_c_s` = `c_opackets` - `s_ipackets`
  - `pktloss_s_c` = `s_opackets` - `c_ipackets`
  - `pktloss_ratio` = (`pktloss_s_c` + `pktloss_c_s`) / (`c_opackets` + `s_opackets`)
- TCP session integrity
  - `tcp_attempted_connection_count` = `c_tcps_connattempt`
  - `tcp_failed_connection_count` = `c_tcps_connects` - `c_tcps_connattempt`

#### CPS Trial PASS

PASS of TCP CPS test trial is conditioned on all of the following criteria being met:

- PASS-C1 TRex must attempt all configured `max_session_number` in `target_setup_duration` time
   - IOW TRex must send connect packets at configured `trial_cps_rate`.
- PASS-C2 Following TRex errors ARE NOT recorded in Target-Counters:
  - Traffic Client
    - No errors recorded so far
  - Traffic Server
    - `err_no_template`, server can’t match L7 template no destination port or IP range

#### CPS-MRR

Reported MRR values are equal to the following TRex counters from Target-Counters:
- `c_m_est_flows`
- `s_m_est_flows`

TODO Add description of separate set of tests for discovering a **safe**
CPS-MTR value (Maximum Transmit Rate) for TRex, where TRex errors **are not**
observed in Target-Counters.

#### CPS-PDR

CPS-PDR values are discovered using MLRsearch, a binary search optimized
for the overall test duration.

CPS-PDR = `trial_cps_rate`, if all of the following conditions are met:

- `tcp_failed_connection_count` < `target_loss_ratio`
- `pktloss_ratio` < `target_loss_ratio`

Measurements to be reported in the CPS-PDR result test message:

- `trial_cps_rate`
- `c_m_est_flows`
- `s_m_est_flows`

#### CPS-NDR

CPS-NDR values are discovered using MLRsearch, a binary search optimized
for the overall test duration.

CPS-NDR = `trial_cps_rate`, if all of the following conditions are met:

- `tcp_failed_connection_count` = 0
- `pktloss_ratio` = 0

Measurements to be reported in the CPS-PDR result test message:

- `trial_cps_rate`
- `c_m_est_flows`
- `s_m_est_flows`

### TCP/IP VPP Telemetry

#### Counters

- VPP show nat44 summary

  ```
  <TODO add sample output>
  ```

- VPP show interface

  ```
  <TODO add sample output>
  ```

- VPP show runtime

  ```
  <TODO add sample output>
  ```

#### Errors

- VPP show errors

  ```
  <TODO add sample output>
  ```