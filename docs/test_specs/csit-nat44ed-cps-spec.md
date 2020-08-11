## Content

<!-- MarkdownTOC autolink="true" -->

- [Tests for NAT44-ED](#tests-for-nat44-ed)
- [CPS Test Objectives](#cps-test-objectives)
- [Input Parameters](#input-parameters)
- [TRex ASTF Program for CPS](#trex-astf-program-for-cps)
- [UDP Measurements and Counters](#udp-measurements-and-counters)
  - [UDP TRex Packets and Sessions](#udp-trex-packets-and-sessions)
  - [UDP TRex Errors](#udp-trex-errors)
  - [UDP VPP Packets and Sessions](#udp-vpp-packets-and-sessions)
  - [UDP VPP Errors](#udp-vpp-errors)
- [TCP Measurements and Counters](#tcp-measurements-and-counters)
  - [TCP TRex Packets and Sessions](#tcp-trex-packets-and-sessions)
  - [TCP TRex Errors](#tcp-trex-errors)
  - [TCP VPP Packets and Sessions](#tcp-vpp-packets-and-sessions)
  - [TCP VPP Errors](#tcp-vpp-errors)
- [CPS Methodology](#cps-methodology)
  - [CPS-MRR](#cps-mrr)
  - [CPS-NDRPDR](#cps-ndrpdr)

<!-- /MarkdownTOC -->

## Tests for NAT44-ED

Two types of tests are developed for NAT44-ED (source network address
and port translation IPv4 to IPv4 with 5-tuple session state):

- Calls-Per-Second, CPS
- Transactions-Per-Second, TPS

Both test types are to be executed separately per each L4 protocol:
TCP/IP and UDP.

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

- max_cps_rate, maximum rate of establishing connections, to be used by
  traffic generator, limited by traffic generator capabilities, Ethernet
  link(s) rate and NIC model.
- min_cps_rate, minimum rate of establishing connections to be used for
  measurements. Search fails if lower transmit rate needs to be used to
  meet search criteria.
- max_session_number, maximum number of sessions to be established and
  tested.
- packet_loss_ratio, maximum acceptable PLR search criteria for PDR
  measurements.
- final_relative_width, required measurement resolution expressed as
  (lower_bound, upper_bound) interval width relative to upper_bound.
- TRex ASTF program, defining the CPS transaction per L4
  protocol tested, including connect sequence (TCP, UDP), delay, close
  sequence, delay. Delay phases are required to account for successfully
  established and closed sessions with associated packet and session
  counters.

## TRex ASTF Program for CPS

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

- Limit of sessions, set to max_session_number.
- IPv4 source and destination address and port ranges matching the
  limit of sessions.
  - Source and destination address changing packet-by-packet with two
    separate profiles i) incrementing sequentially pair-wise and ii)
    changed randomly (with seed) pair-wise.
  - Source port changing randomly within the range.
- Multiplier, target number of transactions per second to be executed.
  Multiplier applies to connect and close phases.
- Duration of trial, function of max_session_number and trial_cps_rate
  - For TCP: 2 x (max_session_number / trial_cps_rate) + 2 x Delay
  - For UDP: (max_session_number / trial_cps_rate) + Delay

## UDP Measurements and Counters

TRex counters polled every set interval (1 sec?).

### UDP TRex Packets and Sessions

```
#### Statistics #####
{
  "1.0088909808546305": {
    "0": {
pp    "opackets": 57481,
pp    "ipackets": 57440,
    },
    "1": {
pp    "opackets": 57440,
pp    "ipackets": 57481,
    },
    "traffic": {
      "client": {
dd      "m_active_flows": 73,
dd      "m_est_flows": 73,
pp      "udps_connects": 57513,
pp      "udps_closed": 57440,
pp      "udps_sndpkt": 57513,
pp      "udps_rcvpkt": 57440
      },
      "server": {
pp      "udps_accepts": 57481,
pp      "udps_closed": 57481,
pp      "udps_sndpkt": 57481,
pp      "udps_rcvpkt": 57481
      }
  }

dd debugging counters
pp primary counters for search and results
ss secondary counters for results
```

Primary counters calculations (TODO to be completed):

- Packet loss
  - int_client_to_server = client_opackets - server_ipackets
  - int_server_to_client = server_opackets - client_ipackets
  - udp_client_to_server = client_udps_sndpkt - server_udps_rcvpkt
  - udp_server_to_client = server_udps_sndpkt - client_udps_rcvpkt
- Session integrity
  - attempted_transaction_count = client_udps_connects
  - failed_transaction_count = server_udps_accepts - client_udps_connects
- To be analysed
  - m_active_flows
  - m_est_flows

[TRex ASTF counters reference](https://trex-tgn.cisco.com/trex/doc/trex_astf.html#_counters_reference).

### UDP TRex Errors

```
  "traffic": {
    "client": {
pp    "udps_keepdrops": 26713,
dd    "err_rx_throttled": 2
pp    "err_c_nf_throttled": 2285312,
pp    "err_flow_overflow": 3563
    },
    "server": {
dd    "err_rx_throttled": 1
    }
  }

dddd debugging errors
pppp primary errors for search and results
```

Primary errors (TODO to be completed):

- "udps_keepdrops", TRex out of capacity, dropping UDP KAs(?)
- "err_c_nf_throttled", TRex out of capacity, throttling workers(?)
- "err_flow_overflow", unknown flow(?)

Debug errors:
- "err_rx_throttled", TRex rx worker throttled down.

[TRex ASTF counters reference](https://trex-tgn.cisco.com/trex/doc/trex_astf.html#_counters_reference).

### UDP VPP Packets and Sessions

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

### UDP VPP Errors

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

## TCP Measurements and Counters

TRex counters polled every set interval (1 sec?).

### TCP TRex Packets and Sessions

```
#### Statistics #####
{
  "36.203108912333846": {
    "0": {
pp      "opackets": 50491515,
pp      "ipackets": 50499873,
    },
    "1": {
pp      "opackets": 50499873,
pp      "ipackets": 50491515,
    },
    "traffic": {
        "client": {
pp          "m_active_flows": 0,
pp          "m_est_flows": 0,
pp          "tcps_connattempt": 64512,
pp          "tcps_connects": 64512,
pp          "tcps_closed": 64512,
dd          "tcps_segstimed": 1977964,
dd          "tcps_rttupdated": 1979334,
dd          "tcps_delack": 55330,
pp          "tcps_sndtotal": 50491515,
pp          "tcps_sndpack": 50125824,
dd          "tcps_sndbyte": 300754944,
dd          "tcps_sndbyte_ok": 300754944,
dd          "tcps_sndctrl": 129024,
dd          "tcps_sndacks": 210155,
dd          "tcps_rcvpack": 50190336,
dd          "tcps_rcvbyte": 300754944,
dd          "tcps_rcvackpack": 1914822,
dd          "tcps_rcvackbyte": 300754944,
dd          "tcps_rcvackbyte_of": 64512,
dd          "tcps_preddat": 48456027,
dd          "tcps_sndwinup": 26512,
dd          "err_rx_throttled": 6551
        },
        "server": {
pp          "m_active_flows": 0,
pp          "m_est_flows": 0,
pp          "tcps_accepts": 64512,
pp          "tcps_connects": 64512,
pp          "tcps_closed": 64512,
dd          "tcps_segstimed": 1905136,
dd          "tcps_rttupdated": 1906572,
dd          "tcps_delack": 109358,
pp          "tcps_sndtotal": 50499873,
pp          "tcps_sndpack": 50125824,
dd          "tcps_sndbyte": 300754944,
dd          "tcps_sndbyte_ok": 300754944,
dd          "tcps_sndctrl": 64512,
dd          "tcps_sndacks": 273719,
dd          "tcps_rcvpack": 50190336,
dd          "tcps_rcvbyte": 300754944,
dd          "tcps_rcvackpack": 1906572,
dd          "tcps_rcvackbyte": 300754944,
dd          "tcps_rcvackbyte_of": 129024,
dd          "tcps_preddat": 48455919,
dd          "tcps_sndwinup": 35818,
dd          "tcps_rcvdupack": 64512,
dd          "err_rx_throttled": 12724
        }

dd debugging counters
pp primary counters for search and results
ss secondary counters for results
```

Primary counters calculations (TODO to be completed):

- Packet loss
  - int_client_to_server = client_opackets - server_ipackets
  - int_server_to_client = server_opackets - client_ipackets
  - tcp_client_to_server = client_tcps_sndpack - server_tcps_rcvpack
  - tcp_server_to_client = server_tcps_sndpack - client_tcps_rcvpack
- Session integrity
  - attempted_transaction_count = client_tcps_connattempt
  - failed_transaction_count = server_tcps_connects - client_tcps_connattempt
  - established_sessions = client_m_est_flows = server_m_est_flows
- To be analysed
  - m_active_flows
  - tcps_sndwinup, window update-only packets sent

[TRex ASTF counters reference](https://trex-tgn.cisco.com/trex/doc/trex_astf.html#_counters_reference).

### TCP TRex Errors

```
  "traffic": {
      "client": {
          "tcps_sndwinup": 26512,
          "err_rx_throttled": 6551
      },
      "server": {
          "tcps_sndwinup": 35818,
          "tcps_rcvdupack": 64512,
          "err_rx_throttled": 12724
      }

dd debugging errors
pp primary errors for search and results
```

Primary errors (TODO to be completed):

- ...

Debug errors (TODO to be completed):

- "err_rx_throttled", TRex rx worker throttled down.

[TRex ASTF counters reference](https://trex-tgn.cisco.com/trex/doc/trex_astf.html#_counters_reference).

### TCP VPP Packets and Sessions

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

### TCP VPP Errors

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

## CPS Methodology

### CPS-MRR

### CPS-NDRPDR
