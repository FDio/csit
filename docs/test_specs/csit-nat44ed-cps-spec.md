## Content

<!-- MarkdownTOC autolink="true" -->

- [Tests for NAT44-ED](#tests-for-nat44-ed)
- [CPS Test Objectives](#cps-test-objectives)
- [Input Parameters](#input-parameters)
- [TRex ASTF Program](#trex-astf-program)
- [CPS Tests with UDP](#cps-tests-with-udp)
  - [TRex Measurements](#trex-measurements)
    - [Counters](#counters)
    - [Calculations](#calculations)
    - [CPS Trial PASS](#cps-trial-pass)
    - [CPS-MRR](#cps-mrr)
    - [CPS-PDR](#cps-pdr)
    - [CPS-NDR](#cps-ndr)
  - [VPP Telemetry](#vpp-telemetry)
    - [Counters](#counters-1)
    - [Errors](#errors)

<!-- /MarkdownTOC -->

## Tests for NAT44-ED

Three types of tests are developed for NAT44-ED (source network address
and port translation IPv4 to IPv4 with 5-tuple session state):

- Connections-Per-Second (CPS), discovering the maximum rate of creating
  NAT44-ED sessions. Measured separately for UDP and TCP connections and
  for different session scale.

- Transactions-Per-Second (TPS), discovering the maximum rate of
  simultaneously creating NAT44-ED sessions and transfering bulk data
  across the corresponding connections. Measured separately for UDP and
  TCP connections, different session scale and different sizes of bulk
  data transactions per each connection.

- Packet throughput, discovering the maximum sustained throughput rate
  of packet data after creating NAT44-ED sessions, without packet and
  data loss (non-drop rate, NDR) and with partial packet and data loss
  (partial drop rate, PDR). PDR measured for configured packet loss
  ratio (PLR) and byte loss ratio (BLR). Measured separately for UDP and
  TCP connections, different session scale and different sizes of bulk
  data transactions per each connection. Connection goodput reported for
  NDR and PDR packet throughput rates.

This note describes CPS.

## CPS Test Objectives

Discover DUT's highest sustain rate of creating fully functional NAT44ED
5-tuple stateful session entries. Session entry is considered fully
functional, if packets associated with this entry are NAT44ED processed
and forwarded in both directions without loss.

Similarly to packet throughput, three CPS rates are discovered:

- CPS-MRR, maximum received rate for CPS, regardless of packet loss.
- CPS-NDR, non-drop rate for CPS, with zero packet loss.
- CPS-PDR, partial drop rate for CPS, with configured packet loss ratio.

## Input Parameters

- `max_cps_rate`, maximum rate of establishing connections, to be used by
  traffic generator, limited by traffic generator capabilities, Ethernet
  link(s) rate and NIC model.
- `min_cps_rate`, minimum rate of establishing connections to be used for
  measurements. Search fails if lower transmit rate needs to be used to
  meet search criteria.
- `max_session_number`, maximum number of sessions to be established and
  tested.
- `target_packet_loss_ratio`, maximum acceptable PLR search criteria for PDR
  measurements with UDP tests. Indicates packet drop impact on data
  throughput without any host side congestion management.
- `byte_loss_ratio`, maximum acceptable PLR search criteria for PDR
  measurements with TCP/IP tests. Indicates packet drop impact on data
  throughput with host side TCP/IP congestion management.
- `final_relative_width`, required measurement resolution expressed as
  (lower_bound, upper_bound) interval width relative to upper_bound.
- TRex ASTF program, defining the CPS transaction per L4 protocol
  tested, including connect sequence (TCP, UDP), delay, close sequence,
  delay. Delay phases are required to account for successfully
  established and closed sessions with associated packet and session
  counters.

## TRex ASTF Program

TRex ASTF program defines following transactions for separate TCP and
UDP tests:

- CPS with TCP
  - connect(syn,syn-ack,ack),
    - pkts client tx 2, rx 1
    - pkts server tx 1, rx 2
  - delay,
    - no packets
  - close(fin,fin-ack,ack,ack)
    - pkts client tx 2, rx 2
    - pkts server tx 1, rx 2
  - delay,
    - no packets
- CPS with UDP
  - connect_and_close(req,ack),
    - pkts client tx 1, rx 1
    - pkts server tx 1, rx 1
  - delay,
    - no packets

TRex ASTF program configuration parameters:

- `limit` of sessions, set to `max_session_number`.
- `multiplier`, target number of transactions per second to be executed.
  Multiplier applies to connect and close phases.
- IPv4 source and destination address and port ranges matching the
  limit of sessions.
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

## CPS Tests with UDP

### TRex Measurements

#### Counters

[TRex ASTF counters reference](https://trex-tgn.cisco.com/trex/doc/trex_astf.html#_counters_reference).

- Interface 1 Client
  - `opackets`
  - `packets`
- Interface 2 Server
  - `opackets`
  - `packets`
- Traffic Client
  - `m_active_flows`
  - `m_est_flows`
  - `m_traffic_duration`
  - `udps_connects`
  - `udps_closed`
  - `udps_sndbyte`
  - `udps_sndpkt`
  - `udps_rcvbyte`
  - `udps_rcvpkt`
  - `udps_keepdrops`, TRex out of capacity, dropping UDP KAs(?) (TODO Test criteria.)
  - `err_rx_throttled`, TRex out of capacity, throttling workers due to Rx overload(?) (TODO Test criteria.)
  - `err_c_nf_throttled`, Number of client side flows that were not opened due to flow-table overflow(?) (TODO Test criteria.)
  - `err_flow_overflow`, too many flows(?) (TODO Test criteria.)
- Traffic Server
  - `m_active_flows`
  - `m_est_flows`
  - `m_traffic_duration`
  - `udps_accepts`
  - `udps_closed`
  - `udps_sndbyte`
  - `udps_sndpkt`
  - `udps_rcvbyte`
  - `udps_rcvpkt`
  - `err_rx_throttled`, TRex out of capacity, throttling workers due to Rx overload(?) (TODO Test criteria.)

TRex counters polled periodically by CSIT python code every 1 sec
interval. (TODO: Shall we also consider more frequent polling e.g. every
0.5 sec ?)

Counter values evaluated for two specific sets:

- Counters-Target-Set: Counters collected at the lowest value of
  `c_m_traffic_duration` conforming with (`c_m_traffic_duration` >
  `target_setup_duration`).
- Counters-Final-Set: Final cumulative counters after trial ends.

#### Calculations

- Interface packet loss
  - `pktloss_c_s` = `c_opackets` - `s_ipackets`
  - `pktloss_s_c` = `s_opackets` - `c_ipackets`
  - `pktloss_ratio` = (`pktloss_s_c` + `pktloss_c_s`) / (`c_opackets` + `s_opackets`)
- UDP session packet loss
  - `udp_pktloss_c_s` = `c_udps_sndpkt` - `s_udps_rcvpkt`
  - `udp_pktloss_s_c` = `s_udps_sndpkt` - `c_udps_rcvpkt`
  - `udp_pktloss_ratio` = (`udp_pktloss_s_c` + `udp_pktloss_c_s`) / (`c_udps_sndpkt` + `s_udps_sndpkt`)
- UDP session byte loss
  - `udp_byteloss_c_s` = `c_udps_sndbyte` - `s_udps_rcvbyte`
  - `udp_byteloss_s_c` = `s_udps_sndbyte` - `c_udps_rcvbyte`
  - `udp_byteloss_ratio` = (`udp_byteloss_s_c` + `udp_byteloss_c_s`) / (`c_udps_sndbyte` + `s_udps_sndbyte`)
- Session integrity
  - `udp_attempted_transaction_count` = `client_udps_connects`
  - `udp_failed_transaction_count` = `server_udps_accepts` - `client_udps_connects`

#### CPS Trial PASS

PASS of CPS test trial is conditioned on all of the following criteria being met:

- PASS-C1 TRex must attempt all configured `max_session_number` in `target_setup_duration` time
   - IOW TRex must send connect packets at configured `trial_cps_rate`.
- PASS-C2 Following TRex errors ARE NOT recorded in Counters-Target-Set:
  - Traffic Client
    - `udps_keepdrops`, TRex out of capacity, dropping UDP KAs(?)
    - `err_rx_throttled`, TRex out of capacity, throttling workers due to Rx overload(?)
    - `err_c_nf_throttled`, Number of client side flows that were not opened due to flow-table overflow(?)
    - `err_flow_overflow`, too many flows(?)
  - Traffic Server
    - `err_rx_throttled`, TRex out of capacity, throttling workers due to Rx overload(?)

#### CPS-MRR

Reported MRR values are equal to the following TRex counters from Counters-Target-Set:
- `c_m_est_flows`
- `s_m_est_flows`

TODO Add description of separate set of tests for discovering a **safe**
CPS-MTR value (Maximum Transmit Rate) for TRex, where TRex errors are
observed in Counters-Target-Set.

#### CPS-PDR

Note: Unless otherwise stated, all listed TRex counter values are from
Counters-Target-Set.

CPS-PDR values are discovered using MLRsearch, a binary search optimized
for the overall test duration.

CPS-PDR = `trial_cps_rate`, if all of the following conditions are met:

- `pktloss_ratio` < `target_packet_loss_ratio`
- `udp_pktloss_ratio` < `target_packet_loss_ratio`

Measurements to be reported in the CPS-PDR result test message:

- `trial_cps_rate`
- `c_m_est_flows`
- `s_m_est_flows`

CPS-NDR = `trial_cps_rate`, if all of the following conditions are met

- `pktloss_ratio` = 0
- `udp_pktloss_ratio` < `target_packet_loss_ratio`

Measurements to be reported in the CPS-PDR result test message:

- `trial_cps_rate`
- `c_m_est_flows`
- `s_m_est_flows`

#### CPS-NDR

Note: Unless otherwise stated, all listed TRex counter values are from
Counters-Target-Set.

CPS-NDR values are discovered using MLRsearch, a binary search optimized
for the overall test duration.

CPS-NDR = `trial_cps_rate`, if all of the following conditions are met:

- `pktloss_ratio` = 0
- `udp_pktloss_ratio` = 0

Measurements to be reported in the CPS-PDR result test message:

- `trial_cps_rate`
- `c_m_est_flows`
- `s_m_est_flows`

### VPP Telemetry

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

