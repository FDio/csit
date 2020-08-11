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
    - [CPS Trial PASS](#cps-trial-pass)
    - [CPS-MRR](#cps-mrr-1)
    - [CPS-PDR](#cps-pdr-1)
    - [CPS-NDR](#cps-ndr-1)
  - [TCP/IP VPP Telemetry](#tcpip-vpp-telemetry)
    - [Counters](#counters-3)
    - [Errors](#errors-1)

<!-- /MarkdownTOC -->

## Tests for NAT44ED

Two types of stateful tests are developed for NAT44ED (source network address
and port translation IPv4 to IPv4 with 5-tuple session state):

- Connections-Per-Second (CPS), discovering the maximum rate of creating
  NAT44ED sessions. Measured separately for UDP and TCP connections and
  for different session scale.

- Packets-Per-Second (PPS), discovering the maximum rate of
simultaneously creating NAT44ED sessions and transfering bulk of data
packets across the corresponding connections. Measured separately for
UDP and TCP connections with different session scale and different data
packet sizes per each connection. Current code is using 64B only for UDP
and default MSS 1460B for TCP/IP.

This note describes CPS tests.

## CPS Test Objectives

Discover DUT's highest sustain rate of creating fully functional NAT44ED
5-tuple stateful session entries. Session entry is considered fully
functional, if packets associated with this entry are NAT44ED processed
by DUT and forwarded in both directions without loss.

Similarly to packet throughput tests, three CPS rates are discovered:

- CPS-MRR, verified connection rate at maximal connection attempt rate,
  regardless of an amount of not established connections. (Connections
  per Second - Maximum Receive Rate.)
- CPS-NDR, maximal connection attempt rate at which all connections get
  established. (Connections per Second - Non Drop Rate.)
- CPS-PDR, maximal connection attempt rate at which ratio of not
  established connections to attempted connections is below configured
  threshold. (Connections per Second - Partial Drop Rate.)

## Input Parameters

- `max_cps_rate`, maximum rate of attempting connections, to be used by
  traffic generator, limited by traffic generator capabilities, Ethernet
  link(s) rate and NIC model.
- `min_cps_rate`, minimum rate of establishing connections to be used for
  measurements. Search fails if lower transmit rate needs to be used to
  meet search criteria.
- `target_session_number`, maximum number of sessions to be established and
  tested.
- `target_loss_ratio`, maximum acceptable connections loss ratio search
  criteria for PDR measurements with UDP tests. Indicates packet drop
  impact on connection establishment rate.
- `final_relative_width`, required measurement resolution expressed as
  (lower_bound, upper_bound) interval width relative to upper_bound.
- stateful traffic profiles, TRex ASTF program defining the connection
  per L4 protocol tested (TCP, UDP), including connect and
  close sequence.

## Stateful traffic profiles

TRex ASTF program defines following TCP and UDP transactions for
discovering NAT44ED CPS limits:

- CPS with TCP
  - connect(syn,syn-ack,ack)
    - pkts client tx 2, rx 1
    - pkts server tx 1, rx 2
  - delay (note: optional, currently not implemented)
    - no packets
  - close(fin,fin-ack,ack,ack)
    - pkts client tx 2, rx 2
    - pkts server tx 1, rx 2
- CPS with UDP
  - connect_and_close(req,ack)
    - pkts client tx 1, rx 1
    - pkts server tx 1, rx 1

TRex ASTF program configuration parameters:

- `limit` of connections, set to `target_session_number`.
- `multiplier`, represents `trial_cps_rate`, a number of connections per
  second to be executed per trial. Multiplier applies to connect phases.
  Close phases occur automatically based on arrival of the last packet
  expected per session.
- IPv4 source and destination address and port ranges matching the
  limit of connections.
  - Source and destination addresses changing packet-by-packet with two
    separate profiles i) incrementing sequentially pair-wise
    (implemented) and ii) changed randomly (with seed) pair-wise (not
    implemented yet).
  - Source port changing randomly within the range.
- `trial_duration`, function of `target_session_number` and `multiplier`
  - `multiplier`, subject of the search, value in the range (`min_cps_rate`,`max_cps_rate`)
  - `target_setup_duration` = `target_session_number` / `trial_cps_rate`
  - For UDP:
    - `trial_duration` = `target_setup_duration` + `late_traffic_start_correction`
    - `late_traffic_start_correction` = 0.1115 seconds (hardcoded for now)
  - For TCP:
    - `trial_duration` = 2 * `target_setup_duration` + `late_traffic_start_correction`
    - `late_traffic_start_correction` = 0.1115 seconds (hardcoded for now)

## UDP CPS Tests

### UDP TRex Measurements

#### Counters

Following TRex ASTF counters are collected by UDP CPS tests for automated
results evaluation (r) and debugging purposes (d):

- Interface 1 Client
  - (r) `opackets`, TRex UDP transaction start
  - (r) `ipackets`, TRex UDP transaction finish
- Interface 2 Server
  - (d) `opackets`
  - (d) `ipackets`
- Traffic Client
  - (d) `m_active_flows`
  - (d) `m_est_flows`
  - (d) `m_traffic_duration`, includes TRex ramp-up overhead, and it can
    be quite far from the actual traffic duration
  - (d) `udps_connects`
  - (d) `udps_closed`
  - (d) `udps_sndbyte`
  - (d) `udps_sndpkt`
  - (d) `udps_rcvbyte`
  - (d) `udps_rcvpkt`
  - (d) `udps_keepdrops`, TRex out of capacity, dropping UDP KAs(?)
<!--
Vratko Polak: Yes, although the traffic profile should have set large
enough keepalive value so zero KA packets are actually sent within the
trial. I did not actually check the value is large enough for the worst
case (ndrpdr search hitting min multiplier of 9001).
-->
  - (d) `err_rx_throttled`, TRex out of capacity, throttling workers due
    to Rx overload(?)
<!--
Vratko Polak: I think this is TRex receiving the packet on L2 level, but
then dropping it because L7 buffers are full. Such packet increases
ipackets, but does not increase any L7 counter (even if traffic profile
wants to receive that packet). But this is just me guessing. TRex docs
say "rx thread was throttled due too many packets in NIC rx queue", and
I did no experiments/investigation to confirm my hypothesis fits with
the observed counters.
-->
  - (d) `err_c_nf_throttled`, Number of client side flows that were not
    opened due to flow-table overflow(?)
  - (d) `err_flow_overflow`, too many flows(?)
- Traffic Server
  - (d) `m_active_flows`
  - (d) `m_est_flows`
  - (r) `m_traffic_duration`
  - (d) `udps_accepts`
  - (d) `udps_closed`
  - (d) `udps_sndbyte`
  - (d) `udps_sndpkt`
  - (d) `udps_rcvbyte`
  - (d) `udps_rcvpkt`
  - (d) `err_rx_throttled`, TRex out of capacity, throttling workers due
    to Rx overload(?)

[TRex ASTF counters reference](https://trex-tgn.cisco.com/trex/doc/trex_astf.html#_counters_reference).

TRex counters are polled once TRex confirms traffic is stopped, after it
is explicitly instructed to stop it. Early attempts to use periodic TRex
counter polling affected TRex behaviour and test results, hence counter
polling is consider as invasive.

#### Calculations

- Interface packet loss
  - pktloss_ratio = (c_opackets - c_ipackets) / c_opackets
- UDP session packet loss (currently not used)
- UDP session byte loss (currently not used)
- UDP session integrity (currently not used)

#### CPS-MRR

Reported MRR values are calculated as follows:

CPS-MRR = `c_ipackets` / `s_traffic_duration`, where
`s_traffic_duration` = TRex Traffic Server `m_traffic_duration`.

In order to ensure a determnistic region of TRex ASTF operation, a
separate set of tests is run for each traffic profile, with vpp-ip4base
DUT instead of vpp-nat44ed, to auto-discover the maximum rate TRex ASTF
traffic profile is capable of. Result of this test is used as a side
reference to compare with the results of NAT44ed CPS-MRR tests.

#### CPS-PDR

CPS-PDR values are discovered using MLRsearch, a binary search optimized
for the overall test duration.

CPS-PDR = max(`trial_cps_rate`) found for `pktloss_ratio` <
`target_loss_ratio`, according to MLRsearch criteria for PDR.

Measurements to be reported in the CPS-PDR result test message:

- PDR_LOWER

#### CPS-NDR

CPS-NDR values are also discovered using MLRsearch.

CPS-NDR = max(`trial_cps_rate`) found for `pktloss_ratio` = 0, according
to MLRsearch criteria for PDR.

Measurements to be reported in the CPS-NDR result test message:

- NDR_LOWER

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
  show hardware verbose (10.30.51.54 - /run/vpp/api.sock):
  Name                Idx   Link  Hardware
  avf-0/3b/2/0                       1     up   avf-0/3b/2/0
    Link speed: 25 Gbps
    Ethernet address 3c:fe:bd:f9:00:00
    flags: initialized admin-up vaddr-dma link-up rx-interrupts
    offload features: l2 vlan rx-polling rss-pf
    num-queue-pairs 3 max-vectors 5 max-mtu 0 rss-key-size 52 rss-lut-size 64
    speed
    stats:
      rx bytes             69368896
      rx unicast           135301620
      rx discards          94585780
      tx bytes             2401281120
      tx unicast           40021352
  avf-0/3b/a/0                       2     up   avf-0/3b/a/0
    Link speed: 25 Gbps
    Ethernet address 3c:fe:bd:f9:01:00
    flags: initialized admin-up vaddr-dma link-up rx-interrupts
    offload features: l2 vlan rx-polling rss-pf
    num-queue-pairs 3 max-vectors 5 max-mtu 0 rss-key-size 52 rss-lut-size 64
    speed
    stats:
      rx bytes             40912192
      rx unicast           134856987
      rx discards          94835635
      tx bytes             2442955680
      tx unicast           40715928
  ```

- VPP show runtime

  ```
  Thread 1 vpp_wk_0 (lcore 2)
  Time 21.5, 10 sec internal node vector rate 0.00 loops/sec 6740197.88
    vector rates in 4.2183e3, out 3.7118e3, drop 0.0000e0, punt 0.0000e0
               Name                 State         Calls          Vectors        Suspends         Clocks       Vectors/Call
  avf-0/3b/2/0-output              active                277           34387               0          1.96e1          124.14
  avf-0/3b/2/0-tx                  active                277           34387               0          3.54e1          124.14
  avf-0/3b/a/0-output              active                380           45245               0          1.92e1          119.07
  avf-0/3b/a/0-tx                  active                380           45245               0          3.36e1          119.07
  avf-input                        polling         144384995           90499               0          3.03e5            0.00
  ethernet-input                   active                381           90499               0          1.91e1          237.53
  ip4-input-no-checksum            active                381           90499               0          4.94e1          237.53
  ip4-lookup                       active                521           79632               0          3.76e1          152.84
  ip4-rewrite                      active                521           79632               0          4.19e1          152.84
  ip4-sv-reassembly-feature        active                381           90499               0          3.78e1          237.53
  nat44-ed-in2out                  active                380           45245               0          1.98e2          119.07
  nat44-ed-in2out-slowpath         active                380           45245               0          2.31e3          119.07
  nat44-ed-out2in                  active                277           34387               0          1.89e2          124.14
  nat44-in2out-worker-handoff      active                381           90499               0          9.42e1          237.53
  unix-epoll-input                 polling            140863               0               0          1.61e3            0.00
  ---------------
  Thread 2 vpp_wk_1 (lcore 58)
  Time 21.5, 10 sec internal node vector rate 0.00 loops/sec 6733488.17
    vector rates in 3.3365e3, out 3.5604e3, drop 0.0000e0, punt 0.0000e0
               Name                 State         Calls          Vectors        Suspends         Clocks       Vectors/Call
  avf-0/3b/2/0-output              active                276           31129               0          2.03e1          112.79
  avf-0/3b/2/0-tx                  active                276           31129               0          3.63e1          112.79
  avf-0/3b/a/0-output              active                332           45254               0          1.87e1          136.31
  avf-0/3b/a/0-tx                  active                332           45254               0          3.48e1          136.31
  avf-input                        polling         166439403           71581               0          4.42e5            0.00
  ethernet-input                   active                277           65516               0          1.89e1          236.52
  ip4-input-no-checksum            active                277           65516               0          4.95e1          236.52
  ip4-lookup                       active                455           76383               0          3.75e1          167.87
  ip4-rewrite                      active                455           76383               0          4.20e1          167.87
  ip4-sv-reassembly-feature        active                277           65516               0          3.85e1          236.52
  nat44-ed-in2out                  active                377           45254               0          1.97e2          120.04
  nat44-ed-in2out-slowpath         active                332           45254               0          2.39e3          136.31
  nat44-ed-out2in                  active                276           31129               0          1.83e2          112.79
  nat44-out2in-worker-handoff      active                277           65516               0          2.17e2          236.52
  unix-epoll-input                 polling            140817               0               0          1.60e3            0.00
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
  - (d) `opackets`
  - (d) `packets`
- Interface 2 Server
  - (d) `opackets`
  - (d) `packets`
- Traffic Client
  - (d) `m_active_flows`
  - (d) `m_est_flows`
  - (d) `m_traffic_duration`
  - (r) `tcps_connattempt`
  - (d) `tcps_connects`
  - (d) `tcps_closed`
- Traffic Server
  - (d) `m_active_flows`
  - (d) `m_est_flows`
  - (r) `m_traffic_duration`
  - (d) `tcps_accepts`
  - (r) `tcps_connects`
  - (d) `tcps_closed`
  - (d) `err_no_template`, server can’t match L7 template no destination port or IP range

[TRex ASTF counters reference](https://trex-tgn.cisco.com/trex/doc/trex_astf.html#_counters_reference).

TRex counters are polled only once by CSIT after traffic is stopped.

#### Calculations

TODO WIP Note: Currently s_tcp_connects is used for counting successful
sessions. But now I am not sure whether it is correct, as already
c_tcps_connects counts NAT sessions that got established (even though
TCP is not fully connected yet). Not sure how the counters behave when
the third packet is lost and retransmitted.

- Interface packet loss
  - `pktloss_c_s` = `c_opackets` - `s_ipackets`
  - `pktloss_s_c` = `s_opackets` - `c_ipackets`
  - `pktloss_ratio` = (`pktloss_s_c` + `pktloss_c_s`) / (`c_opackets` + `s_opackets`)
- TCP session integrity
  - `tcp_attempted_connection_count` = `c_tcps_connattempt`
  - `tcp_failed_connection_count` = `c_tcps_connects` - `c_tcps_connattempt`

#### CPS Trial PASS

TODO WIP Note: Currently any trial measurement fails only if TRex itself
fails, or if we fail to parse some counter. No criteria mentioned here
is currently planned to be implemented; we rely on bad things leading to
too few (maybe zero) passed transactions.

<!--
PASS of TCP CPS test trial is conditioned on all of the following criteria being met:

- PASS-C1 TRex must attempt all configured `target_session_number` in `target_setup_duration` time
   - IOW TRex must send connect packets at configured `trial_cps_rate`.
- PASS-C2 Following TRex errors ARE NOT recorded in Target-Counters:
  - Traffic Client
    - No errors recorded so far
  - Traffic Server
    - `err_no_template`, server can’t match L7 template no destination port or IP range
-->

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